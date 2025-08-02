from enum import StrEnum


class TableNamesEnum(StrEnum):
    EXCHANGE = "xarizmi_exchange"
    PORTFOLIO_ITEM = "xarizmi_portfolio_item"
    SYMBOL = "xarizmi_symbol"
    CANDLESTICK = "xarizmi_candlestick"
    ORDER = "xarizmi_order"
