from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class FileStatus(str, Enum):
    IDENTICAL="identical"; UPSTREAM_CHANGED="upstream_changed"; LOCAL_CHANGED="local_changed"
    POSSIBLE_CONFLICT="possible_conflict"; LOCAL_ONLY="local_only"; UPSTREAM_ONLY="upstream_only"
    MISSING_UPSTREAM="missing_upstream"; IGNORED="ignored"; REVIEWED="reviewed"

@dataclass(slots=True)
class FileMeta:
    exists: bool=False; size: int=0; mtime_ns: int=0; sha256: str|None=None

@dataclass(slots=True)
class FileRecord:
    relative_path: str
    local: FileMeta
    upstream: FileMeta
    baseline_hash: str|None=None
    reviewed_upstream_hash: str|None=None
    status: FileStatus=FileStatus.IDENTICAL
    error: str|None=None
