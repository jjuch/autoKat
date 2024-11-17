import React, { useEffect, useMemo, useRef } from 'react';
import { PlayingState } from '../hooks/gamestate';
import { Poly } from '../components/poly';
// import { Canvas } from 'glsl-canvas';
import GlslCanvas from 'glslCanvas'
import caveShader from '../shaders/cave.glsl';

export function Playing({state}: { state: PlayingState}) {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    // const ctx = canvasRef.current?.getContext("2d");
    const width = canvasRef.current?.width;
    const height = canvasRef.current?.height;
    const glsl = useMemo(() => {
        if (canvasRef.current) {
            const canvas = new GlslCanvas(canvasRef.current, {
                // vertexString: `...`,
                fragmentString: caveShader,
                // alpha: false,
                antialias: true,
                mode: 'flat',
                // extensions: ['EXT_shader_texture_lod']
            });
            for (let i = 0; i < 12; i++) {
                const padded = i.toString().padStart(5, '0');
                canvas.setUniform(`u_disco${i}`, `static/disco_${padded}.png`);
            }
            canvas.setUniform('u_cave', 'static/cave.png');
            canvas.setUniform('u_resolution', [width, height]);
            return canvas;
        }
    }, [canvasRef.current]);

    useEffect(() => {
        if (!glsl) {
            return;
        }
        glsl.setUniform('u_redCone1', ...state.red_cone[0]);
        glsl.setUniform('u_redCone2', ...state.red_cone[1]);
        glsl.setUniform('u_redCone3', ...state.red_cone[2]);
        glsl.setUniform('u_redLight', ...state.red_light);
        glsl.setUniform('u_greenCone1', ...state.green_cone[0]);
        glsl.setUniform('u_greenCone2', ...state.green_cone[1]);
        glsl.setUniform('u_greenCone3', ...state.green_cone[2]);
        glsl.setUniform('u_greenLight', ...state.green_light);
        glsl.setUniform('u_ballPosition', ...(state.ball?.position ?? [-100, -100]));
        // glsl.setUniform('u_ballPosition', 512, 386);
        glsl.setUniform('u_ballRadius', state.ball ? state.ball.radius : -1);
        glsl.setUniform('u_forbiddenRadius', state.pillar.forbidden_radius);
        glsl.setUniform('u_noise', "static/noise.png");
    }, [state, glsl])

    const allScores = [...state.scores, ...Array(state.max_lives - state.scores.length).fill(null)];
    return (
        <>
        <canvas width="1024" height="768" ref={canvasRef} data-textures="static/cave.png"></canvas>
        {/* // <svg>
        //     <circle className="" style={{ transform: `translate(${state.pillar.position[0] - 0}px,${state.pillar.position[1] - 0}px)`}} cx={0} cy={0} r={state.pillar.forbidden_radius} stroke="white" strokeWidth={2}></circle>
        //     <circle className="" style={{ transform: `translate(${state.pillar.position[0] - 0}px,${state.pillar.position[1] - 0}px)`}} cx={0} cy={0} r={state.pillar.radius} fill={"purple"}></circle>
        //     <circle className="entity" style={{ transform: `translate(${state.red_light[0] - 0}px,${state.red_light[1] - 0}px)`}} cx={0} cy={0} r={10} fill="red"></circle>
            
        //     <Poly points={state.red_cone} fill="red" opacity={0.5}></Poly>
        //     <Poly points={state.green_cone} fill="green" opacity={0.5}></Poly>
        //     {state.ball && (
        //         <circle className="" style={{ transform: `translate(${state.ball.position[0] - 0}px,${state.ball.position[1] - 0}px)`}} cx={0} cy={0} r={10} fill="blue"></circle>
        //     )}
        // </svg> */}
        <img src="static/plato.png" style={{width: 100, height: 100, position: "absolute", left: `${state.red_light[0]}px`, top: `${state.red_light[1]}px`, transform: "translate(-50%, -50%)", objectFit: 'contain'}} />
        <img src="static/socrates.png" style={{width: 100, height: 100, position: "absolute", left: `${state.green_light[0]}px`, top: `${state.green_light[1]}px`, transform: "translate(-50%, -50%)", objectFit: 'contain'}} />
        <div style={{ position: 'absolute', bottom: 20, width: '100%', fontSize: 34, display: state.demo_mode ? 'none' : 'block', textAlign: 'center'}}>
            {allScores.map((score, i) => (
                <><span key={i}>{score === null ? "--" : score}</span>{i < allScores.length - 1 ? ' / ' : ''}</>
            ))}
        </div>
        </>
    )
}