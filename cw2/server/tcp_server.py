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
        li = 2 * idx + 1
        ri = 2 * idx + 2
        if li < len(values) and values[li] is not None:
            node.left = Node(values[li])
            queue.append((node.left, li))
        if ri < len(values) and values[ri] is not None:
            node.right = Node(values[ri])
            queue.append((node.right, ri))
    return root

def draw_tree(root):
    if root is None:
        print("Drzewo puste")
        return

    queue = [(root, 0)]
    current_level = 0
    level_nodes = []

    while queue:
        node, level = queue.pop(0)

        if level != current_level:
            print(f"Poziom {current_level}: " + " ".join(map(str, level_nodes)))
            level_nodes = []
            current_level = level

        level_nodes.append(node.val)

        if node.left:
            queue.append((node.left, level + 1))
        if node.right:
            queue.append((node.right, level + 1))

    print(f"Poziom {current_level}: " + " ".join(map(str, level_nodes)))


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

    print("\nDrzewo:")
    draw_tree(root)

    conn.close()
    server.close()

if __name__ == "__main__":
    main()
