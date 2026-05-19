from app.models.academic_degree import AcademicDegree
from app.models.comment import Comment, CommentStatus
from app.models.course import Course
from app.models.evaluation import Evaluation
from app.models.faculty import Faculty
from app.models.professor import Professor
from app.models.professor_evidence import ProfessorEvidence
from app.models.reaction import Reaction, ReactionType
from app.models.report import Report, ReportReason, ReportStatus
from app.models.university import University
from app.models.user import User

__all__ = [
    "AcademicDegree",
    "Comment",
    "CommentStatus",
    "Course",
    "Evaluation",
    "Faculty",
    "Professor",
    "ProfessorEvidence",
    "Reaction",
    "ReactionType",
    "Report",
    "ReportReason",
    "ReportStatus",
    "University",
    "User",
]
