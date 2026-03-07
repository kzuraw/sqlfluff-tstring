import sys

from sqlfluff_tstring.cli import main

try:
    main()
except KeyboardInterrupt:
    sys.exit(130)
