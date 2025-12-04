#!/bin/bash

# CASMO5 calculator script for fz
# This script runs CASMO5 calculations

# Check if CASMO_PATH is set (CMSHOME for cas5 script)
if [ -z "$CASMO_PATH" ]; then
  echo "Error: CASMO_PATH environment variable is not set"
  echo "Please set CASMO_PATH to your CASMO5 installation directory"
  echo "Example: export CASMO_PATH=/opt/studsvik/casmo5"
  exit 1
fi

# Set CMSHOME for cas5 script
export CMSHOME="$CASMO_PATH"
export PATH=$CMSHOME/bin:$PATH

# Check if cas5 script exists
CAS5_SCRIPT="$CASMO_PATH/cas5"
if [ ! -f "$CAS5_SCRIPT" ]; then
  # Try alternative path
  CAS5_SCRIPT="$CASMO_PATH/bin/cas5"
  if [ ! -f "$CAS5_SCRIPT" ]; then
    echo "Error: cas5 script not found at $CASMO_PATH/cas5 or $CASMO_PATH/bin/cas5"
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
elif [ $# -gt 0 ]; then
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

# Get basename without extension for output file handling
BASENAME="${INP%.*}"

# Run CASMO5 using cas5 script
# The cas5 script automatically generates basename.out and basename.cax
# Use -p to avoid prompts, -k to clean existing output files
$CAS5_SCRIPT -p -k "$INP" &
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
