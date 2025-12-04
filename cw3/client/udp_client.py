#!/usr/bin/env python3
import socket
import hashlib
import os
import struct
import sys
import time

PACKET_SIZE = 100
ACK_TIMEOUT = 0.3
MAX_RETRIES = 20
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
        sock.settimeout(ACK_TIMEOUT)

        with open(FILE_PATH, "rb") as f:
            seq = 0
            while True:
                data = f.read(PACKET_SIZE)
                if not data:
                    break

                packet = struct.pack("!I", seq) + data
                retries = 0

                print(f"[SEND] seq={seq}, bytes={len(data)}")

                while True:
                    sock.sendto(packet, (server, port))
                    try:
                        ack, _ = sock.recvfrom(4)
                        ack_seq = struct.unpack("!I", ack)[0]
                        print(f"[RECV ACK] {ack_seq}")

                        if ack_seq == seq:
                            print(f"[OK] Pakiet {seq} potwierdzony")
                            break
                        else:
                            print(f"[BAD ACK] Otrzymano {ack_seq}, oczekiwano {seq}")

                    except socket.timeout:
                        retries += 1
                        print(f"[TIMEOUT] Brak ACK dla {seq}, próba {retries}")
                        if retries > MAX_RETRIES:
                            print("[ERROR] Zbyt wiele retransmisji. Przerwano.")
                            return

                seq += 1

        print("[CLIENT] Wszystkie pakiety wysłane, czekam na hash z serwera...")

        server_hash, _ = sock.recvfrom(1024)
        server_hash = server_hash.decode()

        print("[CLIENT] Hash klienta :", file_hash)
        print("[CLIENT] Hash serwera:", server_hash)

        if server_hash == file_hash:
            print("[RESULT] OK — hashe zgodne")
        else:
            print("[RESULT] BAD — hashe różne")

if __name__ == "__main__":
    main()
