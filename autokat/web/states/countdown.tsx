import React from 'react';
import { CountdownState, PlayingState } from '../hooks/gamestate';
import { Poly } from '../components/poly';
import { Playing } from './playing';

export function Countdown({state, time}: { state: CountdownState, time: number }) {
    return (
        <>
            <Playing state={state.playing_state}></Playing>
            <div style={{position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)"}}>
                <h1>{Math.ceil(state.start_at - time)}</h1>
            </div>
        </>
    )
}