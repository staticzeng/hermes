import os
import sys
import inspect
import threading

from config import VtransConfigParser

CONF_FILE = '/config/hermes.ini'

_config = VtransConfigParser()

VTRANS_VERSION = _config.get("DEFAULT", "VTRANS_VERSION", "1.0.0")
HTTP_PORT = _config.get_int("DEFAULT", "HTTP_PORT", 9999)
TORRENT_BEGIN_PORT = _config.get_int("DEFAULT", "TORRENT_BEGIN_PORT", 16881)
TORRENT_END_PORT = _config.get_int("DEFAULT", "TORRENT_END_PORT", 16891)
TORRENT_DIR = _config.get("DEFAULT", "TORRENT_DIR", "/storage/disks/torrent")
SAVE_DIR = _config.get("DEFAULT", "SAVE_DIR", "/storage/disks")
SEED_TIME = _config.get_int("DEFAULT", "SEED_TIME", 0)
TORRENT_SERVICE_INTERVAL = _config.get_int("DEFAULT", "TORRENT_SERVICE_INTERVAL", 1)
VHD_UTIL_CMD = _config.get("UTIL", "VHD_UTIL_CMD", "/usr/sbin/vhd-util ")
RSYNC_PORT = _config.get_int("RSYNC", "RSYNC_PORT", 10873)
RSYNC_CMD = _config.get("RSYNC", "RSYNC_CMD", "/usr/bin/rsync")
RSYNC_LOG = _config.get("RSYNC", "RSYNC_LOG", "/var/log/rsync.log")

LOG_PATH = _config.get("LOG", "LOG_PATH", "/var/log/hermes.log")
LOG_MAXBYTES = _config.get_int("LOG", "LOG_MAXBYTES", 20)
LOG_BACKUPCOUNT = _config.get_int("LOG", "LOG_BACKUPCOUNT", 5)

_config.write()

''' Job Status ''' 
JOB_STATUS_INACTIVE = 0
JOB_STATUS_INQUEUE = 1
JOB_STATUS_RUNNING = 2
JOB_STATUS_PENDING = 3
JOB_STATUS_SUCCESS = 4
JOB_STATUS_FAILED = 5
JOB_STATUS_CANCELLED = 6

lock = threading.RLock()

if __name__ == "__main__":
    pass
