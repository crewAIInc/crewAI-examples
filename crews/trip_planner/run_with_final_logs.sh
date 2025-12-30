#!/bin/bash

# ==============================================
# Usage:
#   ./run_with_final_log.sh <log_folder> [runs]
#
# Example:
#   ./run_with_final_log.sh logs
#   ./run_with_final_log.sh /var/logs/trips 3
#
# Requirements: tmux must be installed.
# ==============================================

# Input validation
if [ -z "$1" ]; then
    echo "Error: Log folder path required."
    echo "Usage: $0 <log_folder> [runs]"
    exit 1
fi

LOG_DIR="$1"
RUNS="${2:-1}"   # default to 1 if not provided

mkdir -p "$LOG_DIR"

for ((i = 1; i <= RUNS; i++)); do
    TIMESTAMP=$(date +'%d_%m_%y__%H_%M_%S')
    LOG_FILE="$LOG_DIR/crewai_trip_planner_run_${TIMESTAMP}.log"
    SESSION_NAME="triplog_$RANDOM"

    echo "Run $i of $RUNS..."
    echo "Saving final output to: $LOG_FILE"

    tmux new-session -d -s "$SESSION_NAME" "poetry run python3 main.py; \
    tmux capture-pane -pS -2000 > \"$LOG_FILE\"; \
    tmux kill-session -t \"$SESSION_NAME\""

    # Attach only if user is NOT inside tmux
    if [ -z "$TMUX" ] && [ "$i" -eq 1 ]; then
        tmux attach -t "$SESSION_NAME"
    else
        # If already inside tmux or subsequent runs
        tmux wait -S "$SESSION_NAME" 2>/dev/null || true
    fi
done


echo "All runs completed. Logs saved in $LOG_DIR"
