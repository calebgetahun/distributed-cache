from dataclasses import dataclass
from typing import Any, Hashable, Optional

@dataclass
class DLLNode:
    key: Optional[Hashable] = None
    val: Any = None
    prev: Optional["DLLNode"] = None
    next: Optional["DLLNode"] = None
    expiration_time: Optional[float] = None  # UNIX timestamp