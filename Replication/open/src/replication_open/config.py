from pathlib import Path

L_STATES = 4
THRESHOLD = 1.0

KEY_COLUMNS = ("ID", "Pre_1", "Pre_2", "Pre_3", "Pre_4", "Pre_5", "Pre_6", "SC0")
PRE_COLUMNS = ("Pre_1", "Pre_2", "Pre_3", "Pre_4", "Pre_5", "Pre_6")

# /.../Replication/open/src/replication_open/config.py
REPLICATION_ROOT = Path(__file__).resolve().parents[3]   # /.../Replication
OPEN_ROOT = REPLICATION_ROOT / "open"

DEFAULT_RAW_DATA = REPLICATION_ROOT / "data" / "raw" / "IG_Main_ordered_source.csv"
DEFAULT_TRUE_STATE = REPLICATION_ROOT / "data" / "raw" / "true_state.csv"
DEFAULT_LEGACY_TXT = OPEN_ROOT / "data" / "reference" / "Pilot_New_OLSD4_C_NoIV.txt"
