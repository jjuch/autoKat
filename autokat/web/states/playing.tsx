import React from 'react';
import { PlayingState } from '../hooks/gamestate';
import { Poly } from '../components/poly';

export function Playing({state}: { state: PlayingState}) {
    return (
        <svg>
            <circle className="" style={{ transform: `translate(${state.pillar.position[0] - 0}px,${state.pillar.position[1] - 0}px)`}} cx={0} cy={0} r={state.pillar.forbidden_radius} stroke="white" strokeWidth={2}></circle>
            <circle className="" style={{ transform: `translate(${state.pillar.position[0] - 0}px,${state.pillar.position[1] - 0}px)`}} cx={0} cy={0} r={state.pillar.radius} fill={"purple"}></circle>
            <circle className="entity" style={{ transform: `translate(${state.red_light[0] - 0}px,${state.red_light[1] - 0}px)`}} cx={0} cy={0} r={10} fill="red"></circle>
            
            <Poly points={state.red_cone} fill="red" opacity={0.5}></Poly>
            <Poly points={state.green_cone} fill="green" opacity={0.5}></Poly>
            {state.ball && (
                <circle className="" style={{ transform: `translate(${state.ball.position[0] - 0}px,${state.ball.position[1] - 0}px)`}} cx={0} cy={0} r={10} fill="blue"></circle>
            )}
        </svg>
    )
}