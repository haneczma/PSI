import socket
import struct
import sys

HOST = "0.0.0.0"

if  len(sys.argv) < 2:
    print("no port specified, using 8000")
    PORT=8000
else:
  PORT = int( sys.argv[1] )

TREE_SIZE = 15


def recv_exact(conn, n):
    data = b""
    while len(data) < n:
        chunk = conn.recv(n - len(data))
        if not chunk:
            return None
        data += chunk
    return data

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(1)
    print(f"Serwer nasłuchuje na {HOST}:{PORT}")

    conn, addr = server.accept()
    print("Połączono z:", addr)

    tree = [None] * TREE_SIZE

    for i in range(TREE_SIZE):
        packet = recv_exact(conn, 8)
        if packet is None:
            break
        node_id, value = struct.unpack("<ii", packet)
        tree[node_id] = value
        print(f"Odebrano: id={node_id}, value={value}")

    print("\nDrzewo BFS:", tree)
    conn.close()
    server.close()

if __name__ == "__main__":
    main()
