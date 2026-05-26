from typing import Generic, List, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginateResponse(BaseModel, Generic[T]):
    count: int
    total_pages: int
    current_page: int
    items: List[T]
