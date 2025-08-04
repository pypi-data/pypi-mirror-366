from unittest import mock

from dbt_databricks_runner import dbt_helpers


@mock.patch("dbt_databricks_runner.dbt_helpers.dbtRunner")
@mock.patch("dbt_databricks_runner.dbt_helpers.load_spark_session")
@mock.patch("dbt_databricks_runner.dbt_helpers.load_databricks_env")
def test_dbt_local_success(
    mock_load_env, mock_load_spark, mock_dbtRunner, monkeypatch
):
    monkeypatch.setenv("DBT_TARGET", "local")
    # Simulate .databricks.env file exists
    mock_load_env.return_value = (
        None  # Ensure the mock is used and does nothing
    )
    mock_result = mock.Mock()
    mock_result.success = True
    mock_dbtRunner.return_value.invoke.return_value = mock_result
    result = dbt_helpers.dbt(("run",), return_output=True)
    assert result == mock_result
    mock_load_env.assert_called_once()
    mock_load_spark.assert_called_once()
    mock_dbtRunner.return_value.invoke.assert_called_once_with(["run"])


@mock.patch("dbt_databricks_runner.dbt_helpers.dbtRunner")
@mock.patch("dbt_databricks_runner.dbt_helpers.load_spark_session")
@mock.patch("dbt_databricks_runner.dbt_helpers.load_databricks_env")
def test_dbt_local_failure(
    mock_load_env, mock_load_spark, mock_dbtRunner, monkeypatch
):
    import pytest

    monkeypatch.setenv("DBT_TARGET", "local")
    mock_load_env.return_value = None  # Simulate .databricks.env file exists
    mock_result = mock.Mock()
    mock_result.success = False
    mock_result.exception = Exception("fail")
    mock_dbtRunner.return_value.invoke.return_value = mock_result
    with pytest.raises(Exception):
        dbt_helpers.dbt(("run",))
    mock_load_env.assert_called_once()
    mock_load_spark.assert_called_once()
    mock_dbtRunner.return_value.invoke.assert_called_once_with(["run"])


@mock.patch("dbt_databricks_runner.dbt_helpers.dbtRunner")
@mock.patch("dbt_databricks_runner.dbt_helpers.load_spark_session")
@mock.patch("dbt_databricks_runner.dbt_helpers.load_databricks_env")
def test_dbt_non_local(
    mock_load_env, mock_load_spark, mock_dbtRunner, monkeypatch
):
    monkeypatch.setenv("DBT_TARGET", "prod")
    mock_result = mock.Mock()
    mock_result.success = True
    mock_dbtRunner.return_value.invoke.return_value = mock_result
    result = dbt_helpers.dbt(("run",), return_output=True)
    assert result == mock_result
    mock_load_env.assert_not_called()
    mock_load_spark.assert_not_called()
    mock_dbtRunner.return_value.invoke.assert_called_once_with(["run"])


def test_get_dbt_target_env(monkeypatch):
    monkeypatch.setenv("DBT_TARGET", "foo")
    assert dbt_helpers.get_dbt_target(()) == "foo"


def test_get_dbt_target_flag_equals():
    args = ("run", "--target=bar")
    assert dbt_helpers.get_dbt_target(args) == "bar"


def test_get_dbt_target_flag_space():
    args = ("run", "--target", "baz")
    assert dbt_helpers.get_dbt_target(args) == "baz"


def test_get_dbt_target_flag_precedence(monkeypatch):
    monkeypatch.setenv("DBT_TARGET", "foo")
    args = ("run", "--target=bar")
    assert dbt_helpers.get_dbt_target(args) == "bar"
