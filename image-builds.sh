#!/bin/sh
docker build -t open-aps-db:latest ./open-aps-db && \
  docker build -t open-aps-registration-site:latest ./registration-site && \
  docker build -t open-aps-nightscout-ingester:latest ./nightscout-ingester && \
  docker build -t open-aps-downloader:latest ./data-management-app && \
  docker build -t open-aps-open-humans-etl:latest ./open-humans-etl

