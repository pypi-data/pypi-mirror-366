import argparse


def add_bootstrap_schema_parser(
    subparsers: argparse._SubParsersAction,
):
    subparsers.add_parser(
        "bootstrap",
        help=(
            "Bootstrap base schemas, "
            "use CONNECTION_STRING environment variable"
            " to set database connection"
        ),
    )


def get_args_parser():
    parser = argparse.ArgumentParser(description="engineer command utilities")

    # Setup sub-commands
    subparsers = parser.add_subparsers(dest="subcommand")

    # bootstrap_schema command
    add_bootstrap_schema_parser(subparsers)

    return parser
