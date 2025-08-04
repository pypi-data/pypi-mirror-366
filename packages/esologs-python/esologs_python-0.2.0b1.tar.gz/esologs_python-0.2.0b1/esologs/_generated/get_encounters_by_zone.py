from typing import List, Optional

from pydantic import Field

from .base_model import BaseModel


class GetEncountersByZone(BaseModel):
    world_data: Optional["GetEncountersByZoneWorldData"] = Field(alias="worldData")


class GetEncountersByZoneWorldData(BaseModel):
    zone: Optional["GetEncountersByZoneWorldDataZone"]


class GetEncountersByZoneWorldDataZone(BaseModel):
    id: int
    name: str
    encounters: Optional[List[Optional["GetEncountersByZoneWorldDataZoneEncounters"]]]


class GetEncountersByZoneWorldDataZoneEncounters(BaseModel):
    id: int
    name: str


GetEncountersByZone.model_rebuild()
GetEncountersByZoneWorldData.model_rebuild()
GetEncountersByZoneWorldDataZone.model_rebuild()
