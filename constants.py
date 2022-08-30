import logging
import os

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
OUTPUT = "~/Documents/webtoons"
OUTPUT = os.path.normpath(os.path.expanduser(OUTPUT))

# Ddl threads
USE_THREADS = True  # Also uses multiple processes
MAX_IMAGE_THREADS = 3
MAX_CHAPTER_THREADS = 3
USE_CACHE = True
RELOAD_MAIN = False
TIMEOUT = 20
MAX_TIMEOUT_RETRY = 3

# Download library - "selenium" or "requests"
USE_DDL = "requests"

# Parser - "lxml" or "bs4"
USE_PARSER = "lxml"


# Logs
LOG_PARSE = True
LOG_DDL = True
LOG_DDL_FULL = True
LOG_ARCHIVE = True
