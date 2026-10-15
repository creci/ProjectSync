from __future__ import annotations
import json
from dataclasses import dataclass, asdict, field
from pathlib import Path

@dataclass
class Profile:
    name:str='Default'; local_root:str=''; upstream_root:str=''; include:list[str]=field(default_factory=list); exclude:list[str]=field(default_factory=lambda:['.git/**','build/**','out/**']); show_new_upstream_files:bool=False
class ProfileStore:
    def __init__(self):
        self.dir=Path.home()/'.projectsync'; self.dir.mkdir(exist_ok=True); self.path=self.dir/'profiles.json'
    def load_all(self):
        if not self.path.exists(): return {'Default':Profile()}
        try:
            d=json.loads(self.path.read_text(encoding='utf-8')); return {k:Profile(**v) for k,v in d.items()}
        except Exception:return {'Default':Profile()}
    def save_all(self, ps): self.path.write_text(json.dumps({k:asdict(v) for k,v in ps.items()},indent=2),encoding='utf-8')
