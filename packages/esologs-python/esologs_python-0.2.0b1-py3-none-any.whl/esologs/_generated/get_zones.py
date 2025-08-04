from typing import List, Optional

from pydantic import Field

from .base_model import BaseModel


class GetZones(BaseModel):
    world_data: Optional["GetZonesWorldData"] = Field(alias="worldData")


class GetZonesWorldData(BaseModel):
    zones: Optional[List[Optional["GetZonesWorldDataZones"]]]


class GetZonesWorldDataZones(BaseModel):
    id: int
    name: str
    frozen: bool
    brackets: Optional["GetZonesWorldDataZonesBrackets"]
    encounters: Optional[List[Optional["GetZonesWorldDataZonesEncounters"]]]
    difficulties: Optional[List[Optional["GetZonesWorldDataZonesDifficulties"]]]
    expansion: "GetZonesWorldDataZonesExpansion"


class GetZonesWorldDataZonesBrackets(BaseModel):
    type: Optional[str]
    min: float
    max: float
    bucket: float


class GetZonesWorldDataZonesEncounters(BaseModel):
    id: int
    name: str


class GetZonesWorldDataZonesDifficulties(BaseModel):
    id: int
    name: str
    sizes: Optional[List[Optional[int]]]


class GetZonesWorldDataZonesExpansion(BaseModel):
    id: int
    name: str


GetZones.model_rebuild()
GetZonesWorldData.model_rebuild()
GetZonesWorldDataZones.model_rebuild()
