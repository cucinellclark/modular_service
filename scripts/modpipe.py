"""Deployed entry point for the modpipe CLI (wrapped by the dev_container wrap_python3 tool into $KB_TOP/bin/modpipe).
In a source checkout use bin/modpipe instead."""
import os
import sys

# This file is deployed as pybin/modpipe.py; Python puts the script's own directory first on sys.path, where
# "modpipe" would resolve to this file instead of the package in $KB_TOP/lib. Drop that entry.
_here = os.path.dirname(os.path.abspath(__file__))
sys.path = [p for p in sys.path if os.path.abspath(p or os.curdir) != _here]

from modpipe.cli import main  # noqa: E402

sys.exit(main())
