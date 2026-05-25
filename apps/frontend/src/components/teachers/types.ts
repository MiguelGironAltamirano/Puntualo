export interface TeacherReaction {
    icon: string;
    count: number;
}

export interface TeacherComment {
    id: number;
    course: string;
    semester: string;
    mode: string;
    score: string;
    verified: boolean;
    text: string;
    tags: string[];
    likes: number;
    dislikes: number;
    reactions: TeacherReaction[];
}

export interface TeacherMetrics {
    claridad: number;
    facilidad: number;
    ayuda: number;
    total: number;
}

export interface TeacherData {
    name: string;
    rating: string;
    faculty: string;
    department: string;
    avatar: string;
    aiSummary: string;
    education: string;
    university: string;
    research: string[];
    experience: string;
    metrics: TeacherMetrics;
    style: string[];
    comments: TeacherComment[];
}

export interface TeacherSummary {
    id: number | string;
    name: string;
    course: string;
    rating: number;
    claridad: number;
    dificultad: number;
    avatar: string;
    tags: string[];
}
