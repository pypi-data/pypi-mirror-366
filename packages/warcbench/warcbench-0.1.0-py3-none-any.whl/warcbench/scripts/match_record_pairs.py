import base64
import click
import json

from warcbench.scripts.utils import (
    CLICachingConfig,
    CLIProcessorConfig,
    open_and_invoke,
)


@click.command(short_help="Match requests/responses into pairs.")
@click.argument(
    "filepath",
    type=click.Path(exists=True, readable=True, allow_dash=True, dir_okay=False),
)
@click.option(
    "--output-summary-by-uri/--no-output-summary-by-uri",
    default=True,
    show_default=True,
    help="Include a summary of how many pairs and lone records were found for each URI.",
)
@click.option(
    "--output-record-details/--no-output-record-details",
    default=False,
    show_default=True,
    help="Include detailed metadata about records in output.",
)
@click.option(
    "--output-http-headers/--no-output-http-headers",
    default=False,
    show_default=True,
    help="Include http headers with record metadata in output.",
)
@click.option(
    "--include-pair-details/--exclude-pair-details",
    default=False,
    show_default=True,
    help="Include information about matched request/response pairs in output, if output includes record details or http headers.",
)
@click.option(
    "--include-file-protocol-target-uri/--no-include-file-protocol-target-uri",
    default=True,
    show_default=True,
    help="Include records with a Target-URI beginning file:/// in this report.",
)
@click.pass_context
def match_record_pairs(
    ctx,
    filepath,
    output_summary_by_uri,
    output_record_details,
    output_http_headers,
    include_pair_details,
    include_file_protocol_target_uri,
):
    """
    Attempts to match WARC request records with response records and generates
    a report on the results.

    Requests and responses are paired by WARC-Target-URI; records with the nearest
    proximity in the WARC file are grouped together, which is not guaranteed to
    be correct.

    Output can be quite verbose and should be adapted to suit your purposes.

    For the highest-level, least-detailed report, run with `--no-output-summary-by-uri`.

    To ignore records whose WARC-Target-URI specifies the `file:///` protocol
    (which are often not expected to belong to a matched request/response pair),
    run with `--no-include-file-protocol-target-uri`.

    To include more metadata about the records, run with `--output-record-details`
    (WARC headers, offsets, etc.) and/or `--output-http-headers`.

    To included information on pairs, not just lone records, when outputting record
    details or http headers, run with `--include-pair-details`.

    So, for the most-detailed report, run:
    `wb match-record-pairs --output-record-details --output-http-headers --include-pair-details`.

    ---

    Example:

      \b
      $ wb match-record-pairs cnn.com.wacz

      \b
      #
      # SUMMARY
      #

      \b
      Sets of matched requests/responses: 1043
      Requests without responses: 0
      Responses without requests: 0

      \b
      #
      # SUMMARY BY URI
      #

      \b
      http://cnn.com/
      Pairs: 1

      \b
      https://189a226af4173e3b4dabb12e12e5d250.safeframe.googlesyndication.com/safeframe/1-0-41/html/container.html
      Pairs: 2

      \b
      (etc.)
    """
    #
    # Handle options
    #
    ctx.obj["FILEPATH"] = filepath
    ctx.obj["OUTPUT_SUMMARY_BY_URI"] = output_summary_by_uri
    ctx.obj["OUTPUT_RECORD_METADATA"] = output_record_details
    ctx.obj["OUTPUT_HTTP_HEADERS"] = output_http_headers
    ctx.obj["INCLUDE_PAIR_DETAILS"] = include_pair_details
    ctx.obj["INCLUDE_FILE_PROTOCOL_TARGET_URI"] = include_file_protocol_target_uri

    if not ctx.obj["OUTPUT_RECORD_METADATA"] and ctx.obj["OUTPUT_HTTP_HEADERS"]:
        raise click.ClickException(
            "Please pass --output-record-metadata together with --include-http-headers."
        )

    if not ctx.obj["OUTPUT_RECORD_METADATA"] and ctx.obj["INCLUDE_PAIR_DETAILS"]:
        raise click.ClickException(
            "Please pass --output-record-metadata together with --include-pairs."
        )

    #
    # Parse and analyze
    #
    count_only = (
        not ctx.obj["OUTPUT_SUMMARY_BY_URI"] and not ctx.obj["OUTPUT_RECORD_METADATA"]
    )
    if not ctx.obj["INCLUDE_FILE_PROTOCOL_TARGET_URI"]:
        record_filters = [
            lambda record: not record.header.get_field(
                "WARC-Target-URI", b""
            ).startswith(b"file:///")
        ]
    else:
        record_filters = None

    pair_data = open_and_invoke(
        ctx,
        "get_approximate_request_response_pairs",
        invoke_kwargs={"count_only": count_only},
        processor_config=CLIProcessorConfig(
            record_filters=record_filters,
        ),
        cache_config=CLICachingConfig(
            header_bytes=True,
            parsed_headers=True,
            content_block_bytes=ctx.obj["OUTPUT_HTTP_HEADERS"],
        ),
    )

    #
    # Format results
    #
    data = {"counts": pair_data["counts"], "by_uri": {}}

    def decode_uri_bytes(uri_bytes):
        return {
            "latin1": uri_bytes.decode("latin1"),
            "utf-8-replace": uri_bytes.decode("utf-8", errors="replace"),
            "base64-ascii": base64.b64encode(uri_bytes).decode("ascii"),
        }

    def add_uri_to_output(uri_strs):
        # Use latin-1 as a key for some readability, while still preventing collisions
        # if that's wrong and there are decoding errors.
        key = uri_strs["latin1"]
        if key not in data["by_uri"]:
            data["by_uri"][key] = {
                "uri-latin1": uri_strs["latin1"],
                "uri-utf-8-replace": uri_strs["utf-8-replace"],
                "uri-base64-ascii": uri_strs["base64-ascii"],
                "count_pairs": 0,
                "count_lone_requests": 0,
                "count_lone_responses": 0,
            }
        return key

    def format_record(record):
        formatted_record = {
            "offsets": [record.start, record.end],
            "warc_record_headers": record.header.get_parsed_fields(decode=True),
        }
        if ctx.obj["OUTPUT_HTTP_HEADERS"]:
            header_bytes = record.get_http_header_block()
            header_str = header_bytes.decode("utf-8", errors="replace")
            formatted_record["http_headers"] = [
                line for line in header_str.split("\r\n") if line
            ]
        return formatted_record

    def format_record_pair(pair):
        return [format_record(record) for record in pair]

    if ctx.obj["OUTPUT_SUMMARY_BY_URI"] or ctx.obj["OUTPUT_RECORD_METADATA"]:
        for uri_bytes, record_pair_list in pair_data["pairs_by_uri"].items():
            uri_strs = decode_uri_bytes(uri_bytes)
            key = add_uri_to_output(uri_strs)
            pairs = [format_record_pair(pair) for pair in record_pair_list]
            if ctx.obj["INCLUDE_PAIR_DETAILS"]:
                data["by_uri"][key]["record_pairs"] = pairs
            data["by_uri"][key]["count_pairs"] = len(pairs)

        for uri_bytes, record_list in pair_data["lone_requests_by_uri"].items():
            uri_strs = decode_uri_bytes(uri_bytes)
            key = add_uri_to_output(uri_strs)
            data["by_uri"][key]["lone_requests"] = [
                format_record(record) for record in record_list
            ]
            data["by_uri"][key]["count_lone_requests"] = len(
                data["by_uri"][key]["lone_requests"]
            )

        for uri_bytes, record_list in pair_data["lone_responses_by_uri"].items():
            uri_strs = decode_uri_bytes(uri_bytes)
            key = add_uri_to_output(uri_strs)
            data["by_uri"][key]["lone_responses"] = [
                format_record(record) for record in record_list
            ]
            data["by_uri"][key]["count_lone_responses"] = len(
                data["by_uri"][key]["lone_responses"]
            )

    #
    # Output results
    #

    if ctx.obj["OUT"] == "json":
        click.echo(json.dumps(data))
    else:

        def output_record_headers(record):
            for header, values in record["warc_record_headers"].items():
                for value in values:
                    click.echo(f"{indent * 2}{header}: {value}")

        def output_record_http_headers(record):
            for line in record["http_headers"]:
                click.echo(f"{indent * 3}{line}")

        click.echo("#\n# SUMMARY\n#\n")

        click.echo(f"Sets of matched requests/responses: {data['counts']['pairs']}")
        click.echo(f"Requests without responses: {data['counts']['lone_requests']}")
        click.echo(f"Responses without requests: {data['counts']['lone_responses']}")
        click.echo()

        if ctx.obj["OUTPUT_SUMMARY_BY_URI"]:
            click.echo("#\n# SUMMARY BY URI\n#\n")

            for uri in sorted(data["by_uri"]):
                info = data["by_uri"][uri]

                click.echo(uri)
                if info["count_pairs"]:
                    click.echo(f"  Pairs: {info['count_pairs']}")
                if info["count_lone_requests"]:
                    click.echo(f"  Lone requests: {info['count_lone_requests']}")
                if info["count_lone_responses"]:
                    click.echo(f"  Lone responses: {info['count_lone_responses']}")
                click.echo()

        if ctx.obj["OUTPUT_RECORD_METADATA"] and (
            data["counts"]["lone_requests"]
            or data["counts"]["lone_responses"]
            or (data["counts"]["pairs"] and ctx.obj["INCLUDE_PAIR_DETAILS"])
        ):
            click.echo("\n#\n# DETAILS BY URI\n#\n")

            for uri in sorted(data["by_uri"]):
                info = data["by_uri"][uri]
                indent = "  "

                if (
                    not (ctx.obj["INCLUDE_PAIR_DETAILS"] and info["count_pairs"])
                    and not info["count_lone_requests"]
                    and not info["count_lone_responses"]
                ):
                    continue

                click.echo(f"{'-' * 40}")
                click.echo(f"{uri}")
                click.echo(f"{'-' * 40}\n")

                if info["count_pairs"] and ctx.obj["INCLUDE_PAIR_DETAILS"]:
                    for pair in info["record_pairs"]:
                        click.echo(f"{indent}PAIR:")
                        for record in pair:
                            click.echo(
                                f"{indent}Record bytes {record['offsets'][0]}-{record['offsets'][1]}"
                            )
                        click.echo()

                        for record in pair:
                            output_record_headers(record)
                            click.echo()

                            if ctx.obj["OUTPUT_HTTP_HEADERS"]:
                                output_record_http_headers(record)
                                click.echo()

                if info["count_lone_requests"]:
                    click.echo(f"{indent}LONE REQUESTS:\n")

                    for record in info["lone_requests"]:
                        click.echo(
                            f"{indent}Record bytes {record['offsets'][0]}-{record['offsets'][1]}"
                        )
                        click.echo()

                        output_record_headers(record)
                        click.echo()

                        if ctx.obj["OUTPUT_HTTP_HEADERS"]:
                            output_record_http_headers(record)
                            click.echo()

                if info["count_lone_responses"]:
                    click.echo(f"{indent}LONE RESPONSES:\n")

                    for record in info["lone_responses"]:
                        click.echo(
                            f"{indent}Record bytes {record['offsets'][0]}-{record['offsets'][1]}"
                        )
                        click.echo()

                        output_record_headers(record)
                        click.echo()

                        if ctx.obj["OUTPUT_HTTP_HEADERS"]:
                            output_record_http_headers(record)
                            click.echo()

                click.echo()
