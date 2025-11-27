#!/bin/bash
cd client/
docker build -t z37_client .

cd ../server/
docker build -t z37_server .

docker run -t --name z37_server \
  --network-alias z37_server \
  --network z37_network \
  z37_server:latest &

sleep 5
cd ../client/
docker run -t --network z37_network z37_client:latest z37_server 8000 15 &
