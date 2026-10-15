from __future__ import annotations
import os, threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.models import FileMeta, FileRecord
from core.hashing import sha256_file
from core.filters import included, norm_rel
from core.comparator import status_for

def walk(root:Path, inc:list[str], exc:list[str], cancel:threading.Event, pause:threading.Event):
    stack=[root]
    while stack and not cancel.is_set():
        pause.wait(); d=stack.pop()
        try:
            with os.scandir(d) as it:
                for e in it:
                    if cancel.is_set(): return
                    p=Path(e.path); rel=norm_rel(str(p.relative_to(root)))
                    if e.is_dir(follow_symlinks=False):
                        if not any(rel==x.rstrip('/**') or rel.startswith(x.rstrip('/**')+'/') for x in exc if x.endswith('/**')): stack.append(p)
                    elif e.is_file(follow_symlinks=False) and included(rel,inc,exc): yield rel
        except (PermissionError,FileNotFoundError,OSError): continue

def meta(path:Path)->FileMeta:
    try:
        s=path.stat(); return FileMeta(True,s.st_size,s.st_mtime_ns,None)
    except OSError:return FileMeta()

def scan(local_root:Path, up_root:Path, inc:list[str], exc:list[str], show_new:bool, db, cancel, pause, workers=8, batch_cb=None, progress_cb=None):
    rels=list(walk(local_root,inc,exc,cancel,pause))
    if show_new:
        tracked_dirs={str(Path(r).parent).replace('\\','/') for r in rels}
        for r in walk(up_root,inc,exc,cancel,pause):
            if str(Path(r).parent).replace('\\','/') in tracked_dirs and r not in rels: rels.append(r)
    def one(rel):
        pause.wait(); lp=local_root/rel; up=up_root/rel; lm=meta(lp); um=meta(up); c=db.cached(rel); base=reviewed=None
        if c: base,reviewed=c[6],c[7]
        if lm.exists:
            if c and c[0]==lm.size and c[1]==lm.mtime_ns and c[2]: lm.sha256=c[2]
            else: lm.sha256=sha256_file(lp)
        if um.exists:
            if c and c[3]==um.size and c[4]==um.mtime_ns and c[5]: um.sha256=c[5]
            else: um.sha256=sha256_file(up)
        return FileRecord(rel,lm,um,base,reviewed,status_for(lm,um,base,reviewed))
    done=0; batch=[]
    with ThreadPoolExecutor(max_workers=max(1,workers),thread_name_prefix='scan') as ex:
        futs=[ex.submit(one,r) for r in rels]
        for f in as_completed(futs):
            if cancel.is_set(): break
            try: batch.append(f.result())
            except Exception: pass
            done+=1
            if len(batch)>=200:
                db.upsert_many(batch); batch_cb and batch_cb(batch[:]); batch.clear()
            if progress_cb and done%100==0: progress_cb(done,len(rels))
    if batch: db.upsert_many(batch); batch_cb and batch_cb(batch[:])
    progress_cb and progress_cb(done,len(rels))
