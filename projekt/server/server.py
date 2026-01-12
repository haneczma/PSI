import socket
import threading
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

clients = {}
client_id_seq = 0
lock = threading.Lock()
server_socket: socket.socket
running = True


class MessageType(Enum):
    CLIENT_HELLO = 0b00
    SERVER_HELLO = 0b01
    ENCRYPTED_MSG = 0b10
    END_SESSION = 0b11


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
    encription_key = hashlib.sha256(s + b"ENC").digest()
    mac_key = hashlib.sha256(s + b"MAC").digest()
    return encription_key, mac_key


def encrypt_then_mac(encription_key, mac_key, plaintext):
    iv = random.randbytes(16)
    cipher = AES.new(encription_key, AES.MODE_CBC, iv)
    ciphertext = iv + cipher.encrypt(pad(plaintext, AES_BLOCK))
    mac = hmac.new(mac_key, ciphertext, hashlib.sha256).digest()
    return ciphertext, mac


def decrypt_and_verify(encription_key, mac_key, ciphertext, mac):
    expected_mac = hmac.new(mac_key, ciphertext, hashlib.sha256).digest()
    if expected_mac != mac:
        raise ValueError("MAC error")
    iv = ciphertext[:16]
    ct = ciphertext[16:]
    cipher = AES.new(encription_key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ct), AES_BLOCK)


def handle_client(conn, addr, cid):
    print(f"[+] Klient {addr}")

    try:
        data = recv_exact(conn, 10)

        header = struct.unpack(">H", data[:2])[0]
        msg_type = header >> 14
        if msg_type != MessageType.CLIENT_HELLO.value:
            print("Połączenie tzreba zacząć od Client_hello")
            return

        g = header & 0x3FFF
        p = struct.unpack(">I", data[2:6])[0]
        A = struct.unpack(">I", data[6:10])[0]

        b = random.randint(1, p - 1)
        B = pow(g, b, p)

        server_hello = struct.pack(">H I", MessageType.SERVER_HELLO.value << 14, B)
        conn.sendall(server_hello)

        shared_secret = pow(A, b, p)
        encription_key, mac_key = derive_keys(shared_secret)

        with lock:
            clients[cid]["mac_key"] = mac_key
            clients[cid]["encription_key"] = encription_key

        while True:
            # jawna długość ramki
            raw_len = recv_exact(conn, 2)
            length = struct.unpack(">H", raw_len)[0]

            ciphertext = recv_exact(conn, length)
            mac = recv_exact(conn, MAC_LEN)

            plaintext = decrypt_and_verify(encription_key, mac_key, ciphertext, mac)

            msg_type = plaintext[0]
            payload = plaintext[1:]

            if msg_type == MessageType.ENCRYPTED_MSG.value:
                print(f"[{cid}] {payload.decode()}")

            elif msg_type == MessageType.END_SESSION.value:
                print(f"[{cid}] Sesja zakończona przez klienta")
                break

            else:
                print("Nieznany typ wiadomości")
                break

    except Exception as e:
        print(f"[{cid}] Błąd: {e}")
    finally:
        with lock:
            clients.pop(cid, None)
        conn.close()
        print(f"[-] Klient {cid} rozłączony")


def server_console():
    global running
    while running:
        try:
            cmd = input("> ").strip()
        except EOFError:
            break

        if cmd == "list":
            with lock:
                if not clients:
                    print("Brak podłączonych klientów")
                for cid, info in clients.items():
                    print(f"Klient {cid} {info['addr']}")

        elif cmd.startswith("end"):
            parts = cmd.split()
            if len(parts) != 2:
                print("Użycie: end <client_id>")
                continue
            cid = 0
            try:
                cid = int(parts[1])
            except ValueError:
                print("<client_id> musi być typu int")
                continue

            with lock:
                if cid not in clients:
                    print("Nie ma takiego klienta")
                    continue
                conn = clients[cid]["conn"]
                mac_key = clients[cid]["mac_key"]
                encription_key = clients[cid]["encription_key"]

            plaintext = bytes([MessageType.END_SESSION.value])
            ciphertext, mac = encrypt_then_mac(encription_key, mac_key, plaintext)

            frame = struct.pack(">H", len(ciphertext)) + ciphertext + mac
            conn.sendall(frame)
            conn.close()
            with lock:
                clients.pop(cid, None)

            print(f"[+] Zakończono sesję klienta {cid}")

        elif cmd == "quit":
            running = False
            print("Zamykanie serwera...")
            try:
                server_socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            server_socket.close()
            break

        else:
            print("Dostępne polecenia: list | end <client_id> | quit")


def main():
    global client_id_seq
    global server_socket

    if len(sys.argv) != 3:
        print("python3 ./server.py <port> <max_clients>")
        return

    port = int(sys.argv[1])
    max_clients = int(sys.argv[2])

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", port))
    server_socket.listen(max_clients)

    print(f"Serwer nasłuchuje na porcie {port}")

    threading.Thread(target=server_console, daemon=True).start()

    while running:
        try:
            conn, addr = server_socket.accept()
        except OSError:
            break

        with lock:
            client_id_seq += 1
            cid = client_id_seq
            clients[cid] = {
                "conn": conn,
                "addr": addr,
                "mac_key": None,
                "encription_key": None,
            }

        threading.Thread(
            target=handle_client, args=(conn, addr, cid), daemon=True
        ).start()

    try:
        server_socket.close()
    except OSError:
        pass


if __name__ == "__main__":
    main()
