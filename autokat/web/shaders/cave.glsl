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
uniform float u_forbiddenRadius;

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

uniform sampler2D u_noise;
const float PI = 3.14159265359;


// Plasma Globe by nimitz (twitter: @stormoid)
// https://www.shadertoy.com/view/XsjXRm
// License Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License
// Contact the author for other licensing options

//looks best with around 25 rays
#define NUM_RAYS 13.

#define VOLUMETRIC_STEPS 19

#define MAX_ITER 35
#define FAR 6.



mat2 mm2(in float a){float c = cos(a), s = sin(a);return mat2(c,-s,s,c);}
float noise(float x ){return texture2D(u_noise, vec2(x*.01,1.)).x;}

float hash( float n ){return fract(sin(n)*43758.5453);}

float noise(in vec3 p)
{
	vec3 ip = floor(p);
    vec3 fp = fract(p);
	fp = fp*fp*(3.0-2.0*fp);
	
	vec2 tap = (ip.xy+vec2(37.0,17.0)*ip.z) + fp.xy;
	vec2 rg = texture2D( u_noise, (tap + 0.5)/256.0).yx;
	return mix(rg.x, rg.y, fp.z);
}

mat3 m3 = mat3( 0.00,  0.80,  0.60,
              -0.80,  0.36, -0.48,
              -0.60, -0.48,  0.64 );


#define plasma_time (u_time * 1.8)

//See: https://www.shadertoy.com/view/XdfXRj
float flow(in vec3 p, in float t)
{
	float z=2.;
	float rz = 0.;
	vec3 bp = p;
	for (float i= 1.;i < 5.;i++ )
	{
		p += plasma_time*.1;
		rz+= (sin(noise(p+t*0.8)*6.)*0.5+0.5) /z;
		p = mix(bp,p,0.6);
		z *= 2.;
		p *= 2.01;
        p*= m3;
	}
	return rz;	
}

//could be improved
float sins(in float x)
{
 	float rz = 0.;
    float z = 2.;
    for (float i= 0.;i < 3.;i++ )
	{
        rz += abs(fract(x*1.4)-0.5)/z;
        x *= 1.3;
        z *= 1.15;
        x -= plasma_time*.65*z;
    }
    return rz;
}

float segm( vec3 p, vec3 a, vec3 b)
{
    vec3 pa = p - a;
	vec3 ba = b - a;
	float h = clamp( dot(pa,ba)/dot(ba,ba), 0.0, 1. );	
	return length( pa - ba*h )*.5;
}

vec3 path(in float i, in float d)
{
    vec3 en = vec3(0.,0.,1.);
    float sns2 = sins(d+i*0.5)*0.22;
    float sns = sins(d+i*.6)*0.21;
    en.xz *= mm2((hash(i*10.569)-.5)*6.2+sns2);
    en.xy *= mm2((hash(i*4.732)-.5)*6.2+sns);
    return en;
}

vec2 map(vec3 p, float i)
{
	float lp = length(p);
    vec3 bg = vec3(0.);   
    vec3 en = path(i,lp);
    
    float ins = smoothstep(0.11,.46,lp);
    float outs = .15+smoothstep(.0,.15,abs(lp-1.));
    p *= ins*outs;
    float id = ins*outs;
    
    float rz = segm(p, bg, en)-0.011;
    return vec2(rz,id);
}

float march(in vec3 ro, in vec3 rd, in float startf, in float maxd, in float j)
{
	float precis = 0.001;
    float h=0.5;
    float d = startf;
    for( int i=0; i<MAX_ITER; i++ )
    {
        if( abs(h)<precis||d>maxd ) break;
        d += h*1.2;
	    float res = map(ro+rd*d, j).x;
        h = res;
    }
	return d;
}

//volumetric marching
vec3 vmarch(in vec3 ro, in vec3 rd, in float j, in vec3 orig)
{   
    vec3 p = ro;
    vec2 r = vec2(0.);
    vec3 sum = vec3(0);
    float w = 0.;
    for( int i=0; i<VOLUMETRIC_STEPS; i++ )
    {
        r = map(p,j);
        p += rd*.03;
        float lp = length(p);
        
        vec3 col = sin(vec3(1.05,2.5,1.52)*3.94+r.y)*.85+0.4;
        col.rgb *= smoothstep(.0,.015,-r.x);
        col *= smoothstep(0.04,.2,abs(lp-1.1));
        col *= smoothstep(0.1,.34,lp);
        sum += abs(col)*5. * (1.2-noise(lp*2.+j*13.+plasma_time*5.)*1.1) / (log(distance(p,orig)-2.)+.75);
    }
    return sum;
}

//returns both collision dists of unit sphere
vec2 iSphere2(in vec3 ro, in vec3 rd)
{
    vec3 oc = ro;
    float b = dot(oc, rd);
    float c = dot(oc,oc) - 1.;
    float h = b*b - c;
    if(h <0.0) return vec2(-1.);
    else return vec2((-b - sqrt(h)), (-b + sqrt(h)));
}

vec4 plasma(vec2 p)
{	
	//camera
    vec2 um = (u_redLight + u_greenLight) / 2.0 / u_resolution.xy-.5;
    
	//camera
	vec3 ro = vec3(0.,0.,5.);
    vec3 rd = normalize(vec3(p*.7,-1.5));
    mat2 mx = mm2(plasma_time*.4+um.x*6.);
    mat2 my = mm2(plasma_time*0.3+um.y*6.); 
    ro.xz *= mx;rd.xz *= mx;
    ro.xy *= my;rd.xy *= my;
    vec3 bro = ro;
    vec3 brd = rd;
	
    vec3 col = vec3(0.0125,0.,0.025);
    #if 1
    for (float j = 1.;j<NUM_RAYS+1.;j++)
    {
        ro = bro;
        rd = brd;
        mat2 mm = mm2((plasma_time*0.1+((j+1.)*5.1))*j*0.25);
        ro.xy *= mm;rd.xy *= mm;
        ro.xz *= mm;rd.xz *= mm;
        float rz = march(ro,rd,2.5,FAR,j);
		if ( rz >= FAR)continue;
    	vec3 pos = ro+rz*rd;
    	col = max(col,vmarch(pos,rd,j, bro));
    }
    #endif
    
    ro = bro;
    rd = brd;
    vec2 sph = iSphere2(ro,rd);
    
    if (sph.x > 0.)
    {
        vec3 pos = ro+rd*sph.x;
        vec3 pos2 = ro+rd*sph.y;
        vec3 rf = reflect( rd, pos );
        vec3 rf2 = reflect( rd, pos2 );
        float nz = (-log(abs(flow(rf*1.2,plasma_time)-.01)));
        float nz2 = (-log(abs(flow(rf2*1.2,-plasma_time)-.01)));
        col += (0.1*nz*nz* vec3(0.12,0.12,.5) + 0.05*nz2*nz2*vec3(0.55,0.2,.55))*0.8;
    }
    
	return vec4(col*1.3, 1.0);
}

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

vec4 disco(vec2 p, float rot, float reflectionRadius) {

    mat2 rotationMatrix = mat2(
        cos(rot), -sin(rot),
        sin(rot), cos(rot)
    );
    p = rotationMatrix * p;
    float distance = length(p);
    float alpha = 1.0 - step(1.0, distance);
    if (distance > reflectionRadius) {
        return vec4(0.0);
    }
    bool reflection = false;
    if (distance > 1.0) {
        distance = 1.0 - (distance - 1.0) / reflectionRadius;
        p = distance * normalize(p);
        alpha = 0.3;
        reflection = true;
    }
    // float reflectionSlope = atan(1.0 / distance);
    // float alpha = 1.0;
    
    // if (distance > 1.0) {
    //     p = normalize(p) * cos(reflectionSlope * 5.0);
    //     distance = length(p);
    //     // alpha = 0.3;
    // }
    float angle = atan(p.y, p.x);
    float subdivisions = 10.0;
    float deltaAngle = PI / subdivisions;
    float deltaDistance = 1.0 / subdivisions;
    float deltaSlope = PI / subdivisions;
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
    float textureAngle = angleBottomRight + mod(rot, 2.0 * PI);
    textureAngle = mod(textureAngle + 20.0 * PI, 2.0 * PI);
    vec2 textureCoord = vec2(textureAngle / PI / 2.0, (slopeBottomLeft) / PI * 2.0);
    vec4 edgeColor = vec4(0.1, 0.1, 0.1, 1.0);
    vec2 texturePixel = vec2(1.0) / u_resolution;
    vec2 tdx = vec2(texturePixel.x, 0.0);
    vec2 tdy = vec2(0.0, texturePixel.y);
    vec4 textureColor = (
        texture2D(u_cave, textureCoord)
        + texture2D(u_cave, textureCoord + tdx)
        + texture2D(u_cave, textureCoord - tdx)
        + texture2D(u_cave, textureCoord + tdy)
        + texture2D(u_cave, textureCoord - tdy)
        + texture2D(u_cave, textureCoord + tdx + tdy)
        + texture2D(u_cave, textureCoord - tdx + tdy)
        + texture2D(u_cave, textureCoord + tdx - tdy)
        + texture2D(u_cave, textureCoord - tdx - tdy)
    ) / 9.0;
    vec4 caveColor = (textureColor + 0.05) * 1.04;
    float mixStep = smoothstep(0.0, reflection ? 0.04 : 0.02, edgeDistance);
    vec4 color = mix(edgeColor, caveColor, mixStep);
    vec4 green = vec4(0.0, 1.0, 0.0, 1.0);
    float redComponent = clamp(dot(rotationMatrix * normalize(flipY(u_redLight) - u_resolution.xy / 2.0), normalize(bottomRight)), 0.0, 1.0);
    float greenComponent = clamp(dot(rotationMatrix * normalize(flipY(u_greenLight) - u_resolution.xy / 2.0), normalize(bottomRight)), 0.0, 1.0);
    vec4 red = vec4(1.0, 0.0, 0.0, 1.0);
    color += red * redComponent * 0.3 + green * greenComponent * 0.3;
    color.a = alpha;
    if (reflection) {
        color.a = smoothstep(0.5, 0.8, length(color.rgb)) * 0.3;
        color = (color + vec4(0.5, 0.5, 0.5, 0.0)) / 1.4;
        color.a = 0.0;
    }
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

const vec4 fuschia = vec4(252.0, 3.0, 236.0, 255.0) / 255.0;

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

    vec4 caveColor = texture2D(u_cave, st);
    vec2 edgeDistanceVector = u_resolution.xy * 0.5 - abs(gl_FragCoord.xy - u_resolution.xy * 0.5);
    float edgeDistance = min(edgeDistanceVector.x, edgeDistanceVector.y);
    float edgeFactor = 1.0 - smoothstep(0.0, 10.0, edgeDistance);
    vec4 discoColor = disco(
        (gl_FragCoord.xy - u_resolution.xy * 0.5) / u_ballRadius,
        u_time * .8,
        u_forbiddenRadius / u_ballRadius
    );
    vec4 color = mix(caveColor* multiplier + multiplier * 0.15, multiplier, edgeFactor * max(inRedF, inGreenF));
    // color += discoColor * discoColor.a;
    color = mix(color, discoColor, discoColor.a);

    float ballDistance = distance(gl_FragCoord.xy, flipY(u_ballPosition));
    if (u_ballRadius > 0.0 && ballDistance <= u_ballRadius * 1.1) {
        vec2 relativePoint = (gl_FragCoord.xy - flipY(u_ballPosition)) / u_ballRadius;
        vec4 plasmaColor = plasma(relativePoint/ 2.0);
        float ballAngle = atan(relativePoint.y, relativePoint.x);
        vec4 border = mix(
            color,
            fuschia,
            (1.0 - step(1.05 + sin(u_time * 10.0 + ballAngle * 6.0) * sin(u_time * 5.0 - ballAngle * 4.0) / 20.0, ballDistance / u_ballRadius))) * 0.8;
        color = mix(plasmaColor, border, smoothstep(0.9, 1.0, ballDistance / u_ballRadius));
    }

    gl_FragColor = color;
}
