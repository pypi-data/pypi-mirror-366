"""
BT Staking Explorer - Python wrapper for Rust module
"""

from bt_staking_explorer import bt_staking_explorer as _

get_hotkey_stakes = _.get_hotkey_stakes

from .client import StakingClient
from .types import StakeRecord, StakeRecordWithParents

__version__ = "0.1.0"

__all__ = [
    "StakingClient",
    "StakeRecord",
    "StakeRecordWithParents",
    "__version__",
    "get_hotkey_stakes",
]
