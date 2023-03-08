import sys
from step_one.find import find_posts

DEFAULT_NEED = "Forming new habits is hard"

def run():
    # Get the command line arguments, skipping the first one which is the script filename
    args = sys.argv[1:]

    need = " ".join(args) if args else DEFAULT_NEED

    find_posts(need)
