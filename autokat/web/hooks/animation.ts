import { useEffect, useRef } from "react";

export const useAnimationFrame = (callback) => {
  // Use useRef for mutable variables that we want to persist
  // without triggering a re-render on their change
  const requestRef = useRef<ReturnType<typeof requestAnimationFrame>>(0);
  const previousTimeRef = useRef<number>();

  const animate: FrameRequestCallback = (t) => {
    if (previousTimeRef.current != undefined) {
      const dt = t - previousTimeRef.current;
      callback({t: t / 1000, dt: dt / 1000});
    }
    previousTimeRef.current = t;
    requestRef.current = requestAnimationFrame(animate);
  };

  useEffect(() => {
    requestRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(requestRef.current);
  }, []); // Make sure the effect runs only once
};
