import * as React from "react";
import { createRoot } from "react-dom/client";
import { useGameState } from "./hooks/gamestate";
import { useEffect, useState } from "react";
import { useAnimationFrame } from "./hooks/animation";

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

function Dog({ x, y, heading = 0, color = "green" }) {
  const transform = `translate(${x}px,${y}px) rotate(${heading}rad)`;
  const [t, setT] = useState<number>(0);
  useAnimationFrame(({t: animationTime}) => {
    setT(animationTime);
  })
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

function App() {
  const gameState = useGameState();
  const [pointerX, pointerY] = gameState.pointer_position;
  useEffect(() => {
    window.addEventListener("mousemove", (e) => {
      gameState.setDummyPosition(e.clientX, e.clientY);
    });
  });
  return (
    <svg>
      {gameState.sheep.map((e) => (
        <Dog
          key={e.id}
          x={e.x}
          y={e.y}
          heading={e.heading}
          color="green"
        ></Dog>
      ))}
      <Dog
        key={gameState.dog.id}
        x={gameState.dog.x}
        y={gameState.dog.y}
        heading={gameState.dog.heading}
        color="blue"
      ></Dog>
      <circle cx={pointerX} cy={pointerY} stroke="yellow" r={4}></circle>
    </svg>
  );
}
const root = createRoot(document.getElementById("root"));
root.render(<App></App>);
