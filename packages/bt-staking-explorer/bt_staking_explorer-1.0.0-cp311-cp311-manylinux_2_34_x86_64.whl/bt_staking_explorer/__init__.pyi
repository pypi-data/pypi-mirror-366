from typing import Any
from .client import StakingClient
from .types import StakeRecord, StakeRecordWithParents

def get_hotkey_stakes(
    url: str, requests: list[dict[str, Any]]
) -> list[dict[str, Any]]: ...

__version__: str

__all__ = [
    "get_hotkey_stakes",
    "StakingClient",
    "StakeRecord",
    "StakeRecordWithParents",
    "__version__",
]
