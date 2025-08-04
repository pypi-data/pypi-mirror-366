from pathlib import Path

from dotenv import load_dotenv
from pyspark.sql import SparkSession


def find_project_root(start: Path = Path.cwd()) -> Path:
    """
    Find the root dir of the project by looking for a pyproject.toml file.
    """
    for path in [start, *start.parents]:
        if (path / "pyproject.toml").is_file():
            return path
    raise FileNotFoundError("Could not find pyproject.toml")


def load_databricks_env():
    """
    Load the Databricks environment variables from the .databricks.env file
    located in the .databricks directory at the root of the project.

    The .databricks directory is created by the VSCode Databricks extension
    when the user connects to a Databricks workspace.
    """
    project_dir = find_project_root()
    env_file_path = project_dir / ".databricks" / ".databricks.env"

    if env_file_path.exists():
        load_dotenv(env_file_path)
    else:
        raise FileNotFoundError(f"Environment file not found: {env_file_path}")


def load_spark_session() -> SparkSession:
    from databricks.connect import DatabricksSession

    spark = DatabricksSession.builder.getOrCreate()
    return spark
