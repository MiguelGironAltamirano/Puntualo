# Puntualo Backend: Search, Compare & Filters Implementation

## Overview

This document describes the complete implementation of search, comparison, and advanced filtering functionality across the Puntualo backend. All endpoints follow RESTful conventions with proper pagination, error handling, and type safety.

---

## Phase 1: Backend API Enhancements

### 1.1 Course Listing Endpoint

**Endpoint**: `GET /courses`

**Location**: `apps/backend/app/modules/evaluations/routers/courses.py`

**Query Parameters**:
- `q` (string, optional) - Fuzzy search on course name (case-insensitive LIKE)
- `university_id` (int, optional) - Filter by university
- `faculty_id` (int, optional) - Filter by faculty  
- `page` (int, default=1) - Page number (1-indexed)
- `page_size` (int, default=20, max=50) - Items per page
- `sort_by` (enum, default='name') - Sort by 'name' or 'evaluation_count'
- `sort_order` (enum, default='asc') - 'asc' or 'desc'

**Response**: `PaginatedResponse[CourseRead]`

**Example Request**:
```bash
curl "http://localhost:8000/courses?q=calculus&university_id=1&sort_by=evaluation_count&sort_order=desc&page=1&page_size=20"
```

**Features**:
- Automatic evaluation count calculation and sorting
- Case-insensitive search with LIKE matching
- Proper pagination with total_pages, has_next, has_prev
- Filter by university and faculty

---

### 1.2 Enhanced Professor Search

**Endpoint**: `GET /professors`

**Location**: `apps/backend/app/modules/professors/router.py` (lines 91-164)

**New Query Parameters** (in addition to existing):
- `min_clarity`, `max_clarity` (int, 1-5) - Filter by clarity rating range
- `min_easiness`, `max_easiness` (int, 1-5) - Filter by difficulty range
- `min_helpfulness`, `max_helpfulness` (int, 1-5) - Filter by helpfulness range
- `min_punctuality`, `max_punctuality` (int, 1-5) - Filter by punctuality range
- `min_global_score`, `max_global_score` (float, 1-5) - Filter by global score
- `min_evaluations` (int) - Minimum number of evaluations
- `date_from`, `date_to` (ISO date strings) - Filter by creation date range

**Service Enhancement**: 
- Updated `ProfessorService.list_query()` in `apps/backend/app/modules/professors/service.py`
- Implements efficient subquery-based filtering for evaluation score ranges
- Uses BETWEEN queries for date range filtering
- All filters are AND-combined (except search which is OR within related fields)

**Example Requests**:
```bash
# Search with multiple score filters
curl "http://localhost:8000/professors?search=Juan&min_clarity=3&max_easiness=3&min_global_score=4.0"

# Date range filtering
curl "http://localhost:8000/professors?date_from=2024-01-01&date_to=2024-12-31"

# Minimum evaluations
curl "http://localhost:8000/professors?min_evaluations=10&sort_by=global_score&sort_order=desc"
```

**Features**:
- Combines multiple filtering criteria with AND logic
- Efficient database queries using EXISTS subqueries
- Supports sorting by created_at, global_score, or total_evaluations
- All filters are optional and can be combined

---

### 1.3 Evaluation Search Endpoint

**Endpoint**: `GET /evaluations`

**Location**: `apps/backend/app/modules/evaluations/routers/evaluations.py` (new endpoint)

**Query Parameters**:
- `professor_id` (string, optional) - Filter by professor UUID
- `course_id` (int, optional) - Filter by course
- `semester` (string, optional) - Filter by semester (e.g., "2024-1")
- `modality` (enum, optional) - Filter by 'virtual', 'presencial', or 'ambas'
- `min_clarity`, `max_clarity` (int, 1-5)
- `min_easiness`, `max_easiness` (int, 1-5)
- `min_helpfulness`, `max_helpfulness` (int, 1-5)
- `min_punctuality`, `max_punctuality` (int, 1-5)
- `date_from`, `date_to` (ISO date strings)
- `page`, `page_size` (pagination)
- `sort_by` (enum: 'created_at', 'clarity', 'easiness', 'helpfulness', 'punctuality')
- `sort_order` (enum: 'asc', 'desc')

**Response**: Paginated list of evaluations with full details

**Visibility**: Public endpoint (no authentication required)

**Example Requests**:
```bash
# Get all evaluations for a professor
curl "http://localhost:8000/evaluations?professor_id=550e8400-e29b-41d4-a716-446655440000"

# Filter by score ranges
curl "http://localhost:8000/evaluations?min_clarity=4&max_easiness=2&modality=virtual"

# Sort by clarity, descending
curl "http://localhost:8000/evaluations?sort_by=clarity&sort_order=desc"
```

**Features**:
- Public access (no auth required)
- Comprehensive filtering across all evaluation metrics
- Flexible sorting by any metric
- Efficient date range queries
- All filters AND-combined

---

### 1.4 Enhanced Comment Filtering

**Endpoint**: `GET /professors/{professor_id}/comments`

**Location**: `apps/backend/app/modules/evaluations/routers/comments.py`

**New Query Parameters**:
- `search` (string, optional) - Full-text search on comment text (case-insensitive LIKE)
- `min_likes`, `max_likes` (int) - Filter by like count range
- `min_dislikes`, `max_dislikes` (int) - Filter by dislike count range
- `min_net_score` (int) - Filter by net score (likes - dislikes)
- `date_from`, `date_to` (ISO date strings) - Filter by creation date

**Service Enhancement**:
- Updated `CommentService.list_query()` in `apps/backend/app/modules/evaluations/service/comment_service.py`
- Full-text search with case-insensitive matching
- Reaction count filtering
- Excludes removed comments (text = NULL) from search
- Preserves existing hashtag and modality filtering

**Example Requests**:
```bash
# Search comments
curl "http://localhost:8000/professors/550e8400-e29b-41d4-a716-446655440000/comments?search=excellent&order_by=likes"

# Filter by reaction counts
curl "http://localhost:8000/professors/550e8400-e29b-41d4-a716-446655440000/comments?min_likes=5&min_net_score=2"

# Date range + search
curl "http://localhost:8000/professors/550e8400-e29b-41d4-a716-446655440000/comments?search=good&date_from=2024-01-01"
```

**Features**:
- Full-text search on comment content
- Reaction count range filtering
- Net score filtering (likes - dislikes)
- Excludes removed comments from text search
- Maintains backward compatibility with existing filters (course_id, hashtags, modality)

---

### 1.5 Professor Comparison Endpoint

**Endpoints**: 
- `POST /professors/compare` - Compare professors (request body)
- `GET /professors/compare?ids=id1&ids=id2&ids=id3` - Compare professors (query params)

**Location**: `apps/backend/app/modules/professors/router_comparison.py`

**Service**: `apps/backend/app/modules/professors/service_comparison.py`

**Request Body** (POST):
```json
{
    "professor_ids": ["550e8400-e29b-41d4-a716-446655440000", "550e8400-e29b-41d4-a716-446655440001"]
}
```

**Query Parameters** (GET):
- `ids` (list[string]) - Professor IDs to compare (2-4 professors)

**Response Structure**:
```json
{
    "professors": [
        {
            "id": "string",
            "full_name": "string",
            "university_id": "int",
            "faculty_id": "int",
            "global_score": "float | null",
            "total_evaluations": "int",
            "avg_clarity": "float",
            "avg_easiness": "float",
            "avg_helpfulness": "float",
            "avg_punctuality": "float",
            "validation_status": "string",
            "created_at": "datetime",
            "courses": [{"id": "int", "name": "string", "faculty_id": "int"}],
            "evaluation_breakdown": {"virtual": "int", "presencial": "int", "ambas": "int"},
            "common_courses": [{"id": "int", "name": "string"}],
            "recent_comments": [
                {
                    "id": "string",
                    "text": "string",
                    "like_count": "int",
                    "dislike_count": "int",
                    "created_at": "datetime"
                }
            ],
            "ai_summary": {
                "summary": "string",
                "pros": ["string"],
                "cons": ["string"],
                "model_version": "string",
                "generated_at": "datetime"
            }
        }
    ],
    "comparison_metrics": {
        "best_clarity": {"professor_id": "string", "professor_name": "string", "score": "float"},
        "easiest": {"professor_id": "string", "professor_name": "string", "score": "float"},
        "best_helpfulness": {"professor_id": "string", "professor_name": "string", "score": "float"},
        "best_punctuality": {"professor_id": "string", "professor_name": "string", "score": "float"},
        "most_evaluated": {"professor_id": "string", "professor_name": "string", "count": "int"},
        "highest_global_score": {"professor_id": "string", "professor_name": "string", "score": "float"}
    }
}
```

**Constraints**:
- Minimum 2 professors required
- Maximum 4 professors allowed for comparison
- Professors must be active (is_active = true)
- Invalid UUID format returns 400 Bad Request
- Non-existent professors return 404 Not Found

**Example Requests**:
```bash
# POST request
curl -X POST http://localhost:8000/professors/compare \
  -H "Content-Type: application/json" \
  -d '{
    "professor_ids": [
      "550e8400-e29b-41d4-a716-446655440000",
      "550e8400-e29b-41d4-a716-446655440001"
    ]
  }'

# GET request with query params
curl "http://localhost:8000/professors/compare?ids=550e8400-e29b-41d4-a716-446655440000&ids=550e8400-e29b-41d4-a716-446655440001"
```

**Features**:
- Side-by-side comparison of 2-4 professors
- Aggregated scores and metrics
- Common courses identification
- Recent comments for context
- AI summaries if available
- Automatic calculation of best performers in each category
- Evaluation breakdown by teaching modality
- No authentication required (public endpoint)

---

## Database Schema Considerations

All new endpoints leverage existing database indexes:
- `ix_professors_full_name` - Fast professor name searches
- `ix_courses_name` - Fast course name searches  
- `ix_comments_professor_status` - Efficient comment filtering
- `ix_evaluations_*` - Proper indexing for evaluation queries
- `uq_professors_name_university_active` - Unique professor validation
- `uq_courses_name_university_active` - Unique course validation

The `pg_trgm` PostgreSQL extension is already enabled for potential fuzzy matching enhancements.

---

## Error Handling

All endpoints return structured error responses:

```json
{
    "detail": {
        "code": "ERROR_CODE",
        "message": "Human-readable error message"
    }
}
```

Common error codes:
- `MISSING_IDS` - No professor IDs provided for comparison
- `TOO_FEW_PROFESSORS` - Less than 2 professors for comparison
- `TOO_MANY_PROFESSORS` - More than 4 professors for comparison
- `INVALID_ID_FORMAT` - Invalid UUID format
- `PROFESSORS_NOT_FOUND` - One or more professors not found
- `INVALID_VALIDATION_STATUS` - Invalid validation_status value
- `PROFESSOR_NOT_FOUND` - Professor doesn't exist
- `COURSE_NOT_FOUND` - Course doesn't exist

---

## Performance Notes

### Query Optimization
- **Professor search**: Uses indexed name/university/faculty fields with OR logic
- **Evaluation filtering**: Uses efficient AND-combined range queries
- **Comment search**: Only filters on existing text (ignores removed comments)
- **Comparison**: Fetches data in parallel queries, results aggregated in memory

### Pagination
- Default page_size: 20
- Maximum page_size: 50
- All endpoints support standard pagination with total_pages, has_next, has_prev

### Sorting
- By default, results sorted by creation date (descending)
- Most endpoints support configurable sort_by and sort_order
- Secondary sort by ID for consistency

---

## Testing Endpoints

### Using curl

```bash
# Test course listing
curl "http://localhost:8000/courses?q=math&page=1&page_size=10"

# Test professor search with filters
curl "http://localhost:8000/professors?search=juan&min_clarity=3&min_global_score=4.0&sort_by=global_score&sort_order=desc"

# Test evaluations search
curl "http://localhost:8000/evaluations?min_clarity=4&max_easiness=2&modality=virtual&page=1"

# Test comment filtering
curl "http://localhost:8000/professors/{id}/comments?search=excellent&min_likes=5&order_by=likes"

# Test professor comparison
curl -X POST "http://localhost:8000/professors/compare" \
  -H "Content-Type: application/json" \
  -d '{"professor_ids": ["id1", "id2", "id3"]}'
```

---

## Implementation Files Summary

### Core Files Modified
1. **`apps/backend/app/modules/professors/service.py`** - Enhanced `list_query()` with new filters
2. **`apps/backend/app/modules/professors/router.py`** - Added query parameters to GET /professors
3. **`apps/backend/app/modules/evaluations/service/comment_service.py`** - Enhanced `list_query()` with search and reaction filters

### New Files Created
1. **`apps/backend/app/modules/evaluations/routers/courses.py`** - New courses endpoint
2. **`apps/backend/app/modules/evaluations/routers/evaluations.py`** - Enhanced with new evaluation search endpoint
3. **`apps/backend/app/modules/professors/service_comparison.py`** - New comparison service
4. **`apps/backend/app/modules/professors/router_comparison.py`** - New comparison router

### Files Updated (Minor)
1. **`apps/backend/app/modules/evaluations/router.py`** - Added courses subrouter include
2. **`apps/backend/app/modules/evaluations/schemas.py`** - Updated CourseRead schema to include evaluation_count
3. **`apps/backend/app/modules/professors/router.py`** - Added comparison router include

---

## Next Steps (Frontend Integration)

The frontend team should:
1. Create API client utilities (`lib/api.ts`)
2. Build custom React hooks for data fetching (`useProfessors`, `useComments`, etc.)
3. Wire FilterSidebar component to use new API endpoints
4. Implement URL-based filter persistence
5. Add loading/error state handling
6. Connect comparison page to comparison endpoint

All backend endpoints are ready for immediate integration and testing.

