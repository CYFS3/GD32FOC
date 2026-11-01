import json
from pathlib import Path
from kipy import KiCad
from kipy.board_types import Group
k=KiCad();assert k.check_version();b=k.get_board();assert not b.get_groups();fs={f.reference_field.text.value:f for f in b.get_footprints()};m=json.loads(Path('.layout-review/foc-reuse-map.json').read_text());c=b.begin_commit()
try:
 gs=[]
 for key in ['m1_ref','m2_ref']:
  g=Group();g.items=[fs[r[key]] for r in m['rows']];gs.append(g)
 out=b.create_items(gs);assert len(out)==2
 b.push_commit(c,'Group the two repeated FOC module assemblies')
except Exception:b.drop_commit(c);raise
b.save();fresh=b.get_groups();print([(g.id.value,len(g.items)) for g in fresh]);Path('.layout-review/module-reuse-groups.json').write_text(json.dumps([dict(module='M'+str(i+1),id=g.id.value,member_refs=[r['m1_ref' if i==0 else 'm2_ref'] for r in m['rows']]) for i,g in enumerate(out)],indent=2))
