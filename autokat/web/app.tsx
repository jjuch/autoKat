import * as React from "react";
import { createRoot } from "react-dom/client";
import { useGameState } from "./hooks/gamestate";
import { useCallback, useEffect, useState } from "react";
import { useAnimationFrame, useAnimationTime } from "./hooks/animation";
import { Maelstrom } from "./maelstrom";

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

function Sheep({ x, y, heading = 0, color = "green" }) {
  const transform = `translate(${x}px,${y}px) rotate(${heading}rad)`;
  const t = useAnimationTime();
  return (
    <g
      className="entity"
      style={{
        transform,
      }}
    >
      <polygon
        points="0,0 30,0, 30,30, 0,30"
        style={{ stroke: color }}
      ></polygon>

      <Tail x={0} y={0} t={t} color={color}></Tail>
      <Tail x={0} y={15} t={t} color={color}></Tail>
      <Tail x={0} y={30} t={t} color={color}></Tail>
    </g>
  );
}

function Finlet({x, length, color, t, direction = 'down'}) {
  return (
    <g>
      <ellipse
        cx={x}
        cy={(direction === 'down' ? 1 : -1) * 34}
        rx={8}
        ry={length * 2}
        stroke={color}
        style={{ transform: `rotate3d(1, 0, 0, ${Math.sin(Math.PI * t) * Math.PI / 4}rad)`, strokeWidth: 1 }}
      ></ellipse>
    </g>
  )
}
function Dog({ x, y, heading, color = "blue" }) {
  const transform = `translate(${x}px,${y}px) rotate(${heading}rad)`;
  const t = useAnimationTime();
  return (
    <g
      className="entity"
      style={{
        transform,
      }}
    >
      <Finlet x={-45} length={14} color={color} t={t - .3}></Finlet>
      <Finlet x={-30} length={16} color={color} t={t - .2}></Finlet>
      <Finlet x={-15} length={18} color={color} t={t - .1}></Finlet>
      <Finlet x={0} length={20} color={color} t={t + .0}></Finlet>
      <Finlet x={15} length={18} color={color} t={t + .1}></Finlet>
      <Finlet x={30} length={16} color={color} t={t + .2}></Finlet>
      <Finlet x={45} length={14} color={color} t={t + .3}></Finlet>
      <Finlet x={-45} length={14} color={color} t={t - .3} direction="up"></Finlet>
      <Finlet x={-30} length={16} color={color} t={t - .2} direction="up"></Finlet>
      <Finlet x={-15} length={18} color={color} t={t - .1} direction="up"></Finlet>
      <Finlet x={0} length={20} color={color} t={t + .0} direction="up"></Finlet>
      <Finlet x={15} length={18} color={color} t={t + .1} direction="up"></Finlet>
      <Finlet x={30} length={16} color={color} t={t + .2} direction="up"></Finlet>
      <Finlet x={45} length={14} color={color} t={t + .3} direction="up"></Finlet>
      <ellipse
        cx={0}
        cy={0}
        rx={60}
        ry={20}
        stroke={color}
        style={{ strokeWidth: 2 }}
      ></ellipse>
      <circle cx={60} cy={10} stroke={color} r={6}></circle>
      <circle cx={60} cy={-10} stroke={color} r={6}></circle>
    </g>
  );
}

function App() {
  const [gameState, sendCommand] = useGameState();
  const [pointerX, pointerY] = gameState.pointer_position;
  useEffect(() => {
    window.addEventListener("mousemove", (e) => {
      sendCommand({ type: "pointer", position: [e.clientX, e.clientY] });
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
  return (
    <svg>
      <Maelstrom x={200} y={400} size={100}></Maelstrom>
      {gameState.sheep.map((e) => (
        <Sheep
          key={e.id}
          x={e.x}
          y={e.y}
          heading={e.heading}
          color="green"
        ></Sheep>
      ))}
      <Dog
        key={gameState.dog.id}
        x={gameState.dog.x}
        y={gameState.dog.y}
        heading={gameState.dog.heading}
        color="blue"
      ></Dog>
      {!calibrating ? null : (
        <>
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
        </>
      )}
    </svg>
  );
}
const root = createRoot(document.getElementById("root"));
root.render(<App></App>);
