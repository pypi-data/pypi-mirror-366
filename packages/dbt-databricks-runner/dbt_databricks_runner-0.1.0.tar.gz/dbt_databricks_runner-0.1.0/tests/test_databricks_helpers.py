from unittest import mock

import pytest

from dbt_databricks_runner import databricks_helpers


def test_find_project_root_found(tmp_path):
    # Create a fake project structure
    project_root = tmp_path / "myproject"
    project_root.mkdir()
    (project_root / "pyproject.toml").write_text("")
    subdir = project_root / "src"
    subdir.mkdir()
    # Should find project root from subdir
    assert databricks_helpers.find_project_root(subdir) == project_root


def test_find_project_root_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        databricks_helpers.find_project_root(tmp_path)


@mock.patch("dbt_databricks_runner.databricks_helpers.load_dotenv")
@mock.patch("dbt_databricks_runner.databricks_helpers.find_project_root")
def test_load_databricks_env_success(
    mock_find_project_root, mock_load_dotenv, tmp_path, monkeypatch
):
    # Setup fake project root and .databricks.env
    project_root = tmp_path
    (project_root / "pyproject.toml").write_text("")
    databricks_dir = project_root / ".databricks"
    databricks_dir.mkdir()
    env_file = databricks_dir / ".databricks.env"
    env_file.write_text("DUMMY=1\n")
    monkeypatch.chdir(project_root)
    mock_find_project_root.return_value = project_root


@mock.patch("dbt_databricks_runner.databricks_helpers.load_dotenv")
@mock.patch("dbt_databricks_runner.databricks_helpers.find_project_root")
def test_load_databricks_env_missing_env_file(
    mock_find_project_root, mock_load_dotenv, tmp_path, monkeypatch
):
    project_root = tmp_path
    (project_root / "pyproject.toml").write_text("")
    monkeypatch.chdir(project_root)
    mock_find_project_root.return_value = project_root
    with pytest.raises(FileNotFoundError):
        databricks_helpers.load_databricks_env()


@mock.patch("databricks.connect.DatabricksSession")
def test_load_spark_session(mock_DatabricksSession):
    mock_builder = mock_DatabricksSession.builder
    mock_spark = mock.Mock()
    mock_builder.getOrCreate.return_value = mock_spark
    spark = databricks_helpers.load_spark_session()
    assert spark == mock_spark
    mock_builder.getOrCreate.assert_called_once()
