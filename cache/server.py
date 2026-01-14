import socket
import argparse
import json
import sys

from .cache_node import CacheNode, CacheNodeConfig
from .eviction import EvictionPolicy
from typing import Tuple

def load_json_file(path):
    try: 
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"FATAL: config file not found: {path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"FATAL: invalid json in {path}: {e}", file=sys.stderr)
        sys.exit(1)

def parse_args():
    parser = argparse.ArgumentParser(description="Distributed cache node")

    parser.add_argument("--cluster-config", required=True, help="Path to cluster config JSON (global)")
    parser.add_argument("--node-config", required=True, help="Path to node config JSON (this node)")

    return parser.parse_args()

def build_config(cluster_json, node_json) -> Tuple[CacheNodeConfig, str, int]:
    n_shards = int(cluster_json["n_shards"])
    cluster_map = {int(k): (v[0], int(v[1])) for k, v in cluster_json["cluster_map"].items()}

    host = node_json["host"]
    port = int(node_json["port"])
    node_id = node_json.get("node_id", f"{host}:{port}")
    owned_shards = set(map(int, node_json["owned_shards"]))
    capacity = int(node_json["capacity"])

    if set(cluster_map.keys()) != set(range(n_shards)):
        raise ValueError("cluster_map must contain every shard id in [0, n_shards)")

    try:
        policy = EvictionPolicy[node_json.get("policy", "LRU")]
    except KeyError:
        raise ValueError(f"Unknown eviction policy: {node_json.get('policy')}")

    if any(s < 0 or s >= n_shards for s in owned_shards):
        raise ValueError("owned_shards contains shard id outside [0, n_shards)")
    
    for shard_id in owned_shards:
        if cluster_map.get(shard_id) != (host, port):
            raise ValueError(f"config mismatch: shard {shard_id} is owned but cluster_map says {cluster_map.get(shard_id)} not {(host, port)}")

    cfg = CacheNodeConfig(
        node_id=node_id,
        host=host,
        port=port,
        n_shards=n_shards,
        owned_shards=owned_shards,
        cluster_map=cluster_map,
        capacity=capacity,
        policy=policy
    )

    return cfg, host, port

def run_server() -> None:
    """
    Start a TCP server on (host, port). All command logic lives in CacheNode.
    """

    args = parse_args()

    cluster_config = args.cluster_config
    node_config = args.node_config

    cluster_json = load_json_file(cluster_config)
    node_json = load_json_file(node_config)

    try:
        cfg, host, port = build_config(cluster_json, node_json)
    except (KeyError, ValueError) as e:
        print(f"FATAL: invalid config: {e}", file=sys.stderr)
        sys.exit(1)
    
    node = CacheNode(cfg)

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_sock.bind((host, port))
        server_sock.listen(5)
    except OSError as e:
        print(f"FATAL: could not bind to {host}:{port}: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"[cache-server] Listening on {host}:{port} (capacity={cfg.capacity})")

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