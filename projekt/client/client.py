import socket
import struct
import random
import hashlib
import hmac
import sys
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
from enum import Enum

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
    iv = random.randbytes(16)
    cipher = AES.new(encryption_key, AES.MODE_CBC, iv)
    ciphertext = iv + cipher.encrypt(pad(plaintext, AES_BLOCK))
    mac = hmac.new(mac_key, ciphertext, hashlib.sha256).digest()
    return ciphertext, mac


def decrypt_and_verify(encryption_key, mac_key, ciphertext, mac):
    expected_mac = hmac.new(mac_key, ciphertext, hashlib.sha256).digest()
    if expected_mac != mac:
        raise ValueError("MAC error")
    iv = ciphertext[:16]
    ct = ciphertext[16:]
    cipher = AES.new(encryption_key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ct), AES_BLOCK)


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock: socket.socket | None = None
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
        msg_type = header >> 14
        if msg_type != MessageType.SERVER_HELLO.value:
            raise RuntimeError("Oczekiwano ServerHello")

        B = struct.unpack(">I", data[2:6])[0]

        shared_secret = pow(B, a, p)
        self.encryption_key, self.mac_key = derive_keys(shared_secret)

        self.connected = True
        print("[+] Połączono z serwerem")

        with open("client_key.txt", "w") as f:
            f.write(f"shared_secret={shared_secret}\n")
            f.write(self.encryption_key.hex() + "\n")
            f.write(self.mac_key.hex() + "\n")

    def send_message(self, text: str):
        if not self.connected:
            print("Brak połączenia")
            return

        plaintext = bytes([MessageType.ENCRYPTED_MSG.value]) + text.encode()
        ciphertext, mac = encrypt_then_mac(
            self.encryption_key, self.mac_key, plaintext
        )

        frame = struct.pack(">H", len(ciphertext)) + ciphertext + mac
        self.sock.sendall(frame)

    def end_session(self):
        if not self.connected:
            print("Brak połączenia")
            return

        plaintext = bytes([MessageType.END_SESSION.value])
        ciphertext, mac = encrypt_then_mac(
            self.encryption_key, self.mac_key, plaintext
        )

        frame = struct.pack(">H", len(ciphertext)) + ciphertext + mac
        self.sock.sendall(frame)

        self.sock.close()
        self.connected = False
        print("[+] Sesja zakończona")

    def receive_loop(self):
        try:
            while self.connected:
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
                    break
        except Exception:
            self.connected = False


def main():
    if len(sys.argv) != 3:
        print("python3 client.py <host> <port>")
        return

    host = sys.argv[1]
    port = int(sys.argv[2])

    client = Client(host, port)

    print("Polecenia: connect | send <msg> | end | quit")

    while True:
        try:
            cmd = input("> ").strip()
        except EOFError:
            break

        if cmd == "connect":
            client.connect()

        elif cmd.startswith("send"):
            parts = cmd.split(" ", 1)
            if len(parts) != 2:
                print("Użycie: send <wiadomość>")
                continue
            client.send_message(parts[1])

        elif cmd == "end":
            client.end_session()

        elif cmd == "quit":
            if client.connected:
                client.end_session()
            break

        else:
            print("Polecenia: connect | send <msg> | end | quit")


if __name__ == "__main__":
    main()
