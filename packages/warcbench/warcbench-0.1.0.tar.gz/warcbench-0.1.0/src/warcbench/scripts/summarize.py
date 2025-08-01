# Standard library imports
import click
from collections import Counter
import json
from urllib.parse import urlparse

# Warcbench imports
from warcbench.filters import record_content_type_filter
from warcbench.patterns import CONTENT_TYPE_PATTERN, get_warc_named_field_pattern
from warcbench.scripts.utils import CLICachingConfig, CLIProcessorConfig, open_and_parse
from warcbench.utils import find_pattern_in_bytes

# Typing imports
from typing import Any


@click.command(short_help="Summarize the contents of an archive.")
@click.argument(
    "filepath",
    type=click.Path(exists=True, readable=True, allow_dash=True, dir_okay=False),
)
@click.pass_context
def summarize(ctx, filepath):
    """
    Summarizes the contents of an archive, and reports warning and error messages.
    (Use `wb inspect` for more details.)

    ---

    Example:

      \b
      $ wb summarize example.com.warc

      \b
      Found 9 records.
      WARC-Type: 1 warcinfo, 2 request, 6 response

      \b
      Found target URLs from 1 domain.
      example.com

      \b
      Found 4 response content-types.
      1 text/html; charset=UTF-8, 3 text/html, 1 image/png, 1 application/pdf

      \b
      Warnings: []
      Error: None
    """
    ctx.obj["FILEPATH"] = filepath

    summary_data: dict[str, Any] = {
        "record_count": 0,
        "record_types": Counter(),
        "domains": Counter(),
        "content_types": Counter(),
        "warnings": [],
        "error": None,
    }

    def count_records():
        def f(_):
            summary_data["record_count"] += 1

        return f

    def count_types():
        def f(record):
            match = find_pattern_in_bytes(
                get_warc_named_field_pattern("Type"),
                record.header.bytes,
                case_insensitive=True,
            )
            if not match:
                summary_data["warnings"].append(
                    f"No WARC-Type detected for record at {record.start}-{record.end}."
                )
            else:
                summary_data["record_types"].update(
                    [match.group(1).decode("utf-8", errors="replace")]
                )

        return f

    def count_domains():
        def f(record):
            match = find_pattern_in_bytes(
                get_warc_named_field_pattern("Target-URI"),
                record.header.bytes,
                case_insensitive=True,
            )
            if match:
                try:
                    parsed_url = urlparse(
                        match.group(1).decode("utf-8", errors="replace")
                    )
                    if parsed_url.netloc:
                        summary_data["domains"].update([parsed_url.netloc])
                except Exception:
                    summary_data["warnings"].append(
                        f"Unparsable WARC-Target-URI detected for record at {record.start}-{record.end}."
                    )

        return f

    def count_content_types():
        def f(record):
            if record_content_type_filter("msgtype=response")(record):
                http_headers = record.get_http_header_block()
                match = find_pattern_in_bytes(
                    CONTENT_TYPE_PATTERN, http_headers, case_insensitive=True
                )
                if match:
                    try:
                        summary_data["content_types"].update(
                            [match.group(1).decode("utf-8", errors="replace")]
                        )
                    except Exception:
                        summary_data["warnings"].append(
                            f"Unparsable HTTP content-type detected for record at {record.start}-{record.end}."
                        )

        return f

    def get_warnings_and_errors():
        def f(parser):
            summary_data["warnings"] += parser.warnings
            summary_data["error"] = parser.error

        return f

    open_and_parse(
        ctx,
        processor_config=CLIProcessorConfig(
            record_handlers=[
                count_records(),
                count_types(),
                count_domains(),
                count_content_types(),
            ],
            parser_callbacks=[get_warnings_and_errors()],
        ),
        cache_config=CLICachingConfig(
            header_bytes=True,
            content_block_bytes=True,
        ),
    )

    if ctx.obj["OUT"] == "json":
        summary_data["domains"] = list(summary_data["domains"])
        click.echo(json.dumps(summary_data))
    else:

        def s(n):
            return "" if n == 1 else "s"

        click.echo(
            f"Found {summary_data['record_count']} record{s(summary_data['record_count'])}.\n"
            f"WARC-Type: {', '.join(str(value) + ' ' + key for key, value in summary_data['record_types'].items())}\n\n"
            f"Found target URLs from {len(summary_data['domains'])} domain{s(len(summary_data['domains']))}.\n"
            f"{', '.join(summary_data['domains'])}\n\n"
            f"Found {len(summary_data['content_types'])} response content-type{s(len(summary_data['content_types']))}.\n"
            f"{', '.join(str(value) + ' ' + key for key, value in summary_data['content_types'].items())}\n\n"
            f"Warnings: {summary_data['warnings']}\n"
            f"Error: {summary_data['error']}"
        )
