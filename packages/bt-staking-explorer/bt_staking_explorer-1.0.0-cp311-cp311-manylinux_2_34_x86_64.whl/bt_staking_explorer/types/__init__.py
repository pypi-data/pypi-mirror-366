"""
Types for BT Staking Explorer
"""

from dataclasses import dataclass

try:
    from bt_staking_explorer import StakeRecord as RustStakeRecord

    RUST_MODULE_AVAILABLE = True
except ImportError:
    RUST_MODULE_AVAILABLE = False
    RustStakeRecord = None


@dataclass
class StakeRecord:
    """Python wrapper for Rust StakeRecord"""

    hotkey: str
    coldkey: str
    alpha: float
    alpha_raw: int
    ratio: float

    @classmethod
    def from_rust(cls, rust_record) -> "StakeRecord":
        """Create from Rust StakeRecord"""
        return cls(
            hotkey=rust_record.hotkey,
            coldkey=rust_record.coldkey,
            alpha=rust_record.alpha,
            alpha_raw=rust_record.alpha_raw,
            ratio=rust_record.ratio,
        )


@dataclass
class ParentInfo:
    """Information about a parent hotkey"""

    parent_hotkey: str
    proportion: float
    stakes: list[StakeRecord]


@dataclass
class StakeRecordWithParents:
    """Stake record with parent information"""

    hotkey: str
    coldkey: str
    alpha: float
    alpha_raw: int
    ratio: float
    parents: list[ParentInfo]

    @classmethod
    def from_stake_record(
        cls, stake: StakeRecord, parents: list[ParentInfo]
    ) -> "StakeRecordWithParents":
        """Create from StakeRecord and parents"""
        return cls(
            hotkey=stake.hotkey,
            coldkey=stake.coldkey,
            alpha=stake.alpha,
            alpha_raw=stake.alpha_raw,
            ratio=stake.ratio,
            parents=parents,
        )


__all__ = ["StakeRecord", "StakeRecordWithParents", "ParentInfo"]
