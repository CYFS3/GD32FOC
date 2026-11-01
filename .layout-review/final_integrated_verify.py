from pathlib import Path
import json,math
from kipy import KiCad
from kipy.board_types import BoardLayer
from reuse_geometry import bounds,hit,polygon_overlap
load=lambda p:json.loads(Path(p).read_text(encoding='utf8'))
k=KiCad();assert k.check_version();b=k.get_board();fs=b.get_footprints();TP={r['ref'] for r in load('.layout-review/reference-testpoint-audit.json')['current_keystone']};smdstyle=next(f.attributes.mounting_style for f in fs if f.reference_field.text.value=='C200');sel=[f for f in fs if f.reference_field.text.value in TP|{'D22'}];c=b.begin_commit()
for f in sel:f.attributes.mounting_style=smdstyle
assert len(b.update_items(sel))==53;b.push_commit(c,'Set reference testpad and TVS mounting metadata to SMD');b.save()
fs=b.get_footprints();ps=b.get_pads();idref={f.id.value:f.reference_field.text.value for f in fs};overlap=[]
for layer in [BoardLayer.BL_F_Cu,BoardLayer.BL_B_Cu]:
 active=[p for p in ps if layer in p.padstack.layers];polys=b.get_pad_shapes_as_polygons(active,layer);records=[]
 for p,poly in zip(active,polys):
  pts=[]
  for n in poly.outline.nodes:
   if n.has_point:pts.append([n.point.x/1e6,n.point.y/1e6])
   elif n.has_arc:
    for v in [n.arc.start,n.arc.mid,n.arc.end]:pts.append([v.x/1e6,v.y/1e6])
  if pts:records.append(dict(ref=idref[p.parent.value],pin=p.number,net=p.net.name,points=pts,bb=bounds(pts)))
 for i,a in enumerate(records):
  for d in records[i+1:]:
   if a['ref']==d['ref'] or (a['net']==d['net'] and a['net']) or not hit(a['bb'],d['bb']):continue
   if polygon_overlap(a['points'],d['points']):overlap.append([int(layer),a['ref'],a['pin'],a['net'],d['ref'],d['pin'],d['net']])
v=load('.layout-review/power-integrated-validation.json');v['native_copper_overlaps']=overlap;v['power_exception']=dict(ref='D22',delta_mm=[1,0],SMD_corrected=True);v['testpoint_public_metadata_limitations']='Original footprint definition descr/tags not exposed by public SDK; no Manufacturer Part property remains in saved testpoint block.';Path('.layout-review/power-integrated-validation.json').write_text(json.dumps(v,indent=2));print('FINAL saved; overlaps',overlap)
