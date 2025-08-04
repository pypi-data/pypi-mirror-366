import click

from dbt_databricks_runner.dbt_helpers import dbt


@click.command(context_settings=dict(ignore_unknown_options=True))
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
def main(args: tuple[str, ...]) -> None:
    """
    Overrides the dbt-core cli commands to allow connecting to the
    Databricks Cluster locally.

    Set local=False when running in a Databricks notebook to avoid loading the
    Databricks environment variables from the .databricks.env file.
    """

    click.echo(f"Running [dbt {' '.join(list(args))}]")

    dbt(args, return_output=False)

    click.echo(f"dbt {' '.join(list(args))} succeeded")
