from app.models.academic_degree import AcademicDegree
from app.models.ai_job import AiJob
from app.models.banned_term import BannedTerm
from app.models.career import Career
from app.models.career_course import CareerCourse
from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.comment import Comment, CommentStatus
from app.models.course import Course
from app.models.email_verification import EmailVerification
from app.models.evaluation import Evaluation
from app.models.evaluation_hashtag import EvaluationHashtag
from app.models.faculty import Faculty
from app.models.hashtag import Hashtag
from app.models.moderation_action import ModerationAction
from app.models.password_reset import PasswordReset
from app.models.professor import Professor
from app.models.professor_ai_summary import ProfessorAiSummary
from app.models.professor_course import ProfessorCourse
from app.models.professor_degree import ProfessorDegree
from app.models.professor_evidence import ProfessorEvidence
from app.models.reaction import Reaction, ReactionType
from app.models.report import Report, ReportReason, ReportStatus
from app.models.university import University
from app.models.uploaded_document import UploadedDocument
from app.models.user import User
from app.models.user_strike import UserStrike
from app.models.verification_request import VerificationRequest

__all__ = [
    "AcademicDegree",
    "AiJob",
    "BannedTerm",
    "Career",
    "CareerCourse",
    "ChatMessage",
    "ChatSession",
    "Comment",
    "CommentStatus",
    "Course",
    "EmailVerification",
    "Evaluation",
    "EvaluationHashtag",
    "Faculty",
    "Hashtag",
    "ModerationAction",
    "PasswordReset",
    "Professor",
    "ProfessorAiSummary",
    "ProfessorCourse",
    "ProfessorDegree",
    "ProfessorEvidence",
    "Reaction",
    "ReactionType",
    "Report",
    "ReportReason",
    "ReportStatus",
    "University",
    "UploadedDocument",
    "User",
    "UserStrike",
    "VerificationRequest",
]
