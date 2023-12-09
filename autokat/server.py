from __future__ import annotations
import asyncio
from contextlib import asynccontextmanager
import datetime
import json
import os
from threading import Thread
from autokat.game import Game
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.staticfiles import StaticFiles

from autokat.track import Coords, DummyTracker, LaserTracker

task_started = False
tick_time = 0.1
tracker = LaserTracker()
dummy_tracker = DummyTracker()
if os.environ.get('POINTER', 'dummy') == 'dummy':
    tracker = dummy_tracker


async def run_game():
    start_time = datetime.datetime.now(tz=datetime.timezone.utc)
    last_current_time = start_time
    game = Game()
    await asyncio.sleep(tick_time)
    while True:
        current_time = datetime.datetime.now(tz=datetime.timezone.utc)
        dt = current_time - last_current_time
        total_dt = current_time - start_time
        game.tick(pointer_location=tracker.position, total_dt=total_dt, dt=dt, time_since_last_detection=tracker.time_since_last_detection)
        await manager.broadcast(json.dumps({**game.to_dict(), "calibration": tracker.calibration.to_dict()}))
        current_time = datetime.datetime.now(tz=datetime.timezone.utc)
        await asyncio.sleep(
            tick_time
        )
        last_current_time = current_time


@asynccontextmanager
async def lifespan(app: FastAPI):
    thread = Thread(target=tracker.run)
    thread.start()
    asyncio.create_task(run_game())
    yield
    # thread.join()


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="autokat/web/static"), name="static")


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()

templates = Jinja2Templates(directory="autokat/web/templates")


@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            raw_data = await websocket.receive_text()
            # print(raw_data)
            data = json.loads(raw_data)
            match data:
                case {"type": "pointer", "position": [x, y]}:
                    dummy_tracker.position = (x, y)
                case {"type": "calibration", "corner": corner}:
                    tracker.update_calibration(**{corner: Coords(*tracker.raw_position)})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
