import logging
import os
from typing import Optional

from dbt.cli.main import dbtRunner, dbtRunnerResult

from dbt_databricks_runner.databricks_helpers import (
    load_databricks_env,
    load_spark_session,
)


def get_dbt_target(args: tuple[str, ...]) -> str:
    target = os.getenv("DBT_TARGET", "local")
    for i, arg in enumerate(args):
        if "--target=" in arg:
            target = arg.split("=")[1]
            break
        elif arg == "--target" and i + 1 < len(args):
            target = args[i + 1]
            break
    return target


def dbt(
    args: tuple[str, ...], return_output=False
) -> Optional[dbtRunnerResult]:
    target = get_dbt_target(args)
    logging.debug(f"DBT target: {target}")

    if target == "local":
        load_databricks_env()
        load_spark_session()

    dbt = dbtRunner()
    result: dbtRunnerResult = dbt.invoke(list(args))

    if not result.success:
        logging.debug(result.exception)
        raise Exception(f"dbt {' '.join(list(args))} failed")

    if return_output:
        return result
