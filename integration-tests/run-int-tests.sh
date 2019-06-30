#!/bin/sh
image_name="open-aps-int-tests:latest"

docker build -t $image_name . && \
	docker run --rm --network="openapsstreaming_test-network" $image_name

