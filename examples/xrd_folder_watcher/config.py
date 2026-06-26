"""
config.py

Central configuration for the XRD folder watcher.

Set WATCH_FOLDER to the local folder where XRD result files will be dropped.
MATERIALS_TABLE_ID and XRD_PHASES_TABLE_ID are read from the .env file —
paste the IDs printed by setup.py into .env after running it.
"""

import os
from dotenv import load_dotenv

load_dotenv()

WATCH_FOLDER = "./incoming"          # Drop XRD result files here
SCAN_INTERVAL_SEC = 10               # Seconds between folder scans
PROCESSED_LOG = "processed.json"     # Local file for tracking processed uploads

MATERIALS_TABLE_ID = os.getenv("MATERIALS_TABLE_ID", "")
XRD_PHASES_TABLE_ID = os.getenv("XRD_PHASES_TABLE_ID", "")
