import logging
import os
from sys import platform

logging.basicConfig(
	level=logging.INFO,
	format="[%(levelname)s] %(message)s",
	handlers=[
		logging.FileHandler("debug.log"),
		logging.StreamHandler()
	]
)
# Hash function - "sha1" or "b64"
HASH_FUNCTION = "b64"

# Folder output
if platform == 'linux':
    OUTPUT = '/Mangas'
else:
	OUTPUT = "~/Documents/webtoons"
OUTPUT = os.path.normpath(os.path.expanduser(OUTPUT))

# Ddl threads
USE_THREADS = True  # Also uses multiple processes
MAX_IMAGE_THREADS = 5
MAX_CHAPTER_THREADS = 5
USE_CACHE = True
DELETE_UNKNOWN = True # Delete unknown sub-folders
CACHE_AGE = 60*60*24 # Max age for cached file: 1 day
RELOAD_MAIN = False
TIMEOUT = 20
MAX_TIMEOUT_RETRY = 3
CREATE_ARCHIVES = False

# Download library - "selenium" or "requests"
USE_DDL = "requests"

# Parser - "lxml" or "bs4"
USE_PARSER = "lxml"


# Logs
LOG_PARSE = True
LOG_DDL = True
LOG_DDL_FULL = False
LOG_ARCHIVE = True
