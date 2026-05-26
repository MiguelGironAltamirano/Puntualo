/**
 * Puntualo API Client
 * Type-safe utilities for all backend endpoints
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ============================================================================
// TYPES & INTERFACES
// ============================================================================

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface ErrorResponse {
  detail: {
    code: string;
    message: string;
  };
}

// Course types
export interface CourseRead {
  id: number;
  name: string;
  faculty_id: number;
  university_id: number;
  evaluation_count: number;
  created_at: string;
}

// Professor types
export interface ProfessorRead {
  id: string;
  full_name: string;
  university_id: number;
  faculty_id: number;
  validation_status: string;
  global_score: number | null;
  total_evaluations: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  is_provisional: boolean;
}

// Evaluation types
export interface EvaluationRead {
  id: string;
  professor_id: string;
  course_id: number;
  semester: string;
  clarity: number;
  easiness: number;
  helpfulness: number;
  punctuality: number;
  modality: 'virtual' | 'presencial' | 'ambas';
  created_at: string;
}

// Comment types
export interface CommentRead {
  id: string;
  professor_id: string;
  course_id: number;
  text: string;
  modality: 'virtual' | 'presencial' | 'ambas';
  like_count: number;
  dislike_count: number;
  created_at: string;
  hashtags: string[];
  author: string;
}

// Comparison types
export interface CourseInComparison {
  id: number;
  name: string;
  faculty_id: number;
}

export interface CommentInComparison {
  id: string;
  text: string;
  like_count: number;
  dislike_count: number;
  created_at: string;
}

export interface AISummary {
  summary: string;
  pros: string[];
  cons: string[];
  model_version: string;
  generated_at: string;
}

export interface ProfessorComparisonDetail {
  id: string;
  full_name: string;
  university_id: number;
  faculty_id: number;
  global_score: number | null;
  total_evaluations: number;
  avg_clarity: number;
  avg_easiness: number;
  avg_helpfulness: number;
  avg_punctuality: number;
  validation_status: string;
  created_at: string;
  courses: CourseInComparison[];
  evaluation_breakdown: {
    virtual: number;
    presencial: number;
    ambas: number;
  };
  common_courses: CourseInComparison[];
  recent_comments: CommentInComparison[];
  ai_summary?: AISummary;
}

export interface ComparisonMetricEntry {
  professor_id: string;
  professor_name: string;
  score: number | string;
}

export interface ProfessorComparisonResponse {
  professors: ProfessorComparisonDetail[];
  comparison_metrics: {
    best_clarity: ComparisonMetricEntry;
    easiest: ComparisonMetricEntry;
    best_helpfulness: ComparisonMetricEntry;
    best_punctuality: ComparisonMetricEntry;
    most_evaluated: ComparisonMetricEntry;
  };
}

// ============================================================================
// QUERY PARAMETER TYPES
// ============================================================================

export interface CourseListParams {
  q?: string;
  university_id?: number;
  faculty_id?: number;
  page?: number;
  page_size?: number;
  sort_by?: 'name' | 'evaluation_count';
  sort_order?: 'asc' | 'desc';
}

export interface ProfessorListParams {
  search?: string;
  university_id?: number;
  faculty_id?: number;
  min_clarity?: number;
  max_clarity?: number;
  min_easiness?: number;
  max_easiness?: number;
  min_helpfulness?: number;
  max_helpfulness?: number;
  min_punctuality?: number;
  max_punctuality?: number;
  min_global_score?: number;
  max_global_score?: number;
  min_evaluations?: number;
  date_from?: string;
  date_to?: string;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface EvaluationListParams {
  professor_id?: string;
  course_id?: number;
  semester?: string;
  modality?: 'virtual' | 'presencial' | 'ambas';
  min_clarity?: number;
  max_clarity?: number;
  min_easiness?: number;
  max_easiness?: number;
  min_helpfulness?: number;
  max_helpfulness?: number;
  min_punctuality?: number;
  max_punctuality?: number;
  date_from?: string;
  date_to?: string;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface CommentListParams {
  search?: string;
  min_likes?: number;
  max_likes?: number;
  min_dislikes?: number;
  max_dislikes?: number;
  min_net_score?: number;
  date_from?: string;
  date_to?: string;
  course_id?: number;
  modality?: 'virtual' | 'presencial' | 'ambas';
  hashtags?: string[];
  page?: number;
  page_size?: number;
  order_by?: string;
  sort_order?: 'asc' | 'desc';
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Build query string from object, filtering out undefined/null values
 */
function buildQueryString(params: Record<string, any>): string {
  const searchParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      if (Array.isArray(value)) {
        value.forEach((v) => searchParams.append(key, String(v)));
      } else {
        searchParams.set(key, String(value));
      }
    }
  });

  const query = searchParams.toString();
  return query ? `?${query}` : '';
}

/**
 * Make API request with error handling
 */
async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData?.detail?.message || `API Error: ${response.status}`
      );
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error [${endpoint}]:`, error);
    throw error;
  }
}

// ============================================================================
// COURSES ENDPOINTS
// ============================================================================

export const coursesAPI = {
  /**
   * Get paginated list of courses with optional filters
   */
  list: async (
    params?: CourseListParams
  ): Promise<PaginatedResponse<CourseRead>> => {
    const query = buildQueryString(params || {});
    return fetchAPI(`/courses${query}`);
  },

  /**
   * Get single course by ID
   */
  get: async (id: number): Promise<CourseRead> => {
    return fetchAPI(`/courses/${id}`);
  },
};

// ============================================================================
// PROFESSORS ENDPOINTS
// ============================================================================

export const professorsAPI = {
  /**
   * Get paginated list of professors with optional filters and search
   */
  list: async (
    params?: ProfessorListParams
  ): Promise<PaginatedResponse<ProfessorRead>> => {
    const query = buildQueryString(params || {});
    return fetchAPI(`/professors${query}`);
  },

  /**
   * Get single professor by ID
   */
  get: async (id: string): Promise<ProfessorRead> => {
    return fetchAPI(`/professors/${id}`);
  },

  /**
   * Compare 2-4 professors (POST method)
   */
  compare: async (
    professorIds: string[]
  ): Promise<ProfessorComparisonResponse> => {
    return fetchAPI('/professors/compare', {
      method: 'POST',
      body: JSON.stringify({ professor_ids: professorIds }),
    });
  },

  /**
   * Compare 2-4 professors (GET method with query params)
   */
  compareByQuery: async (
    professorIds: string[]
  ): Promise<ProfessorComparisonResponse> => {
    const query = buildQueryString({
      ids: professorIds,
    });
    return fetchAPI(`/professors/compare${query}`);
  },
};

// ============================================================================
// EVALUATIONS ENDPOINTS
// ============================================================================

export const evaluationsAPI = {
  /**
   * Get paginated list of evaluations with optional filters
   */
  list: async (
    params?: EvaluationListParams
  ): Promise<PaginatedResponse<EvaluationRead>> => {
    const query = buildQueryString(params || {});
    return fetchAPI(`/evaluations${query}`);
  },

  /**
   * Get single evaluation by ID
   */
  get: async (id: string): Promise<EvaluationRead> => {
    return fetchAPI(`/evaluations/${id}`);
  },
};

// ============================================================================
// COMMENTS ENDPOINTS
// ============================================================================

export const commentsAPI = {
  /**
   * Get paginated list of comments for a professor with optional filters
   */
  list: async (
    professorId: string,
    params?: CommentListParams
  ): Promise<PaginatedResponse<CommentRead>> => {
    const query = buildQueryString(params || {});
    return fetchAPI(`/professors/${professorId}/comments${query}`);
  },

  /**
   * Get single comment by ID
   */
  get: async (professorId: string, commentId: string): Promise<CommentRead> => {
    return fetchAPI(`/professors/${professorId}/comments/${commentId}`);
  },
};

// ============================================================================
// HELPER FUNCTIONS FOR COMMON PATTERNS
// ============================================================================

/**
 * Search professors by name with optional score filters
 */
export const searchProfessors = async (
  searchTerm: string,
  options?: Partial<ProfessorListParams>
): Promise<PaginatedResponse<ProfessorRead>> => {
  return professorsAPI.list({
    search: searchTerm,
    page: 1,
    page_size: 20,
    ...options,
  });
};

/**
 * Search courses by name
 */
export const searchCourses = async (
  searchTerm: string,
  options?: Partial<CourseListParams>
): Promise<PaginatedResponse<CourseRead>> => {
  return coursesAPI.list({
    q: searchTerm,
    page: 1,
    page_size: 20,
    ...options,
  });
};

/**
 * Get professor with all related data for detail view
 */
export const getProfessorDetail = async (professorId: string) => {
  return professorsAPI.get(professorId);
};

/**
 * Get all evaluations for a professor
 */
export const getProfessorEvaluations = async (
  professorId: string,
  options?: Partial<EvaluationListParams>
): Promise<PaginatedResponse<EvaluationRead>> => {
  return evaluationsAPI.list({
    professor_id: professorId,
    page: 1,
    page_size: 20,
    ...options,
  });
};

/**
 * Get all comments for a professor
 */
export const getProfessorComments = async (
  professorId: string,
  options?: Partial<CommentListParams>
): Promise<PaginatedResponse<CommentRead>> => {
  return commentsAPI.list(professorId, {
    page: 1,
    page_size: 20,
    ...options,
  });
};

/**
 * Compare multiple professors
 */
export const compareProfessors = async (
  professorIds: string[]
): Promise<ProfessorComparisonResponse> => {
  if (professorIds.length < 2 || professorIds.length > 4) {
    throw new Error('Must provide between 2 and 4 professor IDs');
  }
  return professorsAPI.compare(professorIds);
};
