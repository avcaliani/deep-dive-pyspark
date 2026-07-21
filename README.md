# 🐍️ PySpark App

![License](https://img.shields.io/github/license/avcaliani/deep-dive-pyspark?logo=apache&color=lightseagreen)
![Java](https://img.shields.io/badge/Java-21-FF7800?logo=openjdk&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![uv](https://img.shields.io/badge/uv-0.11.29-DE5FE9?logo=astral&logoColor=white)
![Spark](https://img.shields.io/badge/Apache--Spark-4.1.1-E25A1C?logo=apachespark&logoColor=white)
![Delta Lake](https://img.shields.io/badge/Delta_Lake-4.2.0-00ADD8)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)

In this project you will find some stuff that I've done while learning about working with PySpark and [Delta Lake](https://delta.io).
This is a reference scaffold you clone from to start new PySpark projects, not a maintained showcase.

The dataset is a locally-generated, dependency-free mock of Dunder Mifflin's daily paper sales (yes, [The Office](https://en.wikipedia.org/wiki/The_Office_(American_TV_series))) — no download, no internet access needed to run this.

## Quick Start

Java, Spark, uv, and all Python dependencies are baked into the image at build time — no manual install step after `up`.

```bash
# Build the image
docker compose build

# Start the container
docker compose up -d

# Generate the mock sales dataset
docker compose exec app scripts/generate_sales_data.py

# Run the PySpark job
docker compose exec app scripts/run.sh

# When you're done
docker compose down
```

![#output](.docs/output.png)

<details>
<summary>Run locally (without Docker)</summary>

Requires Python 3.12, JDK 21, and [uv](https://docs.astral.sh/uv/) installed locally.

```bash
# Install dependencies
uv sync

# Generate the mock sales dataset
scripts/generate_sales_data.py

# Run the PySpark job
scripts/run.sh

# Run the tests
uv run pytest

# Lint
uv run ruff check .
```

</details>

That's all folks!
