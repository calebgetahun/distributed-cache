import socket

from .cache_node import CacheNode, CacheNodeConfig
from .eviction import EvictionPolicy


def run_server(host: str = "127.0.0.1", port: int = 9000, capacity: int = 1000) -> None:
    """
    Start a TCP server on (host, port). All command logic lives in CacheNode.
    """

    # TEMP: hardcoded 2-node / 4-shard demo config.
    # Run one process on :9000 owning {0,1} and another on :9001 owning {2,3}.
    n_shards = 4
    cluster_map = {
        0: ("127.0.0.1", 9000),
        1: ("127.0.0.1", 9000),
        2: ("127.0.0.1", 9001),
        3: ("127.0.0.1", 9001),
    }

    if port == 9000:
        owned = {0, 1}
    elif port == 9001:
        owned = {2, 3}
    else:
        raise ValueError("For the demo, run on port 9000 or 9001")

    cfg = CacheNodeConfig(
        node_id=f"{host}:{port}",
        n_shards=n_shards,
        owned_shards=owned,
        cluster_map=cluster_map,
        capacity=capacity,
        policy=EvictionPolicy.LRU,
    )
    node = CacheNode(cfg)

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((host, port))
    server_sock.listen(5)

    print(f"[cache-server] Listening on {host}:{port} (capacity={capacity})")

    try:
        while True:
            client_sock, addr = server_sock.accept()
            print(f"[cache-server] Connection from {addr}")
            handle_client(client_sock, node)
    finally:
        server_sock.close()


def handle_client(client_sock: socket.socket, node: CacheNode) -> None:
    """
    Handle one TCP connection. Read lines, delegate to node.handle(), write response.
    """
    buffer = b""
    with client_sock:
        while True:
            chunk = client_sock.recv(4096)
            if not chunk:
                break
            buffer += chunk

            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                line = line.strip()
                if not line:
                    continue

                cmd_line = line.decode("utf-8", errors="replace")
                response = node.handle(cmd_line)

                if response is None:
                    # QUIT
                    return

                client_sock.sendall(response.encode("utf-8") + b"\n")


if __name__ == "__main__":
    run_server()