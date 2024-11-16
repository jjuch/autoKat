from __future__ import annotations
import asyncio
from contextlib import asynccontextmanager
import datetime
import json
import os
from threading import Thread
import traceback

from watchfiles import awatch
from autokat.game import Game
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.staticfiles import StaticFiles

from autokat.multitrack import Detection, DummyMultiLaserTracker, MultiLaserTracker, ProcessingConfigEditor, Vec

task_started = False
tick_time = 0.03
laser_tracker = MultiLaserTracker()
dummy_tracker = DummyMultiLaserTracker()
if os.environ.get('POINTER', 'dummy') == 'dummy':
    laser_tracker = dummy_tracker


def _json_encoder_default(obj):
    if isinstance(obj, datetime.timedelta):
        return obj.total_seconds()
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

async def run_game():
    start_time = datetime.datetime.now(tz=datetime.timezone.utc)
    last_current_time = start_time
    game = Game(laser_tracker=laser_tracker)
    await asyncio.sleep(tick_time)
    while True:
        current_time = datetime.datetime.now(tz=datetime.timezone.utc)
        dt = current_time - last_current_time
        total_dt = current_time - start_time
        for message in game.tick(total_dt=total_dt, dt=dt):
            await manager.broadcast(json.dumps(message, default=_json_encoder_default))
        current_time = datetime.datetime.now(tz=datetime.timezone.utc)
        await asyncio.sleep(
            tick_time
        )
        last_current_time = current_time

async def autoreload_on_frontend_changes():
    async for change in awatch("autokat/web/static", "autokat/web/templates"):
        print(change)
        await manager.broadcast('{"type": "reload"}')

@asynccontextmanager
async def lifespan(app: FastAPI):
    thread = Thread(target=laser_tracker.run)
    thread.start()
    if hasattr(laser_tracker, "processing_config"):
        ProcessingConfigEditor(laser_tracker.processing_config).run_thread()
    asyncio.create_task(run_game())
    asyncio.create_task(autoreload_on_frontend_changes())
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
            try:
                await connection.send_text(message)
            except:
                traceback.print_exc()


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
                case {"type": "pointer", "position": [x, y], "color": color}:
                    dummy_tracker.detect(color, Vec(x, y))
                case {"type": "calibration", "corner": corner}:
                    laser_tracker.update_calibration(**{corner: Vec(*laser_tracker.last_detections["red"].camera_position)})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
