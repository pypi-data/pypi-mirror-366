"""Module for each item in balance sheet
"""

from pydantic import BaseModel

from .balance_sheet_main_group import BalanceSheetMainGroup
from .balance_sheet_main_group import BalanceSheetMainGroupObjects as BSMain
from .balance_sheet_submain_group import BalanceSheetSubMainGroup
from .balance_sheet_submain_group import (
    BalanceSheetSubMainGroupObjects as BSSubMain,
)


class BalanceSheetItem(BaseModel):
    """Class to represent each balance sheet item in accounting.

    Each balance sheet item in accounting have the following properties:
        - account number: the unique IDentifier of this item
        - name: name of this aitem
        - origin: the origin of item of this item
        - balance sheet sub main group: each item must belong to a
            a group in balance sheet
        - balance sheet main group: this property is readonly
        and is determined by balance sheet sub main group

    """

    ID: str
    name: str
    origin: str | None = None
    balance_sheet_sub_main_group: BalanceSheetSubMainGroup

    @property
    def balance_sheet_main_group(self) -> BalanceSheetMainGroup:
        return self.balance_sheet_sub_main_group.balance_sheet_main_group

    @property
    def bsmain(self) -> BalanceSheetMainGroup:
        return self.balance_sheet_main_group

    @property
    def bssubmain(self) -> BalanceSheetSubMainGroup:
        return self.balance_sheet_sub_main_group

    def __str__(self) -> str:
        return str(self.ID) + " - " + self.name

    def to_csv(self, depth: int = 0, end: str = "\n") -> str:
        assert type(end) is str
        csv = ""
        if depth >= 0:
            csv += f"{self.ID},{self.name},{self.origin}"
        if depth >= 1:
            csv += ","
            csv += f"{self.balance_sheet_sub_main_group.to_csv(depth=depth-1)}"
        csv += end
        return csv

    def is_main_asset(self) -> bool:
        return self.bsmain is BSMain.ASSET

    def is_main_liability(self) -> bool:
        return self.bsmain is BSMain.LIABILITY

    def is_main_equity(self) -> bool:
        return self.bsmain is BSMain.EQUITY

    def is_short_term_asset(self) -> bool:
        return self.bssubmain is BSSubMain.SHORT_TERM_ASSET

    def is_long_term_asset(self) -> bool:
        return self.bssubmain is BSSubMain.LONG_TERM_ASSET

    def is_short_term_liability(self) -> bool:
        return self.bssubmain is BSSubMain.SHORT_TERM_LIABILITY

    def is_long_term_liability(self) -> bool:
        return self.bssubmain is BSSubMain.LONG_TERM_LIABILITY

    def is_equity(self) -> bool:
        return self.bssubmain is BSSubMain.OWNERS_EQUITY
