import logging
import sys

from castlecraft_engineer.commands.argparser import get_args_parser
from castlecraft_engineer.database.commands import bootstrap


def main():
    parser = get_args_parser()
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    else:
        args = parser.parse_args()
        if args.subcommand == "bootstrap":
            bootstrap()
        else:
            logging.info("Invalid sub-command")
