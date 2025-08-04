## Overview

This repository contains the dbt-runner to run dbt-spark on Databricks through:
- VSCode extension for local development
- Deployed with Databricks Job Clusters using spark session.

---

## Prerequisites

Before setting up, ensure you have the following tools installed:

- **Databricks CLI:** [Installation Guide](https://docs.databricks.com/aws/en/dev-tools/cli/install)
- **VSCode Databricks Extension:** Available via VSCode marketplace.
- **uv:** [Installation Guide](https://docs.astral.sh/uv/getting-started/installation/)

---
## Set-Up Instructions

1. **Install this repository with pip/uv**

3. **Configure Databricks CLI:**
    - Run `databricks configure --token` and follow prompts to set up authentication.
4. **Set up DBT profiles:**
    - Create or update your `~/.dbt/profiles.yml` with your Databricks connection details.
5. **Run feature preparation pipelines:**
    - Use `uv run dbt run` to execute pipelines.
    - Use `uv run dbt test` to validate models.

---
