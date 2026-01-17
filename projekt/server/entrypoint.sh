#!/bin/sh
# entrypoint.sh
set -e 

tcpdump -i any tcp port 1234 -w /tmp/capture.pcap &

python3 server.py 1234 10