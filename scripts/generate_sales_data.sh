#!/bin/bash
# @author       Anthony Vilarim Caliani
# @contact      github.com/avcaliani
#
# Generates a mock "Dunder Mifflin daily sales" dataset (CSV, medallion
# bronze layer) for local/offline PySpark development. Pure bash builtins
# only, no forked child processes in the per-row loop, so 1M rows stays fast.
#
# LINUX-ONLY: sale_id is sourced from /proc/sys/kernel/random/uuid, a Linux
# procfs interface. This script runs inside the project's Docker container,
# not directly on macOS.
#
# Env vars:
#   NUM_ROWS   total row count across all files   (default 1000000)
#   NUM_FILES  number of part files to split into (default 10, auto-capped
#              down if NUM_ROWS is low relative to NUM_FILES)
#   DATA_PATH  medallion data root                (default /data)

set -euo pipefail

if [ ! -r /proc/sys/kernel/random/uuid ]; then
  echo "generate_sales_data: /proc/sys/kernel/random/uuid not readable." \
       "This script requires Linux/procfs -- run it inside the project's" \
       "Docker container, not directly on macOS/Darwin." >&2
  exit 1
fi

NUM_ROWS="${NUM_ROWS:-1000000}"
NUM_FILES="${NUM_FILES:-10}"
DATA_PATH="${DATA_PATH:-/data}"

if (( NUM_ROWS < 1 )); then
  echo "generate_sales_data: NUM_ROWS must be >= 1 (got ${NUM_ROWS})" >&2
  exit 1
fi
if (( NUM_FILES < 1 )); then
  echo "generate_sales_data: NUM_FILES must be >= 1 (got ${NUM_FILES})" >&2
  exit 1
fi

# Every part file gets at least MIN_ROWS_PER_FILE rows, so NUM_FILES is
# capped to max(1, NUM_ROWS / MIN_ROWS_PER_FILE). E.g. NUM_ROWS=500,
# NUM_FILES=10 -> 500/1000 floors to 0 -> capped to 1 file of 500 rows.
readonly MIN_ROWS_PER_FILE=1000
max_files_by_rows=$(( NUM_ROWS / MIN_ROWS_PER_FILE ))
(( max_files_by_rows < 1 )) && max_files_by_rows=1
if (( NUM_FILES > max_files_by_rows )); then
  echo "generate_sales_data: capping NUM_FILES ${NUM_FILES} -> ${max_files_by_rows}" \
       "(NUM_ROWS=${NUM_ROWS} is low relative to the requested file count)" >&2
  NUM_FILES=$max_files_by_rows
fi

readonly NUM_ROWS
readonly NUM_FILES
readonly DATA_PATH
readonly OUTPUT_DIR="${DATA_PATH}/bronze/dunder-mifflin-sales"

mkdir -p "$OUTPUT_DIR"

# --- Reference data ---------------------------------------------------------
readonly MONTHS=(January February March April May June July August September October November December)
readonly BRANCHES=(Scranton Stamford Utica Nashua Akron Camden)
readonly SALESPEOPLE=(
  "Dwight Schrute" "Jim Halpert" "Andy Bernard" "Phyllis Vance"
  "Stanley Hudson" "Kevin Malone" "Michael Scott" "Pam Beesly"
  "Angela Martin" "Oscar Martinez"
)
readonly PRODUCTS=(
  "Copy Paper" "Cardstock" "Envelopes" "Labels" "Toner"
  "Binder Clips" "Sticky Notes" "Printer Ink"
)
readonly CLIENTS=(
  "Vance Refrigeration" "Prince Family Paper" "Blackbear Landscaping"
  "Web-A-Sketch" "W.B. Jones Groceries" "Cache Cash Register Systems"
  "Northern Light Paper Co" "Utica Office Supply" "Stamford Business Center"
  "Nashua Print & Ship" "Camden County Schools" "Akron Rubber Works"
)
readonly HEADER="sale_id,date,branch,salesperson,client,product,quantity,unit_price,discount_pct"

# --- Row builder -------------------------------------------------------------
# Writes into the global ROW_LINE var instead of returning via command
# substitution -- `$( ... )` always forks a subshell, `printf -v` doesn't.
build_row() {
  local uuid month day year date_field
  local branch salesperson client product
  local quantity cents dollars remainder_cents unit_price discount_pct
  local dirty_roll dirty_kind

  read -r uuid < /proc/sys/kernel/random/uuid

  month="${MONTHS[$(( RANDOM % 12 ))]}"
  day=$(( 1 + RANDOM % 28 ))
  year=$(( 2022 + RANDOM % 3 ))
  date_field="${month} ${day}, ${year}"

  branch="${BRANCHES[$(( RANDOM % ${#BRANCHES[@]} ))]}"
  salesperson="${SALESPEOPLE[$(( RANDOM % ${#SALESPEOPLE[@]} ))]}"
  client="${CLIENTS[$(( RANDOM % ${#CLIENTS[@]} ))]}"
  product="${PRODUCTS[$(( RANDOM % ${#PRODUCTS[@]} ))]}"

  quantity=$(( 1 + RANDOM % 100 ))

  cents=$(( 100 + RANDOM % 14901 ))
  dollars=$(( cents / 100 ))
  remainder_cents=$(( cents % 100 ))
  printf -v unit_price '$%d.%02d' "$dollars" "$remainder_cents"

  discount_pct=$(( RANDOM % 26 ))

  # ~5% dirty rows: missing salesperson | missing date | negative quantity
  # ("Michael's prank returns")
  dirty_roll=$(( RANDOM % 100 ))
  if (( dirty_roll < 5 )); then
    dirty_kind=$(( RANDOM % 3 ))
    case "$dirty_kind" in
      0) salesperson="" ;;
      1) date_field="" ;;
      2) quantity=$(( -1 * quantity )) ;;
    esac
  fi

  # date_field itself contains a comma (e.g. "January 5, 2024"), so it must
  # be CSV-quoted or it silently shifts every column after it by one.
  printf -v ROW_LINE '%s,"%s",%s,%s,%s,%s,%d,%s,%d' \
    "$uuid" "$date_field" "$branch" "$salesperson" "$client" "$product" \
    "$quantity" "$unit_price" "$discount_pct"
}

# --- Generate part files -----------------------------------------------------
base_rows=$(( NUM_ROWS / NUM_FILES ))
extra_rows=$(( NUM_ROWS % NUM_FILES ))

for (( file_idx = 0; file_idx < NUM_FILES; file_idx++ )); do
  printf -v part_name 'part-%05d.csv' "$file_idx"
  part_path="${OUTPUT_DIR}/${part_name}"

  rows_in_file=$base_rows
  (( file_idx < extra_rows )) && rows_in_file=$(( rows_in_file + 1 ))

  {
    printf '%s\n' "$HEADER"
    for (( row_idx = 0; row_idx < rows_in_file; row_idx++ )); do
      build_row
      printf '%s\n' "$ROW_LINE"
    done
  } > "$part_path"

  echo "generate_sales_data: wrote ${rows_in_file} rows -> ${part_path}" >&2
done

echo "generate_sales_data: done. NUM_ROWS=${NUM_ROWS} NUM_FILES=${NUM_FILES} -> ${OUTPUT_DIR}" >&2
