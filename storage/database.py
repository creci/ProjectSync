from __future__ import annotations
import sqlite3, threading, time
from pathlib import Path
from core.models import FileRecord

SCHEMA="""
CREATE TABLE IF NOT EXISTS files(relative_path TEXT PRIMARY KEY, local_size INTEGER, local_mtime_ns INTEGER, local_hash TEXT, upstream_size INTEGER, upstream_mtime_ns INTEGER, upstream_hash TEXT, baseline_hash TEXT, reviewed_upstream_hash TEXT, status TEXT, last_scan REAL);
CREATE INDEX IF NOT EXISTS idx_files_status ON files(status);
"""
class Database:
    def __init__(self,path:Path):
        path.parent.mkdir(parents=True,exist_ok=True); self.path=path; self.lock=threading.RLock(); self._init()
    def connect(self):
        c=sqlite3.connect(self.path,timeout=30); c.execute('PRAGMA journal_mode=WAL'); c.execute('PRAGMA synchronous=NORMAL'); return c
    def _init(self):
        with self.connect() as c: c.executescript(SCHEMA)
    def cached(self, rel:str):
        with self.connect() as c:
            r=c.execute('SELECT local_size,local_mtime_ns,local_hash,upstream_size,upstream_mtime_ns,upstream_hash,baseline_hash,reviewed_upstream_hash,status FROM files WHERE relative_path=?',(rel,)).fetchone()
        return r
    def upsert_many(self, records:list[FileRecord]):
        rows=[(r.relative_path,r.local.size,r.local.mtime_ns,r.local.sha256,r.upstream.size,r.upstream.mtime_ns,r.upstream.sha256,r.baseline_hash,r.reviewed_upstream_hash,r.status.value,time.time()) for r in records]
        with self.connect() as c: c.executemany('INSERT INTO files VALUES(?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(relative_path) DO UPDATE SET local_size=excluded.local_size,local_mtime_ns=excluded.local_mtime_ns,local_hash=excluded.local_hash,upstream_size=excluded.upstream_size,upstream_mtime_ns=excluded.upstream_mtime_ns,upstream_hash=excluded.upstream_hash,baseline_hash=COALESCE(files.baseline_hash,excluded.baseline_hash),reviewed_upstream_hash=files.reviewed_upstream_hash,status=excluded.status,last_scan=excluded.last_scan',rows)
    def set_baseline(self, rel:str, h:str|None):
        with self.connect() as c: c.execute('UPDATE files SET baseline_hash=? WHERE relative_path=?',(h,rel))
    def set_reviewed(self, rel:str, h:str|None):
        with self.connect() as c: c.execute('UPDATE files SET reviewed_upstream_hash=? WHERE relative_path=?',(h,rel))
