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
  color: string;
};
export type GameCommand = CalibrationCommand | PointerCommand;

export type Polygon = [number, number][];

export type PlayingState = {
  name: "playing";
  red_light: [number, number];
  green_light: [number, number];
  ball: {
    position: [number, number];
    velocity: [number, number];
    radius: number;
  };
  pillar: {
    position: [number, number];
    radius: number;
    forbidden_radius: number;
  };
  red_cone: Polygon;
  green_cone: Polygon;
  team_name: string;
  demo_mode: boolean;
  scores: number[];
  max_lives: number;
}

export type CountdownState = {
  name: "countdown";
  start_at: number;
  time_left: number;
  playing_state: PlayingState;
}

export type IntroState = {
  name: "intro";
  playing_state: PlayingState;
  team_name: string;
  red_start_box: Polygon;
  green_start_box: Polygon;
  in_red_start_box: boolean;
  in_green_start_box: boolean;
}

type Highscore = {
  team_name: string;
  score: number;
}

export type GameOverState = {
  name: "game_over";
  scores: number[];
  team_name: string;
  to_intro_at: number;
  top_highscores: Highscore[];
  my_highscore: Highscore;
  my_highscore_index: number;
  skip_to_intro_box: Polygon;
}


type Game = {
  state: PlayingState | CountdownState | IntroState | GameOverState;
  debug: {
    red_position: [number, number];
    green_position: [number, number];
  };
  calibration: Calibration;
  time: number;
}

export const useGame = () => {
  const [gameState, setGameState] = useState<Game>({
    state: {
      name: "playing",
      red_light: [0, 0],
      green_light: [0, 0],
      ball: {
        position: [0, 0],
        velocity: [0, 0],
        radius: 10,
      },
      pillar: {
        position: [0, 0],
        radius: 10,
        forbidden_radius: 100,
      },
      red_cone: [],
      green_cone: [],
      scores: [0],
      max_lives: 5,
      team_name: "team",
      demo_mode: true,
    },
    debug: {
      red_position: [0, 0],
      green_position: [0, 0],
    },
    calibration: {} as Calibration,
    time: 0
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
        const parsedMessage = JSON.parse(message.data);
        switch (parsedMessage.type) {
          case "state":
            setGameState(parsedMessage);
            break;
          case "reload":
            document.location.reload();
            break
        }
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
