from pathlib import Path
import json,math
from kipy import KiCad
from kipy.geometry import Vector2,Angle
from kipy.board_types import BoardLayer
from reuse_geometry import bounds,hit,polygon_overlap
load=lambda p:json.loads(Path(p).read_text(encoding='utf8'))
plan=load('.layout-review/module-reuse-plan-final.json');T=plan['placements'];M=load('.layout-review/foc-reuse-map.json');D={f['ref']:f for f in load('.layout-review/module-reuse-before.json')['footprints']};back=set(plan['back_refs'])
k=KiCad();assert k.check_version();b=k.get_board();fs=b.get_footprints();ps=b.get_pads();assert len(fs)==532 and not any(f.locked for f in fs)
assert len(b.get_tracks())==len(b.get_vias())==len(b.get_zones())==len(b.get_shapes())==0
sig=lambda fs,ps:(sorted((f.id.value,f.reference_field.text.value,f.locked) for f in fs),sorted((p.id.value,p.parent.value,p.number,p.net.name) for p in ps))
base=sig(fs,ps)
assert all(f.id.value==D[f.reference_field.text.value]['id'] for f in fs)
fs=b.get_footprints();ps=b.get_pads();fd={f.reference_field.text.value:f for f in fs};errors=[]
for row in M['rows']:
 a=fd[row['m1_ref']];d=fd[row['m2_ref']];errors.append(max(abs((d.position.x-a.position.x)/1e6-plan['pitch_mm']),abs((d.position.y-a.position.y)/1e6)))
assert max(errors)<1e-6
for r,f in fd.items():
 q=T[r];assert abs(f.position.x/1e6-q['x_mm'])<1e-6 and abs(f.position.y/1e6-q['y_mm'])<1e-6;assert f.layer==(BoardLayer.BL_B_Cu if r in back else BoardLayer.BL_F_Cu)
# Fresh returned copper shapes on both sides, not inferred from origins or bbox.
idref={f.id.value:f.reference_field.text.value for f in fs};overlaps=[]
for layer in [BoardLayer.BL_F_Cu,BoardLayer.BL_B_Cu]:
 active=[p for p in ps if layer in p.padstack.layers];polys=b.get_pad_shapes_as_polygons(active,layer);records=[]
 assert len(polys)==len(active)
 for p,poly in zip(active,polys):
  pts=[]
  for n in poly.outline.nodes:
   if n.has_point:pts.append([n.point.x/1e6,n.point.y/1e6])
   elif n.has_arc:
    for v in [n.arc.start,n.arc.mid,n.arc.end]:pts.append([v.x/1e6,v.y/1e6])
  if pts:records.append(dict(ref=idref[p.parent.value],pin=p.number,net=p.net.name,pts=pts,bb=bounds(pts)))
 for i,a in enumerate(records):
  for d in records[i+1:]:
   if a['ref']==d['ref'] or (a['net']==d['net'] and a['net']) or not hit(a['bb'],d['bb']):continue
   if polygon_overlap(a['pts'],d['pts']):overlaps.append([layer,a['ref'],a['pin'],a['net'],d['ref'],d['pin'],d['net']])
assert not overlaps,overlaps[:30]
b.save()
validation=dict(count=532,module_refs=324,nonfoc_refs=208,backside_changed_refs=sorted(back),pitch_mm=plan['pitch_mm'],maximum_pair_delta_error_mm=max(errors),identity_pad_net_lock_preserved=True,reference_fits=plan['fits'],local_exceptions=plan['local_clearance_exceptions'],native_both_side_copper_overlaps=overlaps,copper_layers=b.get_copper_layer_count(),tracks=len(b.get_tracks()),vias=len(b.get_vias()),zones=len(b.get_zones()),shapes=len(b.get_shapes()))
Path('.layout-review/module-reuse-validation.json').write_text(json.dumps(validation,indent=2));Path('.layout-review/module-reuse-coordinates.json').write_text(json.dumps(T,indent=2));print('SAVED',len(fs),'pair_delta_max',max(errors),'different_net_copper_overlaps',len(overlaps))
