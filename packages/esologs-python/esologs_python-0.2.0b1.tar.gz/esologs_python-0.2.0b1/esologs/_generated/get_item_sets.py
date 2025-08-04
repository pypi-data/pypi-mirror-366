from typing import List, Optional

from pydantic import Field

from .base_model import BaseModel


class GetItemSets(BaseModel):
    game_data: Optional["GetItemSetsGameData"] = Field(alias="gameData")


class GetItemSetsGameData(BaseModel):
    item_sets: Optional["GetItemSetsGameDataItemSets"]


class GetItemSetsGameDataItemSets(BaseModel):
    data: Optional[List[Optional["GetItemSetsGameDataItemSetsData"]]]
    total: int
    per_page: int
    current_page: int
    from_: Optional[int] = Field(alias="from")
    to: Optional[int]
    last_page: int
    has_more_pages: bool


class GetItemSetsGameDataItemSetsData(BaseModel):
    id: int
    name: Optional[str]


GetItemSets.model_rebuild()
GetItemSetsGameData.model_rebuild()
GetItemSetsGameDataItemSets.model_rebuild()
