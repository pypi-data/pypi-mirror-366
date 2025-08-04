#!/usr/bin/env python3
"""Main entry point for Vector DB Query System."""

import sys
from pathlib import Path

# Add src to path for development
src_path = Path(__file__).parent.parent.parent
if src_path.exists():
    sys.path.insert(0, str(src_path))

from vector_db_query.cli.main import cli


def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()