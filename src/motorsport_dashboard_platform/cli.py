from __future__ import annotations

import argparse
import json
import sys

from .example_project import EXAMPLE_PROJECT
from .project_io import save_project
from .validation import ProjectValidator


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mlsw", description="Motorsport dashboard platform tooling")
    subparsers = parser.add_subparsers(dest="command", required=True)

    dump_parser = subparsers.add_parser("dump-example", help="Print the example project JSON")
    dump_parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")

    write_parser = subparsers.add_parser("write-example", help="Write the example project to disk")
    write_parser.add_argument("path", help="Destination JSON path")

    subparsers.add_parser("validate-example", help="Validate the built-in example project")

    args = parser.parse_args(argv)

    if args.command == "dump-example":
        payload = EXAMPLE_PROJECT.to_dict()
        if args.pretty:
            print(json.dumps(payload, indent=2))
        else:
            print(json.dumps(payload, separators=(",", ":")))
        return 0

    if args.command == "write-example":
        save_project(EXAMPLE_PROJECT, args.path, pretty=True)
        print(f"Wrote example project to {args.path}")
        return 0

    if args.command == "validate-example":
        report = ProjectValidator().validate(EXAMPLE_PROJECT)
        if report.is_valid:
            print("Example project is valid.")
            return 0
        for issue in report.issues:
            print(f"[{issue.level}] {issue.path}: {issue.message}", file=sys.stderr)
        return 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
