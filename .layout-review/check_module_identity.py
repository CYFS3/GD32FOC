import json,math
from pathlib import Path
from kipy import KiCad
from reuse_geometry import rot
load=lambda p:json.loads(Path(p).read_text(encoding='utf8'))
k=KiCad();assert k.check_version();b=k.get_board();fs=b.get_footprints();ps=b.get_pads();old=load('.layout-review/module-reuse-before.json');plan=load('.layout-review/module-reuse-plan-final.json');M=load('.layout-review/foc-reuse-map.json');F={f['ref']:f for f in load('.layout-review/module-flipped-geometry.json')};D={f['ref']:f for f in old['footprints']}
assert sorted((f.id.value,f.reference_field.text.value,f.locked) for f in fs)==sorted((f['id'],f['ref'],f['locked']) for f in old['footprints'])
assert sorted((p.id.value,p.parent.value,p.number,p.net.name) for p in ps)==sorted((p['id'],f['id'],p['number'],p['net']) for f in old['footprints'] for p in f['pads'])
fd={f.reference_field.text.value:f for f in fs};angleerrors=[];paderrors=[]
for r,f in fd.items():
 q=plan['placements'][r];angleerrors.append(abs((f.orientation.degrees-q['rotation_deg']+180)%360-180));geom=F.get(r,D[r]);oldpads={p['id']:p for p in geom['pads']}
 for p in ps:
  if p.parent!=f.id:continue
  op=oldpads[p.id.value];v=rot((op['position'][0]-geom['position'][0],op['position'][1]-geom['position'][1]),q['rotation_deg']-geom['angle']);paderrors.append(math.hypot(p.position.x/1e6-q['x_mm']-v[0],p.position.y/1e6-q['y_mm']-v[1]))
assert max(angleerrors)<1e-6;assert max(paderrors)<.000003,max(paderrors)
v=load('.layout-review/module-reuse-validation.json');v.update(original_snapshot_identity_net_lock_comparison=True,max_angle_error_deg=max(angleerrors),max_actual_pad_transform_error_mm=max(paderrors),groups=2)
Path('.layout-review/module-reuse-validation.json').write_text(json.dumps(v,indent=2));print('original net+id verified; max angle',max(angleerrors),'pad transform',max(paderrors))
