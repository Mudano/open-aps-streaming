#!/bin/sh

cleanup() {
  echo "\nStopping Docker services and deleting now that tests have terminated.\n"
	./destroy-int.sh
}

trap cleanup EXIT

./prepare-int.sh && \
	echo "\nWaiting 15 seconds before running tests so that services are all running.\n" && \
	sleep 15 && \
./run-int-tests.sh
