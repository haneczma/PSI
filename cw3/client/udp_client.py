#!/usr/bin/env python3
import socket
import hashlib
import os
import struct
import sys

PACKET_SIZE = 100
ACK_TIMEOUT = 0.3
MAX_RETRIES = 20
FILE_PATH = "data.bin"

def generate_random_file(path, size=10000):
    if not os.path.exists(path):
        with open(path, "wb") as f:
            f.write(os.urandom(size))

def compute_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(4096):
            h.update(chunk)
    return h.hexdigest()

def main():
    server = sys.argv[1]
    port = int(sys.argv[2])

    generate_random_file(FILE_PATH)
    file_hash = compute_hash(FILE_PATH)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(ACK_TIMEOUT)

        with open(FILE_PATH, "rb") as f:
            seq = 0
            while True:
                data = f.read(PACKET_SIZE)
                if not data:
                    break
                packet = struct.pack("!I", seq) + data
                retries = 0
                while True:
                    sock.sendto(packet, (server, port))
                    try:
                        ack, _ = sock.recvfrom(4)
                        ack_seq = struct.unpack("!I", ack)[0]
                        if ack_seq == seq:
                            break
                    except socket.timeout:
                        retries += 1
                        if retries > MAX_RETRIES:
                            return
                seq += 1

        server_hash, _ = sock.recvfrom(1024)
        server_hash = server_hash.decode()

        print(file_hash)
        print(server_hash)

        if server_hash == file_hash:
            print("OK")
        else:
            print("BAD")

if __name__ == "__main__":
    main()
