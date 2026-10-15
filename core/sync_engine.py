from __future__ import annotations
import os, shutil, tempfile, time
from pathlib import Path

def atomic_copy(src:Path,dst:Path,backup_root:Path|None=None):
    if not src.is_file(): raise FileNotFoundError(src)
    dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists() and backup_root:
        backup_root.mkdir(parents=True,exist_ok=True); shutil.copy2(dst,backup_root/dst.name)
    fd,tmp=tempfile.mkstemp(prefix='.projectsync-',dir=dst.parent); os.close(fd)
    try:
        shutil.copy2(src,tmp); os.replace(tmp,dst)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
