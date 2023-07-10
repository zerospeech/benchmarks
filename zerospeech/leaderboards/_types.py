from enum import Enum


class LeaderboardBenchmarkName(str, Enum):
    ABX_15 = "ABX-15"
    ABX_17 = "ABX-17"
    ABX_LS_LG = "ABX-LS-Legacy"
    ABX_LS = "ABX-LS"
    TDE_15 = "TDE-15"
    TDE_17 = "TDE-17"
    TTS0_19 = "TTS0-19"
    sLM_21 = "sLM-21"
    prosAudit = "prosAudit"
