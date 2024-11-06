import React from "react";
import { SVGProps } from "react";

export function Poly({ points, ...rest }: Omit<SVGProps<SVGPolygonElement>, 'points'> & { points: [number, number][] }) {
    return (
      <polygon
        points={points.map((p) => p.join(",")).join(" ")}
        {...rest}
      ></polygon>
    );
  }