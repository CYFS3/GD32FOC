from pathlib import Path
import json,math
from kipy import KiCad
from kipy.geometry import Vector2,Angle
from kipy.board_types import BoardLayer,PadType
from reuse_geometry import bounds,hit,polygon_overlap
load=lambda p:json.loads(Path(p).read_text(encoding='utf8'))
plan=load('.layout-review/power-integrated-plan.json');T=plan['placements'];M=load('.layout-review/foc-reuse-map.json');before=load('.layout-review/power-integrated-before.json');TP={r['ref'] for r in load('.layout-review/reference-testpoint-audit.json')['current_keystone']}
k=KiCad();assert k.check_version();b=k.get_board();fs=b.get_footprints();ps=b.get_pads();assert len(fs)==532 and not any(f.locked for f in fs)
sig=lambda ff,pp:(sorted((f.id.value,f.reference_field.text.value,f.locked) for f in ff),sorted((p.id.value,p.parent.value,p.number,p.net.name) for p in pp))
original=(sorted((f['id'],f['ref'],f['locked']) for f in before['footprints']),sorted((p['id'],f['id'],p['number'],p['net']) for f in before['footprints'] for p in f['pads']))
assert sig(fs,ps)==original
c=b.begin_commit()
try:
 for f in fs:
  q=T[f.reference_field.text.value];f.position=Vector2.from_xy_mm(q['x_mm'],q['y_mm']);f.orientation=Angle.from_degrees(q['rotation_deg'])
 assert len(b.update_items(fs))==532
 fresh=b.get_footprints();pads=b.get_pads();assert sig(fresh,pads)==original
 maxerr=max(max(abs(f.position.x/1e6-T[f.reference_field.text.value]['x_mm']),abs(f.position.y/1e6-T[f.reference_field.text.value]['y_mm'])) for f in fresh);assert maxerr<3e-6
 assert all(int(f.layer)==T[f.reference_field.text.value]['layer'] for f in fresh)
 b.push_commit(c,'Restore reference power-to-FOC geometry and duplicate second drive below')
except Exception:b.drop_commit(c);raise
fs=b.get_footprints();ps=b.get_pads();fd={f.reference_field.text.value:f for f in fs};assert sig(fs,ps)==original
pair=max(max(abs((fd[r['m2_ref']].position.x-fd[r['m1_ref']].position.x)/1e6),abs((fd[r['m2_ref']].position.y-fd[r['m1_ref']].position.y)/1e6-plan['pitch_mm'])) for r in M['rows']);assert pair<3e-6
centres=[]
for r in TP:
 f=fd[r];p=next(p for p in ps if p.parent==f.id);err=math.hypot(p.position.x-f.position.x,p.position.y-f.position.y);assert err<3
 assert p.pad_type==PadType.PT_SMD and p.padstack.drill.diameter.x==0 and list(p.padstack.layers)==[BoardLayer.BL_F_Cu,BoardLayer.BL_F_Mask]
 assert all(abs(cl.size.x-1270000)<=1 and abs(cl.size.y-1270000)<=1 for cl in p.padstack.copper_layers);centres.append(err)
# Validate all corrected 5 model instances and both sides.
libs={f['lib_id'] for f in load('.layout-review/module-smd-library-fixes.json')['files']};smd=[]
for f in fs:
 if str(f.definition.id) in libs:
  for p in f.definition.pads:assert p.pad_type==PadType.PT_SMD and p.padstack.drill.diameter.x==0 and len([x for x in p.padstack.layers if x in [BoardLayer.BL_F_Cu,BoardLayer.BL_B_Cu]])==1
  smd.append(f.reference_field.text.value)
b.save()
validation=dict(saved=True,count=532,pair_pitch_mm=plan['pitch_mm'],pair_error_mm=pair,source_translation_mm=plan['source_translation_mm'],position_error_mm=maxerr,testpoint_count=52,testpoint_max_center_error_nm=max(centres),corrected_smd_instances=len(smd),identity_and_net_preserved=True,back_count=sum(f.layer==BoardLayer.BL_B_Cu for f in fs),groups=[dict(id=g.id.value,count=len(g.items)) for g in b.get_groups()],bounds=plan['bounds'],control_groups=plan['groups'])
Path('.layout-review/power-integrated-validation.json').write_text(json.dumps(validation,indent=2));print('SAVED',validation)
# Read actual polygons; report conflicts without destroying source template geometry.
idref={f.id.value:f.reference_field.text.value for f in fs};overlap=[]
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
validation['native_copper_overlaps']=overlap;Path('.layout-review/power-integrated-validation.json').write_text(json.dumps(validation,indent=2));print('Actual different-net overlaps',overlap)
