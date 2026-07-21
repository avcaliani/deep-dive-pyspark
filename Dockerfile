FROM python:3.12-slim

ENV JAVA_HOME="/usr/lib/jvm/temurin-21-jdk-amd64"

ENV SPARK_HOME="/opt/spark"
ENV SPARK_VERSION="4.1.1"
ENV HADOOP_VERSION="3"
ENV PATH="$SPARK_HOME/bin:$PATH"

ENV PYSPARK_PYTHON=python
ENV PATH="$SPARK_HOME/python:$PATH"

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /opt

# Java (Eclipse Temurin, via the Adoptium apt repo)
RUN apt-get update && apt-get -y install --no-install-recommends wget apt-transport-https gnupg && \
    wget -O - https://packages.adoptium.net/artifactory/api/gpg/key/public | gpg --dearmor -o /etc/apt/trusted.gpg.d/adoptium.gpg && \
    echo "deb https://packages.adoptium.net/artifactory/deb $(awk -F= '/^VERSION_CODENAME/{print $2}' /etc/os-release) main" > /etc/apt/sources.list.d/adoptium.list && \
    apt-get update && apt-get -y install temurin-21-jdk && apt-get -y autoremove

# Spark
ADD "https://archive.apache.org/dist/spark/spark-$SPARK_VERSION/spark-$SPARK_VERSION-bin-hadoop$HADOOP_VERSION.tgz" .
RUN tar -xzf spark*.tgz && rm -f spark*.tgz && mv spark* spark

# uv
COPY --from=ghcr.io/astral-sh/uv:0.11.29 /uv /uvx /bin/

CMD tail -f /dev/null
