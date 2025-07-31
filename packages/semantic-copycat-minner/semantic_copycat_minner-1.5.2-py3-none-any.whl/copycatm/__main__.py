"""
CLI entry point for the copycatm command.
"""

import sys
from .cli.commands import main

if __name__ == "__main__":
    sys.exit(main()) 