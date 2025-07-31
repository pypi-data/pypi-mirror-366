#!/usr/bin/env python3
from __future__ import annotations

import json as json_mod
import logging
import os
import subprocess
import sys
from typing import Any

import click
from tabulate import tabulate
from toolforge_weld.errors import ToolforgeError, ToolforgeUserError, print_error_context

from toolforge_envvars_cli.config import get_loaded_config
from toolforge_envvars_cli.envvars import EnvvarsClient

LOGGER = logging.getLogger("toolforge" if __name__ == "__main__" else __name__)
HIDDEN_VALUE = "****************"
TRUNCATE_LENGTH = 50


def handle_error(e: Exception, debug: bool = False) -> None:
    user_error = isinstance(e, ToolforgeUserError)

    prefix = "Error: "
    if not user_error:
        prefix = f"{e.__class__.__name__}: "

    click.echo(click.style(f"{prefix}{e}", fg="red"))

    if debug:
        LOGGER.exception(e)

        if isinstance(e, ToolforgeError):
            print_error_context(e)
    elif not user_error:
        click.echo(
            click.style(
                "Please report this issue to the Toolforge admins if it persists: https://w.wiki/6Zuu",
                fg="red",
            )
        )


def _format_headers(headers: list[str]) -> list[str]:
    return [click.style(item, bold=True) for item in headers]


@click.version_option(prog_name="Toolforge envvars CLI")
@click.group(name="toolforge", help="Toolforge command line")
@click.option(
    "-v",
    "--verbose",
    help="Show extra verbose output. NOTE: Do not rely on the format of the verbose output",
    is_flag=True,
    default=(os.environ.get("TOOLFORGE_VERBOSE", "0") == "1"),
    hidden=(os.environ.get("TOOLFORGE_CLI", "0") == "1"),
)
@click.option(
    "-d",
    "--debug",
    help=(
        "show logs to debug the toolforge-envvars-* packages. For extra verbose output for say build or "
        "job, see --verbose"
    ),
    is_flag=True,
    default=(os.environ.get("TOOLFORGE_DEBUG", "0") == "1"),
    hidden=(os.environ.get("TOOLFORGE_CLI", "0") == "1"),
)
@click.pass_context
def toolforge_envvars(ctx: click.Context, verbose: bool, debug: bool) -> None:
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["debug"] = debug
    ctx.obj["config"] = get_loaded_config()
    ctx.obj["envvars_client"] = EnvvarsClient.from_config(config=ctx.obj["config"])
    pass


@toolforge_envvars.command(name="list", help="List all your envvars.")
@click.option(
    "--json",
    is_flag=True,
    help="If set, will ignore all other options and output the envvars, including the values in json format.",
)
@click.option(
    "--show-values",
    is_flag=True,
    default=False,
    show_default=True,
    help="By default envvar values are hidden. To see the values, use --show-values",
)
@click.option(
    "--truncate/--no-truncate",
    default=False,
    show_default=True,
    help="To only show parts of a long evvar value, use --truncate",
)
@click.pass_context
def envvar_list(ctx: click.Context, json: bool, show_values: bool, truncate: bool) -> None:
    envvars_client = ctx.obj["envvars_client"]
    display_messages = not json
    list_response = envvars_client.get("/envvars", display_messages=display_messages)

    if json:
        result = json_mod.dumps(list_response, indent=4)

    elif not show_values:
        envvars = list_response["envvars"]
        result = tabulate(
            [[envvar["name"], HIDDEN_VALUE] for envvar in envvars],
            headers=_format_headers(["name", "value"]),
            tablefmt="plain",
        )

    else:
        envvars = list_response["envvars"]
        result = tabulate(
            [
                [
                    envvar["name"],
                    (
                        (envvar["value"][:TRUNCATE_LENGTH] + "...")
                        if truncate and len(envvar["value"]) >= TRUNCATE_LENGTH
                        else envvar["value"]
                    ),
                ]
                for envvar in envvars
            ],
            headers=_format_headers(["name", "value"]),
            tablefmt="plain",
        )

    click.echo(result)


@toolforge_envvars.command(name="show", help="Show a specific envvar.")
@click.argument("ENVVAR_NAME", required=True)
@click.option("--json", is_flag=True, help="If set, will output in json format")
@click.pass_context
def envvar_show(ctx: click.Context, envvar_name: str, json: bool) -> None:
    envvars_client = ctx.obj["envvars_client"]
    display_messages = not json
    get_response = envvars_client.get(f"/envvars/{envvar_name}", display_messages=display_messages)

    if json:
        click.echo(json_mod.dumps(get_response, indent=4))
    else:
        envvar = get_response["envvar"]
        click.echo(
            tabulate(
                [[envvar["name"], envvar["value"]]],
                headers=_format_headers(["name", "value"]),
                tablefmt="plain",
            )
        )


def _should_prompt():
    "For easy mocking"
    return sys.stdin.isatty()


def read_value(ctx: click.Context, param: click.Parameter, value: Any) -> str:
    if value is not None:
        return value

    if _should_prompt():
        value = click.prompt("Enter the value of your envvar (Hit Ctrl+C to cancel)")
    else:
        value = sys.stdin.read()

    return value


@toolforge_envvars.command(name="create", help="Create/update an envvar.")
@click.argument("ENVVAR_NAME", required=True)
@click.argument("ENVVAR_VALUE", required=False, callback=read_value)
@click.option(
    "--json",
    help="If set, will output in json format",
    is_flag=True,
)
@click.pass_context
def envvar_create(ctx: click.Context, envvar_name: str, envvar_value: str | None, json: bool) -> None:
    envvars_client = ctx.obj["envvars_client"]
    display_messages = not json
    create_response = envvars_client.post(
        "/envvars", json={"name": envvar_name, "value": envvar_value}, display_messages=display_messages
    )

    if json:
        click.echo(json_mod.dumps(create_response, indent=4))
    else:
        envvar = create_response["envvar"]
        click.echo(
            tabulate(
                [[envvar["name"], envvar["value"]]],
                headers=_format_headers(["name", "value"]),
                tablefmt="plain",
            )
        )


@toolforge_envvars.command(name="delete", help="Delete an envvar.")
@click.argument("ENVVAR_NAME", required=True)
@click.option(
    "--json",
    help="If set, will output in json format",
    is_flag=True,
)
@click.option(
    "--yes-im-sure",
    help="If set, will not ask for confirmation",
    is_flag=True,
)
@click.pass_context
def envvar_delete(ctx: click.Context, envvar_name: str, json: bool = False, yes_im_sure: bool = False) -> None:
    envvars_client = ctx.obj["envvars_client"]
    display_messages = not json

    if not yes_im_sure:
        if not click.prompt(
            text=f"Are you sure you want to delete {envvar_name}? (this can't be undone) [yN]",
            default="no",
            show_default=False,
            type=lambda val: val.lower() in ["y", "Y", "1", "yes", "true"],
        ):
            click.echo("Aborting at user's request")
            sys.exit(1)

    delete_response = envvars_client.delete(f"/envvars/{envvar_name}", display_messages=display_messages)

    if json:
        click.echo(json_mod.dumps(delete_response, indent=4))
    else:
        envvar = delete_response["envvar"]
        click.echo(f"Deleted {envvar_name}, here is its last value: ")
        click.echo(
            tabulate(
                [[envvar["name"], envvar["value"]]],
                headers=_format_headers(["name", "value"]),
                tablefmt="plain",
            )
        )


@toolforge_envvars.command(name="quota", help="Get envvars quota information.")
@click.option(
    "--json",
    help="If set, will output in json format",
    is_flag=True,
)
@click.pass_context
def envvar_quota(ctx: click.Context, json: bool = False) -> None:
    envvars_client = ctx.obj["envvars_client"]
    display_messages = not json
    quota_response = envvars_client.get("/quotas", display_messages=display_messages)

    if json:
        click.echo(json_mod.dumps(quota_response, indent=4))
    else:
        quota = quota_response["quota"]
        formatted_quota = [[quota["quota"], quota["used"], quota["quota"] - quota["used"]]]

        click.echo(
            tabulate(
                formatted_quota,
                headers=_format_headers(["quota", "used", "available"]),
                tablefmt="plain",
            )
        )


def main() -> int:
    # this is needed to setup the logging before the subcommand discovery
    res = toolforge_envvars.parse_args(ctx=click.Context(command=toolforge_envvars), args=sys.argv)
    debug = "-d" in res or "--debug" in res
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    try:
        toolforge_envvars()
    except subprocess.CalledProcessError as e:
        handle_error(e, debug=debug)
        return e.returncode
    except Exception as e:
        handle_error(e, debug=debug)
        return 1

    return 0


if __name__ == "__main__":
    main()
