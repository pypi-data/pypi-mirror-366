import csv
import json
import os
import pathlib

from sqlalchemy import Engine
from sqlalchemy import text

from xarizmi.db.models.constants import TableNamesEnum


def export_table_to_csv(
    table_name: str, output_file: str, engine: Engine
) -> None:
    """
    Exports a PostgreSQL table to a CSV file using an existing SQLAlchemy
    engine.

    Args:
        table_name (str): Name of the table to export.
        output_file (str): Path to the output CSV file.
        engine (sqlalchemy.engine.Engine): SQLAlchemy engine
        connected to the database.
    """
    with engine.connect() as connection:
        # Query the table
        query = text(f"SELECT * FROM {table_name}")
        result = connection.execute(query)

        # Fetch column names (headers)
        headers = result.keys()

        # Export to CSV
        with open(output_file, mode="w", newline="") as csv_file:
            writer = csv.writer(csv_file)

            # Write headers
            writer.writerow(headers)

            # Write rows
            for row in result:
                writer.writerow(row)

    print(f"Table {table_name} has been exported to {output_file}")


def export_table_to_json(
    table_name: str, output_file: str | pathlib.Path, engine: Engine
) -> None:
    """
    Exports a PostgreSQL table to a JSON file using SQLAlchemy with
    optional limit and offset.

    Args:
        table_name (str): Name of the table to export.
        output_file (str): Path to the output JSON file.
        engine (sqlalchemy.engine.Engine): SQLAlchemy engine
        connected to the database.
    """
    with engine.connect() as connection:
        # Build the query with optional LIMIT and OFFSET
        limit = 1000000
        for step in range(0, 10000):
            offset = step * limit

            query = f"SELECT * FROM {table_name}"
            if limit is not None:
                query += f" LIMIT {limit}"
            if offset is not None:
                query += f" OFFSET {offset}"

            # Execute the query
            result = connection.execute(text(query))

            # Fetch column names (headers)
            headers = result.keys()

            # Convert rows to a list of dictionaries
            data = [dict(zip(headers, row)) for row in result]

            if len(data) <= 0:
                break

            # Export to JSON
            with open(
                str(output_file).replace(".json", f"_{step}.json"), mode="w"
            ) as json_file:
                json.dump(data, json_file, indent=4, default=str)

        print(
            f"Table {table_name} has been exported to "
            f"{output_file} (Limit: {limit}, Offset: {offset})"
        )


def export_candlestick_table_to_json(
    output_file: str | pathlib.Path, engine: Engine
) -> None:
    with engine.connect() as connection:
        # Build the query with optional LIMIT and OFFSET
        limit = 1000000
        for step in range(0, 1000):
            offset = step * limit

            query = f"""SELECT a.*,
            b.exchange_name as exchange_name,
            b.base_currency as base_currency,
            b.quote_currency as quote_currency,
            b.fee_currency as fee_currency
            FROM {TableNamesEnum.CANDLESTICK.value} as a
            INNER JOIN {TableNamesEnum.SYMBOL.value} as b
            ON a.symbol_id = b.id
            """
            if limit is not None:
                query += f" LIMIT {limit}"
            if offset is not None:
                query += f" OFFSET {offset}"

            # Execute the query
            result = connection.execute(text(query))

            # Fetch column names (headers)
            headers = result.keys()

            # Convert rows to a list of dictionaries
            data = [dict(zip(headers, row)) for row in result]

            if len(data) <= 0:
                break

            # Export to JSON
            with open(
                str(output_file).replace(".json", f"_{step}.json"), mode="w"
            ) as json_file:
                json.dump(data, json_file, indent=4, default=str)


def export_all_xarizmi_tables_to_json(
    engine: Engine,
    parent_dir: pathlib.Path = pathlib.Path(os.getcwd()),
) -> None:
    export_table_to_json(
        TableNamesEnum.EXCHANGE.value,
        parent_dir / f"{TableNamesEnum.EXCHANGE.value}.json",
        engine=engine,
    )
    export_table_to_json(
        TableNamesEnum.SYMBOL.value,
        parent_dir / f"{TableNamesEnum.SYMBOL.value}.json",
        engine=engine,
    )
    export_candlestick_table_to_json(
        parent_dir / f"{TableNamesEnum.CANDLESTICK.value}.json",
        engine=engine,
    )
    export_table_to_json(
        TableNamesEnum.PORTFOLIO_ITEM.value,
        parent_dir / f"{TableNamesEnum.PORTFOLIO_ITEM.value}.json",
        engine=engine,
    )
