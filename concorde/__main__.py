import notmuch
import concorde.instructions as instr
import sys

if len(sys.argv) < 2:
    print("Usage: %s <filename>" % sys.argv[0])
    sys.exit(1)

with notmuch.Database(mode=notmuch.Database.MODE.READ_WRITE) as db:
    instr.process_file(db, sys.argv[1])
