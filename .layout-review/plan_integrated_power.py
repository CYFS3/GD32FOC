from pathlib import Path
import json,math
from reuse_geometry import fit,rot,hit
load=lambda p:json.loads(Path(p).read_text(encoding='utf8'))
D={f['ref']:f for f in load('.layout-review/power-integrated-ready.json')['footprints']};S={f['reference']:f for f in load('.layout-review/reference-coordinates.json')['FOC']['footprints']};M=load('.layout-review/foc-reuse-map.json');P=load('.layout-review/power-reference-map.json');G=load('.layout-review/placement-groups.json');TP={r['ref'] for r in load('.layout-review/reference-testpoint-audit.json')['current_keystone']};old=load('.layout-review/module-reuse-plan-final.json');T={};fits={};shift=(-89.1235,-69.8475)
def mapped(r,src,pm=None):
 pm=pm if isinstance(pm,dict) else None
 if r in TP or r=='CN5':q=dict(x=S[src]['at'][0],y=S[src]['at'][1],angle=S[src]['rotation_deg'],max_pad_center_error_mm=0 if r in TP else None,origin_offset_mm=[0,0],matched_pins=1 if r in TP else 0)
 else:
  cur=D[r].copy();cur['pads']=[p for p in cur['pads'] if pm is None or p['number'] in pm];q=fit(cur,S[src],pm)
 fits[r]=q;T[r]=[q['x']+shift[0],q['y']+shift[1],q['angle']]
for row in M['rows']:
 if row['source_ref']:mapped(row['m1_ref'],row['source_ref'],row.get('pad_number_mapping_current_to_source'))
for row in P['rows']:mapped(row['current_ref'],row['source_ref'],row.get('current_to_source_pin_map'))
# Preserve only six-pin connector exception; all old testpoint departures are removed.
e=next(e for e in old['local_clearance_exceptions'] if e['m1_ref']=='CN5');T['CN5'][0]+=e['delta_mm'][0];T['CN5'][1]+=e['delta_mm'][1]
for i,row in enumerate([r for r in M['rows'] if not r['source_ref']]):T[row['m1_ref']]=[57+(i%8)*5,68+(i//8)*5,0]
def bbox(r,t):
 f=D[r];x,y,a=t;bx,by,w,h=f['bbox'];px,py=f['position'];pts=[rot((u-px,v-py),a-f['angle']) for u in [bx,bx+w] for v in [by,by+h]];return [x+min(v[0] for v in pts),y+min(v[1] for v in pts),x+max(v[0] for v in pts),y+max(v[1] for v in pts)]
def union(rr):
 bb=[bbox(r,T[r]) for r in rr];return [min(v[0] for v in bb),min(v[1] for v in bb),max(v[2] for v in bb),max(v[3] for v in bb)]
a=[r['m1_ref'] for r in M['rows']];ab=union(a);pitch=math.ceil((ab[3]-ab[1]+8)*2)/2
for row in M['rows']:
 x,y,ang=T[row['m1_ref']];T[row['m2_ref']]=[x,y+pitch,ang]
# Remaining whole functional groups: use source-adjacent lower-left space.
rest=set(D)-set(T);dest={'mcu':(10,77),'hslink':(10,108),'display_buttons':(43,151),'mcu_debug':(80,151)};groups={}
for group,v in G['groups'].items():
 rr=[r for r in v['refs'] if r in rest]
 if not rr:continue
 bb=[D[r]['bbox'] for r in rr];xmin=min(x[0] for x in bb);ymin=min(x[1] for x in bb)
 target=dest.get(group,(10,168));dx=target[0]-xmin;dy=target[1]-ymin
 for r in rr:T[r]=[D[r]['position'][0]+dx,D[r]['position'][1]+dy,D[r]['angle']]
 groups[group]=dict(refs=rr,delta_mm=[dx,dy],bbox=union(rr))
assert len(T)==532
out=dict(placements={r:dict(x_mm=q[0],y_mm=q[1],rotation_deg=q[2],layer=D[r]['layer']) for r,q in T.items()},pitch_mm=pitch,source_translation_mm=shift,fits=fits,groups=groups,bounds=dict(M1=union(a),M2=union([r['m2_ref'] for r in M['rows']]),power=union([r['current_ref'] for r in P['rows']])))
Path('.layout-review/power-integrated-plan.json').write_text(json.dumps(out,indent=2));print('pitch',pitch,'bounds',out['bounds']);print('groups',[(g,len(x['refs']),x['bbox']) for g,x in groups.items()]);print('power max residual',sorted([(r['current_ref'],fits[r['current_ref']]['max_pad_center_error_mm']) for r in P['rows']],key=lambda x:-(x[1] or 0))[:12])
