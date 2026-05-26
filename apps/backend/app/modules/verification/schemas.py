from pydantic import BaseModel


class UploadCarnetResponse(BaseModel):

    detail: str

    side: str

    is_verified: bool

    request_status: str
