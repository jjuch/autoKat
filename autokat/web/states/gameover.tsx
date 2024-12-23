import React from "react";
import {
  CountdownState,
  GameOverState,
  PlayingState,
} from "../hooks/gamestate";
import { Poly } from "../components/poly";
import { Playing } from "./playing";

export function GameOver({
  state,
  time,
}: {
  state: GameOverState;
  time: number;
}) {
  const n = 10;
  const hue = (time * 200) % 360;
  return (
    <>
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          textShadow: `0px 0px 40px currentColor}`,
          textAlign: "center",
          fontSize: 40,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
        }}
      >
        <div
          style={{
            position: "absolute",
            left: 0,
            right: 0,
            width: "100%",
            height: "100%",
            background: "url(/static/cave.png)",
            backgroundSize: "cover",
            zIndex: -100,
            filter: `hue-rotate(${hue}deg)`,
          }}
        ></div>
        <img src="static/socrates-sunglasses.png" alt="socrates-sunglasses" style={{ position: "absolute", top: 30 + 5 * Math.sin(time * 15), left: 30, width: 200, height: 200, objectFit: 'contain'}} />
        <img src="static/plato-sunglasses.png" alt="plato-sunglasses" style={{ position: "absolute", top: 30 + 5 * Math.sin(time * 15 + 2), right: 30, width: 200, height: 200, objectFit: 'contain'}} />
        <div style={{ marginBottom: 40, fontSize: 60 }}>GAME OVER</div>
        <div>
          <table
            style={{
              textAlign: "left",
              marginRight: "auto",
              marginLeft: "auto",
              backdropFilter: "brightness(50%) blur(10px)",
            }}
          >
            {state.top_highscores.slice(0, n).map((hs, i) => (
              <tr
                key={i}
                style={{
                  fontWeight: i === state.my_highscore_index ? 800 : 400,
                }}
              >
                <td style={{ paddingRight: 20 }}>{i + 1}.</td>
                <td style={{ paddingRight: 40 }}>{hs.team_name}</td>
                <td>{hs.score}</td>
              </tr>
            ))}
            {state.my_highscore_index > n && (
              <tr>
                <td colSpan={3} style={{ textAlign: "left" }}>
                  ...
                </td>
              </tr>
            )}
            {state.my_highscore_index + 1 > n && (
              <tr style={{ fontWeight: 800 }}>
                <td style={{ paddingRight: 20 }}>
                  {state.my_highscore_index + 1}.
                </td>
                <td style={{ paddingRight: 40 }}>
                  {state.my_highscore.team_name}
                </td>
                <td>{state.my_highscore.score}</td>
              </tr>
            )}
          </table>
        </div>
        <span style={{ position: "absolute", bottom: 20, right: 20, textAlign: 'right' }}>
          {Math.ceil(state.to_intro_at - time)}
        </span>
      </div>
    </>
  );
}
