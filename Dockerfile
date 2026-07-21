FROM python:3.12-slim

# Java 4 Spark 👇
ENV JAVA_HOME="/opt/java/openjdk"
ENV PATH="$JAVA_HOME/bin:$PATH"

# Spark 👇
ENV SPARK_HOME="/opt/spark"
ENV SPARK_VERSION="4.1.1"
ENV HADOOP_VERSION="3"
ENV PATH="$SPARK_HOME/bin:$PATH"

ENV PYSPARK_PYTHON=python
ENV PATH="$SPARK_HOME/python:$PATH"

# Python UV 👇
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
# Keep the venv outside /app: docker-compose bind-mounts the repo over /app
# at runtime, which would otherwise hide whatever got synced here at build time.
ENV UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /opt

# Java 
COPY --from=eclipse-temurin:21-jdk /opt/java/openjdk /opt/java/openjdk

# uv
COPY --from=ghcr.io/astral-sh/uv:0.11.29 /uv /uvx /bin/

# Spark
ADD "https://archive.apache.org/dist/spark/spark-$SPARK_VERSION/spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION.tgz" .
RUN tar -xzf spark*.tgz && rm -f spark*.tgz && mv spark* spark


WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

CMD tail -f /dev/null
