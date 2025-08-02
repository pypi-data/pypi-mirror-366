from .balance_sheet_item import BalanceSheetItem


class BalanceSheetItemTuple:

    def __init__(
        self,
        balance_sheet_item: BalanceSheetItem,
        debit: float,
        credit: float,
    ) -> None:
        self.balance_sheet_item = balance_sheet_item
        self.debit = debit
        self.credit = credit

    @property
    def balance_sheet_item(self) -> BalanceSheetItem:
        return self._balance_sheet_item

    @balance_sheet_item.setter
    def balance_sheet_item(self, balance_sheet_item: BalanceSheetItem) -> None:
        assert isinstance(balance_sheet_item, BalanceSheetItem)
        self._balance_sheet_item = balance_sheet_item
