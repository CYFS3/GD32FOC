import json
from pathlib import Path
from kipy import KiCad
from kipy.geometry import Vector2
k=KiCad();k.check_version();b=k.get_board();fs=[f for f in b.get_footprints() if f.reference_field.text.value in ['CN27','CN1027']];assert len(fs)==2;c=b.begin_commit()
for f in fs:f.position=Vector2.from_xy_mm(f.position.x/1e6-.1,f.position.y/1e6+.1)
b.update_items(fs);b.push_commit(c,'Increase paired source testpoint clearance by 0.1 mm');b.save()
p=Path('.layout-review/module-reuse-plan-final.json');d=json.loads(p.read_text());
for r in ['CN27','CN1027']:d['placements'][r]['x_mm']-=.1;d['placements'][r]['y_mm']+=.1
d['local_clearance_exceptions'].append(dict(m1_ref='CN27',m2_ref='CN1027',delta_mm=[-.1,.1],reason='DRC source shunt pad to enlarged testpoint clearance 0.1846mm; paired outward correction'))
p.write_text(json.dumps(d,indent=2));print('Saved paired CN27/CN1027 offset (-.1,+.1)')
