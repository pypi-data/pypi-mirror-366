"""Module for sub main group of items in Balance Sheet
"""

from pydantic import BaseModel

from .balance_sheet_main_group import BalanceSheetMainGroup
from .balance_sheet_main_group import BalanceSheetMainGroupObjects as BSMain


class BalanceSheetSubMainGroup(BaseModel):
    """
    Class to determine Balance Sheet Sub Group.

    Balance Sheet Sub Main Group is one level more granular classification
    of items in balances sheet.

    Balance Sheet Main Group and Sub Main groups are:
    - Asset
        - Current asset
        - Long-term investment
        - Property, plant, and equipment
        - Intangible asset
    - Liability
        - Current Liability
        - Long-term liability
    - Equity
        - Owner's Investment

    """

    id: int
    name: str
    balance_sheet_main_group: BalanceSheetMainGroup

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"BalanceSheetMainGroup(id={self.id}, name={self.name})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BalanceSheetSubMainGroup):
            return False
        return self.id == other.id

    def to_csv(self, depth: int = 0, end: str = "") -> str:
        """Returns comma separated value representation."""
        if depth < 0:
            return "" + end
        deep_part = f"{self.balance_sheet_main_group.to_csv(depth=depth-1)}"
        if deep_part:
            deep_part = "," + deep_part
        return f"{self.id},{self.name}" + deep_part + end


# Balance Sheet Sub Main Group Objects

SHORT_TERM_ASSET = BalanceSheetSubMainGroup(
    id=1,
    name="Short Term Asset",
    balance_sheet_main_group=BSMain.ASSET,
)

LONG_TERM_ASSET = BalanceSheetSubMainGroup(
    id=2,
    name="Long Term Asset",
    balance_sheet_main_group=BSMain.ASSET,
)

SHORT_TERM_LIABILITY = BalanceSheetSubMainGroup(
    id=11,
    name="Short Term Liability",
    balance_sheet_main_group=BSMain.LIABILITY,
)

LONG_TERM_LIABILITY = BalanceSheetSubMainGroup(
    id=12,
    name="Long Term Liability",
    balance_sheet_main_group=BSMain.LIABILITY,
)

OWNERS_EQUITY = BalanceSheetSubMainGroup(
    id=21,
    name="Owner's Equity",
    balance_sheet_main_group=BSMain.EQUITY,
)


class BalanceSheetSubMainGroupObjects:
    """Class with class level attributes which contains
    standard balance sheet submain group objects.

    Attributes
    ----------
    SHORT_TERM_ASSET : BalanceSheetSubMainGroup
    LONG_TERM_ASSET : BalanceSheetSubMainGroup
    SHORT_TERM_LIABILITY : BalanceSheetSubMainGroup
    LONG_TERM_LIABILITY : BalanceSheetSubMainGroup
    OWNERS_EQUITY : BalanceSheetSubMainGroup
    """

    SHORT_TERM_ASSET = SHORT_TERM_ASSET
    LONG_TERM_ASSET = LONG_TERM_ASSET
    SHORT_TERM_LIABILITY = SHORT_TERM_LIABILITY
    LONG_TERM_LIABILITY = LONG_TERM_LIABILITY
    OWNERS_EQUITY = OWNERS_EQUITY
