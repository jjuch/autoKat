import React from 'react';
import { CountdownState, IntroState, PlayingState } from '../hooks/gamestate';
import { Poly } from '../components/poly';
import { Playing } from './playing';

export function Intro({state, time}: { state: IntroState, time: number }) {
    return (
        <>
            <Playing state={state.playing_state}></Playing>
            <div style={{position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)"}}>
                <h1>LOOOOL</h1>
            </div>
        </>
    )
}