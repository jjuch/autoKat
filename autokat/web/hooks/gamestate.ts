import { useCallback, useEffect, useRef, useState } from "react";

type Calibration = {
  top_left?: [number, number];
  top_right?: [number, number];
  bottom_left?: [number, number];
  bottom_right?: [number, number];
};

type CalibrationCommand = {
  type: "calibration";
  corner: keyof Calibration;
};

type PointerCommand = {
  type: "pointer";
  position: [number, number];
};
export type GameCommand = CalibrationCommand | PointerCommand;

export const useGameState = () => {
  const [gameState, setGameState] = useState({
    sheep: [] as any[],
    dog: { x: 0, y: 0, id: 1_000_000, type: "dog", heading: 0 },
    total_dt: 0 as number,
    pointer_position: [0, 0],
    calibration: {} as Calibration,
    maelstrom: {
      center: [100, 100],
      radius: 100,
    },
    intro_box: [[0, 0], [100, 100]],
    state: 'intro' as 'intro' | 'playing' | 'victory',
  });
  const ws = useRef<null | WebSocket>(null);
  const sendCommand = useCallback(
    (command: GameCommand) => {
      console.log("command", command);
      ws.current?.send(JSON.stringify(command));
    },
    [ws]
  );
  useEffect(() => {
    function connect() {
      ws.current = new WebSocket(`ws://${document.location.host}/ws`);
      ws.current.addEventListener("message", (message) => {
        setGameState(JSON.parse(message.data));
      });
      ws.current.addEventListener('close', (e) => {
        setTimeout(connect, 500);
      });
      ws.current.addEventListener('error', (e) => {
        ws.current?.close();
      });
    }
    connect();
   
  }, []);
  return [gameState, sendCommand] as const;
};
