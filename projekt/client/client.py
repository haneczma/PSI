import socket
import struct
import random
import hashlib
import hmac
import sys
import select
import os

from enum import Enum
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import CBC
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.padding import PKCS7

MAC_LEN = 32
AES_BLOCK = 16


class MessageType(Enum):
    CLIENT_HELLO = 0
    SERVER_HELLO = 1
    ENCRYPTED_MSG = 2
    END_SESSION = 3


def recv_exact(sock, n):
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError
        data += chunk
    return data


def derive_keys(shared_secret: int):
    s = shared_secret.to_bytes(4, "big")
    encryption_key = hashlib.sha256(s + b"ENC").digest()
    mac_key = hashlib.sha256(s + b"MAC").digest()
    return encryption_key, mac_key


def encrypt_then_mac(encryption_key, mac_key, plaintext):
    iv = os.urandom(16)

    padder = PKCS7(128).padder()
    padded = padder.update(plaintext) + padder.finalize()

    cipher = Cipher(AES(encryption_key), CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext_body = encryptor.update(padded) + encryptor.finalize()

    ciphertext = iv + ciphertext_body
    mac = hmac.new(mac_key, ciphertext, hashlib.sha256).digest()

    return ciphertext, mac


def decrypt_and_verify(encryption_key, mac_key, ciphertext, mac):
    expected_mac = hmac.new(mac_key, ciphertext, hashlib.sha256).digest()
    if not hmac.compare_digest(expected_mac, mac):
        raise ValueError("MAC error")

    iv = ciphertext[:16]
    ct = ciphertext[16:]

    cipher = Cipher(AES(encryption_key), CBC(iv))
    decryptor = cipher.decryptor()
    padded = decryptor.update(ct) + decryptor.finalize()

    unpadder = PKCS7(128).unpadder()
    plaintext = unpadder.update(padded) + unpadder.finalize()

    return plaintext


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock: socket.socket
        self.encryption_key = None
        self.mac_key = None
        self.connected = False

    def connect(self):
        if self.connected:
            print("Już połączono")
            return

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

        # Parametry Diffie-Hellmana
        p = 2147483647
        g = 5
        a = random.randint(1, p - 1)
        A = pow(g, a, p)

        header = (MessageType.CLIENT_HELLO.value << 14) | g
        msg = struct.pack(">H I I", header, p, A)
        self.sock.sendall(msg)

        data = recv_exact(self.sock, 6)
        header = struct.unpack(">H", data[:2])[0]
        if header >> 14 != MessageType.SERVER_HELLO.value:
            raise RuntimeError

        B = struct.unpack(">I", data[2:6])[0]

        shared_secret = pow(B, a, p)
        self.encryption_key, self.mac_key = derive_keys(shared_secret)

        self.connected = True
        print("[+] Połączono z serwerem")

    def send_message(self, text):
        if not self.connected:
            return

        plaintext = bytes([MessageType.ENCRYPTED_MSG.value]) + text.encode()
        ciphertext, mac = encrypt_then_mac(self.encryption_key, self.mac_key, plaintext)
        frame = struct.pack(">H", len(ciphertext)) + ciphertext + mac
        self.sock.sendall(frame)

    def end_session(self):
        if not self.connected:
            return

        plaintext = bytes([MessageType.END_SESSION.value])
        ciphertext, mac = encrypt_then_mac(self.encryption_key, self.mac_key, plaintext)
        frame = struct.pack(">H", len(ciphertext)) + ciphertext + mac
        self.sock.sendall(frame)

        self.sock.close()
        self.connected = False
        print("[+] Sesja zakończona")

    def handle_incoming(self):
        raw_len = recv_exact(self.sock, 2)
        length = struct.unpack(">H", raw_len)[0]
        ciphertext = recv_exact(self.sock, length)
        mac = recv_exact(self.sock, MAC_LEN)

        plaintext = decrypt_and_verify(
            self.encryption_key, self.mac_key, ciphertext, mac
        )
        msg_type = plaintext[0]

        if msg_type == MessageType.END_SESSION.value:
            print("[!] Serwer zakończył sesję")
            self.sock.close()
            self.connected = False
        elif msg_type == MessageType.ENCRYPTED_MSG.value:
            print(f"[Serwer] {plaintext[1:].decode()}")


def main():
    if len(sys.argv) != 3:
        print("python3 client.py <host> <port>")
        return

    client = Client(sys.argv[1], int(sys.argv[2]))
    print("Polecenia: connect | send <msg> | end | quit")

    while True:
        inputs = [sys.stdin]
        if client.connected:
            inputs.append(client.sock)

        ready, _, _ = select.select(inputs, [], [])

        for r in ready:
            if r == sys.stdin:
                print("> ", end="", flush=True)
                cmd = sys.stdin.readline().strip()
                if cmd == "connect":
                    client.connect()
                elif cmd.startswith("send "):
                    client.send_message(cmd.split(" ", 1)[1])
                elif cmd == "end":
                    client.end_session()
                elif cmd == "quit":
                    if client.connected:
                        client.end_session()
                    return
                else:
                    print("Polecenia: connect | send <msg> | end | quit")

            elif r == client.sock:
                client.handle_incoming()


if __name__ == "__main__":
    main()
