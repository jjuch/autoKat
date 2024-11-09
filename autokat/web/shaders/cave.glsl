#ifdef GL_ES
precision mediump float;
#endif

uniform vec2 u_resolution;
uniform vec2 u_mouse;
uniform float u_time;
uniform sampler2D u_cave;
uniform vec2 u_redLight;
uniform vec2 u_redCone1;
uniform vec2 u_redCone2;
uniform vec2 u_redCone3;
uniform vec2 u_greenLight;
uniform vec2 u_greenCone1;
uniform vec2 u_greenCone2;
uniform vec2 u_greenCone3;
uniform vec2 u_ballPosition;
uniform float u_ballRadius;

uniform sampler2D u_disco0;
uniform sampler2D u_disco1;
uniform sampler2D u_disco2;
uniform sampler2D u_disco3;
uniform sampler2D u_disco4;
uniform sampler2D u_disco5;
uniform sampler2D u_disco6;
uniform sampler2D u_disco7;
uniform sampler2D u_disco8;
uniform sampler2D u_disco9;
uniform sampler2D u_disco10;
uniform sampler2D u_disco11;

float sign(vec2 p1, vec2 p2, vec2 p3) {
    return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y);
}

bool pointInTriangle (vec2 pt, vec2 v1, vec2 v2, vec2 v3) {
    float d1 = sign(pt, v1, v2);
    float d2 = sign(pt, v2, v3);
    float d3 = sign(pt, v3, v1);

    bool has_neg = (d1 < 0.0) || (d2 < 0.0) || (d3 < 0.0);
    bool has_pos = (d1 > 0.0) || (d2 > 0.0) || (d3 > 0.0);

    return !(has_neg && has_pos);
}
vec2 flipY(vec2 st) {
    return vec2(st.x, u_resolution.y - st.y);
}
void main() {
    vec2 st = gl_FragCoord.xy / u_resolution.xy;

    vec4 red = vec4(1.0, 0.0, 0.0, 1.0);
    vec4 green = vec4(0.0, 1.0, 0.0, 1.0);
    vec4 black = vec4(0.1, 0.1, 0.1, 1.0);
    vec3 multiplierRgb = vec3(0.1, 0.1, 0.1);
    bool inRed = pointInTriangle(gl_FragCoord.xy, flipY(u_redCone1), flipY(u_redCone2), flipY(u_redCone3));
    bool inGreen = pointInTriangle(gl_FragCoord.xy, flipY(u_greenCone1), flipY(u_greenCone2), flipY(u_greenCone3));
    // if (!inRed && !inGreen) {
    //     multiplierRgb = vec3(1.0, 1.0, 1.0);
    // } else {
    if (inRed) {
        multiplierRgb += vec3(1.0, 0.1, 0.1);
    }
    if (inGreen) {
        multiplierRgb += vec3(0.1, 1.0, 0.1);
    }
    // }
    vec4 multiplier = vec4(clamp(multiplierRgb.rgb, vec3(0.0), vec3(1.0)), 1.0);
    // bool inTriangle = pointInTriangle(gl_FragCoord.xy, flipY(u_redCone1), flipY(u_redCone2), flipY(u_redCone3));
    // vec4 multiplier = inTriangle ? green : black;
    
    if (u_ballRadius > 0.0 && distance(gl_FragCoord.xy, flipY(u_ballPosition)) <= u_ballRadius) {
        vec2 tl = flipY(u_ballPosition) - vec2(u_ballRadius, u_ballRadius);
        vec2 br = flipY(u_ballPosition) + vec2(u_ballRadius, u_ballRadius);
        vec2 uv = (gl_FragCoord.xy - tl) / (br - tl);
        int frame = int(mod(u_time * 10.0, 12.0));
        vec4 disco;
        if (frame == 0) {
            disco = texture2D(u_disco0, uv);
        } else if (frame == 1) {
            disco = texture2D(u_disco1, uv);
        } else if (frame == 2) {
            disco = texture2D(u_disco2, uv);
        } else if (frame == 3) {
            disco = texture2D(u_disco3, uv);
        } else if (frame == 4) {
            disco = texture2D(u_disco4, uv);
        } else if (frame == 5) {
            disco = texture2D(u_disco5, uv);
        } else if (frame == 6) {
            disco = texture2D(u_disco6, uv);
        } else if (frame == 7) {
            disco = texture2D(u_disco7, uv);
        } else if (frame == 8) {
            disco = texture2D(u_disco8, uv);
        } else if (frame == 9) {
            disco = texture2D(u_disco9, uv);
        } else if (frame == 10) {
            disco = texture2D(u_disco10, uv);
        } else if (frame == 11) {
            disco = texture2D(u_disco11, uv);
        }
        gl_FragColor = disco * (vec4(1.0) - (multiplier == vec4(1.0) ? vec4(0.0) : multiplier));
    } else {
        gl_FragColor = texture2D(u_cave, st) * multiplier + multiplier * 0.15;
    }
    
}