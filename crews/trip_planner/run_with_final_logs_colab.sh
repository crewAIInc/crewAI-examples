#!/usr/bin/env bash
# Force bash (if executed with sh)
if [ -z "$BASH_VERSION" ]; then exec bash "$0" "$@"; fi

# ==============================================
# Google Colab-compatible execution logger
# Captures only final visible output of program
#
# Usage:
#   bash run_with_final_logs_colab.sh <log_folder> <runs>
# ==============================================

# Validate args
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Error: Two parameters required."
    echo "Usage: $0 <log_folder> <runs>"
    exit 1
fi

LOG_DIR="$1"
RUNS="$2"

# Validate RUNS numeric
if ! [[ "$RUNS" =~ ^[0-9]+$ ]] || [ "$RUNS" -lt 1 ]; then
    echo "Error: <runs> must be a positive integer"
    exit 1
fi

mkdir -p "$LOG_DIR"

for ((i=1; i<=RUNS; i++)); do
    TIMESTAMP=$(date +'%d_%m_%y__%H_%M_%S')
    LOG_FILE="$LOG_DIR/crewai_trip_planner_run_${TIMESTAMP}.log"
    TMP_RAW=$(mktemp)

    echo "Run $i of $RUNS..."
    echo "Saving final output to: $LOG_FILE"

    # Capture execution (CR -> newline to simulate final visible state)
    poetry run python3 main.py | sed -u 's/\r/\n/g' > "$TMP_RAW"

    # Keep last lines of terminal, adjustable (200 default)
    tail -n 200 "$TMP_RAW" > "$LOG_FILE"
    rm "$TMP_RAW"
done

echo "All runs completed. Logs saved in: $LOG_DIR"
