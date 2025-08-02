"""Balance Sheet Items Objects
"""

from .balance_sheet_item import BalanceSheetItem
from .balance_sheet_submain_group import (
    BalanceSheetSubMainGroupObjects as BSSubMain,
)

# Balance Sheet Item Objects
# These are objects that can be used

CASH = BalanceSheetItem(
    ID="101-0000000001",
    name="Cash",
    origin="Cash available",
    balance_sheet_sub_main_group=BSSubMain.SHORT_TERM_ASSET,
)

ACCOUNTS_RECEIVABLE = BalanceSheetItem(
    ID="101-0000000002",
    name="Accounts Receivable",
    origin="Accounts receivable (AR) is the balance"
    " of money due to a firm for goods or services"
    "delivered or used but not yet paid for by customer",
    balance_sheet_sub_main_group=BSSubMain.SHORT_TERM_ASSET,
)

ALLOWANCE_FOR_BAD_DEBTS = BalanceSheetItem(
    ID="101-0000000003",
    name="Allowance for Bad Debts",
    origin="An allowance for bad debt is a valuation account "
    "used to estimate the amount of a firm's receivables that"
    "may ultimately be uncollectible.",
    balance_sheet_sub_main_group=BSSubMain.SHORT_TERM_ASSET,
)

INVENTORY = BalanceSheetItem(
    ID="101-0000000004",
    name="Inventory",
    origin=(
        "Inventory is the raw materials used to produce"
        "goods as well as the goods that are available for sale."
        "The three types of inventory include raw materials,"
        "work-in-progress, and finished goods."
    ),
    balance_sheet_sub_main_group=BSSubMain.SHORT_TERM_ASSET,
)

SHORT_PREPAID_INSURANCE = BalanceSheetItem(
    ID="101-0000000005",
    name="Prepaid Insurance",
    origin=(
        "A prepaid expense is carried on an insurance company's"
        " balance sheet as a current asset until it is consumed."
    ),
    balance_sheet_sub_main_group=BSSubMain.SHORT_TERM_ASSET,
)

TRUCK = BalanceSheetItem(
    ID="102-0000000001",
    name="Truck",
    origin="Trucks",
    balance_sheet_sub_main_group=BSSubMain.LONG_TERM_ASSET,
)

LAND = BalanceSheetItem(
    ID="102-0000000002",
    name="Land",
    origin="Land",
    balance_sheet_sub_main_group=BSSubMain.LONG_TERM_ASSET,
)

BUILDING = BalanceSheetItem(
    ID="102-0000000003",
    name="Building",
    origin="Building",
    balance_sheet_sub_main_group=BSSubMain.LONG_TERM_ASSET,
)

PREPAID_INSURANCE = BalanceSheetItem(
    ID="101-0000000004",
    name="Prepaid Insurance",
    origin=(
        "A prepaid expense is carried on an insurance"
        "company's balance sheet"
        "as a current asset until it is consumed."
    ),
    balance_sheet_sub_main_group=BSSubMain.LONG_TERM_ASSET,
)


ACCOUNTS_PAYABLE = BalanceSheetItem(
    ID="201-0000000001",
    name="Accounts Payable",
    origin="Accounts Payable",
    balance_sheet_sub_main_group=BSSubMain.SHORT_TERM_LIABILITY,
)

NOTES_PAYABLE = BalanceSheetItem(
    ID="211-0000000001",
    name="Notes Payable",
    origin="Notes Payable",
    balance_sheet_sub_main_group=BSSubMain.LONG_TERM_LIABILITY,
)

ORIGINAL_INVESTMENT = BalanceSheetItem(
    ID="211-0000000001",
    name="Original Investment",
    origin="Original investment by owners of the company",
    balance_sheet_sub_main_group=BSSubMain.OWNERS_EQUITY,
)
RETAINED_EARNINGS = BalanceSheetItem(
    ID="211-0000000001",
    name="Retained Earnings",
    origin="Retained Earnings is the earning that"
    "is re-invested in the company",
    balance_sheet_sub_main_group=BSSubMain.OWNERS_EQUITY,
)
