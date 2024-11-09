import * as React from "react";
import { createRoot } from "react-dom/client";
import { useGame } from "./hooks/gamestate";
import { SVGProps, useCallback, useEffect, useState } from "react";
import { useAnimationFrame, useAnimationTime } from "./hooks/animation";
import { Maelstrom } from "./maelstrom";
import { Playing } from "./states/playing";
import { Countdown } from "./states/countdown";
import { Intro } from "./states/intro";

const SCREEN_WIDTH = 1024;
const SCREEN_HEIGHT = 768;

function Tail({
  x,
  y,
  t,
  length = 70,
  curls = 2,
  width = 20,
  color = "green",
}) {
  let pathParts: string[] = [`M${x},${y}`];
  for (let sx = 0; sx < length; sx++) {
    const sy =
      Math.sin((2 * Math.PI * sx * curls) / length - t * Math.PI * curls) *
      width *
      (sx / length);
    pathParts.push(`L${-sx + x},${-sy + y}`);
  }
  return (
    <path
      d={pathParts.join(" ")}
      style={{ stroke: color, fill: "none" }}
    ></path>
  );
}

function Sheep({ id, x, y, heading = 0, color = "green", scale = 1 }) {
  heading = 0;
  const transform = `translate(${x}px,${
    y
  }px)`;
  const t = useAnimationTime();
  const hueRot = Math.PI / 2;
  return (
    <g
      className="entity"
      style={{
        transform,
        filter: `hue-rotate(${hueRot}rad)`,
      }}
    >
      <image href="/static/christmas-gift-doodle.gif" width="60" style={{transform: `scale(${scale}) translate(-30px, -35px) rotate(${heading}rad)`}}></image>
      {/* <circle cx={0} cy={0} r={3} fill="yellow"></circle> */}
    </g>
  );
}


function Dog({ x, y, heading, color = "#037ffc" }) {
  const transform = `rotate(${heading}rad) scaleX(-1)`;
  const t = useAnimationTime();
  return (
    <g className="entity" style={{ transform: `translate(${x - 50}px,${y - 80}px)`}}>
      <g
        className="entity"
        style={{
          transform,
          transformOrigin: '50px 80px',
          strokeWidth: 4
        }}
      >
      <image href="/static/tree2.gif" width={100}></image>
      </g>
    </g>
  );
}


function App() {
  const [gameState, sendCommand] = useGame();
  const [pointerX, pointerY] = gameState.debug.red_position;
  useEffect(() => {
    window.addEventListener("mousemove", (e) => {
      sendCommand({ type: "pointer", position: [e.clientX, e.clientY], color: "red" });
    });
  }, []);
  const [calibrating, setCalibrating] = useState(false);
  useEffect(() => {
    window.addEventListener("keydown", (e) => {
      switch (e.key) {
        case "c":
          setCalibrating((c) => !c);
          break;
        case "q":
          sendCommand({
            type: "calibration",
            corner: "top_left",
          });
          break;
        case "w":
          sendCommand({
            type: "calibration",
            corner: "top_right",
          });
          break;
        case "a":
          sendCommand({
            type: "calibration",
            corner: "bottom_left",
          });
          break;
        case "s":
          sendCommand({
            type: "calibration",
            corner: "bottom_right",
          });
          break;
      }
    });
  }, []);
  // style={{ transform: `translate(${gameState.state.red_light[0]} - 0}px,${gameState.state.red_light[1] - 0}px)`}}
  return (
    <>
        {(gameState.state.name === "playing" || gameState.state.playing_state) && (
          <Playing state={'playing_state' in gameState.state ? gameState.state.playing_state : gameState.state} />
        )}
        {gameState.state.name === "countdown" && (
          <Countdown state={gameState.state} time={gameState.time}/>
        )}
        {gameState.state.name === "intro" && (
          <Intro state={gameState.state} time={gameState.time}/>
        )}
        {!calibrating ? null : (
          <svg>
            {/* pointer position dot */}
            <circle
              cx={pointerX}
              cy={pointerY}
              stroke="yellow"
              r={6}
              fill="yellow"
            ></circle>
            {/* pointer position text */}
            <text
              x={300}
              y={300}
              stroke="yellow"
              fill="yellow"
              style={{ fontSize: "20px" }}
            >
              pointer {Math.round(pointerX)}, {Math.round(pointerY)}
            </text>
            {/* corner dots and coordinates */}
            <circle cx={0} cy={0} stroke="yellow" r={6} fill="yellow"></circle>
            <text
              x={10}
              y={10}
              stroke="yellow"
              fill="yellow"
              style={{
                fontSize: "20px",
                dominantBaseline: "hanging",
                textAnchor: "start",
              }}
            >
              {gameState.calibration.top_left?.map(Math.round).join(",")}
            </text>
            <circle
              cx={0}
              cy={SCREEN_HEIGHT - 1}
              stroke="yellow"
              r={6}
              fill="yellow"
            ></circle>
            <text
              x={10}
              y={SCREEN_HEIGHT - 1}
              stroke="yellow"
              fill="yellow"
              style={{
                fontSize: "20px",
                dominantBaseline: "auto",
                textAnchor: "start",
              }}
            >
              {gameState.calibration.bottom_left?.map(Math.round).join(",")}
            </text>
            <circle
              cx={SCREEN_WIDTH - 1}
              cy={0}
              stroke="yellow"
              r={6}
              fill="yellow"
            ></circle>
            <text
              x={SCREEN_WIDTH - 1 - 10}
              y={10}
              stroke="yellow"
              fill="yellow"
              style={{
                fontSize: "20px",
                dominantBaseline: "hanging",
                textAnchor: "end",
              }}
            >
              {gameState.calibration.top_right?.map(Math.round).join(",")}
            </text>
            <circle
              cx={SCREEN_WIDTH - 1}
              cy={SCREEN_HEIGHT - 1}
              stroke="yellow"
              r={6}
              fill="yellow"
            ></circle>
            <text
              x={SCREEN_WIDTH - 1 - 10}
              y={SCREEN_HEIGHT - 1 - 10}
              stroke="yellow"
              fill="yellow"
              style={{
                fontSize: "20px",
                dominantBaseline: "auto",
                textAnchor: "end",
              }}
            >
              {gameState.calibration.bottom_right?.map(Math.round).join(",")}
            </text>
          </svg>
        )}
    </>
  );
}
const root = createRoot(document.getElementById("root"));
root.render(<App></App>);
