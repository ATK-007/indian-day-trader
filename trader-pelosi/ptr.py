#!/usr/bin/env python3
"""
trader-pelosi/ptr.py
Compatibility wrapper for trader-insider.
Maps Congressional STOCK Act queries to Indian SEBI Insider Trading & Bulk Deals.
"""

import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
INSIDER_SCRIPT = os.path.join(PARENT_DIR, "trader-insider", "insider.py")

if __name__ == "__main__":
    # Forward all arguments directly to insider.py
    os.system(f"python3 {INSIDER_SCRIPT} " + " ".join(f'"{arg}"' for arg in sys.argv[1:]))
