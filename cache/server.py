import socket
from typing import Optional

from .eviction import EvictionPolicy
from .base import Cache
from .factory import CacheFactory


def run_server(host: str = "127.0.0.1", port: int = 9000, capacity: int = 1000) -> None:
    """
    Start a TCP server on (host, port) using an in-memory cache.
    """
    cache = CacheFactory.create_cache(capacity=capacity, policy=EvictionPolicy.LRU, shards=1)


    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((host, port))
    server_sock.listen(5)

    print(f"[cache-server] Listening on {host}:{port} (capacity={capacity})")

    try:
        while True:
            client_sock, addr = server_sock.accept()
            print(f"[cache-server] Connection from {addr}")
            handle_client(client_sock, cache)
    finally:
        server_sock.close()


def handle_client(client_sock: socket.socket, cache: Cache[str, str]) -> None:
    """
    Handle a single client connection using a simple line-based text protocol.
    """
    buffer = b""

    with client_sock:
        while True:
            chunk = client_sock.recv(4096)
            if not chunk:
                # Client disconnected
                break

            buffer += chunk

            # Process all full lines currently in the buffer
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                line = line.strip()
                if not line:
                    continue

                cmd_line = line.decode("utf-8", errors="replace")
                response = process_command(cmd_line, cache)

                if response is None:
                    return

                client_sock.sendall(response.encode("utf-8") + b"\n")

def process_command(line: str, cache: Cache[str, str]) -> Optional[str]:
    """
    Parse and execute a single command line against the cache.
    Returns a string response or None to close connection.
    """
    parts = line.split()
    if not parts:
        return "ERR empty_command"

    cmd = parts[0].upper()

    if cmd == "GET":
        if len(parts) != 2:
            return "ERR usage: GET key"
        key = parts[1]
        val = cache.get(key)
        return f"VALUE {val}" if val is not None else "NOT_FOUND"

    if cmd == "PUT":
        if not (3 <= len(parts) <= 4):
            return "ERR usage: PUT key value [ttl]"

        key = parts[1]
        value = parts[2]

        ttl = None
        if len(parts) == 4:
            try:
                ttl = float(parts[3])
            except ValueError:
                return "ERR ttl must be numeric"

        cache.put(key, value, ttl)
        return "STORED"

    if cmd == "DEL":
        if len(parts) != 2:
            return "ERR usage: DEL key"
        key = parts[1]
        ok = cache.delete(key)
        return "DELETED" if ok else "NOT_FOUND"

    if cmd == "STATS":
        s = cache.get_stats()
        return (
            f"HITS {s.hits} "
            f"MISSES {s.misses} "
            f"EVICTIONS {s.evictions} "
            f"GETS {s.gets} "
            f"PUTS {s.puts}"
        )

    if cmd == "QUIT":
        # close connection
        return None

    return f"ERR unknown_command {cmd}"

if __name__ == "__main__":
    run_server()