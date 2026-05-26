from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.faculty import Faculty
from app.models.university import University


class CatalogService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_universities(self) -> list[University]:
        stmt = select(University).order_by(University.name.asc())
        return list((await self.db.execute(stmt)).scalars().all())

    async def get_university(self, university_id: int) -> University | None:
        stmt = select(University).where(University.id == university_id)
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def list_faculties(self, university_id: int) -> list[Faculty]:
        stmt = (
            select(Faculty)
            .where(Faculty.university_id == university_id)
            .order_by(Faculty.name.asc())
        )
        return list((await self.db.execute(stmt)).scalars().all())
