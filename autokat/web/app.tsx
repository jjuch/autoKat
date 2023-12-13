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

function Finlet({ x, length, color, t, direction = "down" }) {
  return (
    <g>
      <ellipse
        cx={x}
        cy={(direction === "down" ? 1 : -1) * 34}
        rx={8}
        ry={length * 2}
        stroke={color}
        style={{
          transform: `rotate3d(1, 0, 0, ${
            (Math.sin(Math.PI * t) * Math.PI) / 4
          }rad)`,
          strokeWidth: 2,
        }}
      ></ellipse>
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
  const [[introBoxX1, introBoxY1], [introBoxX2, introBoxY2]] =
    gameState.intro_box;
  let caughtSheep = 0;
  let totalSheep = gameState.sheep.length;
  gameState.sheep.forEach((s) => {
    if (s.state === "caught") {
      caughtSheep += 1;
    }
  });
  return (
    <>
      <svg>
      <Dog
          key={gameState.dog.id}
          x={gameState.dog.x}
          y={gameState.dog.y}
          heading={gameState.dog.heading}
        ></Dog>
        {gameState.state !== "intro" ? null : (
          <>
            <text
              x={(introBoxX1 + introBoxX2) / 2}
              y={introBoxY1 - 10}
              fill="green"
              style={{
                fontSize: "40px",
                dominantBaseline: "auto",
                textAnchor: "middle",
              }}
            >
              BEGIN
            </text>
            <rect
              x={introBoxX1}
              y={introBoxY1}
              width={introBoxX2 - introBoxX1}
              height={introBoxY2 - introBoxY1}
              stroke="green"
              strokeWidth={4}
              strokeDasharray={"10"}
            ></rect>
            <text
              x={(introBoxX1 + introBoxX2) / 2}
              y={introBoxY2 + 10}
              fill="green"
              style={{
                fontSize: "40px",
                dominantBaseline: "hanging",
                textAnchor: "middle",
              }}
            >
              HIER
            </text>
          </>
        )}
        {gameState.state !== "victory" ? null : (
          <g>
            <text
              x={SCREEN_WIDTH / 2}
              y={10}
              fill="green"
              style={{
                fontSize: "120px",
                dominantBaseline: "hanging",
                textAnchor: "middle",
              }}
            >
              HOERA!
            </text>
            <text
              x={SCREEN_WIDTH / 2}
              y={120}
              fill="green"
              style={{
                fontSize: "40px",
                dominantBaseline: "hanging",
                textAnchor: "middle",
              }}
            >
              <tspan x={SCREEN_WIDTH / 2} dy={40}>Je hebt kerstmis gered!</tspan>
              <tspan x={SCREEN_WIDTH / 2} dy={60}>Binnen {Math.round(gameState.seconds_to_next_game ?? 0)} seconden beginnen we opnieuw!</tspan>
            </text>
          </g>
        )}
        {gameState.state !== "playing" ? null : (
          <g>
            <text
              x={SCREEN_WIDTH / 2}
              y={10}
              fill="green"
              style={{
                fontSize: "40px",
                dominantBaseline: "hanging",
                textAnchor: "middle",
              }}
            >
              Je hebt {caughtSheep} van de {totalSheep} cadeautjes gevangen!
            </text>
            <Maelstrom
              x={gameState.maelstrom.center[0]}
              y={gameState.maelstrom.center[1]}
              // r={gameState.maelstrom.radius}
            ></Maelstrom>
            {gameState.sheep.map((e) => (
              <Sheep
                id={e.id}
                key={e.id}
                x={e.x}
                y={e.y}
                heading={e.heading}
                color="green"
                scale={e.scale}
              ></Sheep>
            ))}
          </g>
        )}
        
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
      <div
        style={{
          display: gameState.state === "intro" ? "flex" : "none",
          flexDirection: "row",
          position: "absolute",
          top: 0,
          left: 0,
          color: "#34ebcf",
        }}
      >
        
      </div>
    </>
  );
}
const root = createRoot(document.getElementById("root"));
root.render(<App></App>);
