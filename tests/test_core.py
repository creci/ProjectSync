from pathlib import Path
from core.filters import included,norm_rel
from core.hashing import sha256_file
from core.models import FileMeta,FileStatus
from core.comparator import status_for

def test_filters(): assert included('src/a.cpp',['src/**'],['build/**']); assert not included('build/a.o',[],['build/**'])
def test_hash(tmp_path):
 p=tmp_path/'a';p.write_text('abc');assert sha256_file(p)=='ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
def test_status():
 a=FileMeta(True,1,1,'a');b=FileMeta(True,1,1,'b');assert status_for(a,b,'a',None)==FileStatus.UPSTREAM_CHANGED
