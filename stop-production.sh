#!/bin/sh

docker-compose -f docker-compose.yml -f prod.docker-compose.yml down

echo "\nThe Nightscout-Open Humans data solution has now been stopped." 
echo ""

