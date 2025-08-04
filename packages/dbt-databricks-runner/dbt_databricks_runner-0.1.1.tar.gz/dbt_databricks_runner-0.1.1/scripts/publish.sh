#!/bin/bash

if [ -z "$(printenv UV_PUBLISH_TOKEN)" ]; then
    echo "UV_PUBLISH_TOKEN is not set"
    exit 1
fi

echo "Publishing dbt-databricks-runner to PyPI..."


rm -rf dist/


uv sync
uv build

uv publish