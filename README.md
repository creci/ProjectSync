# ProjectSync

ProjectSync is a PySide6 desktop tool for reviewing a customized subset of a large upstream source tree. It uses relative-path mapping, SQLite metadata caching, bounded background scanning, SHA-256 verification, BASE/LOCAL/UPSTREAM status classification, on-demand text diffs, profiles, pause/cancel, and safe foundations for synchronization.

## Install
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux: source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Workflow
Choose Local and Upstream roots, save a profile, then Scan. Local files define the tracked set by default. Selecting a file calculates its unified diff on demand. Metadata/hashes are cached in `~/.projectsync/cache.db`, so unchanged files can reuse hashes on later scans.

## Architecture
`core/` contains scanning, comparison, hashing, diff and sync logic. `storage/` contains SQLite and profiles. `widgets/` contains the Qt model. `app/` owns UI orchestration. Filesystem work is performed outside the GUI thread and results are delivered in batches.

## BASE comparison
When a baseline hash exists: LOCAL==BASE and UPSTREAM!=BASE => upstream changed; LOCAL!=BASE and UPSTREAM==BASE => local changed; both changed => possible conflict; LOCAL==UPSTREAM => identical.

## Performance
Directory traversal uses `os.scandir`; hashing streams chunks; workers are bounded; UI receives batches; diffs are computed only when selected. Use `tools/generate_tree.py` to generate test trees.

## Tests
```bash
pytest -q
```

## PyInstaller
```bash
pip install pyinstaller
pyinstaller ProjectSync.spec
```
