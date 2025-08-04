from pathlib import Path
from typing import Optional

import click

from .converters.clickhouse_converter import ClickHouseConverter
from .parsers.postgres_parser import PostgreSQLParser
from .utils.exceptions import ParseError


def convert_ddl(postgres_ddl: str) -> str:
    """
    Convert PostgreSQL DDL to ClickHouse DDL

    Args:
        postgres_ddl: PostgreSQL DDL statements as string

    Returns:
        ClickHouse DDL as string

    Raises:
        ParseError: If parsing fails
    """
    parser = PostgreSQLParser()
    converter = ClickHouseConverter()

    # Parse PostgreSQL DDL
    tables = parser.parse_ddl(postgres_ddl)

    # Convert to ClickHouse DDL
    clickhouse_ddl = converter.convert_tables(tables)

    return clickhouse_ddl


def convert_file(input_file: str, output_file: Optional[str] = None) -> str:
    """
    Convert PostgreSQL DDL file to ClickHouse DDL file

    Args:
        input_file: Path to PostgreSQL DDL file
        output_file: Path to output ClickHouse DDL file (optional)

    Returns:
        ClickHouse DDL as string
    """
    # Read input file
    with open(input_file, "r", encoding="utf-8") as f:
        postgres_ddl = f.read()

    # Convert DDL
    clickhouse_ddl = convert_ddl(postgres_ddl)

    # Write output file if specified
    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(clickhouse_ddl)

    return clickhouse_ddl


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--output", "-o", help="Output file path")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def cli(input_file: str, output: Optional[str], verbose: bool) -> None:
    """Convert PostgreSQL DDL to ClickHouse DDL"""
    try:
        if verbose:
            click.echo(f"Converting {input_file}...")

        result = convert_file(input_file, output)

        if output:
            click.echo(f"Conversion complete! Output written to {output}")
        else:
            click.echo("Conversion complete!")
            click.echo("\n--- ClickHouse DDL ---")
            click.echo(result)

    except ParseError as e:
        click.echo(f"Parse error: {e}", err=True)
        exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        exit(1)


if __name__ == "__main__":
    cli()
