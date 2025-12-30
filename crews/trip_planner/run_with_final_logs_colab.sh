# ==============================================
# Google Colab compatible runner
# Captures only final visible output of program
#
# Usage:
#   sh run_with_final_logs_colab.sh <log_folder> [runs]
#
# Example:
#   sh run_with_final_logs_colab.sh /content/logs
#   sh run_with_final_logs_colab.sh /content/logs 3
# ==============================================

#!/usr/bin/env bash
# Force bash (if user runs via sh)
if [ -z "$BASH_VERSION" ]; then exec bash "$0" "$@"; fi

if [ -z "$1" ]; then
    echo "Error: Log folder path required."
    echo "Usage: $0 <log_folder> [runs]"
    exit 1
fi

LOG_DIR="$1"
RUNS="${2:-1}"      # defaults to 1
mkdir -p "$LOG_DIR"

for ((i=1; i<=RUNS; i++)); do
    TIMESTAMP=$(date +'%d_%m_%y__%H_%M_%S')
    LOG_FILE="$LOG_DIR/crewai_trip_planner_run_${TIMESTAMP}.log"
    TMP_RAW=$(mktemp)

    echo "Run $i of $RUNS..."
    echo "Saving final output to: $LOG_FILE"

    # Capture output, process CR-based rewriting
    poetry run python3 main.py | sed -u 's/\r/\n/g' > "$TMP_RAW"

    # Save last 200 lines as final visible content window
    tail -n 200 "$TMP_RAW" > "$LOG_FILE"
    rm "$TMP_RAW"
done

echo "All runs completed. Logs saved in $LOG_DIR"