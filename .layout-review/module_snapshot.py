from pathlib import Path
import json,shutil
from kipy import KiCad
k=KiCad();assert k.check_version();b=k.get_board();fs=b.get_footprints();ps=b.get_pads();bb=b.get_item_bounding_box(fs)
assert len(fs)==532 and not any(f.locked for f in fs)
assert len(b.get_tracks())==len(b.get_vias())==len(b.get_zones())==len(b.get_shapes())==0
rows=[]
for f,v in zip(fs,bb):
 rows.append(dict(ref=f.reference_field.text.value,id=f.id.value,position=[f.position.x/1e6,f.position.y/1e6],angle=f.orientation.degrees,layer=f.layer,locked=f.locked,bbox=[v.pos.x/1e6,v.pos.y/1e6,v.size.x/1e6,v.size.y/1e6],pads=[dict(number=p.number,id=p.id.value,position=[p.position.x/1e6,p.position.y/1e6],net=p.net.name) for p in ps if p.parent==f.id]))
Path('.layout-review/module-reuse-before.json').write_text(json.dumps(dict(footprints=rows,layers=b.get_copper_layer_count()),indent=2))
b.save();shutil.copy2('GD32F5_FOC.kicad_pcb','.layout-review/module-reuse-before.kicad_pcb')
print('Snapshot saved',len(rows),sum(len(r['pads']) for r in rows))
