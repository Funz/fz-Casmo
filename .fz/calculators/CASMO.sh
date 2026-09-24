#!/bin/bash
# CASMO.sh — fz runner for Studsvik CASMO5.
# Usage: CASMO.sh <compiled input file | directory containing one *.inp>
#
# Executable lookup (first match wins):
#   1. $CASMO_CMD                       explicit command (e.g. /opt/studsvik/bin/cas5)
#   2. $CASMO_PATH/cas5, $CASMO_PATH/bin/cas5
#   3. cas5 found on PATH
# Extra options passed to the launcher: $CASMO_OPTS (default "-p -k").
# Produces <basename>.out (parsed by the CASMO model) and <basename>.cax
# (lattice data for CMS-LINK / SIMULATE).

if [ -n "$CASMO_CMD" ]; then
  CAS5="$CASMO_CMD"
elif [ -n "$CASMO_PATH" ]; then
  export CMSHOME="${CMSHOME:-$CASMO_PATH}"
  export PATH="$CASMO_PATH/bin:$PATH"
  for c in "$CASMO_PATH/cas5" "$CASMO_PATH/bin/cas5"; do
    [ -f "$c" ] && { CAS5="$c"; break; }
  done
else
  CAS5=$(command -v cas5)
fi
if [ -z "$CAS5" ]; then
  echo "CASMO5 launcher not found: set CASMO_CMD, or CASMO_PATH (install dir), or put cas5 on PATH" >&2
  exit 2
fi

# Locate the input file. fz passes every file of the case (static files included)
# as arguments, in no guaranteed order: take the first *.inp / *.cas among them.
if [ -d "$1" ]; then cd "$1" || exit 2; set --; fi
INP=""
for a in "$@"; do case "$a" in *.inp|*.cas) INP="$a"; break ;; esac; done
[ -z "$INP" ] && INP=$(ls *.inp *.cas 2>/dev/null | head -n 1)
if [ -z "$INP" ] || [ ! -f "$INP" ]; then
  echo "No CASMO input file (*.inp, *.cas) found" >&2
  exit 2
fi
BASENAME="${INP%.*}"

# Run, recording the child PID so that fz can kill it on interrupt
# $CAS5 and $CASMO_OPTS are intentionally unquoted (may hold a command with options)
$CAS5 ${CASMO_OPTS--p -k} "$INP" &
PID_CASMO=$!
echo $PID_CASMO >> PID
wait $PID_CASMO
EXIT_CODE=$?
rm -f PID

if [ $EXIT_CODE -ne 0 ]; then
  echo "CASMO5 exited with status $EXIT_CODE" >&2
  exit $EXIT_CODE
fi
# A zero exit status without an output file is still a failure
if [ ! -s "$BASENAME.out" ]; then
  echo "CASMO5 produced no $BASENAME.out" >&2
  exit 1
fi
exit 0
