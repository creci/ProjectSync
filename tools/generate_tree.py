import argparse, pathlib
p=argparse.ArgumentParser();p.add_argument('root');p.add_argument('--count',type=int,default=10000);a=p.parse_args();r=pathlib.Path(a.root);r.mkdir(parents=True,exist_ok=True)
for i in range(a.count):
 d=r/f'd{i//1000:04d}';d.mkdir(exist_ok=True);(d/f'f{i:07d}.txt').write_text(f'file {i}\n')
print(f'created {a.count} files in {r}')
