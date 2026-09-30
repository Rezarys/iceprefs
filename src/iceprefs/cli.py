"""Command line entry point."""

import argparse
import json
import sys

from . import __version__
from .prefs import DEFAULT_PATH, PrefsError, load


def build_parser():
    parser = argparse.ArgumentParser(
        prog="iceprefs",
        description="Print an Ice preferences file as readable JSON. The file "
                    "is only ever read.",
    )
    parser.add_argument(
        "path", nargs="?", default=None, metavar="PATH",
        help="path to a preferences file; defaults to " + DEFAULT_PATH,
    )
    parser.add_argument(
        "-k", "--key", action="append", default=[], metavar="NAME",
        help="only this setting; repeat the option for several settings",
    )
    parser.add_argument(
        "--compact", action="store_true",
        help="print one line instead of an indented block",
    )
    parser.add_argument("--version", action="version", version="iceprefs " + __version__)
    return parser


def select(settings, wanted):
    if not wanted:
        return settings
    return {name: settings[name] for name in settings if name in set(wanted)}


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        settings = load(args.path)
    except PrefsError as exc:
        sys.stderr.write("iceprefs: %s\n" % exc)
        return 2

    if args.key:
        missing = sorted(set(args.key) - set(settings))
        if missing:
            sys.stderr.write("iceprefs: no such setting: %s\n" % ", ".join(missing))
            return 2
        settings = select(settings, args.key)

    if args.compact:
        text = json.dumps(settings, sort_keys=True, ensure_ascii=False,
                          separators=(",", ":"))
    else:
        text = json.dumps(settings, indent=2, sort_keys=True, ensure_ascii=False)
    sys.stdout.write(text + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
