from typing import Optional

from pydantic import Field

from .base_model import BaseModel


class GetCharacterById(BaseModel):
    character_data: Optional["GetCharacterByIdCharacterData"] = Field(
        alias="characterData"
    )


class GetCharacterByIdCharacterData(BaseModel):
    character: Optional["GetCharacterByIdCharacterDataCharacter"]


class GetCharacterByIdCharacterDataCharacter(BaseModel):
    id: int
    name: str
    class_id: int = Field(alias="classID")
    race_id: int = Field(alias="raceID")
    guild_rank: int = Field(alias="guildRank")
    hidden: bool
    server: "GetCharacterByIdCharacterDataCharacterServer"


class GetCharacterByIdCharacterDataCharacterServer(BaseModel):
    name: str
    region: "GetCharacterByIdCharacterDataCharacterServerRegion"


class GetCharacterByIdCharacterDataCharacterServerRegion(BaseModel):
    name: str


GetCharacterById.model_rebuild()
GetCharacterByIdCharacterData.model_rebuild()
GetCharacterByIdCharacterDataCharacter.model_rebuild()
GetCharacterByIdCharacterDataCharacterServer.model_rebuild()
