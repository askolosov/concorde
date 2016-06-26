import notmuch
import concorde.instructions as instr
import sys
import time
from . import logger

if len(sys.argv) < 2:
    print("Usage: %s <filename>" % sys.argv[0])
    sys.exit(1)

max_tries = 3
wait_interval = 1
i = 0
db = None

while i < max_tries and not db:
    i += 1
    
    try:
        db = notmuch.Database(mode=notmuch.Database.MODE.READ_WRITE)
    except notmuch.NotmuchError:
        logger.warning("Failed to open notmuch database. Waiting for %d seconds for another attempt...", wait_interval)
        time.sleep(wait_interval)

if not db:
    logger.error("Notmuch database couldn't be opened after %d attempts.", i)
    sys.exit(1)
        
with db:
    instr.process_file(db, sys.argv[1])
