/**
 * Cinta infinita de materias y facultades. Textura de prueba social, no ruido.
 * El track se duplica para un loop continuo; bajo reduced-motion la red de
 * seguridad global congela la animación (queda estático y legible).
 */
const subjects = [
    "Cálculo Avanzado",
    "Ingeniería Civil",
    "Derecho",
    "Medicina",
    "Arquitectura",
    "Economía",
    "Psicología",
    "Química Orgánica",
    "Física",
    "Programación",
    "Administración",
    "Biología",
];

function Track() {
    return (
        <ul className="flex items-center gap-10 px-5 shrink-0" aria-hidden="true">
            {subjects.map((s, i) => (
                <li key={`${s}-${i}`} className="flex items-center gap-10 whitespace-nowrap">
                    <span className="text-sm font-bold text-[#475569]">{s}</span>
                    <span className="w-1.5 h-1.5 rounded-full bg-[#bae6fd] shrink-0" />
                </li>
            ))}
        </ul>
    );
}

export function SubjectMarquee() {
    return (
        <section className="mt-2 mb-8 w-full" aria-label="Materias y facultades disponibles">
            <div
                className="pl-marquee relative w-full overflow-hidden"
                style={{
                    maskImage:
                        "linear-gradient(to right, transparent, black 12%, black 88%, transparent)",
                    WebkitMaskImage:
                        "linear-gradient(to right, transparent, black 12%, black 88%, transparent)",
                }}
            >
                <div className="pl-marquee-track flex w-max">
                    {/* Dos copias idénticas: el -50% del keyframe equivale a un ciclo exacto. */}
                    <Track />
                    <Track />
                </div>
            </div>
        </section>
    );
}
