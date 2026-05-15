from app.models.academic_degree import AcademicDegree
from app.models.class_ import Class
from app.models.like import Like
from app.models.professor import Professor
from app.models.rating_category import RatingCategory
from app.models.rating_detail import RatingDetail
from app.models.review import Review, ReviewStatus
from app.models.subject import Subject
from app.models.university import University
from app.models.user import User

__all__ = [
    "User",
    "AcademicDegree",
    "University",
    "Subject",
    "RatingCategory",
    "Professor",
    "Class",
    "Review",
    "ReviewStatus",
    "RatingDetail",
    "Like",
]
