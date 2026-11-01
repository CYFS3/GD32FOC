from pathlib import Path
import json,math,collections
from reuse_geometry import rot,bounds,hit,polygon_overlap
load=lambda p:json.loads(Path(p).read_text(encoding='utf8'))
plan=load('.layout-review/module-reuse-plan.json');D={f['ref']:f for f in load('.layout-review/module-reuse-before.json')['footprints']};P=load('.layout-review/module-pad-polygons-before.json');M=load('.layout-review/foc-reuse-map.json');T=plan['placements'];ids={f['id']:r for r,f in D.items()};pair={r['m1_ref']:r['m2_ref'] for r in M['rows']};back=set(plan['back_refs'])
layers=load('.layout-review/module-pad-layers.json')
corrected={pid for item in load('.layout-review/false-pth-candidates.json') for pid in item['pad_ids']}
raw=collections.defaultdict(list)
for p in P:raw[ids[p['parent']]].append(p)
def polys(r,x=None,y=None):
 f=D[r];q=T[r];x=q['x_mm'] if x is None else x;y=q['y_mm'] if y is None else y;result=[]
 for p in raw[r]:
  pts=[]
  for pt in p['points']:
   v=rot((pt[0]-f['position'][0],pt[1]-f['position'][1]),-f['angle'])
   if r in back:v=(-v[0],v[1])
   v=rot(v,q['rotation_deg']);pts.append([x+v[0],y+v[1]])
  result.append(dict(ref=r,pin=p['number'],net=p['net'],points=pts,bbox=bounds(pts),layer=q['layer'],both=(len(layers[p['id']]['layers'])>3 and p['id'] not in corrected)))
 return result
allpoly={r:polys(r) for r in T}
def conflicts(r,pp,margin=.2):
 out=[]
 for s,qq in allpoly.items():
  if s==r:continue
  for a in pp:
   for b in qq:
    if (a['layer']!=b['layer'] and not (a['both'] or b['both'])) or (a['net']==b['net'] and a['net']) or not hit(a['bbox'],b['bbox'],margin):continue
    if polygon_overlap(a['points'],b['points'],margin):out.append((r,a['pin'],s,b['pin']))
 return out
# Existing source compact test pads changed to real Keystone posts; minimal two-module paired shift only for clashes.
adjust=[]
for r in ['CN5','CN14','CN15','CN17','CN18','CN19','CN20','CN21','CN22','CN23','CN24','CN25','CN26','CN37','CN38','CN40']:
 old=(T[r]['x_mm'],T[r]['y_mm']);reason=conflicts(r,allpoly[r])
 if not reason:continue
 cand=sorted([(i*i+j*j,i*.1,j*.1) for i in range(-15,16) for j in range(-15,16)])
 for ds,dx,dy in cand:
  pp=polys(r,old[0]+dx,old[1]+dy)
  if conflicts(r,pp):continue
  r2=pair[r];pp2=polys(r2,T[r2]['x_mm']+dx,T[r2]['y_mm']+dy)
  if conflicts(r2,pp2):continue
  for ref,ppp in [(r,pp),(r2,pp2)]:T[ref]['x_mm']+=dx;T[ref]['y_mm']+=dy;allpoly[ref]=ppp
  adjust.append(dict(m1_ref=r,m2_ref=r2,delta_mm=[dx,dy],reason='Current package larger than original reference; avoid different-net pad overlap',original_conflicts=reason));break
 else:
  # Keep core exact; incompatible large post moves to explicitly documented peripheral shelf.
  for j in range(80):
   x=12+(j%12)*4;y=78+(j//12)*4;dx=x-old[0];dy=y-old[1];r2=pair[r]
   pp=polys(r,x,y);pp2=polys(r2,T[r2]['x_mm']+dx,T[r2]['y_mm']+dy)
   if conflicts(r,pp) or conflicts(r2,pp2):continue
   for ref,ppp in [(r,pp),(r2,pp2)]:T[ref]['x_mm']+=dx;T[ref]['y_mm']+=dy;allpoly[ref]=ppp
   adjust.append(dict(m1_ref=r,m2_ref=r2,delta_mm=[dx,dy],reason='Oversized through-hole post cannot clear both copper sides locally; paired peripheral shelf',original_conflicts=reason));break
  else:raise RuntimeError('No peripheral position '+r)
remaining=[]
for r in pair:
 for c in conflicts(r,allpoly[r],0):
  if c[0]<c[2]:remaining.append(c)
assert not remaining,remaining
plan['placements']=T;plan['local_clearance_exceptions']=adjust;plan['copper_overlaps_after_adjustment']=remaining
Path('.layout-review/module-reuse-plan-final.json').write_text(json.dumps(plan,indent=2));print('paired minimal shifts',len(adjust));print(adjust)
