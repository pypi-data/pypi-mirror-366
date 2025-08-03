import os
import sys
from pathlib import Path

from rich import print as rprint

from cli import Args, parse_args
from console import run_loop
from db import benchmark_query, get_db_driver, query_and_print_result
from domain import RunBehaviours
from errors import StdinIsTTYError, error_follow_up, is_error_unexpected
from utils import get_data_dir

AUTHOR = "@dhth"
ISSUES_URL = "https://github.com/dhth/graphc/issues"


def main():
    try:
        args = parse_args()

        if args.debug:
            print_debug_info(args)
            return

        db_uri = get_db_uri(args.db_uri)
        driver = get_db_driver(db_uri)
        driver.verify_connectivity()

        if args.query:
            query = get_query(args.query)

            if args.benchmark:
                benchmark_query(
                    driver,
                    query,
                    args.bench_num_runs,
                    args.bench_warmup_num_runs,
                    args.print_query,
                )
            else:
                behaviours = RunBehaviours(
                    args.write, args.output_format, args.print_query
                )
                query_and_print_result(driver, query, behaviours)
        else:
            user_data_dir = get_data_dir()
            history_file_path = Path(user_data_dir) / "history.txt"
            behaviours = RunBehaviours(args.write, args.output_format, args.print_query)
            run_loop(driver, db_uri, history_file_path, behaviours)
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as e:
        rprint(f"[red]Error[/red]: {e}", file=sys.stderr)

        if is_error_unexpected(e):
            rprint(
                f"""\
---
This isn't supposed to happen; let [blue]{AUTHOR}[/] know via [blue]{ISSUES_URL}[/]\
""",
                file=sys.stderr,
            )

        follow_up = error_follow_up(e)
        if follow_up:
            print(file=sys.stderr)
            print(
                follow_up,
                file=sys.stderr,
            )

        sys.exit(1)


def print_debug_info(args: Args):
    db_uri = get_db_uri(args.db_uri)

    query = get_query(args.query) if args.query else None

    print(f"""\
debug info

database URI               {db_uri}\
""")

    if query:
        print(f"""\
query                      {query}\
""")

    if args.benchmark:
        print(f"""\
benchmark                  {args.benchmark}
benchmark num runs         {args.bench_num_runs}
benchmark warmup num runs  {args.bench_warmup_num_runs}\
""")

    if args.write:
        print(f"""\
write output               {args.write}
output format              {args.output_format.value}\
""")


def get_db_uri(db_uri_from_flag: str | None) -> str:
    db_uri = db_uri_from_flag or os.environ.get("DB_URI")

    if db_uri is None:
        raise ValueError(
            "database URI not provided; either provide --db-uri/-d or set DB_URI"
        )

    db_uri = db_uri.strip()
    if db_uri == "":
        raise ValueError("database URI is empty")

    return db_uri


def get_query(query_from_args: str) -> str:
    if query_from_args == "-":
        if sys.stdin.isatty():
            raise StdinIsTTYError("cannot read query from stdin when it is a TTY")

        try:
            query = sys.stdin.read().strip()
            return query
        except Exception as e:
            raise RuntimeError(f"couldn't read query from stdin: {e}") from e

    return query_from_args


if __name__ == "__main__":
    main()
