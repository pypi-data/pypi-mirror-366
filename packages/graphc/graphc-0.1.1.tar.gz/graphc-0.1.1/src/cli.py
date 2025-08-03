import argparse
from dataclasses import dataclass

from domain.output import OutputFormat


@dataclass
class Args:
    query: str | None
    db_uri: str | None
    benchmark: bool
    bench_num_runs: int
    bench_warmup_num_runs: int
    debug: bool
    write: bool
    output_format: OutputFormat
    print_query: bool


def parse_args() -> Args:
    parser = argparse.ArgumentParser(
        description="Query Neo4j/AWS Neptune databases via an interactive console",
        prog="graphc",
        epilog="""\
examples:
  # Interactive mode
  DB_URI='bolt://127.0.0.1:7687' DB_USER='user' DB_PASSWORD='password' graphc
  graphc -d 'bolt://abc.xyz.us-east-1.neptune.amazonaws.com:8182'

  # One-off query mode
  graphc --query 'MATCH (n: Node) RETURN n.id, n.name LIMIT 5'
  graphc -q - < query.cypher
  echo 'MATCH (n: Node) RETURN n.id, n.name LIMIT 5' | graphc -q -
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-q",
        "--query",
        type=str,
        metavar="STRING",
        help="Cypher query to execute. If not provided, starts interactive console",
    )

    parser.add_argument(
        "-d",
        "--db-uri",
        type=str,
        metavar="STRING",
        help="Database URI",
    )

    parser.add_argument(
        "-b",
        "--benchmark",
        action="store_true",
        help="Benchmark query execution times without showing results (only applicable in query mode)",
    )

    parser.add_argument(
        "-n",
        "--bench-num-runs",
        type=int,
        default=5,
        metavar="INTEGER",
        help="Number of benchmark runs (default: 5)",
    )

    parser.add_argument(
        "-W",
        "--bench-warmup-num-runs",
        type=int,
        default=0,
        metavar="INTEGER",
        help="Number of warmup runs before benchmarking (default: 0)",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print debug information without doing anything",
    )

    parser.add_argument(
        "-w",
        "--write",
        action="store_true",
        help="Write query results to file (or start console with 'write results' mode on)",
    )

    parser.add_argument(
        "-f",
        "--format",
        choices=OutputFormat.choices(),
        default=OutputFormat.default().value,
        help="Output file format for query results",
    )

    parser.add_argument(
        "-p",
        "--print-query",
        action="store_true",
        help="Print the query (or start console with 'print query' mode on)",
    )

    args = parser.parse_args()

    if args.query:
        if args.benchmark and args.write:
            raise ValueError("cannot write output while benchmarking")

        if args.benchmark and args.bench_num_runs < 1:
            raise ValueError("number of benchmark runs must be >= 1")

        if args.benchmark and args.bench_warmup_num_runs < 0:
            raise ValueError("number of warmup runs must be >= 0")
    else:
        if args.benchmark:
            raise ValueError("benchmarking is only applicable in query mode")

    output_format = OutputFormat.from_string(args.format)

    return Args(
        query=args.query,
        db_uri=args.db_uri,
        benchmark=args.benchmark,
        bench_num_runs=args.bench_num_runs,
        bench_warmup_num_runs=args.bench_warmup_num_runs,
        debug=args.debug,
        write=args.write,
        output_format=output_format,
        print_query=args.print_query,
    )
