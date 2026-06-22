#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

/usr/bin/env python3 "$SCRIPT_DIR/update_live_data.py" --skill-root "$SKILL_ROOT"
