#!/bin/sh
image_name="open-aps-int-tests:latest"
compose_network_name="open-aps-test-network"

docker build -t $image_name . && \
	docker run --rm --network=$compose_network_name $image_name

