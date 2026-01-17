#!/bin/sh
# entrypoint.sh
set -e

tcpdump -i eth0 tcp -w /tmp/capture.pcap -U &

python3 server.py 1234 10