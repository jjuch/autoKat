#ifdef GL_ES
precision mediump float;
#endif

// plasma: https://www.shadertoy.com/view/XsjXRm

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

const float PI = 3.14159265359;

float sign(vec2 p1, vec2 p2, vec2 p3) {
    return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y);
}

vec2 flipY(vec2 st) {
    return vec2(st.x, u_resolution.y - st.y);
}

float segmentDistance(vec2 a, vec2 b, vec2 p) {
    float nom = abs(
        (b.y - a.y) * p.x
        - (b.x - a.x) * p.y
        + b.x * a.y
        - b.y * a.x
    );
    float denom = distance(a, b);
    return denom > 0.0 ? nom / denom : distance(a, p);
}

vec4 disco(vec2 p, float rot) {

    mat2 rotationMatrix = mat2(
        cos(rot), -sin(rot),
        sin(rot), cos(rot)
    );
    p = rotationMatrix * p;
    float subdivisions = 10.0;
    float deltaAngle = PI / subdivisions;
    float deltaDistance = 1.0 / subdivisions;
    float deltaSlope = PI / subdivisions;
    float angle = atan(p.y, p.x);
    float distance = length(p);
    float slope = asin(distance);

    float angleBottomLeft = floor(angle / deltaAngle) * deltaAngle;
    float angleBottomRight = ceil(angle / deltaAngle) * deltaAngle;
    float angleTopLeft = angleBottomLeft;
    float angleTopRight = angleBottomRight;

    float slopeBottomLeft = floor(slope / deltaSlope) * deltaSlope;
    float slopeBottomRight = slopeBottomLeft;
    float slopeTopLeft = ceil(slope / deltaSlope) * deltaSlope;
    float slopeTopRight = slopeTopLeft;

    float distanceBottomLeft = sin(slopeBottomLeft);
    float distanceBottomRight = sin(slopeBottomRight);
    float distanceTopLeft = sin(slopeTopLeft);
    float distanceTopRight = sin(slopeTopRight);

    vec2 bottomLeft = vec2(distanceBottomLeft * cos(angleBottomLeft), distanceBottomLeft * sin(angleBottomLeft));
    vec2 bottomRight = vec2(distanceBottomRight * cos(angleBottomRight), distanceBottomRight * sin(angleBottomRight));
    vec2 topLeft = vec2(distanceTopLeft * cos(angleTopLeft), distanceTopLeft * sin(angleTopLeft));
    vec2 topRight = vec2(distanceTopRight * cos(angleTopRight), distanceTopRight * sin(angleTopRight));

    float edgeDistance = min(
        segmentDistance(bottomLeft, bottomRight, p),
        min(
            segmentDistance(bottomRight, topRight, p),
            min(
                segmentDistance(topRight, topLeft, p),
                segmentDistance(topLeft, bottomLeft, p)
            )
        )
    );
    float alpha = 1.0 - step(1.0, distance);
    float textureAngle = angleBottomRight + mod(rot, 2.0 * PI);
    textureAngle = mod(textureAngle + 20.0 * PI, 2.0 * PI);
    vec2 textureCoord = vec2(textureAngle / PI / 2.0, (slopeBottomLeft) / PI * 2.0);
    vec4 edgeColor = vec4(0.1, 0.1, 0.1, 1.0);
    vec4 caveColor = (texture2D(u_cave, textureCoord) + 0.05) * 1.04;
    float mixStep = smoothstep(0.0, 0.02, edgeDistance);
    vec4 color = mix(edgeColor, caveColor, mixStep);
    vec4 green = vec4(0.0, 1.0, 0.0, 1.0);
    float redComponent = clamp(dot(rotationMatrix * normalize(flipY(u_redLight) - u_resolution.xy / 2.0), normalize(bottomRight)), 0.0, 1.0);
    float greenComponent = clamp(dot(rotationMatrix * normalize(flipY(u_greenLight) - u_resolution.xy / 2.0), normalize(bottomRight)), 0.0, 1.0);
    vec4 red = vec4(1.0, 0.0, 0.0, 1.0);
    color += red * redComponent * 0.3 + green * greenComponent * 0.3;
    color.a = alpha;
    return color;
}

bool pointInTriangle (vec2 pt, vec2 v1, vec2 v2, vec2 v3) {
    float d1 = sign(pt, v1, v2);
    float d2 = sign(pt, v2, v3);
    float d3 = sign(pt, v3, v1);

    bool has_neg = (d1 < 0.0) || (d2 < 0.0) || (d3 < 0.0);
    bool has_pos = (d1 > 0.0) || (d2 > 0.0) || (d3 > 0.0);

    return !(has_neg && has_pos);
}

void main() {
    vec2 st = gl_FragCoord.xy / u_resolution.xy;

    vec4 red = vec4(1.0, 0.0, 0.0, 1.0);
    vec4 green = vec4(0.0, 1.0, 0.0, 1.0);
    vec4 black = vec4(0.1, 0.1, 0.1, 1.0);
    vec3 multiplierRgb = vec3(0.1, 0.1, 0.1);
    bool inRed = pointInTriangle(gl_FragCoord.xy, flipY(u_redCone1), flipY(u_redCone2), flipY(u_redCone3));
    float inRedF = inRed ? 1.0 : 0.0;
    bool inGreen = pointInTriangle(gl_FragCoord.xy, flipY(u_greenCone1), flipY(u_greenCone2), flipY(u_greenCone3));
    float inGreenF = inGreen ? 1.0 : 0.0;
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
        vec4 caveColor = texture2D(u_cave, st);
        vec2 edgeDistanceVector = u_resolution.xy * 0.5 - abs(gl_FragCoord.xy - u_resolution.xy * 0.5);
        float edgeDistance = min(edgeDistanceVector.x, edgeDistanceVector.y);
        float edgeFactor = 1.0 - smoothstep(0.0, 10.0, edgeDistance);
        vec4 discoColor = disco((gl_FragCoord.xy - u_resolution.xy * 0.5) / u_ballRadius, u_time);
        vec4 color = mix(caveColor* multiplier + multiplier * 0.15, multiplier, edgeFactor * max(inRedF, inGreenF));
        // color += discoColor * discoColor.a;
        color = mix(color, discoColor, discoColor.a);
        gl_FragColor = color;
    }
    
}
