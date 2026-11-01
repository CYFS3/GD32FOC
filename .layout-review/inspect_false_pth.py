import json
from pathlib import Path
from kipy import KiCad
k=KiCad();assert k.check_version();b=k.get_board();fs=b.get_footprints();ps=b.get_pads();M=json.loads(Path('.layout-review/foc-reuse-map.json').read_text(encoding='utf8'));rs={r[key] for r in M['rows'] for key in ['m1_ref','m2_ref']};d=[]
for f in fs:
 if f.reference_field.text.value not in rs:continue
 pp=[p for p in ps if p.parent==f.id and 0<p.padstack.drill.diameter.x<10000]
 if pp:d.append(dict(ref=f.reference_field.text.value,pads=[p.number for p in pp],pad_ids=[p.id.value for p in pp],drill_mm=[p.padstack.drill.diameter.x/1e6 for p in pp],definition=str(f.definition)))
Path('.layout-review/false-pth-candidates.json').write_text(json.dumps(d,indent=2));print(len(d));print([(r['ref'],r['pads']) for r in d]);print(d[0]['definition'][:400])
