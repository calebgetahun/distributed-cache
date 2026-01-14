from dataclasses import dataclass
from typing import Dict, Optional, Set, Tuple
import zlib

from .base import Cache, CacheStats
from .eviction import EvictionPolicy
from .factory import CacheFactory

Address = Tuple[str, int] # (host, port)

@dataclass(frozen=True)
class CacheNodeConfig:
    node_id: str
    n_shards: int
    owned_shards: Set[int]
    cluster_map: Dict[int, Address]
    capacity: int
    policy: EvictionPolicy

class CacheNode:
    def __init__(self, cfg: CacheNodeConfig):
        self.cfg = cfg
        self._validate_cfg()
        self.local_shards: Dict[int, Cache[str, str]] = CacheFactory.create_local_shards(
            total_capacity=self.cfg.capacity, 
            policy=self.cfg.policy, 
            shard_ids=sorted(self.cfg.owned_shards),
        )

    def _validate_cfg(self) -> None:
        if self.cfg.n_shards <= 0:
            raise ValueError("n_shards must be > 0")
        if not self.cfg.owned_shards:
            raise ValueError("owned_shards cannot be empty")
        if any(s < 0 or s >= self.cfg.n_shards for s in self.cfg.owned_shards):
            raise ValueError("owned_shards contains invalid shard id")
        if set(self.cfg.cluster_map.keys()) != set(range(self.cfg.n_shards)):
            raise ValueError("cluster_map must contain every shard_id in [0, n_shards)")

    def shard_id(self, key: str) -> int:
        # Stable across processes/machines
        return zlib.crc32(key.encode("utf-8")) % self.cfg.n_shards

    def _addr_for(self, shard_id: int) -> Address:
        return self.cfg.cluster_map[shard_id]

    def _moved(self, shard_id: int) -> str:
        host, port = self._addr_for(shard_id)
        return f"MOVED {shard_id} {host}:{port}"

    def _sum_stats(self) -> CacheStats:
        total = CacheStats()
        for c in self.local_shards.values():
            s = c.get_stats()
            total.hits += s.hits
            total.misses += s.misses
            total.evictions += s.evictions
            total.gets += s.gets
            total.puts += s.puts
        return total

    def handle(self, line: str) -> Optional[str]:
        """
        Parse and execute one command. Returns a response string,
        or None to close the connection (QUIT).
        """
        parts = line.split()
        if not parts:
            return "ERR empty_command"

        cmd = parts[0].upper()

        # Non-keyed commands
        if cmd == "QUIT":
            return None

        if cmd == "STATS":
            s = self._sum_stats()
            return f"HITS {s.hits} MISSES {s.misses} EVICTIONS {s.evictions} GETS {s.gets} PUTS {s.puts}"

        # Keyed commands: enforce ownership via MOVED
        if cmd == "GET":
            if len(parts) != 2:
                return "ERR usage: GET key"
            key = parts[1]
            sid = self.shard_id(key)
            if sid not in self.cfg.owned_shards:
                return self._moved(sid)
            val = self.local_shards[sid].get(key)
            return f"VALUE {val}" if val is not None else "NOT_FOUND"

        if cmd == "PUT":
            if not (3 <= len(parts) <= 4):
                return "ERR usage: PUT key value [ttl]"
            key, value = parts[1], parts[2]
            sid = self.shard_id(key)
            if sid not in self.cfg.owned_shards:
                return self._moved(sid)

            ttl = None
            if len(parts) == 4:
                try:
                    ttl = float(parts[3])
                except ValueError:
                    return "ERR ttl must be numeric"

            self.local_shards[sid].put(key, value, ttl)
            return "STORED"

        if cmd == "DEL":
            if len(parts) != 2:
                return "ERR usage: DEL key"
            key = parts[1]
            sid = self.shard_id(key)
            if sid not in self.cfg.owned_shards:
                return self._moved(sid)
            ok = self.local_shards[sid].delete(key)
            return "DELETED" if ok else "NOT_FOUND"

        return f"ERR unknown_command {cmd}"