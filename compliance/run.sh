#!/usr/bin/env bash
#
# Aeglero compliance engine - Bash entrypoint (Linux/macOS CI & cron).
#
# Runs the Python engine, then reads the resulting SPRS score and fails the
# build if it drops below a threshold. This is the "compliance gate" used by
# scheduled/CI runs so a regression in posture blocks a merge or pages an owner.
#
# Usage:
#   ./compliance/run.sh                 # gate at the default minimum SPRS
#   COMPLIANCE_MIN_SPRS=100 ./compliance/run.sh
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATUS_JSON="${SCRIPT_DIR}/output/status.json"
MIN_SPRS="${COMPLIANCE_MIN_SPRS:-90}"

# Pick a WORKING Python. The `import sys` probe rejects the Windows Store stub,
# which resolves as `python` but does nothing. `py` gets a -3 arg (Windows launcher).
PY=()
for cand in python3 python py; do
  if command -v "$cand" >/dev/null 2>&1; then
    args=(); [[ "$cand" == "py" ]] && args=(-3)
    if "$cand" "${args[@]}" -c "import sys" >/dev/null 2>&1; then
      PY=("$cand" "${args[@]}"); break
    fi
  fi
done
if [[ ${#PY[@]} -eq 0 ]]; then
  echo "ERROR: no working Python found on PATH" >&2; exit 2
fi

echo ">> Running Aeglero compliance engine..."
"${PY[@]}" "${SCRIPT_DIR}/run.py"

if [[ ! -f "$STATUS_JSON" ]]; then
  echo "ERROR: ${STATUS_JSON} was not produced" >&2
  exit 2
fi

# Extract the SPRS score (pure shell; no jq dependency).
SCORE="$(grep -m1 '"sprs_score"' "$STATUS_JSON" | grep -oE '[0-9]+' | head -n1)"
if [[ -z "${SCORE:-}" ]]; then
  echo "ERROR: could not parse sprs_score from ${STATUS_JSON}" >&2
  exit 2
fi

echo ">> SPRS score: ${SCORE} (gate: >= ${MIN_SPRS})"
if (( SCORE < MIN_SPRS )); then
  echo "FAIL: SPRS ${SCORE} is below the required minimum ${MIN_SPRS}." >&2
  exit 1
fi
echo "PASS: compliance posture meets the gate."
