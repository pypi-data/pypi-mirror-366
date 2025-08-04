from typing import List, Optional

from pydantic import Field

from .base_model import BaseModel


class GetMaps(BaseModel):
    game_data: Optional["GetMapsGameData"] = Field(alias="gameData")


class GetMapsGameData(BaseModel):
    maps: Optional["GetMapsGameDataMaps"]


class GetMapsGameDataMaps(BaseModel):
    data: Optional[List[Optional["GetMapsGameDataMapsData"]]]
    total: int
    per_page: int
    current_page: int
    from_: Optional[int] = Field(alias="from")
    to: Optional[int]
    last_page: int
    has_more_pages: bool


class GetMapsGameDataMapsData(BaseModel):
    id: int
    name: Optional[str]


GetMaps.model_rebuild()
GetMapsGameData.model_rebuild()
GetMapsGameDataMaps.model_rebuild()
