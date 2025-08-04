"""CLI for interacting with the parts database."""

from datetime import datetime, timezone
import logging
from typing import Optional

import requests
from rich.table import Table
import typer
from typing_extensions import Annotated

from app.console import get_console
from app.constants import API_KEY_NAME, ApiPaths
from app.utils.checks import require_api_endpoint_and_key
from app.utils.datetime_utils import format_utc_to_local

logger = logging.getLogger(__name__)

parts_app = typer.Typer()


def _format_date_utc_or_none(date_str: str | None) -> str:
    """Format a date string or return an empty string if None."""
    if date_str:
        return format_utc_to_local(date_str)
    return ''


def _set_date_to_end_of_day(date_str: str) -> str:
    """Set the date to the end of the day for the given YYYY-MM-DD string.

    Args:
        date_str (str): A date string in the format 'YYYY-MM-DD'.

    Returns:
        str: The ISO 8601 formatted string representing the date at 23:59:59
        UTC.

    Raises:
        ValueError: If the input string does not match the 'YYYY-MM-DD' format.
    """
    date_dt = datetime.strptime(date_str, '%Y-%m-%d').replace(
        hour=23, minute=59, second=59
    )
    return date_dt.replace(tzinfo=timezone.utc).isoformat()


def create_table(verbose: bool) -> Table:
    """Create a table for displaying part information."""
    table = Table(title='Parts')
    table.add_column('Part Number', justify='left')
    table.add_column('Lot Number')
    table.add_column('Constituent Lot Numbers')
    table.add_column('Manufactured At', justify='left')
    table.add_column('Expires At', justify='left')
    if verbose:
        table.add_column('Created By')
        table.add_column('Created At')
        table.add_column('Updated By')
        table.add_column('Updated At')
    return table


def parse_constituent_lot_numbers(value: str) -> list[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(',')]


@parts_app.command(name='display')
@require_api_endpoint_and_key()
def display_parts(
    ctx: typer.Context,
    verbose: Annotated[
        bool, typer.Option('--verbose', '-v', help='Display verbose output')
    ] = False,
):
    """Display a table of parts in the database."""

    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']
    console = get_console()

    parts_url = f'{api_endpoint}{ApiPaths.PARTS}'
    headers = {API_KEY_NAME: api_key}

    page = 1
    size = 50
    parts = []
    while True:
        result = requests.get(
            parts_url,
            headers=headers,
            params={'page': page, 'size': size},
        )
        result.raise_for_status()
        data = result.json()
        items = data.get('items', [])
        parts.extend(items)
        if len(items) < size:
            break
        page += 1

    if not parts:
        console.print('No parts found.')
        raise typer.Exit()

    table = create_table(verbose)
    for part in parts:
        row_data = [
            part['part_number'],
            part['lot_number'],
            ','.join(sorted(part['constituent_lot_numbers'])),
            _format_date_utc_or_none(part.get('manufactured_at_utc')),
            _format_date_utc_or_none(part.get('expires_at_utc')),
        ]
        if verbose:
            row_data.extend(
                [
                    part.get('created_by') or 'N/A',
                    format_utc_to_local(part['created_at_utc']),
                    part.get('updated_by') or 'N/A',
                    format_utc_to_local(part['updated_at_utc']),
                ]
            )
        table.add_row(*row_data)

    console.print(table)


@parts_app.command(name='create')
@require_api_endpoint_and_key()
def create_part(
    ctx: typer.Context,
    part_number: Annotated[str, typer.Option(help='Part number')],
    constituent_lot_numbers: Annotated[
        str,
        typer.Option(help='Comma separated list of constituent lot numbers'),
    ],
    manufactured_at: Annotated[
        Optional[str],
        typer.Option(help='Manufacturing date in YYYY-MM-DD format (optional)'),
    ] = None,
    expires_at: Annotated[
        Optional[str],
        typer.Option(help='Expiration date in YYYY-MM-DD format (optional)'),
    ] = None,
):
    """Create a part in the database."""
    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    console = get_console()

    if not part_number:
        console.print('Part number is required.')
        raise typer.Exit(code=1)

    if not constituent_lot_numbers:
        console.print('Constituent lot numbers are required.')
        raise typer.Exit(code=1)

    parts_url = f'{api_endpoint}{ApiPaths.PARTS}'
    headers = {API_KEY_NAME: api_key}

    data = {
        'part_number': part_number,
        'constituent_lot_numbers': parse_constituent_lot_numbers(
            constituent_lot_numbers
        ),
    }

    if manufactured_at:
        try:
            manufactured_at_utc = _set_date_to_end_of_day(manufactured_at)
            data['manufactured_at_utc'] = manufactured_at_utc
        except ValueError as e:
            console.print(f'Invalid manufacturing date format: {e}')
            raise typer.Exit(code=1)

    if expires_at:
        try:
            expires_at_utc = _set_date_to_end_of_day(expires_at)
            data['expires_at_utc'] = expires_at_utc
        except ValueError as e:
            console.print(f'Invalid expiration date format: {e}')
            raise typer.Exit(code=1)

    result = requests.post(parts_url, headers=headers, json=data)
    result.raise_for_status()
    part = result.json()

    console.log('Part created successfully.')

    table = create_table(True)
    table.add_row(
        part['part_number'],
        part['lot_number'],
        ','.join(sorted(part['constituent_lot_numbers'])),
        _format_date_utc_or_none(part.get('manufactured_at_utc')),
        _format_date_utc_or_none(part.get('expires_at_utc')),
        part.get('created_by') or 'N/A',
        format_utc_to_local(part['created_at_utc']),
        part.get('updated_by') or 'N/A',
        format_utc_to_local(part['updated_at_utc']),
    )
    console.print(table)


@parts_app.command(name='count')
@require_api_endpoint_and_key()
def count_parts(
    ctx: typer.Context,
    part_number: Annotated[
        Optional[str], typer.Option(help='Part number to filter by')
    ] = None,
    location: Annotated[
        Optional[str], typer.Option(help='Location to filter by')
    ] = None,
):
    """Count the number of parts in the database."""
    api_endpoint = ctx.obj['api_endpoint']
    api_key = ctx.obj['api_key']

    parts_url = f'{api_endpoint}{ApiPaths.PARTS}count'
    headers = {API_KEY_NAME: api_key}

    filter_params = {
        k: v
        for k, v in {'part_number': part_number, 'location': location}.items()
        if v is not None
    }

    result = requests.get(parts_url, headers=headers, params=filter_params)
    result.raise_for_status()
    data = result.json()

    table = Table(title='counts')
    table.add_column('Part Number', justify='left')
    table.add_column('Location')
    table.add_column('Available')
    table.add_column('Reserved')

    for item in data:
        part_number = item.get('part_number', '')
        for country, status_counts in item['count'].items():
            available = str(status_counts.get('Available', '0'))
            reserved = str(status_counts.get('Reserved', '0'))
            table.add_row(part_number, country, available, reserved)

    console = get_console()
    console.print(table)
