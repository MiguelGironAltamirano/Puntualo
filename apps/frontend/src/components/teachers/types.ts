import { CommentReactions, AISummaryData } from "@/components/globalTypes";

export interface TeacherComment {
    id: number;
    course: string;
    semester: string;
    mode: string;
    score: string;
    verified: boolean;
    text: string;
    tags: string[];
    reactions: CommentReactions;
}

export interface TeacherMetrics {
    claridad: number;
    facilidad: number;
    ayuda: number;
    puntualidad: number;
    total: number;
}

export interface TeacherData {
    name: string;
    rating: string;
    faculty: string;
    department: string;
    avatar: string;
    aiSummary: AISummaryData;
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
    claridad: number | null;
    dificultad: number | null;
    puntualidad: number | null;
    avatar: string;
    tags: string[];
}
