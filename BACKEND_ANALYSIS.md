# Puntualo Backend Codebase Analysis

## Executive Summary

Puntualo is a FastAPI-based Python backend for an academic rating platform. The system allows students to rate professors on multiple criteria and submit comments. It features comprehensive authentication, content moderation, role-based access control, and professional validation pipelines.

---

## 1. User and Comment Models/Schemas

### User Model (`app/models/user.py`)

**Table**: `users`

**Primary Fields:**
- `id` (UUID, PK): Generated via `gen_random_uuid()`
- `email` (String, UNIQUE, INDEXED): User's email address
- `username` (String, UNIQUE, INDEXED): Username for login
- `full_name` (String): User's full name
- `dni` (String, UNIQUE, NULLABLE): National ID number
- `hashed_password` (String): Bcrypt-hashed password
- `role` (String, DEFAULT='student'): Role enumeration ('student' or 'admin')
- `provider` (String, DEFAULT='local'): Auth provider ('local' or OAuth)
- `is_verified` (Boolean, DEFAULT=False): Email verification status
- `strike_count` (Integer, DEFAULT=0): Moderation strikes count
- `career_id` (BigInteger FK): References `careers.id` (nullable)

**Mixins:**
- `TimestampMixin`: `created_at`, `updated_at` (both with timezone)
- `SoftDeleteMixin`: `is_active` (Boolean), `deleted_at` (nullable)

**Constraints:**
- `CHECK constraint`: `role IN ('student','admin')`
- `UNIQUE` on `email` and `username`
- Foreign key to `careers` table with `SET NULL` on delete

---

### Comment Model (`app/models/comment.py`)

**Table**: `comments`

**Primary Fields:**
- `id` (UUID, PK): Generated via `gen_random_uuid()`
- `evaluation_id` (UUID FK, UNIQUE): 1:1 relationship with evaluation (CASCADE delete)
- `user_id` (UUID FK, NULLABLE, INDEXED): Creator of comment (SET NULL on delete)
- `professor_id` (UUID FK, INDEXED): Target professor (CASCADE delete)
- `course_id` (BigInteger FK): Associated course (RESTRICT delete)
- `text` (Text, NULLABLE): The comment text (max 2000 chars)
- `modality` (String(15)): Teaching mode ('virtual'|'presencial'|'ambas')
- `status` (String(30), INDEXED, DEFAULT='published'): Moderation status
- `hidden_at` (DateTime, NULLABLE): Timestamp when hidden for review
- `removed_at` (DateTime, NULLABLE): Timestamp when removed
- `moderation_verdict` (String(20), NULLABLE): AI moderation decision

**Denormalized Counters:**
- `like_count` (Integer, DEFAULT=0): Number of likes
- `dislike_count` (Integer, DEFAULT=0): Number of dislikes
- `reports_count` (Integer, DEFAULT=0): Number of reports

**Status Enum** (`CommentStatus`):
- `PUBLISHED`: Visible to all
- `HIDDEN_PENDING_REVIEW`: Awaiting AI moderation
- `REMOVED`: Deleted by moderation

**Mixins:**
- `TimestampMixin`: `created_at`, `updated_at`
- `SoftDeleteMixin`: `is_active`, `deleted_at`

**Constraints:**
- `CHECK`: `status IN ('published','hidden_pending_review','removed')`
- `CHECK`: `modality IN ('virtual','presencial','ambas')`
- `CHECK`: `(removed_at IS NULL) OR (text IS NULL)` - text cleared on removal
- `INDEX`: `(professor_id, status)` for filtering

**Key Design Notes:**
- Comments are **anonymous in the public API** but `user_id` is stored internally for moderation and strikes
- 1:1 relationship with evaluations ensures one comment per evaluation
- Counters are denormalized for query performance

---

### Evaluation Model (`app/models/evaluation.py`)

**Table**: `evaluations`

**Primary Fields:**
- `id` (UUID, PK): Generated via `gen_random_uuid()`
- `user_id` (UUID FK, INDEXED): The evaluator (CASCADE delete)
- `professor_id` (UUID FK, INDEXED): The evaluated professor (CASCADE delete)
- `course_id` (BigInteger FK): Associated course (RESTRICT delete)
- `semester` (String(7)): Semester code (e.g., "2026-1")
- `modality` (String(15)): Teaching mode

**Rating Metrics** (all Integer, 1-5 scale):
- `clarity`: How clear the professor explains
- `easiness`: Course difficulty/ease
- `helpfulness`: How helpful the professor is
- `punctuality`: Professor's punctuality

**Mixins:**
- `TimestampMixin`: `created_at`, `updated_at`

**Constraints:**
- `UNIQUE(user_id, professor_id, course_id, semester)`: One evaluation per combination
- `CHECK`: All 4 metrics between 1 and 5
- `CHECK`: `modality IN ('virtual','presencial','ambas')`

**Key Design Notes:**
- **Not soft-deleted** - preserves historical professor scores
- The 4 metrics feed into professor's `global_score` calculation
- Each evaluation can have an optional associated comment

---

### Professor Model (`app/models/professor.py`)

**Table**: `professors`

**Primary Fields:**
- `id` (UUID, PK): Generated via `gen_random_uuid()`
- `full_name` (String(200), INDEXED): Professor name
- `university_id` (BigInteger FK): References `universities.id` (RESTRICT)
- `faculty_id` (BigInteger FK): References `faculties.id` (RESTRICT)
- `validation_status` (String(30)): Validation pipeline status
- `registered_by_id` (UUID FK, NULLABLE): User who registered (SET NULL)
- `global_score` (Numeric(3,2), NULLABLE): Aggregate score (1.00-5.00)
- `total_evaluations` (Integer, DEFAULT=0): Denormalized count

**Mixins:**
- `TimestampMixin`: `created_at`, `updated_at`
- `SoftDeleteMixin`: `is_active`, `deleted_at`

**Constraints:**
- `UNIQUE` on (lowercase full_name, university_id) **where is_active=true**
- `CHECK`: `validation_status IN ('pending_validation','validated','not_found','rejected')`
- `CHECK`: `global_score IS NULL OR global_score BETWEEN 1.0 AND 5.0`

---

## 2. Database Structure and Tables

### Complete Schema Map

```
universities
  ├─> faculties (FK: university_id)
  │    └─> professors (FK: university_id, faculty_id)
  │         ├─> evaluations (FK: professor_id)
  │         │    ├─> comments (FK: evaluation_id, professor_id, course_id) [1:1]
  │         │    │    ├─> comment_reactions (FK: comment_id)
  │         │    │    ├─> comment_reports (FK: comment_id)
  │         │    │    └─> user_strikes (FK: comment_id, via moderation_actions)
  │         │    └─> evaluation_hashtags (FK: evaluation_id, hashtag_id) [M:M]
  │         ├─> professor_degrees (FK: professor_id)
  │         ├─> professor_courses (FK: professor_id, course_id)
  │         ├─> professor_evidence (FK: professor_id)
  │         ├─> professor_ai_summary (FK: professor_id)
  │         └─> moderation_actions (FK: comment_id)
  │              └─> user_strikes (FK: moderation_action_id)
  │
  ├─> careers (FK: university_id)
  │    └─> users (FK: career_id)
  │         ├─> evaluations (FK: user_id)
  │         ├─> email_verifications (pending registrations)
  │         ├─> password_resets (for password recovery)
  │         ├─> verification_requests (for document verification)
  │         │    └─> uploaded_documents (FK: user_id)
  │         ├─> comment_reactions (FK: user_id)
  │         ├─> comment_reports (FK: user_id)
  │         └─> user_strikes (FK: user_id)
  │
  └─> courses (FK: university_id)
       ├─> evaluations (FK: course_id)
       ├─> comments (FK: course_id)
       ├─> professor_courses (FK: course_id)
       └─> career_courses (FK: course_id)

hashtags
  └─> evaluation_hashtags [M:M with evaluations]

banned_terms
  (for content moderation filtering)

academic_degrees
  └─> professor_degrees [1:M]
```

### Critical Tables

| Table | PK Type | Key Features | Notes |
|-------|---------|--------------|-------|
| `users` | UUID | Email verification, role-based, strike tracking | Soft-deleted |
| `professors` | UUID | Validation pipeline, global score, denormalized counts | Soft-deleted |
| `evaluations` | UUID | Multi-metric ratings, 1 per (user, prof, course, semester) | Not soft-deleted |
| `comments` | UUID | Anon in public API, full moderation lifecycle | Soft-deleted |
| `comment_reactions` | UUID | Like/dislike per user per comment | UNIQUE(comment_id, user_id) |
| `comment_reports` | UUID | Report system with escalation | UNIQUE(comment_id, user_id) |
| `user_strikes` | UUID | Strike history for account suspension | Links user → comment → moderation_action |
| `email_verifications` | UUID | Pending registrations with time-limited codes | Code stored as HMAC hash |
| `password_resets` | UUID | Password recovery tokens | Code stored as HMAC hash |
| `verification_requests` | UUID | Document verification workflow | Tracks approval/rejection status |
| `uploaded_documents` | UUID | User ID documents (carnet, matricula) | Stores file path, dimensions, quality score |
| `moderation_actions` | UUID | AI moderation decisions audit log | Records decision + reasoning |
| `evaluation_hashtags` | Composite | M:M between evaluations & hashtags | PK: (evaluation_id, hashtag_id) |
| `hashtags` | BigInteger | Usage count for discovery | GIN index on label for full-text search |

---

## 3. Authentication & Authorization Patterns

### Authentication Flow

**Registration (2-step email verification):**
1. Client POSTs `/auth/register` with email, username, full_name, password, career_id, dni
2. Server generates 6-digit code, hashes it with HMAC-SHA256, stores in `email_verifications`
3. Email sent with plaintext code
4. Client POSTs `/auth/register/verify` with email + code
5. Server verifies code (timing-safe comparison with `hmac.compare_digest`), creates `User`, deletes verification record
6. Returns `UserResponse` with tokens

**Login:**
1. Client POSTs `/auth/login` with email + password
2. Server queries `users` by email, verifies password with bcrypt
3. Returns `access_token` + `refresh_token`

**Token Types:**
- **Access Token** (30 min default): JWT with `sub` (email), `role`, `type: "access"`
- **Refresh Token** (7 days): JWT with same payload but `type: "refresh"`
- **Algorithm**: HS256
- **Secret**: `SECRET_KEY` from environment

**Password Reset:**
1. Similar 2-step flow using `password_resets` table
2. Code sent via email, stored as HMAC hash
3. Max 5 attempts per reset request

### Authorization

**Dependency Injection Pattern:**

```python
# Basic authentication (any verified user)
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: Session = Depends(get_db),
) -> User:
    # Decodes token, validates type, fetches user from DB
    # Checks is_active flag

# Admin-only protection
async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != "admin":
        raise HTTPException(403, "Admin access required")
```

**Role-Based Access Control (RBAC):**
- `student` role: Can create evaluations/comments, react, report (default)
- `admin` role: Access `/api/admin/*` moderation endpoints
- Check implemented at endpoint level via dependency injection

**Account Suspension:**
- When `user.strike_count >= 3`, account set to `is_active = False`
- `get_current_user` dependency checks `is_active` and rejects inactive users
- Strikes tied to removed comments via `user_strikes` table

### Key Security Mechanisms

**Password Security:**
- Bcrypt with automatic salt generation (`bcrypt.gensalt()`)
- Password stored as `hashed_password` in `users` table
- Verification uses `bcrypt.checkpw()` (timing-safe comparison)

**Token Security:**
- JWT tokens use HS256 (symmetric key)
- `SECRET_KEY` must be set in environment (no default)
- Tokens include expiration (`exp` claim)
- Token type validation (`type: "access"` vs `type: "refresh"`)

**Verification Codes:**
- Generated as 6-digit random code: `secrets.randbelow(1000000)`
- **Never stored in plaintext**; stored as HMAC-SHA256 hash
- Hash includes email + code: `HMAC(email:code)`
- Timing-safe comparison with `hmac.compare_digest()`
- **Time-limited**: Expires in 10 minutes (configurable)
- **Attempt-limited**: Max 5 attempts before rejection

---

## 4. Existing Encryption & Security Mechanisms

### Hashing

1. **Passwords**: Bcrypt with salt
   - Function: `hash_password(password: str) -> str`
   - Uses `bcrypt.gensalt()` for random salt
   - Verification: `verify_password(plain, hashed) -> bool`

2. **Verification Codes**: HMAC-SHA256
   - Function: `_hash_verification_code(code: str, email: str) -> str`
   - Includes email in the hash to prevent code reuse across accounts
   - Uses `settings.SECRET_KEY` as HMAC key

### SSL/TLS Database Connections

**For PostgreSQL (Aiven):**
- Production URLs include `?sslmode=require`
- SSL context created with custom CA handling (Aiven uses self-signed CA)
- Configuration in `app/db/async_session.py` and `app/core/config.py`:
  ```python
  ssl_ctx = ssl.create_default_context()
  ssl_ctx.check_hostname = False       # Skip hostname verification
  ssl_ctx.verify_mode = ssl.CERT_NONE  # Skip CA chain validation
  ```
- Note: Connection is still encrypted; only validation is skipped

### Data Anonymization

- **Comments**: Public API returns comments without `user_id`
- **Internal Tracking**: `user_id` stored for moderation and strikes
- Comments served to public without identifying the author

### Content Security

**Banned Terms Filtering:**
- Table `banned_terms` with severity levels
- Heuristic filter for spam detection:
  - `HEURISTIC_SPAM_BLOCK_THRESHOLD`: 0.7
  - `HEURISTIC_SPAM_FLAG_THRESHOLD`: 0.4
  - `HEURISTIC_MAX_UPPERCASE_RATIO`: 0.7
  - Obfuscation check enabled by default
- New hashtags undergo banned terms check before creation

**Comment Moderation:**
- Status tracking: `PUBLISHED` → `HIDDEN_PENDING_REVIEW` → `REMOVED`
- When comment accumulates 5+ reports, AI moderation pipeline triggers
- Decisions logged in `moderation_actions` table with reasoning
- Admin can manually override via `/api/admin/moderation/*` endpoints

---

## 5. API Endpoint Patterns

### Authentication Endpoints (`/auth`)

```
POST   /auth/register                 → RegisterStartResponse
POST   /auth/register/verify          → UserResponse (201)
POST   /auth/login                    → TokenResponse
POST   /auth/refresh                  → TokenResponse
POST   /auth/password-reset/start     → PasswordResetStartResponse
POST   /auth/password-reset/verify    → {}
POST   /auth/password-reset/confirm   → PasswordResetConfirmResponse
GET    /auth/me                       → UserResponse [PROTECTED]
```

### Professors Endpoints (`/professors`)

```
GET    /professors                    → List professors (public, filterable)
GET    /professors/{id}               → Professor detail (public)
GET    /professors/{id}/comments      → Comments for professor (public, paginated)
POST   /professors/compare            → Compare 2-4 professors
GET    /professors/compare?ids=...    → Batch comparison
```

### Evaluations Endpoints (`/evaluations`)

```
POST   /evaluations                   → Create evaluation [PROTECTED, verified user]
GET    /evaluations                   → List evaluations (public)
GET    /evaluations/mine              → List user's evaluations [PROTECTED]
GET    /evaluations/{id}              → Evaluation detail (public)
```

### Comments Endpoints (embedded in evaluations)

```
GET    /professors/{prof_id}/comments → Paginated comments with filtering
GET    /comments/{id}                 → Single comment (public)
```

### Reactions Endpoints

```
POST   /comments/{id}/reactions       → Like/dislike [PROTECTED]
DELETE /comments/{id}/reactions       → Remove reaction [PROTECTED]
GET    /comments/{id}/reactions       → Reactions summary
```

### Reports Endpoints

```
POST   /comments/{id}/reports         → Report comment [PROTECTED, rate-limited]
GET    /comments/{id}/reports         → Reports summary (admin)
```

### Admin Endpoints (`/api/admin`)

```
GET    /api/admin/moderation/pending  → List pending moderation [ADMIN]
GET    /api/admin/moderation/comments/{id} → Moderation details [ADMIN]
POST   /api/admin/moderation/comments/{id}/decide → Apply decision [ADMIN]
GET    /api/admin/moderation/stats    → Moderation statistics [ADMIN]
GET    /api/admin/moderation/banned-terms → Banned terms list [ADMIN]
```

### Catalogs Endpoints (`/catalogs`)

```
GET    /catalogs/universities         → List universities
GET    /catalogs/faculties            → List faculties
GET    /catalogs/careers              → List careers
GET    /catalogs/courses              → List courses
GET    /catalogs/academic-degrees     → List academic degrees
```

### Verification Endpoints (`/verification`)

```
POST   /verification/start            → Initiate document verification [PROTECTED]
GET    /verification/status           → Check verification status [PROTECTED]
POST   /verification/upload           → Upload verification document [PROTECTED]
```

### Response Format

All endpoints follow consistent error handling:
```json
{
  "detail": {
    "code": "ERROR_CODE",
    "message": "Human-readable message"
  }
}
```

---

## 6. Configuration & Environment Variables

### Location
`apps/backend/app/core/config.py` - Settings class

### Database Configuration

```python
DATABASE_URL                    # Required; PostgreSQL connection string
DB_POOL_SIZE                    # Default: 5 (async)
DB_MAX_OVERFLOW                 # Default: 2 (async)
DB_SYNC_POOL_SIZE              # Default: 2 (sync)
DB_SYNC_MAX_OVERFLOW           # Default: 1 (sync)
DB_POOL_TIMEOUT                # Default: 30 seconds
DB_POOL_RECYCLE                # Default: 1800 seconds (connection reuse)
```

### Security Configuration

```python
SECRET_KEY                      # Required; for JWT & HMAC
JWT_SECRET                      # Alternative/legacy secret
ALGORITHM                       # Default: HS256
ACCESS_TOKEN_EXPIRE_MINUTES    # Default: 30 minutes
```

### Email Configuration

```python
SMTP_HOST                       # Email server
SMTP_PORT                       # Default: 587
SMTP_USER                       # Credentials
SMTP_PASSWORD                   # Credentials
SMTP_FROM                       # Sender address
SMTP_TLS                        # Default: true
SMTP_SSL                        # Default: false
```

### Email Verification

```python
EMAIL_VERIFICATION_TTL_MINUTES  # Default: 10 minutes (code expiry)
EMAIL_VERIFICATION_MAX_ATTEMPTS # Default: 5 attempts
PASSWORD_RESET_TTL_MINUTES     # Default: 10 minutes
PASSWORD_RESET_MAX_ATTEMPTS    # Default: 5 attempts
```

### OAuth (Google)

```python
GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET
```

### Redis & Celery

```python
REDIS_URL                       # Default: redis://localhost:6379/0
CELERY_BROKER_URL              # Default: redis://localhost:6379/1
CELERY_RESULT_BACKEND          # Default: redis://localhost:6379/2
```

### Content Moderation

```python
COMMENT_MIN_LENGTH             # Default: 20 characters
COMMENT_MAX_LENGTH             # Default: 2000 characters
COMMENT_REPORT_REASON_MAX_LENGTH # Default: 500 characters
MODERATION_HIDE_THRESHOLD      # Default: 5 reports to trigger AI
LLM_MODERATION_ENABLED         # Default: false
MODERATION_VERIFIED_EMAIL_DOMAIN # Default: unmsm.edu.pe
```

### Heuristic Spam Detection

```python
HEURISTIC_SPAM_BLOCK_THRESHOLD    # Default: 0.7
HEURISTIC_SPAM_FLAG_THRESHOLD     # Default: 0.4
HEURISTIC_MAX_UPPERCASE_RATIO     # Default: 0.7
HEURISTIC_OBFUSCATION_CHECK       # Default: true
```

### Report Rate Limiting

```python
REPORT_RATE_LIMIT_PER_HOUR        # Default: 10 reports/hour
REPORT_ABUSE_THRESHOLD            # Default: 5
REPORT_MODERATION_TRIGGER_THRESHOLD # Default: 5.0
```

### Professor Validation Pipeline

```python
UNMSM_USER_AGENT                # User-Agent for scraping UNMSM
UNMSM_RATE_LIMIT_SECONDS        # Default: 1.0 second
OPENALEX_API_BASE               # Default: https://api.openalex.org
OPENALEX_INSTITUTION_ID         # Default: I192513696 (UNMSM)
ORCID_API_BASE                  # Default: https://pub.orcid.org/v3.0
TAVILY_API_KEY                  # For fallback enrichment
TAVILY_BUDGET_HARD_CAP          # Default: 950 queries
```

### Caching

```python
CACHE_TTL_PROFESSOR_DETAIL_SECONDS       # Default: 300 seconds
CACHE_TTL_PROFESSOR_COMMENTS_SECONDS     # Default: 120 seconds
CACHE_TTL_COURSES_SEARCH_SECONDS         # Default: 60 seconds
```

### AI Summary (Gemini)

```python
GEMINI_API_KEY
GEMINI_MODEL                    # Default: gemini-2.5-flash
NLP_SUMMARY_MIN_REVIEWS         # Default: 5 (trigger threshold)
NLP_SUMMARY_MAX_REVIEWS         # Default: 100
NLP_SUMMARY_BEAT_SECONDS        # Default: 900 (15 min)
IA_SUMMARY_HOOK_ENABLED         # Default: false
```

### Document Verification

```python
VERIFICATION_MAX_FILE_SIZE_BYTES # Default: 5 MB
VERIFICATION_MIN_WIDTH           # Default: 800 px
VERIFICATION_MIN_HEIGHT          # Default: 600 px
VERIFICATION_MIN_SHARPNESS       # Default: 10.0
```

### Score Calculation (Hardcoded)

```python
SCORE_WEIGHT_CLARITY            # 0.25
SCORE_WEIGHT_EASINESS           # 0.25
SCORE_WEIGHT_HELPFULNESS        # 0.25
SCORE_WEIGHT_PUNCTUALITY        # 0.25
# Sum must equal 1.0 (validated at import time)
```

---

## 7. Key Architectural Decisions

### Anonymity Design
- Comments are **1:1 with evaluations** and public but **anonymous**
- `user_id` stored in DB for internal strikes/moderation tracking
- Public API (`GET /professors/{id}/comments`) never exposes `user_id`

### Soft Deletes vs Hard Deletes
- **Soft-deleted**: `users`, `professors`, `comments`
  - Preserves data for audits, cascades, and analytics
  - Queries filter on `is_active = true` by default
- **Not soft-deleted**: `evaluations`
  - Preserves historical ratings even if user/professor deleted
  - Ensures score history integrity

### Denormalization Strategy
- `professors.global_score`: Pre-calculated from evaluations
- `professors.total_evaluations`: Count cache
- `comments.{like_count, dislike_count, reports_count}`: Counters
- **Goal**: Fast API responses without complex aggregations

### Connection Pooling
- Aiven plan limited to 20 connections (3 reserved)
- Conservative pool sizes to share between sync/async engines and Celery
- Settings tunable per environment

### Code Verification (Multi-step)
1. Generate code: `secrets.randbelow(1000000)` → "123456"
2. Hash code: `HMAC-SHA256(email:code)` → stored in DB
3. Verify: Timing-safe comparison with `hmac.compare_digest()`
4. Prevents: Code reuse, timing attacks, replay attacks

---

## 8. Security Considerations & Notes

### Strengths
✅ Bcrypt for password hashing with automatic salting  
✅ JWT tokens with expiration and type validation  
✅ Timing-safe code verification (HMAC-SHA256)  
✅ Rate limiting on password resets (5 attempts, 10 min TTL)  
✅ Role-based access control for admin functions  
✅ Comment anonymization for public API  
✅ Soft deletes for audit trail  
✅ SSL/TLS for database connections  
✅ Heuristic spam detection with multiple thresholds  
✅ Content moderation pipeline with audit logging  

### Areas to Monitor
⚠️ SSL verification disabled for self-signed Aiven CA  
⚠️ Database connection pool sharing between multiple engines  
⚠️ Email credentials stored in environment variables  
⚠️ Admin endpoints not rate-limited  
⚠️ Session management tied to token expiry only  
⚠️ No apparent API rate limiting (except reports)  

---

## 9. Database Statistics

- **33 migration files** in `alembic/versions/`
- **PostgreSQL 15+** recommended (UUID support)
- **32 tables** in final schema
- **Full schema redesign** in migration `5436e56a199d` to normalize UUIDs

---

## 10. Testing & Health Checks

```
GET  /                → {"message": "Puntualo backend funcionando"}
GET  /health/db       → {"database": "connected"} (connectivity check)
```

