"""Convenience entry point for local clause inference; no fitting or API calls."""
from contractguard.cli import main
import sys

if __name__ == '__main__':
    raise SystemExit(main(['predict', *sys.argv[1:]]))
