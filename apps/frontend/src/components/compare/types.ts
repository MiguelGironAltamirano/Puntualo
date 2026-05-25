export interface Review {
    text: string;
    course: string;
    date: string;
}

export interface Teacher {
    id: string;
    name: string;
    course: string;
    school: string;
    rating: number;      // Mapeado a Nivel de Aprendizaje en la UI
    difficulty: number;  // Nivel de Dificultad
    clarity: number;     // Claridad al Explicar
    takeAgain: string;
    avatar?: string;
    tags: string[];
    reviews?: Review[];
}
