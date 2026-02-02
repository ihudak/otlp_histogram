#!/bin/bash
# Helper script to run the histogram sender
# Usage: ./run.sh [--loop] [--interval SECONDS]

cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Load environment variables from .env
export $(cat .env | xargs)

# Run the script with all passed arguments
python send_histogram.py "$@"
