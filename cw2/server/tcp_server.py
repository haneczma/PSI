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
    lines = []
    level = [root]
    width = 4

    while any(level):
        current_vals = []
        next_level = []
        for node in level:
            if node:
                current_vals.append(f"{node.val}")
                next_level.append(node.left)
                next_level.append(node.right)
            else:
                current_vals.append(" ")
                next_level.append(None)
                next_level.append(None)

        spacing = width * (2 ** (len(lines)))
        line = ""
        for val in current_vals:
            line += val.center(spacing)
        lines.append(line)
        level = next_level

    for line in lines:
        print(line.rstrip())

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
