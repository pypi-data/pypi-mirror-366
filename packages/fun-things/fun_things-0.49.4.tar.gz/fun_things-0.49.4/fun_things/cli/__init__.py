import argparse
from .freeze import Freeze
from .install import Install


def cli():
    parser = argparse.ArgumentParser(
        description="Pub/Sub consumer common.",
    )
    subparser = parser.add_subparsers(
        dest="command",
    )

    Freeze().run(subparser)

    Install().run(subparser)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
        return

    parser.print_help()
