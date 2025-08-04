from typing import List, Optional

from pydantic import Field

from .base_model import BaseModel


class GetItems(BaseModel):
    game_data: Optional["GetItemsGameData"] = Field(alias="gameData")


class GetItemsGameData(BaseModel):
    items: Optional["GetItemsGameDataItems"]


class GetItemsGameDataItems(BaseModel):
    data: Optional[List[Optional["GetItemsGameDataItemsData"]]]
    total: int
    per_page: int
    current_page: int
    from_: Optional[int] = Field(alias="from")
    to: Optional[int]
    last_page: int
    has_more_pages: bool


class GetItemsGameDataItemsData(BaseModel):
    id: int
    name: Optional[str]
    icon: Optional[str]


GetItems.model_rebuild()
GetItemsGameData.model_rebuild()
GetItemsGameDataItems.model_rebuild()
