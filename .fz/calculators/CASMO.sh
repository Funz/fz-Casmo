#!/bin/bash

# CASMO5 calculator script for fz
# This script runs CASMO5 calculations

# Check if CASMO_PATH is set
if [ -z "$CASMO_PATH" ]; then
  echo "Error: CASMO_PATH environment variable is not set"
  echo "Please set CASMO_PATH to your CASMO5 installation directory"
  echo "Example: export CASMO_PATH=/opt/studsvik/casmo5"
  exit 1
fi

# Check if CASMO5 executable exists
CASMO_EXE="$CASMO_PATH/casmo5"
if [ ! -f "$CASMO_EXE" ]; then
  # Try alternative path
  CASMO_EXE="$CASMO_PATH/bin/casmo5"
  if [ ! -f "$CASMO_EXE" ]; then
    echo "Error: CASMO5 executable not found at $CASMO_PATH/casmo5 or $CASMO_PATH/bin/casmo5"
    exit 1
  fi
fi

# If directory as input, cd into it
if [ -d "$1" ]; then
  cd "$1"
  INP=`ls *.inp 2>/dev/null | head -n 1`
  if [ -z "$INP" ]; then
    INP=`ls *.cas 2>/dev/null | head -n 1`
  fi
  if [ -z "$INP" ]; then
    INP=`ls * 2>/dev/null | grep -v '\.out$\|\.log$\|output\.txt$' | head -n 1`
  fi
  shift
# If $* are files, find the input file
elif [ $# -gt 1 ]; then
  INP=""
  for f in "$@"; do
    if [ -f "$f" ]; then
      INP="$f"
      break
    fi
  done
  if [ -z "$INP" ]; then
    echo "No input file found. Exiting."
    exit 1
  fi
  shift $#
else
  echo "Usage: $0 <input_file or input_directory>"
  exit 2
fi

# Store process ID for tracking
echo $$ >> PID

# Run CASMO5 with the input file
# Redirect output to output.txt for parsing
$CASMO_EXE $INP > output.txt 2>&1 &
PID_CASMO=$!
echo $PID_CASMO >> PID
wait $PID_CASMO

# Store the exit code
EXIT_CODE=$?

# Clean up PID file
if [ -f "PID" ]; then
  rm -f "PID"
fi

# Exit with CASMO's exit code
exit $EXIT_CODE
