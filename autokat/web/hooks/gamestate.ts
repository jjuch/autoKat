import { useEffect, useRef, useState } from "react";

export const useGameState = () => {
  const [gameState, setGameState] = useState({
    sheep: [] as any[],
    dog: {x: 0, y: 0, id: 1_000_000, type: 'dog', heading: 0},
    total_dt: 0 as number,
    pointer_position: [0, 0],
    setDummyPosition(x, y) {},
  });
  const ws = useRef<null | WebSocket>(null);
  useEffect(() => {
    ws.current = new WebSocket(`ws://${document.location.host}/ws`);
    ws.current.addEventListener("message", (message) => {
      setGameState({
        ...JSON.parse(message.data),
        setDummyPosition(x, y) {
          ws.current?.send(JSON.stringify([x, y]));
        },
      });
    });
  }, []);
  return gameState;
};
