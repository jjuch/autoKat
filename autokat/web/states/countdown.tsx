import React from 'react';
import { CountdownState, PlayingState } from '../hooks/gamestate';
import { Poly } from '../components/poly';
import { Playing } from './playing';

export function Countdown({state, time}: { state: CountdownState, time: number }) {
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
                <div>GET READY</div>
                <div>{state.playing_state.team_name.toUpperCase()}</div>
            </div>
            <div style={{position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)"}}>
                <h1>{Math.ceil(state.start_at - time)}</h1>
            </div>
        </>
    )
}