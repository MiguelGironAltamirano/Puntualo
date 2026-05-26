# Quick Testing Guide - Search, Compare & Filters

## Running the Backend

The backend should be running with hot reload:
```bash
cd apps/backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## API Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| **GET** | `/courses` | List courses with pagination and search |
| **GET** | `/professors` | Enhanced search with advanced filters |
| **GET** | `/evaluations` | List all evaluations with filters |
| **GET** | `/professors/{id}/comments` | Enhanced comment search and filters |
| **POST** | `/professors/compare` | Compare 2-4 professors |
| **GET** | `/professors/compare?ids=...` | Compare using query params |

---

## Test Cases

### 1. Course Listing

**Basic search:**
```bash
curl "http://localhost:8000/courses?q=calculus&page=1&page_size=10"
```

**With sorting by evaluation count:**
```bash
curl "http://localhost:8000/courses?sort_by=evaluation_count&sort_order=desc"
```

**Filter by university:**
```bash
curl "http://localhost:8000/courses?university_id=1&faculty_id=2"
```

---

### 2. Professor Search with Filters

**Search by name:**
```bash
curl "http://localhost:8000/professors?search=juan"
```

**Filter by score ranges:**
```bash
curl "http://localhost:8000/professors?min_clarity=3&max_clarity=5&min_global_score=4.0"
```

**Filter by difficulty:**
```bash
curl "http://localhost:8000/professors?min_evaluations=5&max_easiness=2"
```

**Date range + sorting:**
```bash
curl "http://localhost:8000/professors?date_from=2024-01-01&date_to=2024-12-31&sort_by=global_score&sort_order=desc"
```

**Combined filters:**
```bash
curl "http://localhost:8000/professors?search=juan&university_id=1&min_clarity=4&min_global_score=4.5"
```

---

### 3. Evaluation Search

**Get all evaluations for a professor:**
```bash
curl "http://localhost:8000/evaluations?professor_id=550e8400-e29b-41d4-a716-446655440000"
```

**Filter by modality and score:**
```bash
curl "http://localhost:8000/evaluations?modality=virtual&min_clarity=4&max_easiness=3"
```

**Sort by specific metric:**
```bash
curl "http://localhost:8000/evaluations?sort_by=helpfulness&sort_order=desc"
```

**Paginate results:**
```bash
curl "http://localhost:8000/evaluations?page=2&page_size=50"
```

---

### 4. Comment Search & Filtering

**Search comments by text:**
```bash
curl "http://localhost:8000/professors/550e8400-e29b-41d4-a716-446655440000/comments?search=excellent"
```

**Filter by reaction counts:**
```bash
curl "http://localhost:8000/professors/550e8400-e29b-41d4-a716-446655440000/comments?min_likes=5&min_net_score=2"
```

**Sort by likes:**
```bash
curl "http://localhost:8000/professors/550e8400-e29b-41d4-a716-446655440000/comments?order_by=likes"
```

**Combined filters:**
```bash
curl "http://localhost:8000/professors/550e8400-e29b-41d4-a716-446655440000/comments?search=great&course_id=1&modality=virtual&min_likes=3"
```

---

### 5. Professor Comparison

**Compare 2 professors (POST):**
```bash
curl -X POST "http://localhost:8000/professors/compare" \
  -H "Content-Type: application/json" \
  -d '{
    "professor_ids": [
      "550e8400-e29b-41d4-a716-446655440000",
      "550e8400-e29b-41d4-a716-446655440001"
    ]
  }'
```

**Compare 3 professors (GET):**
```bash
curl "http://localhost:8000/professors/compare?ids=550e8400-e29b-41d4-a716-446655440000&ids=550e8400-e29b-41d4-a716-446655440001&ids=550e8400-e29b-41d4-a716-446655440002"
```

**Compare 4 professors (maximum):**
```bash
curl -X POST "http://localhost:8000/professors/compare" \
  -H "Content-Type: application/json" \
  -d '{
    "professor_ids": [
      "uuid1",
      "uuid2",
      "uuid3",
      "uuid4"
    ]
  }'
```

---

## Expected Response Structures

### Course Response
```json
{
  "items": [
    {
      "id": 1,
      "name": "Calculus I",
      "faculty_id": 2,
      "university_id": 1,
      "evaluation_count": 45,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 120,
  "page": 1,
  "page_size": 20,
  "total_pages": 6,
  "has_next": true,
  "has_prev": false
}
```

### Professor Search Response
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "full_name": "Dr. Juan Pérez",
      "university_id": 1,
      "faculty_id": 2,
      "validation_status": "validated",
      "global_score": 4.5,
      "total_evaluations": 50,
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-05-26T00:00:00Z",
      "is_provisional": false
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8,
  "has_next": true,
  "has_prev": false
}
```

### Evaluation Response
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "professor_id": "550e8400-e29b-41d4-a716-446655440001",
      "course_id": 1,
      "semester": "2024-1",
      "clarity": 4,
      "easiness": 3,
      "helpfulness": 5,
      "punctuality": 4,
      "modality": "presencial",
      "created_at": "2024-05-20T15:30:00Z"
    }
  ],
  "total": 500,
  "page": 1,
  "page_size": 20,
  "total_pages": 25,
  "has_next": true,
  "has_prev": false
}
```

### Comment Response
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "professor_id": "550e8400-e29b-41d4-a716-446655440001",
      "course_id": 1,
      "text": "Excellent professor, very clear explanations!",
      "modality": "presencial",
      "like_count": 15,
      "dislike_count": 1,
      "created_at": "2024-05-25T10:20:00Z",
      "hashtags": ["clear", "helpful"],
      "author": "Anónimo"
    }
  ],
  "total": 87,
  "page": 1,
  "page_size": 20,
  "total_pages": 5,
  "has_next": true,
  "has_prev": false
}
```

### Comparison Response
```json
{
  "professors": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "full_name": "Dr. Juan Pérez",
      "university_id": 1,
      "faculty_id": 2,
      "global_score": 4.5,
      "total_evaluations": 50,
      "avg_clarity": 4.6,
      "avg_easiness": 3.2,
      "avg_helpfulness": 4.7,
      "avg_punctuality": 4.3,
      "validation_status": "validated",
      "created_at": "2024-01-01T00:00:00Z",
      "courses": [
        {"id": 1, "name": "Calculus I", "faculty_id": 2},
        {"id": 2, "name": "Linear Algebra", "faculty_id": 2}
      ],
      "evaluation_breakdown": {
        "virtual": 10,
        "presencial": 35,
        "ambas": 5
      },
      "common_courses": [
        {"id": 1, "name": "Calculus I"}
      ],
      "recent_comments": [
        {
          "id": "550e8400-e29b-41d4-a716-446655440002",
          "text": "Very clear and helpful!",
          "like_count": 5,
          "dislike_count": 0,
          "created_at": "2024-05-25T10:20:00Z"
        }
      ],
      "ai_summary": {
        "summary": "Dr. Pérez is an excellent teacher...",
        "pros": ["Clear explanations", "Helpful", "Organized"],
        "cons": ["Sometimes slow pace"],
        "model_version": "GPT-4",
        "generated_at": "2024-05-20T00:00:00Z"
      }
    }
  ],
  "comparison_metrics": {
    "best_clarity": {
      "professor_id": "550e8400-e29b-41d4-a716-446655440000",
      "professor_name": "Dr. Juan Pérez",
      "score": 4.6
    },
    "easiest": {
      "professor_id": "550e8400-e29b-41d4-a716-446655440001",
      "professor_name": "Dra. Elena García",
      "score": 2.9
    },
    "best_helpfulness": {
      "professor_id": "550e8400-e29b-41d4-a716-446655440000",
      "professor_name": "Dr. Juan Pérez",
      "score": 4.7
    },
    "best_punctuality": {
      "professor_id": "550e8400-e29b-41d4-a716-446655440000",
      "professor_name": "Dr. Juan Pérez",
      "score": 4.3
    },
    "most_evaluated": {
      "professor_id": "550e8400-e29b-41d4-a716-446655440000",
      "professor_name": "Dr. Juan Pérez",
      "count": 50
    }
  }
}
```

---

## Common Errors to Check

### 400 Bad Request
- Invalid page_size (>50)
- Missing required IDs for comparison
- Invalid query parameter values

### 404 Not Found
- Professor doesn't exist
- Course doesn't exist
- Less than 2 professors for comparison

### 422 Unprocessable Entity
- Too many professors (>4) for comparison
- Invalid validation_status value
- Invalid date format (should be ISO format)

---

## Performance Testing

### Large Dataset Queries
```bash
# Test pagination with large result set
curl "http://localhost:8000/professors?page=50&page_size=50"

# Test complex filtering
curl "http://localhost:8000/professors?min_clarity=3&max_clarity=4&min_helpfulness=3&min_evaluations=10"

# Test sorting by computed metrics
curl "http://localhost:8000/courses?sort_by=evaluation_count&sort_order=desc&page=1&page_size=50"
```

### Concurrent Requests
Use a tool like Apache Bench or wrk to test concurrent requests:
```bash
ab -n 100 -c 10 "http://localhost:8000/courses?q=math"
```

---

## Debugging Tips

1. **Check logs** for query execution times in uvicorn console
2. **Use pagination** - Don't fetch all results at once
3. **Verify UUID format** - Format should be exactly: `550e8400-e29b-41d4-a716-446655440000`
4. **Test filters individually** before combining
5. **Check database** - Use `psql` to verify data exists:
   ```sql
   SELECT * FROM professors LIMIT 5;
   SELECT * FROM courses LIMIT 5;
   SELECT * FROM evaluations LIMIT 5;
   ```

---

## Frontend Integration Checklist

- [ ] Create `lib/api.ts` with all endpoint utilities
- [ ] Create custom hooks: `useProfessors`, `useComments`, `useCourses`, `useEvaluations`, `useCompareProfessors`
- [ ] Wire FilterSidebar to use new API endpoints
- [ ] Implement URL-based filter persistence
- [ ] Add loading skeleton screens
- [ ] Add error boundary and error messages
- [ ] Test with real data from backend
- [ ] Implement pagination UI
- [ ] Test all filter combinations

---

## That's it! 🎉

All backend endpoints are ready for testing and frontend integration. The database is properly indexed, queries are optimized, and error handling is comprehensive.

