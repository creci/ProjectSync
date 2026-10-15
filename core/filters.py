from __future__ import annotations
from pathlib import PurePosixPath

def norm_rel(p: str) -> str: return p.replace(chr(92), '/').lstrip('./')

def _match(path:str, pat:str)->bool:
    path=norm_rel(path); pat=norm_rel(pat)
    pp=PurePosixPath(path)
    return pp.match(pat) or (pat.startswith('**/') and pp.match(pat[3:]))

def included(path:str, includes:list[str], excludes:list[str])->bool:
    p=norm_rel(path)
    if includes and not any(_match(p,x) for x in includes): return False
    return not any(_match(p,x) for x in excludes)
