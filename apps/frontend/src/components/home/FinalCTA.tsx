'use client'

import Link from "next/link";

export function FinalCTA() {
    return (
        <section className="mt-24 w-full">
            <div className="relative overflow-hidden rounded-2xl bg-[#0284c7] px-8 py-14 sm:px-14 sm:py-16 text-center shadow-[0_8px_30px_rgb(2,132,199,0.18)]">
                {/* Halo sutil, decorativo */}
                <div
                    aria-hidden="true"
                    className="absolute -top-24 left-1/2 -translate-x-1/2 w-[420px] h-[420px] bg-white/10 rounded-full blur-[90px] pointer-events-none"
                />

                <div className="relative z-10 flex flex-col items-center">
                    <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white text-balance max-w-2xl mb-4">
                        Decide tu próximo semestre con datos, no de oído.
                    </h2>
                    <p className="text-sky-50 text-sm sm:text-base font-medium max-w-xl mb-8">
                        Crea tu cuenta gratis y accede al buscador inteligente, las comparativas y la síntesis por IA de reseñas reales.
                    </p>

                    <div className="flex flex-col sm:flex-row items-center gap-3">
                        <Link
                            href="/register"
                            className="px-8 py-3 rounded-full bg-white text-[#0369a1] font-bold text-sm no-underline transition-colors hover:bg-sky-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-[#0284c7]"
                        >
                            Crear cuenta gratis
                        </Link>
                        <Link
                            href="/login"
                            className="px-8 py-3 rounded-full border-2 border-white/40 text-white font-bold text-sm no-underline transition-colors hover:bg-white/10 focus:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-[#0284c7]"
                        >
                            Ya tengo cuenta
                        </Link>
                    </div>
                </div>
            </div>
        </section>
    );
}
