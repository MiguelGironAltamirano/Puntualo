"""full_schema_redesign

Drops every existing table with CASCADE and rebuilds the entire schema from
scratch to avoid ALTER COLUMN USING issues when changing VARCHAR PKs/FKs to
native UUID / BigInteger types.

Revision ID: 5436e56a199d
Revises: b3a7c5d9e1f2
Create Date: 2026-05-20 00:20:38.208899

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "5436e56a199d"
down_revision: Union[str, Sequence[str], None] = "b3a7c5d9e1f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Leaf-first drop order (dependencies resolved).
_ALL_TABLES = [
    "user_strikes",
    "moderation_actions",
    "comment_reports",
    "comment_reactions",
    "comments",
    "evaluation_hashtags",
    "evaluations",
    "professor_degrees",
    "professor_courses",
    "professor_evidence",
    "professors",
    "verification_requests",
    "uploaded_documents",
    "hashtags",
    "career_courses",
    "courses",
    "careers",
    "faculties",
    "universities",
    "academic_degrees",
    "users",
    "banned_terms",
]


def _drop_all() -> None:
    for table in _ALL_TABLES:
        op.execute(f"DROP TABLE IF EXISTS {table} CASCADE")


def upgrade() -> None:
    _drop_all()
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # ── 1. universities ────────────────────────────────────────────────
    op.create_table(
        "universities",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("country", sa.String(100), nullable=False, server_default="Perú"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("name", name="uq_universities_name"),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── 2. academic_degrees ────────────────────────────────────────────
    op.create_table(
        "academic_degrees",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("level", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "level IN ('bachelor','master','doctorate','specialization')",
            name="ck_academic_degrees_level",
        ),
        sa.UniqueConstraint("name"),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── 3. faculties ───────────────────────────────────────────────────
    op.create_table(
        "faculties",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("university_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["university_id"], ["universities.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("name", "university_id", name="uq_faculties_name_university"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_faculties_university_id", "faculties", ["university_id"])

    # ── 4. careers ─────────────────────────────────────────────────────
    op.create_table(
        "careers",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("faculty_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["faculty_id"], ["faculties.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("name", "faculty_id", name="uq_careers_name_faculty"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_careers_faculty_id", "careers", ["faculty_id"])

    # ── 5. courses (catalog — BigInteger Identity, SoftDelete) ─────────
    op.create_table(
        "courses",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("university_id", sa.BigInteger(), nullable=False),
        sa.Column("faculty_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["university_id"], ["universities.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["faculty_id"], ["faculties.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_courses_name", "courses", ["name"])
    op.create_index("ix_courses_university_id", "courses", ["university_id"])
    op.create_index("ix_courses_faculty_id", "courses", ["faculty_id"])
    op.create_index("ix_courses_is_active", "courses", ["is_active"])
    op.create_index(
        "uq_courses_name_university_active",
        "courses",
        [sa.text("lower(name)"), sa.text("university_id")],
        unique=True,
        postgresql_where=sa.text("is_active = true"),
    )

    # ── 6. career_courses (junction) ───────────────────────────────────
    op.create_table(
        "career_courses",
        sa.Column("career_id", sa.BigInteger(), nullable=False),
        sa.Column("course_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["career_id"], ["careers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("career_id", "course_id", name="pk_career_courses"),
    )
    op.create_index("ix_career_courses_career_id", "career_courses", ["career_id"])
    op.create_index("ix_career_courses_course_id", "career_courses", ["course_id"])

    # ── 7. users ───────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("dni", sa.String(), nullable=True),
        sa.Column("career_id", sa.BigInteger(), nullable=True),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False, server_default="student"),
        sa.Column("provider", sa.String(), nullable=False, server_default="local"),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("strike_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["career_id"], ["careers.id"], ondelete="SET NULL"),
        sa.CheckConstraint("role IN ('student','admin')", name="ck_users_role"),
        sa.UniqueConstraint("dni"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.create_index("ix_users_career_id", "users", ["career_id"])
    op.create_index("ix_users_is_active", "users", ["is_active"])

    # ── 8. professors ──────────────────────────────────────────────────
    op.create_table(
        "professors",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("university_id", sa.BigInteger(), nullable=False),
        sa.Column("faculty_id", sa.BigInteger(), nullable=False),
        sa.Column("validation_status", sa.String(30), nullable=False, server_default="pending_validation"),
        sa.Column("registered_by_id", sa.UUID(), nullable=True),
        sa.Column("global_score", sa.Numeric(3, 2), nullable=True),
        sa.Column("total_evaluations", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["university_id"], ["universities.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["faculty_id"], ["faculties.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["registered_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.CheckConstraint(
            "validation_status IN ('pending_validation','validated','rejected')",
            name="ck_professors_validation_status",
        ),
        sa.CheckConstraint(
            "global_score IS NULL OR global_score BETWEEN 1.0 AND 5.0",
            name="ck_professors_global_score_range",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_professors_full_name", "professors", ["full_name"])
    op.create_index("ix_professors_university_id", "professors", ["university_id"])
    op.create_index("ix_professors_faculty_id", "professors", ["faculty_id"])
    op.create_index("ix_professors_is_active", "professors", ["is_active"])
    op.create_index(
        "uq_professors_name_university_active",
        "professors",
        [sa.text("lower(full_name)"), sa.text("university_id")],
        unique=True,
        postgresql_where=sa.text("is_active = true"),
    )

    # ── 9. professor_evidence ──────────────────────────────────────────
    op.create_table(
        "professor_evidence",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("professor_id", sa.UUID(), nullable=False),
        sa.Column("source", sa.String(30), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("found", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("affiliation_confirmed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("confidence", sa.Numeric(3, 2), nullable=True),
        sa.Column("raw_payload", postgresql.JSONB(), nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["professor_id"], ["professors.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_professor_evidence_professor_id", "professor_evidence", ["professor_id"])
    op.create_index("idx_professor_evidence_lookup", "professor_evidence", ["professor_id", "source"])

    # ── 10. professor_courses (junction) ───────────────────────────────
    op.create_table(
        "professor_courses",
        sa.Column("professor_id", sa.UUID(), nullable=False),
        sa.Column("course_id", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["professor_id"], ["professors.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("professor_id", "course_id", name="pk_professor_courses"),
    )
    op.create_index("ix_professor_courses_professor_id", "professor_courses", ["professor_id"])
    op.create_index("ix_professor_courses_course_id", "professor_courses", ["course_id"])

    # ── 11. professor_degrees (junction) ───────────────────────────────
    op.create_table(
        "professor_degrees",
        sa.Column("professor_id", sa.UUID(), nullable=False),
        sa.Column("degree_id", sa.BigInteger(), nullable=False),
        sa.Column("institution", sa.String(200), nullable=True),
        sa.Column("year_obtained", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["professor_id"], ["professors.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["degree_id"], ["academic_degrees.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("professor_id", "degree_id", name="pk_professor_degrees"),
    )
    op.create_index("ix_professor_degrees_professor_id", "professor_degrees", ["professor_id"])
    op.create_index("ix_professor_degrees_degree_id", "professor_degrees", ["degree_id"])

    # ── 12. hashtags (GIN index requires pg_trgm) ──────────────────────
    op.create_table(
        "hashtags",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("label", sa.String(100), nullable=False),
        sa.Column("created_by_id", sa.UUID(), nullable=True),
        sa.Column("usage_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("label"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_hashtags_created_by_id", "hashtags", ["created_by_id"])
    op.create_index(
        "ix_hashtags_label_gin",
        "hashtags",
        ["label"],
        postgresql_using="gin",
        postgresql_ops={"label": "gin_trgm_ops"},
    )

    # ── 13. uploaded_documents ─────────────────────────────────────────
    op.create_table(
        "uploaded_documents",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("document_type", sa.String(20), nullable=False),
        sa.Column("file_path", sa.Text(), nullable=False),
        sa.Column("mime_type", sa.String(50), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.CheckConstraint("document_type IN ('carnet','matricula')", name="ck_uploaded_documents_type"),
        sa.CheckConstraint(
            "mime_type IN ('image/jpeg','image/png','application/pdf')",
            name="ck_uploaded_documents_mime",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_uploaded_documents_user_id", "uploaded_documents", ["user_id"])

    # ── 14. verification_requests ──────────────────────────────────────
    op.create_table(
        "verification_requests",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("document_id", sa.UUID(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["document_id"], ["uploaded_documents.id"], ondelete="SET NULL"),
        sa.CheckConstraint(
            "status IN ('pending','approved','rejected')",
            name="ck_verification_requests_status",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_verification_requests_user_id", "verification_requests", ["user_id"])

    # ── 15. evaluations ────────────────────────────────────────────────
    op.create_table(
        "evaluations",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("professor_id", sa.UUID(), nullable=False),
        sa.Column("course_id", sa.BigInteger(), nullable=False),
        sa.Column("semester", sa.String(7), nullable=False),
        sa.Column("clarity", sa.Integer(), nullable=False),
        sa.Column("easiness", sa.Integer(), nullable=False),
        sa.Column("helpfulness", sa.Integer(), nullable=False),
        sa.Column("punctuality", sa.Integer(), nullable=False),
        sa.Column("modality", sa.String(15), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["professor_id"], ["professors.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint(
            "user_id", "professor_id", "course_id", "semester",
            name="uq_evaluations_user_professor_course_semester",
        ),
        sa.CheckConstraint("clarity BETWEEN 1 AND 5", name="ck_evaluations_clarity"),
        sa.CheckConstraint("easiness BETWEEN 1 AND 5", name="ck_evaluations_easiness"),
        sa.CheckConstraint("helpfulness BETWEEN 1 AND 5", name="ck_evaluations_helpfulness"),
        sa.CheckConstraint("punctuality BETWEEN 1 AND 5", name="ck_evaluations_punctuality"),
        sa.CheckConstraint("modality IN ('virtual','presencial','ambas')", name="ck_evaluations_modality"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_evaluations_user_id", "evaluations", ["user_id"])
    op.create_index("ix_evaluations_professor_id", "evaluations", ["professor_id"])
    op.create_index("ix_evaluations_course_id", "evaluations", ["course_id"])

    # ── 16. evaluation_hashtags (junction) ─────────────────────────────
    op.create_table(
        "evaluation_hashtags",
        sa.Column("evaluation_id", sa.UUID(), nullable=False),
        sa.Column("hashtag_id", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["evaluation_id"], ["evaluations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["hashtag_id"], ["hashtags.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("evaluation_id", "hashtag_id", name="pk_evaluation_hashtags"),
    )
    op.create_index("ix_evaluation_hashtags_evaluation_id", "evaluation_hashtags", ["evaluation_id"])
    op.create_index("ix_evaluation_hashtags_hashtag_id", "evaluation_hashtags", ["hashtag_id"])

    # ── 17. comments ───────────────────────────────────────────────────
    op.create_table(
        "comments",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("evaluation_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=True),
        sa.Column("professor_id", sa.UUID(), nullable=False),
        sa.Column("course_id", sa.BigInteger(), nullable=False),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column("modality", sa.String(15), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default=sa.text("'published'")),
        sa.Column("hidden_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("removed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("moderation_verdict", sa.String(20), nullable=True),
        sa.Column("like_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("dislike_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("reports_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["evaluation_id"], ["evaluations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["professor_id"], ["professors.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("evaluation_id", name="uq_comments_evaluation_id"),
        sa.CheckConstraint(
            "status IN ('published','hidden_pending_review','removed')",
            name="ck_comments_status",
        ),
        sa.CheckConstraint(
            "modality IN ('virtual','presencial','ambas')",
            name="ck_comments_modality",
        ),
        sa.CheckConstraint(
            "(removed_at IS NULL) OR (text IS NULL)",
            name="ck_comments_text_null_when_removed",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_comments_user_id", "comments", ["user_id"])
    op.create_index("ix_comments_professor_id", "comments", ["professor_id"])
    op.create_index("ix_comments_status", "comments", ["status"])
    op.create_index("ix_comments_professor_status", "comments", ["professor_id", "status"])
    op.create_index("ix_comments_is_active", "comments", ["is_active"])

    # ── 18. comment_reactions ──────────────────────────────────────────
    op.create_table(
        "comment_reactions",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("comment_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["comment_id"], ["comments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("comment_id", "user_id", name="uq_reactions_user_comment"),
        sa.CheckConstraint("type IN ('like','dislike')", name="ck_reactions_type"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_comment_reactions_comment_id", "comment_reactions", ["comment_id"])
    op.create_index("ix_comment_reactions_user_id", "comment_reactions", ["user_id"])

    # ── 19. comment_reports ────────────────────────────────────────────
    op.create_table(
        "comment_reports",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("comment_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("reason", sa.String(20), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["comment_id"], ["comments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("comment_id", "user_id", name="uq_reports_user_comment"),
        sa.CheckConstraint(
            "reason IN ('spam','hate_speech','harassment','off_topic','other')",
            name="ck_reports_reason",
        ),
        sa.CheckConstraint(
            "status IN ('pending','under_review','resolved_offensive','resolved_safe')",
            name="ck_reports_status",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_comment_reports_comment_id", "comment_reports", ["comment_id"])
    op.create_index("ix_comment_reports_user_id", "comment_reports", ["user_id"])

    # ── 20. moderation_actions ─────────────────────────────────────────
    op.create_table(
        "moderation_actions",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("comment_id", sa.UUID(), nullable=False),
        sa.Column("decision", sa.String(), nullable=False),
        sa.Column("reasoning", sa.Text(), nullable=False),
        sa.Column("reports_count_at_trigger", sa.Integer(), nullable=False),
        sa.Column("triggered_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["comment_id"], ["comments.id"], ondelete="CASCADE"),
        sa.CheckConstraint("decision IN ('keep','remove')", name="ck_moderation_actions_decision"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_moderation_actions_comment_id", "moderation_actions", ["comment_id"])

    # ── 21. user_strikes ───────────────────────────────────────────────
    op.create_table(
        "user_strikes",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("comment_id", sa.UUID(), nullable=False),
        sa.Column("moderation_action_id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["comment_id"], ["comments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["moderation_action_id"], ["moderation_actions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_strikes_user_id", "user_strikes", ["user_id"])
    op.create_index("ix_user_strikes_comment_id", "user_strikes", ["comment_id"])
    op.create_index("ix_user_strikes_moderation_action_id", "user_strikes", ["moderation_action_id"])

    # ── 22. banned_terms ───────────────────────────────────────────────
    op.create_table(
        "banned_terms",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("term", sa.String(100), nullable=False),
        sa.Column("severity", sa.String(10), nullable=False, server_default="high"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("severity IN ('low','medium','high')", name="ck_banned_terms_severity"),
        sa.UniqueConstraint("term"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    for table in _ALL_TABLES:
        op.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
