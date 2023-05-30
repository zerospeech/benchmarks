from enum import Enum
from typing import Type, Dict, Any, Optional

from .abxLS import ABXLSLeaderboard
from .prosaudit import ProsAuditLeaderboard
from .sLM21 import SLM21Leaderboard
from .tde17 import TDE17Leaderboard
from .._models import Leaderboard


class UnspecifiedLeaderboard(Exception):
    """ A leaderboard of unknown type """
    pass


class BenchmarkLeaderboard(str, Enum):
    """ Defined leaderboards for each benchmark """

    def __new__(
            cls,
            leaderboard_cls: Type[Leaderboard],
    ):
        """ Allow setting parameters on enum """
        cls_obj = leaderboard_cls(data=[])
        label = cls_obj._type  # noqa: private access
        obj = str.__new__(cls, label)
        obj.cls = leaderboard_cls
        return obj

    prosAudit = ProsAuditLeaderboard
    sLM21 = SLM21Leaderboard
    abx_LS = ABXLSLeaderboard
    # todo implement tss019 leaderboard
    # tts019 = ...
    # todo implement abx17 leaderboard
    # abx_17 = ...
    tde17 = TDE17Leaderboard

    @classmethod
    def from_dict(cls, ld_data: Dict[str, Any], *, force_type: Optional[str] = None) -> Leaderboard:
        if force_type:
            return cls(force_type).cls.parse_obj(ld_data)
        elif '_type' in ld_data:
            return cls(ld_data['_type']).cls.parse_obj(ld_data)
        raise UnspecifiedLeaderboard("This leaderboard does not contain type name")
