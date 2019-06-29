#!/bin/sh
image_name="open-aps-int-tests:latest"

docker build -t $image_name integration-test-project/ && \
	docker run --rm $image_name

