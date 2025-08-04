from typing import List, Optional

from pydantic import Field

from .base_model import BaseModel


class GetGuildById(BaseModel):
    guild_data: Optional["GetGuildByIdGuildData"] = Field(alias="guildData")


class GetGuildByIdGuildData(BaseModel):
    guild: Optional["GetGuildByIdGuildDataGuild"]


class GetGuildByIdGuildDataGuild(BaseModel):
    id: int
    name: str
    description: str
    faction: "GetGuildByIdGuildDataGuildFaction"
    server: "GetGuildByIdGuildDataGuildServer"
    tags: Optional[List[Optional["GetGuildByIdGuildDataGuildTags"]]]


class GetGuildByIdGuildDataGuildFaction(BaseModel):
    name: str


class GetGuildByIdGuildDataGuildServer(BaseModel):
    name: str
    region: "GetGuildByIdGuildDataGuildServerRegion"


class GetGuildByIdGuildDataGuildServerRegion(BaseModel):
    name: str


class GetGuildByIdGuildDataGuildTags(BaseModel):
    id: int
    name: str


GetGuildById.model_rebuild()
GetGuildByIdGuildData.model_rebuild()
GetGuildByIdGuildDataGuild.model_rebuild()
GetGuildByIdGuildDataGuildServer.model_rebuild()
