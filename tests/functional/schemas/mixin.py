from uuid import UUID

from pydantic import BaseModel


class UUIDValidation(BaseModel):
    id: UUID


class PaginationValidation(BaseModel):
    total: int
    page: int
    page_size: int
    next_page: int | None = None
    previous_page: int | None = None
    available_pages: int
