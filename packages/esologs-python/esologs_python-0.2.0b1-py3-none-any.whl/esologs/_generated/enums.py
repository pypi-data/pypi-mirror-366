from enum import Enum


class CharacterRankingMetricType(str, Enum):
    bosscdps = "bosscdps"
    bossdps = "bossdps"
    bossndps = "bossndps"
    bossrdps = "bossrdps"
    default = "default"
    dps = "dps"
    hps = "hps"
    krsi = "krsi"
    playerscore = "playerscore"
    playerspeed = "playerspeed"
    cdps = "cdps"
    ndps = "ndps"
    rdps = "rdps"
    tankhps = "tankhps"
    wdps = "wdps"
    healercombineddps = "healercombineddps"
    healercombinedbossdps = "healercombinedbossdps"
    healercombinedcdps = "healercombinedcdps"
    healercombinedbosscdps = "healercombinedbosscdps"
    healercombinedndps = "healercombinedndps"
    healercombinedbossndps = "healercombinedbossndps"
    healercombinedrdps = "healercombinedrdps"
    healercombinedbossrdps = "healercombinedbossrdps"
    tankcombineddps = "tankcombineddps"
    tankcombinedbossdps = "tankcombinedbossdps"
    tankcombinedcdps = "tankcombinedcdps"
    tankcombinedbosscdps = "tankcombinedbosscdps"
    tankcombinedndps = "tankcombinedndps"
    tankcombinedbossndps = "tankcombinedbossndps"
    tankcombinedrdps = "tankcombinedrdps"
    tankcombinedbossrdps = "tankcombinedbossrdps"


class EventDataType(str, Enum):
    All = "All"
    Buffs = "Buffs"
    Casts = "Casts"
    CombatantInfo = "CombatantInfo"
    DamageDone = "DamageDone"
    DamageTaken = "DamageTaken"
    Deaths = "Deaths"
    Debuffs = "Debuffs"
    Dispels = "Dispels"
    Healing = "Healing"
    Interrupts = "Interrupts"
    Resources = "Resources"
    Summons = "Summons"
    Threat = "Threat"


class ExternalBuffRankFilter(str, Enum):
    Any = "Any"
    Require = "Require"
    Exclude = "Exclude"


class FightRankingMetricType(str, Enum):
    default = "default"
    execution = "execution"
    feats = "feats"
    score = "score"
    speed = "speed"
    progress = "progress"


class GraphDataType(str, Enum):
    Summary = "Summary"
    Buffs = "Buffs"
    Casts = "Casts"
    DamageDone = "DamageDone"
    DamageTaken = "DamageTaken"
    Deaths = "Deaths"
    Debuffs = "Debuffs"
    Dispels = "Dispels"
    Healing = "Healing"
    Interrupts = "Interrupts"
    Resources = "Resources"
    Summons = "Summons"
    Survivability = "Survivability"
    Threat = "Threat"


class GuildRank(str, Enum):
    NonMember = "NonMember"
    Applicant = "Applicant"
    Recruit = "Recruit"
    Member = "Member"
    Officer = "Officer"
    GuildMaster = "GuildMaster"


class HardModeLevelRankFilter(str, Enum):
    Any = "Any"
    Highest = "Highest"
    NormalMode = "NormalMode"
    Level0 = "Level0"
    Level1 = "Level1"
    Level2 = "Level2"
    Level3 = "Level3"
    Level4 = "Level4"


class HostilityType(str, Enum):
    Friendlies = "Friendlies"
    Enemies = "Enemies"


class KillType(str, Enum):
    All = "All"
    Encounters = "Encounters"
    Kills = "Kills"
    Trash = "Trash"
    Wipes = "Wipes"


class LeaderboardRank(str, Enum):
    Any = "Any"
    LogsOnly = "LogsOnly"


class RankingCompareType(str, Enum):
    Rankings = "Rankings"
    Parses = "Parses"


class RankingTimeframeType(str, Enum):
    Today = "Today"
    Historical = "Historical"


class ReportRankingMetricType(str, Enum):
    bossdps = "bossdps"
    bossrdps = "bossrdps"
    default = "default"
    dps = "dps"
    hps = "hps"
    krsi = "krsi"
    playerscore = "playerscore"
    playerspeed = "playerspeed"
    rdps = "rdps"
    tankhps = "tankhps"
    wdps = "wdps"


class RoleType(str, Enum):
    Any = "Any"
    DPS = "DPS"
    Healer = "Healer"
    Tank = "Tank"


class SubscriptionStatus(str, Enum):
    Silver = "Silver"
    Gold = "Gold"
    Platinum = "Platinum"
    LegacySilver = "LegacySilver"
    LegacyGold = "LegacyGold"
    LegacyPlatinum = "LegacyPlatinum"
    AlchemicalSociety = "AlchemicalSociety"


class TableDataType(str, Enum):
    Summary = "Summary"
    Buffs = "Buffs"
    Casts = "Casts"
    DamageDone = "DamageDone"
    DamageTaken = "DamageTaken"
    Deaths = "Deaths"
    Debuffs = "Debuffs"
    Dispels = "Dispels"
    Healing = "Healing"
    Interrupts = "Interrupts"
    Resources = "Resources"
    Summons = "Summons"
    Survivability = "Survivability"
    Threat = "Threat"


class ViewType(str, Enum):
    Default = "Default"
    Ability = "Ability"
    Source = "Source"
    Target = "Target"
