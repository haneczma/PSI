#!/usr/bin/env python3
import socket
import hashlib
import os
import struct
import sys

PACKET_SIZE = 100
FILE_PATH = "data.bin"

def generate_random_file(path, size=10000):
    if not os.path.exists(path):
        with open(path, "wb") as f:
            f.write(os.urandom(size))
        print("[CLIENT] Wygenerowano plik:", path)

def compute_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(4096):
            h.update(chunk)
    return h.hexdigest()

def main():
    server = sys.argv[1]
    port = int(sys.argv[2])

    print("[CLIENT] Adres serwera:", server)
    print("[CLIENT] Port:", port)

    generate_random_file(FILE_PATH)
    file_hash = compute_hash(FILE_PATH)
    print("[CLIENT] Hash klienta:", file_hash)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        with open(FILE_PATH, "rb") as f:
            seq = 0
            while True:
                data = f.read(PACKET_SIZE)
                if not data:
                    break

                packet = struct.pack("!I", seq) + data
                sock.sendto(packet, (server, port))
                print(f"[SEND] seq={seq}, bytes={len(data)}")
                seq += 1

    print("[CLIENT] Wszystkie pakiety wysłane.")
    print("[CLIENT] Hash klienta:", file_hash)

if __name__ == "__main__":
    main()
