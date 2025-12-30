#!/bin/bash

# ==============================================
# Google Colab compatible runner
# Captures only final visible output of program
#
# Usage:
#   bash run_with_final_logs_colab.sh <log_folder> [runs]
#
# Example:
#   bash run_with_final_logs_colab.sh /content/logs
#   bash run_with_final_logs_colab.sh /content/logs 3
# ==============================================

if [ -z "$1" ]; then
    echo "Error: Log folder path required."
    echo "Usage: $0 <log_folder> [runs]"
    exit 1
fi

LOG_DIR="$1"
RUNS="${2:-1}"

mkdir -p "$LOG_DIR"

for ((i = 1; i <= RUNS; i++)); do
    TIMESTAMP=$(date +'%d_%m_%y__%H_%M_%S')
    LOG_FILE="$LOG_DIR/crewai_trip_planner_run_${TIMESTAMP}.log"
    TMP_RAW=$(mktemp)

    echo "Run $i of $RUNS..."
    echo "Saving final output to: $LOG_FILE"

    # Run script, record text while converting '\r' overwrite to separate lines
    poetry run python3 main.py | sed -u 's/\r/\n/g' > "$TMP_RAW"

    # Extract final terminal view (last 200 lines, adjustable)
    tail -n 200 "$TMP_RAW" > "$LOG_FILE"

    rm "$TMP_RAW"
done

echo "All runs completed. Logs saved in $LOG_DIR"
