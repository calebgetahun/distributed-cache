"""
Benchmark the single-threaded TCP cache server using a single client connection.
This script issues a mix of GET and PUT requests and measures total throughput
as well as p50, p95, and p99 request latency.

"""

import socket
import time

HOST = "127.0.0.1"
PORT = 9000

OPS = 50_000     # total operations to send
KEYSPACE = 10_000   # number of rotating keys
READ_RATIO = 0.5    # 50% GET, 50% PUT

def send_line(sock: socket.socket, line: str) -> None:
    sock.sendall(line.encode("utf-8") + b"\n")


def recv_line(sock: socket.socket) -> str:
    """Read exactly one '\\n'-terminated line from socket."""
    buf = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            raise ConnectionError("Server closed connection")
        buf += chunk
        if b"\n" in buf:
            line, rest = buf.split(b"\n", 1)
            return line.decode("utf-8", errors="replace").strip()


def main():
    latencies = []

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    print(f"--- Single-Client TCP Benchmark ---")
    print(f"Server: {HOST}:{PORT}")
    print(f"Ops: {OPS:,}")
    print(f"Keyspace: {KEYSPACE:,}")
    print(f"GET/PUT ratio: {READ_RATIO*100:.0f}% / {100-READ_RATIO*100:.0f}%\n")

    start_total = time.perf_counter()

    for i in range(OPS):
        key = f"key{i % KEYSPACE}"
        value = "x" * 32  # 32-byte payload

        # Select GET or PUT based on READ_RATIO
        is_get = (i % 100) < (READ_RATIO * 100)
        if is_get:
            cmd = f"GET {key}"
        else:
            cmd = f"PUT {key} {value}"

        t0 = time.perf_counter()
        send_line(s, cmd)
        _ = recv_line(s)
        t1 = time.perf_counter()

        latencies.append((t1 - t0) * 1000.0)  # milliseconds

    end_total = time.perf_counter()
    s.close()

    duration = end_total - start_total
    ops_sec = OPS / duration

    print(f"Total time: {duration:.3f}s")
    print(f"Throughput: {ops_sec:,.0f} ops/sec")

    # Latency distribution
    lat_sorted = sorted(latencies)
    len_latencies = len(lat_sorted)
    p50 = lat_sorted[int(0.50 * len_latencies)]
    p95 = lat_sorted[int(0.95 * len_latencies)]
    p99 = lat_sorted[int(0.99 * len_latencies)]

    print("\nLatency (ms):")
    print(f"  p50 = {p50:.3f}")
    print(f"  p95 = {p95:.3f}")
    print(f"  p99 = {p99:.3f}")

if __name__ == "__main__":
    main()
