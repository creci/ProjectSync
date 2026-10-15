from __future__ import annotations
from core.models import FileMeta, FileStatus

def status_for(local:FileMeta, up:FileMeta, base:str|None, reviewed:str|None)->FileStatus:
    if not local.exists and up.exists:return FileStatus.UPSTREAM_ONLY
    if local.exists and not up.exists:return FileStatus.MISSING_UPSTREAM
    if not local.exists and not up.exists:return FileStatus.LOCAL_ONLY
    if local.sha256 == up.sha256:return FileStatus.IDENTICAL
    if reviewed and up.sha256==reviewed:return FileStatus.REVIEWED
    if base:
        lc=local.sha256!=base; uc=up.sha256!=base
        if not lc and uc:return FileStatus.UPSTREAM_CHANGED
        if lc and not uc:return FileStatus.LOCAL_CHANGED
        if lc and uc:return FileStatus.POSSIBLE_CONFLICT
    return FileStatus.POSSIBLE_CONFLICT
