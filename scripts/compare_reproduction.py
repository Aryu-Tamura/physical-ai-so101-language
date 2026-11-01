"""Compare all recorded physical trajectories in an independently checked-out copy."""
import argparse,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--copy',required=True);a=p.parse_args();other=Path(a.copy)
results={}
for source,dest in [('evaluation','reproduced'),('recovery','reproduced_recovery')]:
 original=ROOT/'outputs'/source;repeated=other/'outputs'/dest
 assert json.loads((original/'summary.json').read_text())==json.loads((repeated/'summary.json').read_text())
 files=sorted((original/'traces').glob('*.json'));assert len(files)==len(list((repeated/'traces').glob('*.json')))
 for f in files:
  assert f.read_bytes()==(repeated/'traces'/f.name).read_bytes(),f.name
 results[source]={'summary_equal':True,'byte_identical_trajectories':len(files)}
(ROOT/'outputs/reproduction_check.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
