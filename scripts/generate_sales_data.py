#!/usr/bin/env python3
#
# Generates a mock "Dunder Mifflin daily sales" dataset (CSV, medallion
# bronze layer). Standard library only -- no pip install, no venv, just a
# plain `python3 scripts/generate_sales_data.py`.
#
# Env vars:
#   NUM_ROWS   total row count across all files   (default 1000000)
#   NUM_FILES  number of part files to split into (default 10, auto-capped
#              down if NUM_ROWS is low relative to NUM_FILES)
#   DATA_PATH  medallion data root                (default /data)

import csv
import os
import random
import sys
import uuid
from pathlib import Path

MIN_ROWS_PER_FILE = 1000

MONTHS = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December',
]
BRANCHES = ['Scranton', 'Stamford', 'Utica', 'Nashua', 'Akron', 'Camden']
SALESPEOPLE = [
    'Dwight Schrute', 'Jim Halpert', 'Andy Bernard', 'Phyllis Vance',
    'Stanley Hudson', 'Kevin Malone', 'Michael Scott', 'Pam Beesly',
    'Angela Martin', 'Oscar Martinez',
]
PRODUCTS = [
    'Copy Paper', 'Cardstock', 'Envelopes', 'Labels', 'Toner',
    'Binder Clips', 'Sticky Notes', 'Printer Ink',
]
CLIENTS = [
    'Vance Refrigeration', 'Prince Family Paper', 'Blackbear Landscaping',
    'Web-A-Sketch', 'W.B. Jones Groceries', 'Cache Cash Register Systems',
    'Northern Light Paper Co', 'Utica Office Supply', 'Stamford Business Center',
    'Nashua Print & Ship', 'Camden County Schools', 'Akron Rubber Works',
]
HEADER = ['sale_id', 'date', 'branch', 'salesperson', 'client', 'product', 'quantity', 'unit_price', 'discount_pct']


def resolve_num_files(num_rows: int, num_files: int) -> int:
    max_files_by_rows = max(1, num_rows // MIN_ROWS_PER_FILE)
    if num_files <= max_files_by_rows:
        return num_files
    print(
        f'generate_sales_data: capping NUM_FILES {num_files} -> {max_files_by_rows} '
        f'(NUM_ROWS={num_rows} is low relative to the requested file count)',
        file=sys.stderr,
    )
    return max_files_by_rows


def build_row() -> list:
    date_field = f'{random.choice(MONTHS)} {random.randint(1, 28)}, {random.randint(2022, 2024)}'
    salesperson = random.choice(SALESPEOPLE)
    quantity = random.randint(1, 100)

    # ~5% dirty rows: missing salesperson | missing date | negative quantity
    # ("Michael's prank returns")
    if random.random() < 0.05:
        dirty_kind = random.randint(0, 2)
        if dirty_kind == 0:
            salesperson = ''
        elif dirty_kind == 1:
            date_field = ''
        else:
            quantity = -quantity

    cents = random.randint(100, 15000)
    unit_price = f'${cents // 100}.{cents % 100:02d}'

    return [
        str(uuid.uuid4()),
        date_field,
        random.choice(BRANCHES),
        salesperson,
        random.choice(CLIENTS),
        random.choice(PRODUCTS),
        quantity,
        unit_price,
        random.randint(0, 25),
    ]


def write_part_file(path: Path, num_rows: int) -> None:
    with path.open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        for _ in range(num_rows):
            writer.writerow(build_row())


def main() -> None:
    num_rows = int(os.environ.get('NUM_ROWS', 1_000_000))
    num_files = int(os.environ.get('NUM_FILES', 10))
    data_path = os.environ.get('DATA_PATH', '/data')

    if num_rows < 1:
        sys.exit(f'generate_sales_data: NUM_ROWS must be >= 1 (got {num_rows})')
    if num_files < 1:
        sys.exit(f'generate_sales_data: NUM_FILES must be >= 1 (got {num_files})')

    num_files = resolve_num_files(num_rows, num_files)

    output_dir = Path(data_path) / 'bronze' / 'dunder-mifflin' / 'sales'
    output_dir.mkdir(parents=True, exist_ok=True)

    base_rows, extra_rows = divmod(num_rows, num_files)

    for file_idx in range(num_files):
        rows_in_file = base_rows + (1 if file_idx < extra_rows else 0)
        part_path = output_dir / f'part-{file_idx:05d}.csv'
        write_part_file(part_path, rows_in_file)
        print(f'generate_sales_data: wrote {rows_in_file} rows -> {part_path}', file=sys.stderr)

    print(f'generate_sales_data: done. NUM_ROWS={num_rows} NUM_FILES={num_files} -> {output_dir}', file=sys.stderr)


if __name__ == '__main__':
    main()
