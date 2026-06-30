'use client'

import { motion, useReducedMotion } from "motion/react";
import type { ReactNode } from "react";

interface RevealProps {
    children: ReactNode;
    /** Retraso en segundos antes de animar. */
    delay?: number;
    className?: string;
}

/**
 * Revela su contenido al entrar en viewport (fade + subida).
 * Si el usuario pidió menos movimiento, se renderiza estático (visible).
 * `once: true` → no re-anima al volver a hacer scroll.
 */
export function Reveal({ children, delay = 0, className }: RevealProps) {
    const reduceMotion = useReducedMotion();

    if (reduceMotion) {
        return <div className={className}>{children}</div>;
    }

    return (
        <motion.div
            className={className}
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1], delay }}
        >
            {children}
        </motion.div>
    );
}
