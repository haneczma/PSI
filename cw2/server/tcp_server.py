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


class Node:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

def recv_exact(conn, n):
    data = b""
    while len(data) < n:
        chunk = conn.recv(n - len(data))
        if not chunk:
            return None
        data += chunk
    return data

def build_tree(values):
    if values[0] is None:
        return None
    root = Node(values[0])
    queue = [(root, 0)]
    while queue:
        node, idx = queue.pop(0)
        left_i = 2 * idx + 1
        right_i = 2 * idx + 2
        if left_i < len(values) and values[left_i] is not None:
            node.left = Node(values[left_i])
            queue.append((node.left, left_i))
        if right_i < len(values) and values[right_i] is not None:
            node.right = Node(values[right_i])
            queue.append((node.right, right_i))
    return root

def inorder(node):
    if node:
        inorder(node.left)
        print(node.val, end=" ")
        inorder(node.right)

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(1)
    print(f"Serwer nasłuchuje na {HOST}:{PORT}")

    conn, addr = server.accept()
    print("Połączono z:", addr)

    values = [None] * TREE_SIZE
    for _ in range(TREE_SIZE):
        packet = recv_exact(conn, 8)
        if packet is None:
            break
        node_id, value = struct.unpack("<ii", packet)
        values[node_id] = value
        print(f"Odebrano: id={node_id}, value={value}")

    print("\nRekonstrukcja drzewa...")
    root = build_tree(values)
    print("Inorder:", end=" ")
    inorder(root)
    print()

    conn.close()
    server.close()

if __name__ == "__main__":
    main()
