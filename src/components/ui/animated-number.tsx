'use client';

import { useEffect, useRef } from 'react';
import { animate, useInView, useMotionValue, useReducedMotion } from 'motion/react';

interface Props {
  value: number;
  duration?: number;
  className?: string;
  format?: (n: number) => string;
}

/** Counts up to `value` once visible, and tweens between later updates. */
export function AnimatedNumber({ value, duration = 1.1, className, format }: Props) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true });
  const reduce = useReducedMotion();
  const mv = useMotionValue(0);
  const fmt = format ?? ((n: number) => Math.round(n).toLocaleString('en-IN'));

  useEffect(() => {
    const unsub = mv.on('change', (v) => {
      if (ref.current) ref.current.textContent = fmt(v);
    });
    return unsub;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mv]);

  useEffect(() => {
    if (!inView) return;
    if (reduce) {
      mv.set(value);
      return;
    }
    const controls = animate(mv, value, { duration, ease: [0.22, 1, 0.36, 1] });
    return () => controls.stop();
  }, [inView, value, duration, reduce, mv]);

  return (
    <span ref={ref} className={className} aria-label={String(value)}>
      {fmt(reduce ? value : 0)}
    </span>
  );
}
