[![Code checks and tests](https://github.com/paalvibe/bricksops/actions/workflows/check-and-test.yaml/badge.svg)](https://github.com/paalvibe/bricksops/actions/workflows/check-and-test.yaml)
# Brickops
DataOps framework for Databricks

Table of contents:

- [Getting started](#getting-started)
- [Purpose](#purpose)
- [Naming functions](#naming-functions)
  - [Catalog name from path: catname_from_path()](#catalog-name-from-path-catname_from_path)
  - [Environment specific database name: dbname()](#environment-specific-database-name-dbname)
  - [Table name: tablename()](#table-name-tablename)
- [Deployment functions](#deployment-functions)
  - [Auto-deploying a spark pipeline](#auto-deploying-a-spark-pipeline)
- [Getting started](#getting-started)
- [How to get into devcontainer from the command line](#how-to-get-into-devcontainer-from-the-command-line)
- [Configuration options for naming and mesh levels](#configuration-options-for-naming-and-mesh-levels)
- [Underlying philosophy](#underlying-philosophy)


## Getting Started

The package can be installed with pip:

``````bash
pip install brickops
``````

## Purpose
Brickops is a framework to automatically name Databricks assets, like Unity Catalog (UC) schemas, tables and jobs, according to environment (e.g. dev, staging, prod) and domain/project/flow names (where domain, project, flow are derived from the folder path in the repository).

This enables the users (data engineers, etc) to easily develop and deploy data sets, models and pipelines, and automatically comply with organizational principles.

Brickops contains naming functions for UC assets and autojob() functions for auto-deploying jobs.
In the near future autodeploy of DLT pipelines will be added.

## Naming funtions

Bricksops works in the context of a folder path, representing data pipeline or flow:

orgs/`acme`/domains/`transport`/projects/`taxinyc`/flows/`revenue`/

The structure here is:

- org: `acme`
    - domain: `transport`
        - project: `taxinyc`
            - flow: `revenue`

### Catalog name from path: catname_from_path()

Example output from naming functions from notebooks under that path:

``````python
# Name functions enables automatic env+user specific database naming
from libs.catname import catname_from_path
from libs.dbname import dbname

cat = catname_from_path()
print(f"Catalog name derived from path: {cat}")
``````

Default output (use the domain):
```
Catalog name derived from path: transport
```

Output with optional full mesh prefixing (org_domain_project):
```
Catalog name derived from path: acme_transport_taxinyc
```

### Environment specific database name: dbname()

Database (schema name) with environment prefix:
``````python
db = dbname(db="revenue", cat=cat)
print("DB name: {db}")
``````

Output in dev environment:
``````
DB name: transport.dev_paldevibe_main_0e7768a7_revenue
``````

Output in prod environment:
``````
DB name: transport.revenue
``````

### Table name: tablename()

```
from brickops.datamesh.naming import build_table_name as tablename

revenue_by_borough_tbl = tablename(cat=catalog, db="revenue", tbl="revenue_by_borough")
print(f"revenue_by_borough_tbl: {revenue_by_borough_tbl}")
```

Output in dev environment:
``````
transport.dev_paldevibe_branchname_0e7768a7_revenue.revenue_by_borough
``````

Output in prod environment:
``````
transport.revenue.revenue_by_borough
``````

In dev (and all environments except prod), the database name is prefixed with username, branch and commit ref. The automatic prefixes prevents notebooks running in development mode from overwriting production data.

## Deployment functions


### Auto-deploying a spark pipeline


``````python
from brickops.dataops.deploy.autojob import autojob

response = autojob()
``````

This job will automatically name and generate a job based on a deployment.yml file in the folder, e.g. `orgs/acme/domains/transport/projects/taxinyc/flows/revenue/deployment.yml`.

In development, the job name created will be:

`acme_transport_taxinyc_dev_abirkhan_branchname_4c6799ab_revenue`

In production, the job name created will be:

`acme_transport_taxinyc_revenue`

The automatic prefixes in dev prevents development jobs from overwriting production jobs.

## Getting started
This project uses [uv](https://docs.astral.sh/uv/). It might be easies to use the devcontainer,
defined in `.devcontainer`, which is supported by VSCode and other toos.

If you want a local install, follow the installation instructions for your platform on the project homepage.

Next, make sure you are in the project root and run the following command in the terminal:

```shell
uv sync
```

This will create a virtual environment and install the required packages in it.
The project configuration can be found in [`pyproject.toml`](./pyproject.toml).

You can now run the tests with
```shell
uv run pytest
```

## How to get into devcontainer from command line

```
make start-devcontainer
make devcontainer-shell
```

## Configuration options for naming and mesh levels

Naming of resources (catalogs, db/schemas, jobs, pipelines) can be configured in a file called .brickopscfg/config.yaml
in the root of tour repo. example configurations can be found in [tests/.brickopscfg/config.yml](tests/.brickopscfg/config.yml).

Mesh levels refers here to the granularity/depth of your organization represented in the repo structure, e.g. organization, domain and project.

An example configuration could be:

```
naming:
  job:
    prod: "{domain}_{project}_{env}"
    other: "{domain}_{project}_{env}_{username}_{gitbranch}_{gitshortref}"
  pipeline:
    prod: "{domain}_{project}_{env}_dlt"
    other: "{domain}_{project}_{env}_{username}_{gitbranch}_{gitshortref}_dlt"
  catalog:
    prod: "{domain}"
    other: "{domain}"
  db:
    prod: "{db}"
    other: "{env}_{username}_{gitbranch}_{gitshortref}_{db}"
```

Let us now see what resource names would be produced from a notebook located at
`something/domains/marketing/projects/projectfoo/flows/prep/foo_notebook`.

For catalogs the configuration above means the domain section of a path is used,
for jobs a combination of domain, project and env.

The resource names would become:

* job name:
  * prod: `marketing_projectfoo_prod`
  * dev: `marketing_projectfoo_env_paldevibe_branchname_82e5d310`
* pipeline name:
  * prod: `marketing_projectfoo_prod_dlt`
  * dev: `marketing_projectfoo_env_paldevibe_branchname_82e5d310_dlt`
* catalog name:
  * prod: `sales`
  * dev: `sales`
* db name for a database/schema called `customers`:
  * prod: `customers`
  * dev: `customers_env_paldevibe_branchname_82e5d310`

* With org support, in the following notebook: `/Repos/test@foobar.foo/dataplatform/something/org/acme/domains/sales/projects/projectfoo/flows/testflow/foo_notebook`, a config of `{org}_{domain}_{project}_{env}` would result in `acme_sales_projectfoo_prod` for a production environment.

## Development tools

### Ruff

How to run ruff:

```
make ruff
```

Without make:

```
uv run ruff check --output-format=github .
```

### Mypy

How to run mypy:

```
make mypy
```

Without make:

```
mypy .
```


## Underlying philosophy

The framework is partly based on the thoughts presented in the article [Data Platform Urbanism - Sustainable Plans for your Data Work](https://www.linkedin.com/pulse/data-platform-urbanism-sustainable-plans-your-work-p%25C3%25A5l-de-vibe/).

It can be explored in the open source workshop [Databricks DataOps course](https://github.com/paalvibe/databricks-dataops-course).
