from pydantic import BaseModel


class AdminStatsResponse(BaseModel):

    users_pending: int

    professors_pending: int
