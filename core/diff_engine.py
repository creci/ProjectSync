from __future__ import annotations
import difflib
from pathlib import Path

def read_text(path:Path, limit=20*1024*1024):
    if path.stat().st_size>limit:return None,'File too large for internal text diff'
    b=path.read_bytes()
    if b'\0' in b[:8192]:return None,'Binary file'
    for enc in ('utf-8-sig','utf-8','utf-16','cp1252'):
        try:return b.decode(enc).splitlines(),None
        except UnicodeDecodeError:pass
    return None,'Binary or unsupported encoding'

def unified(a:Path,b:Path,rel:str):
    aa,e1=read_text(a); bb,e2=read_text(b)
    if aa is None or bb is None:return e1 or e2 or 'Cannot diff'
    return '\n'.join(difflib.unified_diff(aa,bb,fromfile='LOCAL/'+rel,tofile='UPSTREAM/'+rel,lineterm=''))
