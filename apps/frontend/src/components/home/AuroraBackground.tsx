/**
 * Aurora decorativa del hero. Reemplaza los dos halos estáticos por blobs cian
 * que derivan lento. Puramente decorativa (aria-hidden) y detrás del contenido.
 * Bajo `prefers-reduced-motion: reduce` la red de seguridad global congela la animación.
 */
export function AuroraBackground() {
    return (
        <div
            aria-hidden="true"
            className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-5xl h-[640px] overflow-hidden pointer-events-none z-0"
        >
            <div className="pl-aurora-a absolute left-[6%] top-[-6%] w-[520px] h-[520px] rounded-full bg-[#bae6fd] opacity-40 blur-[110px]" />
            <div className="pl-aurora-b absolute right-[4%] top-[-2%] w-[480px] h-[480px] rounded-full bg-[#e0f2fe] opacity-50 blur-[100px]" />
            <div className="pl-aurora-a absolute left-1/2 top-[10%] w-[360px] h-[360px] -translate-x-1/2 rounded-full bg-[#7dd3fc] opacity-20 blur-[120px]" />
        </div>
    );
}
