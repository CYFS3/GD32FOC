import json
from pathlib import Path
from kipy import KiCad
from kipy.board_types import BoardLayer
k=KiCad();assert k.check_version();b=k.get_board();fs=b.get_footprints();m=json.loads(Path('.layout-review/foc-reuse-map.json').read_text(encoding='utf8'));refs={r[key] for r in m['rows'] if r.get('source_layer')=='B.Cu' for key in ['m1_ref','m2_ref']}
c=b.begin_commit()
try:
 flip=b.flip_items([f for f in fs if f.reference_field.text.value in refs]);assert len(flip)==18
 ps=b.get_pads();rows=[]
 for f in b.get_footprints():
  if f.reference_field.text.value not in refs:continue
  v=b.get_item_bounding_box(f);pads=[p for p in ps if p.parent==f.id]
  rows.append(dict(ref=f.reference_field.text.value,id=f.id.value,position=[f.position.x/1e6,f.position.y/1e6],angle=f.orientation.degrees,layer=f.layer,locked=f.locked,bbox=[v.pos.x/1e6,v.pos.y/1e6,v.size.x/1e6,v.size.y/1e6],pads=[dict(number=p.number,id=p.id.value,position=[p.position.x/1e6,p.position.y/1e6],net=p.net.name) for p in pads]))
 Path('.layout-review/module-flipped-geometry.json').write_text(json.dumps(rows))
 print('Public flip geometry sampled',len(rows),sorted(refs))
finally:b.drop_commit(c)
