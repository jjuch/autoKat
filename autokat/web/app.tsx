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

function Sheep({ x, y, heading = 0, color = "green", scale = 1 }) {
  const transform = `translate(${x - 15}px,${
    y - 15
  }px) rotate(${heading}rad) scale(${scale})`;
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
          strokeWidth: 1,
        }}
      ></ellipse>
    </g>
  );
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
      <Finlet x={-45} length={14} color={color} t={t - 0.3}></Finlet>
      <Finlet x={-30} length={16} color={color} t={t - 0.2}></Finlet>
      <Finlet x={-15} length={18} color={color} t={t - 0.1}></Finlet>
      <Finlet x={0} length={20} color={color} t={t + 0.0}></Finlet>
      <Finlet x={15} length={18} color={color} t={t + 0.1}></Finlet>
      <Finlet x={30} length={16} color={color} t={t + 0.2}></Finlet>
      <Finlet x={45} length={14} color={color} t={t + 0.3}></Finlet>
      <Finlet
        x={-45}
        length={14}
        color={color}
        t={t - 0.3}
        direction="up"
      ></Finlet>
      <Finlet
        x={-30}
        length={16}
        color={color}
        t={t - 0.2}
        direction="up"
      ></Finlet>
      <Finlet
        x={-15}
        length={18}
        color={color}
        t={t - 0.1}
        direction="up"
      ></Finlet>
      <Finlet
        x={0}
        length={20}
        color={color}
        t={t + 0.0}
        direction="up"
      ></Finlet>
      <Finlet
        x={15}
        length={18}
        color={color}
        t={t + 0.1}
        direction="up"
      ></Finlet>
      <Finlet
        x={30}
        length={16}
        color={color}
        t={t + 0.2}
        direction="up"
      ></Finlet>
      <Finlet
        x={45}
        length={14}
        color={color}
        t={t + 0.3}
        direction="up"
      ></Finlet>
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
  const [[introBoxX1, introBoxY1], [introBoxX2, introBoxY2]] =
    gameState.intro_box;
  let caughtSheep = 0;
  let totalSheep = gameState.sheep.length;
  gameState.sheep.forEach(s => {
    if (s.state === 'caught') {
      caughtSheep += 1;
    }
  })
  return (
    <>
      <svg>
        {gameState.state !== "intro" ? null : (
          <>
            <text
              x={(introBoxX1 + introBoxX2) / 2}
              y={introBoxY1 - 10}
              fill="#34ebcf"
              style={{
                fontSize: "40px",
                dominantBaseline: "auto",
                textAnchor: "middle",
              }}
            >
              MOVE HERE
            </text>
            <rect
              x={introBoxX1}
              y={introBoxY1}
              width={introBoxX2 - introBoxX1}
              height={introBoxY2 - introBoxY1}
              stroke="blue"
              strokeWidth={4}
              strokeDasharray={"10"}
            ></rect>
            <text
              x={(introBoxX1 + introBoxX2) / 2}
              y={introBoxY2 + 10}
              fill="#34ebcf"
              style={{
                fontSize: "40px",
                dominantBaseline: "hanging",
                textAnchor: "middle",
              }}
            >
              TO START
            </text>
          </>
        )}
        {gameState.state !== "playing" ? null : (
          <g>
            <text x={SCREEN_WIDTH / 2} y={10} fill="#34ebcf"
              style={{
                fontSize: "40px",
                dominantBaseline: "hanging",
                textAnchor: "middle",
              }}>You've caught {caughtSheep} of {totalSheep} sinesquids</text>
            <Maelstrom
              x={gameState.maelstrom.center[0]}
              y={gameState.maelstrom.center[1]}
              r={gameState.maelstrom.radius}
            ></Maelstrom>
            {gameState.sheep.map((e) => (
              <Sheep
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
        {gameState.state}
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
        <video
          src="/static/instructions.mp4"
          autoPlay={true}
          loop={true}
          style={{
            width: 320,
            height: 240,
          }}
        ></video>
        <div
          style={{
            paddingLeft: "2em",
            paddingTop: "1em",
            fontFamily: "impact",
            fontSize: "30px",
          }}
        >
          <ol>
            <li>
              Put on the tin-foil hat (it keeps Jupiter's hard radiation from
              boiling your brain)
            </li>
            <li>
              Befriend an alien squid by putting it on your head. Hold on tight!
            </li>
            <li>Aim its laser to guide the blue Anomacollie</li>
            <li>Herd the green Sinesquids into the maelstrom</li>
          </ol>
        </div>
      </div>
    </>
  );
}
const root = createRoot(document.getElementById("root"));
root.render(<App></App>);
