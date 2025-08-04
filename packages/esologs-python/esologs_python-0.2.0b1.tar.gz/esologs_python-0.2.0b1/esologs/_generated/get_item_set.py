from typing import Optional

from pydantic import Field

from .base_model import BaseModel


class GetItemSet(BaseModel):
    game_data: Optional["GetItemSetGameData"] = Field(alias="gameData")


class GetItemSetGameData(BaseModel):
    item_set: Optional["GetItemSetGameDataItemSet"]


class GetItemSetGameDataItemSet(BaseModel):
    id: int
    name: Optional[str]


GetItemSet.model_rebuild()
GetItemSetGameData.model_rebuild()
