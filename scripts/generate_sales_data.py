#!/usr/bin/env python3
#
# Generates a mock "Dunder Mifflin daily sales"
#
# Env vars:
#   NUM_ROWS   total row count across all files     (default 1000000)
#   NUM_FILES  number of part files to split into   (default 10)
#   DATA_PATH  output path                         (default /data)

import csv
import os
import random
import sys
import uuid
from pathlib import Path

INVALID_PCT = 5

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
CSV_HEADER = ['sale_id', 'date', 'branch', 'salesperson', 'client', 'product', 'quantity', 'unit_price', 'discount_pct']


def maybe_buggy(row: dict) -> dict:
    if random.randint(0, 99) >= INVALID_PCT:
        return row

    match random.randint(0, 2):
        case 0:
            row['salesperson'] = ''
        case 1:
            row['date'] = ''
        case _:
            row['quantity'] = -row['quantity']

    return row


def build_row() -> list:
    cents = random.randint(100, 15000)
    row = maybe_buggy({
        'sale_id': str(uuid.uuid4()),
        'date': f'{random.choice(MONTHS)} {random.randint(1, 28)}, {random.randint(2022, 2024)}',
        'branch': random.choice(BRANCHES),
        'salesperson': random.choice(SALESPEOPLE),
        'client': random.choice(CLIENTS),
        'product': random.choice(PRODUCTS),
        'quantity': random.randint(1, 100),
        'unit_price': f'${cents // 100}.{cents % 100:02d}',
        'discount_pct': random.randint(0, 25),
    })
    return [row[col] for col in CSV_HEADER]


def write_part_file(path: Path, num_rows: int) -> None:
    with path.open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADER)
        for _ in range(num_rows):
            writer.writerow(build_row())


def main() -> None:
    num_rows = int(os.environ.get('NUM_ROWS', 1_000_000))
    num_files = int(os.environ.get('NUM_FILES', 10))
    data_path = os.environ.get('DATA_PATH', '/data')

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
