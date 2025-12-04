#!/bin/bash

docker-compose build
docker-compose up

#docker exec udp_server tc qdisc add dev eth0 root netem delay 1000ms 500ms loss 50%&

