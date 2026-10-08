#!/bin/bash
# Runs the checks and the eight steps. About 15 seconds on a laptop; nothing to install.
set -e
cd "$(dirname "$0")"
python3 tests.py
for step in step1_book step2_match step3_priority step4_market step5_fast step6_market step7_crash step8_band; do
  echo
  echo "=== $step.py"
  python3 $step.py
done
