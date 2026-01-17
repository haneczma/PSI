#!/bin/sh
# entrypoint.sh

tcpdump -i any tcp port 1234 -w /capture.pcap &

python3 server.py 1234 10