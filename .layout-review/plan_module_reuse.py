from pathlib import Path
import json,math,collections
from reuse_geometry import rot,fit,bounds,hit,polygon_overlap
load=lambda p:json.loads(Path(p).read_text(encoding='utf8'))
D={f['ref']:f for f in load('.layout-review/module-reuse-before.json')['footprints']};F={f['ref']:f for f in load('.layout-review/module-flipped-geometry.json')};S={f['reference']:f for f in load('.layout-review/reference-coordinates.json')['FOC']['footprints']};M=load('.layout-review/foc-reuse-map.json');G=load('.layout-review/placement-groups.json');P=load('.layout-review/module-pad-polygons-before.json')
T={};fits={}
for row in M['rows']:
 r=row['m1_ref'];src=row['source_ref']
 if not src:continue
 pm=row.get('pad_number_mapping_current_to_source');pm=pm if isinstance(pm,dict) else None
 if r=='CN5':q=dict(x=S[src]['at'][0],y=S[src]['at'][1],angle=S[src]['rotation_deg'],max_pad_center_error_mm=None,origin_offset_mm=[0,0],matched_pins=0,functional_replacement=True)
 else:q=fit(F.get(r,D[r]),S[src],pm)
 fits[r]=q;T[r]=[q['x'],q['y'],q['angle']]
# New features do not perturb original reference geometry; dedicated peripheral shelf.
new=[row for row in M['rows'] if not row['source_ref']]
for i,row in enumerate(new):T[row['m1_ref']]=[146+(i%8)*5,138+(i//8)*5,0]
def bbox(r,t):
 f=F.get(r,D[r]);x,y,a=t;bx,by,w,h=f['bbox'];p=f['position'];pts=[rot((u-p[0],v-p[1]),a-f['angle']) for u in [bx,bx+w] for v in [by,by+h]];return [x+min(v[0] for v in pts),y+min(v[1] for v in pts),x+max(v[0] for v in pts),y+max(v[1] for v in pts)]
bbs=[bbox(r,t) for r,t in T.items()];minx=min(b[0] for b in bbs);miny=min(b[1] for b in bbs);maxx=max(b[2] for b in bbs);maxy=max(b[3] for b in bbs);shift=[10-minx,10-miny];pitch=round((maxx-minx+8)*1000)/1000
for r,t in T.items():t[0]+=shift[0];t[1]+=shift[1]
for row in M['rows']:T[row['m2_ref']]=[T[row['m1_ref']][0]+pitch,T[row['m1_ref']][1],T[row['m1_ref']][2]]
module_bottom=max(bbox(r,t)[3] for r,t in T.items());other=[r for r in D if r not in T];omin=min(D[r]['bbox'][1] for r in other);ody=module_bottom+12-omin
for r in other:T[r]=[D[r]['position'][0],D[r]['position'][1]+ody,D[r]['angle']]
# Native front copper outlines transformed; back-side capacitors are mirrored geometrically and excluded from front cross-component pairs.
idref={f['id']:r for r,f in D.items()};polys=[]
for p in P:
 r=idref[p['parent']];f=D[r];q=T[r];points=[]
 for pt in p['points']:
  local=rot((pt[0]-f['position'][0],pt[1]-f['position'][1]),-f['angle'])
  if r in F:local=(-local[0],local[1])
  v=rot(local,q[2]);points.append([q[0]+v[0],q[1]+v[1]])
 if points:polys.append(dict(ref=r,pin=p['number'],net=p['net'],layer='B.Cu' if r in F else 'F.Cu',points=points,bbox=bounds(points)))
coll=[]
for i,a in enumerate(polys):
 for b in polys[i+1:]:
  if a['ref']==b['ref'] or a['layer']!=b['layer'] or (a['net']==b['net'] and a['net']) or not hit(a['bbox'],b['bbox']):continue
  if polygon_overlap(a['points'],b['points']):coll.append([a['ref'],a['pin'],a['net'],b['ref'],b['pin'],b['net']])
boxcoll=[]
for i,row in enumerate(M['rows']):
 a=row['m1_ref']
 for row2 in M['rows'][i+1:]:
  b=row2['m1_ref']
  if (a in F)==(b in F) and hit(bbox(a,T[a]),bbox(b,T[b])):boxcoll.append([a,b])
result=dict(placements={r:dict(x_mm=t[0],y_mm=t[1],rotation_deg=t[2],layer='B.Cu' if r in F else 'F.Cu') for r,t in T.items()},pitch_mm=pitch,reference_translation_mm=shift,nonfoc_translation_mm=[0,ody],module_count=324,nonfoc_count=len(other),back_refs=sorted(F),fits=fits,source_bbox=[minx,miny,maxx,maxy],copper_overlaps=coll,module1_bbox_overlaps=boxcoll)
Path('.layout-review/module-reuse-plan.json').write_text(json.dumps(result,indent=2));print('pitch',pitch,'module bottom',module_bottom,'nonfocdy',ody,'copper pairs',len(coll),'bboxpairs',len(boxcoll));print('copper',coll);print('largest fits',sorted([(r,v['max_pad_center_error_mm']) for r,v in fits.items() if v['max_pad_center_error_mm'] is not None],key=lambda x:-x[1])[:10])
