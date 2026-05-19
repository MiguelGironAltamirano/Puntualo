"""models refactor

Esta migración:
  1. Merge los 2 heads (`617857f3f635` y `6e7291ffaa57`) en un único head.
  2. DROP de las tablas overlapping del PR del compañero
     (reviews, rating_details, rating_categories, likes, classes, subjects, teachers).
  3. ALTER `universities` para agregar TimestampMixin + UNIQUE(name).
  4. CREATE `faculties` (nueva entidad).
  5. ALTER `professors`: reemplaza columns string `university`/`faculty` por FKs
     `university_id`/`faculty_id`, y agrega `global_score`/`total_evaluations` + CHECK.
  6. CREATE `courses`, `evaluations`, `comments`, `comment_reactions`, `comment_reports`.

Mantiene intactas: `universities` (con timestamps nuevos), `academic_degrees`,
`users`, `professor_evidence`.

ATENCIÓN: la transformación de `professors.university` (String) → `university_id` (FK)
ejecuta `TRUNCATE professors RESTART IDENTITY CASCADE` al inicio del ALTER. Wipea
los profesores existentes y, por CASCADE, también `professor_evidence`.
Recrear datos vía POST /professors después del upgrade.

Revision ID: b3a7c5d9e1f2
Revises: 6e7291ffaa57, 617857f3f635
Create Date: 2026-05-18 23:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "b3a7c5d9e1f2"
down_revision: Union[str, Sequence[str], None] = ("6e7291ffaa57", "617857f3f635")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ──────────────────────────────────────────────────────────────────
    # 1. DROP overlapping tables del PR del compañero (orden leaf-first)
    # ──────────────────────────────────────────────────────────────────
    op.drop_table("rating_details")
    op.drop_table("likes")
    op.drop_table("reviews")
    op.drop_table("rating_categories")
    op.drop_table("classes")
    op.drop_table("teachers")
    op.drop_table("subjects")

    # El enum `resena_estado` fue creado en `ef5a73d642ed` y no fue renombrado
    # por `617857f3f635` (la rename migration solo tocó nombres de columnas).
    # Al dropear `reviews` el tipo queda huérfano — lo eliminamos explícitamente.
    op.execute("DROP TYPE IF EXISTS resena_estado")

    # ──────────────────────────────────────────────────────────────────
    # 2. ALTER universities — TimestampMixin + UNIQUE(name)
    # ──────────────────────────────────────────────────────────────────
    op.add_column(
        "universities",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.add_column(
        "universities",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_unique_constraint("uq_universities_name", "universities", ["name"])

    # ──────────────────────────────────────────────────────────────────
    # 3. CREATE faculties
    # ──────────────────────────────────────────────────────────────────
    op.create_table(
        "faculties",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("university_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["university_id"], ["universities.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "name", "university_id", name="uq_faculties_name_university"
        ),
    )
    op.create_index(
        "ix_faculties_university_id", "faculties", ["university_id"]
    )

    # ──────────────────────────────────────────────────────────────────
    # 4. ALTER professors — reemplaza strings por FKs + agrega score cols
    # ──────────────────────────────────────────────────────────────────
    # Wipe data existente. Las columnas `university`/`faculty` (String) cambian
    # de tipo a FK Integer; las nuevas columnas son NOT NULL y los rows previos
    # no tienen valor que poner. Decisión de equipo: para MVP recrear vía
    # POST /professors después del upgrade. CASCADE wipea professor_evidence.
    op.execute("TRUNCATE professors RESTART IDENTITY CASCADE")

    # Drop old unique index (referencia la columna `university` que vamos a dropear)
    op.drop_index(
        "uq_professors_name_university_active",
        table_name="professors",
    )

    op.drop_column("professors", "university")
    op.drop_column("professors", "faculty")

    op.add_column(
        "professors",
        sa.Column("university_id", sa.Integer(), nullable=False),
    )
    op.add_column(
        "professors",
        sa.Column("faculty_id", sa.Integer(), nullable=False),
    )
    op.create_foreign_key(
        "fk_professors_university_id",
        "professors",
        "universities",
        ["university_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_professors_faculty_id",
        "professors",
        "faculties",
        ["faculty_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index(
        "ix_professors_university_id", "professors", ["university_id"]
    )
    op.create_index(
        "ix_professors_faculty_id", "professors", ["faculty_id"]
    )

    op.add_column(
        "professors",
        sa.Column("global_score", sa.Float(), nullable=True),
    )
    op.add_column(
        "professors",
        sa.Column(
            "total_evaluations",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
    )
    op.create_check_constraint(
        "ck_professors_global_score_range",
        "professors",
        "global_score IS NULL OR global_score BETWEEN 1.0 AND 5.0",
    )

    # Recrear unique index ahora con `university_id`
    op.create_index(
        "uq_professors_name_university_active",
        "professors",
        [sa.text("lower(full_name)"), sa.text("university_id")],
        unique=True,
        postgresql_where=sa.text("is_active = true"),
    )

    # ──────────────────────────────────────────────────────────────────
    # 5. CREATE courses
    # ──────────────────────────────────────────────────────────────────
    op.create_table(
        "courses",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("university_id", sa.Integer(), nullable=False),
        sa.Column("faculty_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["university_id"], ["universities.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["faculty_id"], ["faculties.id"], ondelete="RESTRICT"
        ),
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

    # ──────────────────────────────────────────────────────────────────
    # 6. CREATE evaluations
    # ──────────────────────────────────────────────────────────────────
    op.create_table(
        "evaluations",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("professor_id", sa.String(), nullable=False),
        sa.Column("course_id", sa.String(), nullable=False),
        sa.Column("semester", sa.String(length=7), nullable=False),
        sa.Column("clarity", sa.Integer(), nullable=False),
        sa.Column("easiness", sa.Integer(), nullable=False),
        sa.Column("helpfulness", sa.Integer(), nullable=False),
        sa.Column("punctuality", sa.Integer(), nullable=False),
        sa.Column("course_difficulty", sa.Integer(), nullable=False),
        sa.Column("modality", sa.String(length=15), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["professor_id"], ["professors.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["course_id"], ["courses.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "professor_id",
            "course_id",
            "semester",
            name="uq_evaluations_user_professor_course_semester",
        ),
        sa.CheckConstraint(
            "clarity BETWEEN 1 AND 5", name="ck_evaluations_clarity"
        ),
        sa.CheckConstraint(
            "easiness BETWEEN 1 AND 5", name="ck_evaluations_easiness"
        ),
        sa.CheckConstraint(
            "helpfulness BETWEEN 1 AND 5", name="ck_evaluations_helpfulness"
        ),
        sa.CheckConstraint(
            "punctuality BETWEEN 1 AND 5", name="ck_evaluations_punctuality"
        ),
        sa.CheckConstraint(
            "course_difficulty BETWEEN 1 AND 5",
            name="ck_evaluations_difficulty",
        ),
        sa.CheckConstraint(
            "modality IN ('virtual','presencial','ambas')",
            name="ck_evaluations_modality",
        ),
    )
    op.create_index("ix_evaluations_user_id", "evaluations", ["user_id"])
    op.create_index(
        "ix_evaluations_professor_id", "evaluations", ["professor_id"]
    )
    op.create_index("ix_evaluations_course_id", "evaluations", ["course_id"])

    # ──────────────────────────────────────────────────────────────────
    # 7. CREATE comments
    # ──────────────────────────────────────────────────────────────────
    op.create_table(
        "comments",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("evaluation_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=True),
        sa.Column("professor_id", sa.String(), nullable=False),
        sa.Column("course_id", sa.String(), nullable=False),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column("modality", sa.String(length=15), nullable=False),
        sa.Column(
            "is_verified",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=30),
            server_default=sa.text("'published'"),
            nullable=False,
        ),
        sa.Column("hidden_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("removed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "moderation_verdict", sa.String(length=20), nullable=True
        ),
        sa.Column(
            "helpful_count",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "not_helpful_count",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "reports_count",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["evaluation_id"], ["evaluations.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["professor_id"], ["professors.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["course_id"], ["courses.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
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
    )
    op.create_index("ix_comments_user_id", "comments", ["user_id"])
    op.create_index("ix_comments_professor_id", "comments", ["professor_id"])
    op.create_index("ix_comments_status", "comments", ["status"])
    op.create_index(
        "ix_comments_professor_status", "comments", ["professor_id", "status"]
    )
    op.create_index("ix_comments_is_active", "comments", ["is_active"])

    # ──────────────────────────────────────────────────────────────────
    # 8. CREATE comment_reactions
    # ──────────────────────────────────────────────────────────────────
    op.create_table(
        "comment_reactions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("comment_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["comment_id"], ["comments.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "comment_id", "user_id", name="uq_reactions_user_comment"
        ),
        sa.CheckConstraint(
            "type IN ('helpful','not_helpful')",
            name="ck_reactions_type",
        ),
    )
    op.create_index(
        "ix_comment_reactions_comment_id", "comment_reactions", ["comment_id"]
    )
    op.create_index(
        "ix_comment_reactions_user_id", "comment_reactions", ["user_id"]
    )

    # ──────────────────────────────────────────────────────────────────
    # 9. CREATE comment_reports
    # ──────────────────────────────────────────────────────────────────
    op.create_table(
        "comment_reports",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("comment_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("reason", sa.String(length=20), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.String(length=30),
            server_default=sa.text("'pending'"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["comment_id"], ["comments.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "comment_id", "user_id", name="uq_reports_user_comment"
        ),
        sa.CheckConstraint(
            "reason IN ('spam','hate_speech','harassment','off_topic','other')",
            name="ck_reports_reason",
        ),
        sa.CheckConstraint(
            "status IN ('pending','under_review','resolved_offensive','resolved_safe')",
            name="ck_reports_status",
        ),
    )
    op.create_index(
        "ix_comment_reports_comment_id", "comment_reports", ["comment_id"]
    )
    op.create_index(
        "ix_comment_reports_user_id", "comment_reports", ["user_id"]
    )


def downgrade() -> None:
    # Drop tablas nuevas (orden reverso)
    op.drop_table("comment_reports")
    op.drop_table("comment_reactions")
    op.drop_table("comments")
    op.drop_table("evaluations")
    op.drop_table("courses")

    # Revertir alter de professors
    op.drop_index(
        "uq_professors_name_university_active", table_name="professors"
    )
    op.drop_constraint(
        "ck_professors_global_score_range", "professors", type_="check"
    )
    op.drop_column("professors", "total_evaluations")
    op.drop_column("professors", "global_score")
    op.drop_constraint(
        "fk_professors_faculty_id", "professors", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_professors_university_id", "professors", type_="foreignkey"
    )
    op.drop_index("ix_professors_faculty_id", table_name="professors")
    op.drop_index("ix_professors_university_id", table_name="professors")
    op.drop_column("professors", "faculty_id")
    op.drop_column("professors", "university_id")
    op.add_column(
        "professors",
        sa.Column(
            "university",
            sa.String(length=150),
            server_default="",
            nullable=False,
        ),
    )
    op.add_column(
        "professors",
        sa.Column(
            "faculty",
            sa.String(length=150),
            server_default="",
            nullable=False,
        ),
    )
    op.alter_column("professors", "university", server_default=None)
    op.alter_column("professors", "faculty", server_default=None)
    op.create_index(
        "uq_professors_name_university_active",
        "professors",
        [sa.text("lower(full_name)"), sa.text("university")],
        unique=True,
        postgresql_where=sa.text("is_active = true"),
    )

    # Drop faculties
    op.drop_index("ix_faculties_university_id", table_name="faculties")
    op.drop_table("faculties")

    # Revertir universities
    op.drop_constraint("uq_universities_name", "universities", type_="unique")
    op.drop_column("universities", "updated_at")
    op.drop_column("universities", "created_at")

    # NO se recrean teachers/classes/subjects/reviews/etc. — fueron eliminadas
    # intencionalmente por overlapping con el dominio Course/Evaluation/Comment/etc.
    # Para recuperarlas, correr las migraciones históricas del compañero en una DB nueva.
