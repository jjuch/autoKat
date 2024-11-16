import React from 'react';
import { IntroState, Polygon } from '../hooks/gamestate';
import { Playing } from './playing';

const bounds = (poly: Polygon) => {
    const xs = poly.map(([x, y]) => x);
    const ys = poly.map(([x, y]) => y);
    return {
        left: Math.min(...xs),
        right: Math.max(...xs),
        top: Math.min(...ys),
        bottom: Math.max(...ys),
    }
}

// box-shadow: 0px 0px 20px 34px rgba(45,255,196,0.52);

function StartBox({poly, color}: { poly: Polygon, color: string }) {
    const b = bounds(poly);
    return (
        <div style={{
            position: "absolute",
            top: b.top,
            left: b.left,
            width: b.right - b.left,
            height: b.bottom - b.top,
            borderWidth: 3,
            borderColor: color,
            borderStyle: "dashed",
            fontSize: 40,
            color: color,
            display: "flex",
            justifyContent: "center",
            flexDirection: "column",
            textAlign: "center",
            textShadow: `0px 0px 40px ${color}`,
            backgroundColor: "rgba(0,0,0,0.5)",
        }}>
            MOVE {color.toUpperCase()} LASER HERE TO START
        </div>
    )
}
export function Intro({state, time}: { state: IntroState, time: number }) {
    return (
        <>
            <div style={{
                position: "absolute",
                top: 30,
                left: "0",
                width: '100%',
                color: 'rgb(252, 3, 236)',
                textShadow: `0px 0px 40px currentColor}`,
                textAlign: "center",
                fontSize: 40,
            }}>
                <div>THE {state.team_name.toUpperCase()}'{state.team_name.endsWith('s') ? '' : 'S'}</div>
                <div style={{ fontSize: 48}}>RAVE CAVE</div>
            </div>
            <StartBox poly={state.red_start_box} color="red"></StartBox>
            <StartBox poly={state.green_start_box} color="green"></StartBox>
        </>
    )
}