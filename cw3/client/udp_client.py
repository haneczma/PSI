#!/usr/bin/env python3
import socket
import hashlib
import os
import struct
import time

SERVER = "127.0.0.1"
PORT = 8000

PACKET_SIZE = 100
ACK_TIMEOUT = 0.3
MAX_RETRIES = 20

FILE_PATH = "data.bin"


def generate_random_file(path, size=10000):
    if not os.path.exists(path):
        with open(path, "wb") as f:
            f.write(os.urandom(size))
        print(f"[CLIENT] Wygenerowano plik {path} ({size} B)")


def compute_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(4096):
            h.update(chunk)
    return h.hexdigest()


def main():
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
                while True:
                    print(f"[SEND] seq={seq}, len={len(data)}")
                    sock.sendto(packet, (SERVER, PORT))

                    try:
                        ack, _ = sock.recvfrom(4)
                        ack_seq = struct.unpack("!I", ack)[0]

                        if ack_seq == seq:
                            print(f"[ACK] seq={seq} OK")
                            break
                        else:
                            print(f"[ACK] błędny nr seq={ack_seq}, oczekiwano={seq}")

                    except socket.timeout:
                        retries += 1
                        print(f"[TIMEOUT] powtarzam seq={seq}, próba {retries}")
                        if retries > MAX_RETRIES:
                            print("[ERROR] zbyt wiele retransmisji, przerwano")
                            return

                seq += 1

        print("[CLIENT] Wszystkie pakiety wysłane. Oczekiwanie na hash z serwera...")

        server_hash, _ = sock.recvfrom(1024)
        server_hash = server_hash.decode()

        print("[CLIENT] Hash serwera:", server_hash)
        print("[CLIENT] Hash klienta :", file_hash)

        if server_hash == file_hash:
            print("\n[SUKCES] Hashe są identyczne. Transmisja prawidłowa")
        else:
            print("\n[BŁĄD] Hash różny — plik uszkodzony podczas transmisji")


if __name__ == "__main__":
    main()
