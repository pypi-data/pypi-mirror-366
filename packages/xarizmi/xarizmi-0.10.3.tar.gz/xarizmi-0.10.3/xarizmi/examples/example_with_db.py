import datetime
from datetime import datetime as dt

import pytz

from xarizmi.candlestick import Candlestick
from xarizmi.config import get_config
from xarizmi.db import run_db_migration
from xarizmi.db.actions.candlestick import get_filtered_candlesticks
from xarizmi.db.actions.candlestick import upsert_candlestick
from xarizmi.db.actions.exchange import bulk_upsert_exchanges
from xarizmi.db.actions.order import delete_all_cancelled_orders
from xarizmi.db.actions.order import delete_unique_order
from xarizmi.db.actions.order import get_orders
from xarizmi.db.actions.order import get_unique_order
from xarizmi.db.actions.order import upsert_order
from xarizmi.db.actions.portfolio import upsert_portfolio
from xarizmi.db.actions.portfolio.portfolio_read import (
    get_portfolio_items_between_dates,
)
from xarizmi.db.actions.symbol import bulk_upsert_symbols
from xarizmi.db.actions.symbol import get_symbol
from xarizmi.db.client import session_scope
from xarizmi.enums import IntervalTypeEnum
from xarizmi.enums import OrderStatusEnum
from xarizmi.enums import SideEnum
from xarizmi.models.exchange import Exchange
from xarizmi.models.orders import Order
from xarizmi.models.portfolio import Portfolio
from xarizmi.models.portfolio import PortfolioItem
from xarizmi.models.symbol import Symbol


def xarizmi_db_example() -> None:
    config = get_config()
    config.DATABASE_URL = "postgresql://postgres:1@localhost/xarizmi"

    run_db_migration()
    # insert exchanges to exchange table
    with session_scope() as session:
        exchanges = bulk_upsert_exchanges(
            exchanges=[
                Exchange(name=name)
                for name in [
                    "KUCOIN",
                    "crypto.com",
                    "BINANCE",
                    "COINBASE",
                ]
            ],
            session=session,
        )
        print(
            "Exchanges created in db:\n "
            f"{[vars(exchange) for exchange in exchanges]}",
            end="\n-----------\n",
        )

    # insert symbols to Symbol table
    with session_scope() as session:
        bulk_upsert_symbols(
            [
                Symbol.build(
                    base_currency="BTC",
                    quote_currency="USDT",
                    fee_currency="USDT",
                    exchange="COINBASE",
                ),
                Symbol.build(
                    base_currency="ETH",
                    quote_currency="USDT",
                    fee_currency="USDT",
                    exchange="BINANCE",
                ),
                Symbol.build(
                    base_currency="CRO",
                    quote_currency="USDT",
                    fee_currency="USDT",
                    exchange="KUCOIN",
                ),
                Symbol.build(
                    base_currency="CRO",
                    quote_currency="USD",
                    fee_currency="USD",
                    exchange="crypto.com",
                ),
                Symbol.build(
                    base_currency="BTC",
                    quote_currency="USD",
                    fee_currency="USD",
                    exchange="crypto.com",
                ),
            ],
            session=session,
        )

    target_symbol = Symbol.build(
        base_currency="CRO",
        quote_currency="USD",
        fee_currency="USD",
        exchange="crypto.com",
    )

    symbol_id = get_symbol(target_symbol, session=session).id
    upsert_candlestick(
        symbol_id=symbol_id,
        session=session,
        candlestick=Candlestick(
            symbol=target_symbol,
            close=1000,
            open=4,
            low=3,
            high=30000,
            volume=10000,
            amount=1,
            interval=1732385697000,
            datetime=dt(2024, 11, 23, 18, 14, 0, tzinfo=pytz.UTC),
            interval_type=IntervalTypeEnum.HOUR_1,
        ),
    )

    candlestick_chart = get_filtered_candlesticks(
        session=session,
        symbol=target_symbol,
        filter_by_interval_type=IntervalTypeEnum.DAY_14,
    )
    candlestick_chart.plot()
    print(">>>>>>>>>>>>>>>>>>>>>")

    portfolio = Portfolio(
        items=[
            PortfolioItem(
                symbol=Symbol.build(
                    base_currency="CRO",
                    quote_currency="USD",
                    fee_currency="USD",
                    exchange="crypto.com",
                ),
                market_value=1000,
                quantity=0.001,
                datetime=dt(2024, 11, 25),
            ),
            PortfolioItem(
                symbol=Symbol.build(
                    base_currency="BTC",
                    quote_currency="USD",
                    fee_currency="USD",
                    exchange="crypto.com",
                ),
                market_value=1000,
                quantity=10000,
                datetime=dt(2024, 11, 25),
            ),
            PortfolioItem(
                symbol=Symbol.build(
                    base_currency="BTC",
                    quote_currency="USD",
                    fee_currency="USD",
                    exchange="crypto.com",
                ),
                market_value=2000,
                quantity=10000,
                datetime=dt(2024, 11, 25),
            ),
        ]
    )

    upsert_portfolio(
        portfolio=portfolio,
        session=session,
    )

    res = get_portfolio_items_between_dates(
        session=session,
        start_date=datetime.datetime(2024, 11, 25),
        end_date=datetime.datetime(2024, 11, 25),
    )
    print(res)

    # ============== Order ===================
    BTC_USDT = Symbol.build(
        base_currency="BTC",
        quote_currency="USDT",
        fee_currency="USDT",
        exchange="COINBASE",
    )
    # create pydantic order
    order = Order(
        symbol=BTC_USDT,
        price=75000,
        amount=0.1,
        status=OrderStatusEnum.ACTIVE,
        side=SideEnum.BUY,
        order_id="FAKEORDERID",
    )
    upsert_order(order=order, session=session)
    # an other order
    order = Order(
        symbol=BTC_USDT,
        price=50000,
        amount=0.2,
        status=OrderStatusEnum.DONE,
        side=SideEnum.SELL,
        order_id="FAKEORDERID_2",
    )
    upsert_order(order=order, session=session)
    # an other order with CANCELLED status
    order = Order(
        symbol=BTC_USDT,
        price=1000000,
        amount=0.2,
        status=OrderStatusEnum.CANCELLED,
        side=SideEnum.BUY,
        order_id="FAKEORDERID_3",
    )
    upsert_order(order=order, session=session)

    order = get_unique_order(
        session=session,
        symbol=BTC_USDT,
        order_id="FAKEORDERID",
    )  # type: ignore
    print(f"Pydantic Order read from DB: {order=}")

    # get all orders
    orders = get_orders(
        session=session,
        symbol=BTC_USDT,
    )
    print(f"Number of all orders in order table: {len(orders)}")
    # get active buy orders
    orders = get_orders(
        session=session,
        symbol=BTC_USDT,
        filter_by_side=SideEnum.BUY,
        filter_by_status=[OrderStatusEnum.ACTIVE],
    )
    print(f"Number of all active orders in order table: {len(orders)}")

    delete_unique_order(
        session=session, symbol=BTC_USDT, order_id="FAKEORDERID_2"
    )
    # get all orders after delete on record
    orders = get_orders(
        session=session,
        symbol=BTC_USDT,
    )
    print(f"Number of all orders in order table: {len(orders)}")

    # delete all cancelled orders
    delete_all_cancelled_orders(session=session)
    # get all orders after delete on record
    orders = get_orders(
        session=session,
        symbol=BTC_USDT,
    )
    print(f"Number of all orders in order table: {len(orders)}")


# export_table_to_csv("xarizmi_symbol", "xarizmi_symbol.csv", get_engine())
