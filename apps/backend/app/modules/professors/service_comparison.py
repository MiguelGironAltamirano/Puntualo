"""Professor comparison service.

Handles fetching and aggregating data for comparing multiple professors.
"""
import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment, CommentStatus
from app.models.course import Course
from app.models.evaluation import Evaluation
from app.models.professor import Professor
from app.models.professor_ai_summary import ProfessorAiSummary
from app.models.professor_course import ProfessorCourse


class ComparisonService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_comparison_data(
        self,
        professor_ids: list[str],
    ):
        """
        Get comparison data for multiple professors.
        
        Returns:
            {
                "professors": [{professor data with metrics}],
                "comparison_metrics": {best scores and counts}
            }
        """
        # Normalize IDs
        normalized_ids = [uuid.UUID(pid) if isinstance(pid, str) else pid for pid in professor_ids]
        
        # Fetch all professors
        prof_stmt = select(Professor).where(Professor.id.in_(normalized_ids), Professor.is_active.is_(True))
        professors = list((await self.db.execute(prof_stmt)).scalars().all())
        
        if not professors:
            return {"professors": [], "comparison_metrics": {}}
        
        # Build comparison data for each professor
        comparison_data = []
        
        for prof in professors:
            # Get courses taught by this professor
            courses = await self._get_professor_courses(prof.id)
            
            # Get evaluation breakdown by modality
            eval_breakdown = await self._get_evaluation_breakdown(prof.id)
            
            # Get average scores per evaluation metric
            avg_scores = await self._get_average_scores(prof.id)
            
            # Get 5 most recent comments
            recent_comments = await self._get_recent_comments(prof.id, limit=5)
            
            # Get AI summary if exists
            ai_summary = await self._get_ai_summary(prof.id)
            
            # Find common courses with other professors
            common_courses = await self._get_common_courses(prof.id, [p.id for p in professors if p.id != prof.id])
            
            comparison_data.append({
                "id": str(prof.id),
                "full_name": prof.full_name,
                "university_id": prof.university_id,
                "faculty_id": prof.faculty_id,
                "global_score": float(prof.global_score) if prof.global_score else None,
                "total_evaluations": prof.total_evaluations,
                "avg_clarity": avg_scores.get("clarity", 0),
                "avg_easiness": avg_scores.get("easiness", 0),
                "avg_helpfulness": avg_scores.get("helpfulness", 0),
                "avg_punctuality": avg_scores.get("punctuality", 0),
                "validation_status": prof.validation_status,
                "created_at": prof.created_at,
                "courses": courses,
                "evaluation_breakdown": eval_breakdown,
                "common_courses": common_courses,
                "recent_comments": recent_comments,
                "ai_summary": ai_summary,
            })
        
        # Calculate comparison metrics (best in each category)
        comparison_metrics = self._calculate_comparison_metrics(comparison_data)
        
        return {
            "professors": comparison_data,
            "comparison_metrics": comparison_metrics,
        }

    async def _get_professor_courses(self, professor_id: uuid.UUID):
        """Get list of courses taught by professor."""
        stmt = (
            select(Course.id, Course.name, Course.faculty_id)
            .join(ProfessorCourse, ProfessorCourse.course_id == Course.id)
            .where(
                ProfessorCourse.professor_id == professor_id,
                Course.is_active.is_(True),
            )
            .order_by(Course.name.asc())
        )
        rows = (await self.db.execute(stmt)).all()
        return [
            {"id": row[0], "name": row[1], "faculty_id": row[2]}
            for row in rows
        ]

    async def _get_evaluation_breakdown(self, professor_id: uuid.UUID):
        """Get count of evaluations by modality."""
        stmt = (
            select(Evaluation.modality, func.count(Evaluation.id).label("count"))
            .where(Evaluation.professor_id == professor_id)
            .group_by(Evaluation.modality)
        )
        rows = (await self.db.execute(stmt)).all()
        breakdown = {"virtual": 0, "presencial": 0, "ambas": 0}
        for row in rows:
            breakdown[row[0]] = row[1]
        return breakdown

    async def _get_average_scores(self, professor_id: uuid.UUID):
        """Get average scores for all metrics."""
        stmt = select(
            func.coalesce(func.avg(Evaluation.clarity), 0).label("clarity"),
            func.coalesce(func.avg(Evaluation.easiness), 0).label("easiness"),
            func.coalesce(func.avg(Evaluation.helpfulness), 0).label("helpfulness"),
            func.coalesce(func.avg(Evaluation.punctuality), 0).label("punctuality"),
        ).where(Evaluation.professor_id == professor_id)
        
        row = (await self.db.execute(stmt)).one()
        return {
            "clarity": float(row[0]),
            "easiness": float(row[1]),
            "helpfulness": float(row[2]),
            "punctuality": float(row[3]),
        }

    async def _get_recent_comments(self, professor_id: uuid.UUID, limit: int = 5):
        """Get most recent published comments."""
        stmt = (
            select(
                Comment.id,
                Comment.text,
                Comment.like_count,
                Comment.dislike_count,
                Comment.created_at,
                Course.name,
            )
            .join(Course, Course.id == Comment.course_id)
            .where(
                Comment.professor_id == professor_id,
                Comment.status == CommentStatus.PUBLISHED.value,
                Comment.text.isnot(None),
            )
            .order_by(Comment.created_at.desc())
            .limit(limit)
        )
        rows = (await self.db.execute(stmt)).all()
        return [
            {
                "id": str(row[0]),
                "text": row[1],
                "like_count": row[2],
                "dislike_count": row[3],
                "created_at": row[4],
                "course_name": row[5],
            }
            for row in rows
        ]

    async def _get_ai_summary(self, professor_id: uuid.UUID):
        """Get AI summary if exists."""
        stmt = (
            select(ProfessorAiSummary)
            .where(ProfessorAiSummary.professor_id == professor_id)
            .order_by(ProfessorAiSummary.created_at.desc())
            .limit(1)
        )
        summary = (await self.db.execute(stmt)).scalar_one_or_none()
        if summary:
            return {
                "summary": summary.summary,
                "pros": summary.pros,
                "cons": summary.cons,
                "model_version": summary.model_version,
                "generated_at": summary.generated_at,
            }
        return None

    async def _get_common_courses(
        self,
        professor_id: uuid.UUID,
        other_professor_ids: list[uuid.UUID],
    ):
        """Get courses taught by this professor and at least one other compared professor."""
        if not other_professor_ids:
            return []
        
        # Subqueries for each other professor's courses
        stmt = (
            select(Course.id, Course.name, func.count(ProfessorCourse.professor_id).label("prof_count"))
            .join(ProfessorCourse, ProfessorCourse.course_id == Course.id)
            .where(
                Course.is_active.is_(True),
                ProfessorCourse.professor_id.in_([professor_id] + other_professor_ids),
            )
            .group_by(Course.id, Course.name)
            .having(func.count(ProfessorCourse.professor_id) > 1)  # Taught by at least 2 professors
            .order_by(Course.name.asc())
        )
        rows = (await self.db.execute(stmt)).all()
        return [
            {"id": row[0], "name": row[1]}
            for row in rows
        ]

    def _calculate_comparison_metrics(self, comparison_data: list[dict]):
        """Calculate which professor is best in each category."""
        if not comparison_data:
            return {}
        
        metrics = {}
        
        # Find best clarity
        best_clarity = max(
            comparison_data,
            key=lambda x: x.get("avg_clarity", 0),
        )
        metrics["best_clarity"] = {
            "professor_id": best_clarity["id"],
            "professor_name": best_clarity["full_name"],
            "score": best_clarity.get("avg_clarity", 0),
        }
        
        # Find best easiness (lowest difficulty)
        best_easiness = min(
            comparison_data,
            key=lambda x: x.get("avg_easiness", 5),
        )
        metrics["easiest"] = {
            "professor_id": best_easiness["id"],
            "professor_name": best_easiness["full_name"],
            "score": best_easiness.get("avg_easiness", 0),
        }
        
        # Find best helpfulness
        best_helpfulness = max(
            comparison_data,
            key=lambda x: x.get("avg_helpfulness", 0),
        )
        metrics["best_helpfulness"] = {
            "professor_id": best_helpfulness["id"],
            "professor_name": best_helpfulness["full_name"],
            "score": best_helpfulness.get("avg_helpfulness", 0),
        }
        
        # Find best punctuality
        best_punctuality = max(
            comparison_data,
            key=lambda x: x.get("avg_punctuality", 0),
        )
        metrics["best_punctuality"] = {
            "professor_id": best_punctuality["id"],
            "professor_name": best_punctuality["full_name"],
            "score": best_punctuality.get("avg_punctuality", 0),
        }
        
        # Find most evaluated
        most_evaluated = max(
            comparison_data,
            key=lambda x: x.get("total_evaluations", 0),
        )
        metrics["most_evaluated"] = {
            "professor_id": most_evaluated["id"],
            "professor_name": most_evaluated["full_name"],
            "count": most_evaluated.get("total_evaluations", 0),
        }
        
        # Find highest global score
        with_scores = [p for p in comparison_data if p.get("global_score") is not None]
        if with_scores:
            best_score = max(
                with_scores,
                key=lambda x: x.get("global_score", 0),
            )
            metrics["highest_global_score"] = {
                "professor_id": best_score["id"],
                "professor_name": best_score["full_name"],
                "score": best_score.get("global_score", 0),
            }
        
        return metrics
