from kipy import KiCad
from kipy.geometry import Vector2,Angle
from pathlib import Path
import json,math
k=KiCad();assert k.check_version();b=k.get_board();fs=b.get_footprints();pads=b.get_pads();bb=b.get_item_bounding_box(fs);F={f.reference_field.text.value:f for f in fs};B={f.reference_field.text.value:(z.pos.x/1e6,z.pos.y/1e6,(z.pos.x+z.size.x)/1e6,(z.pos.y+z.size.y)/1e6) for f,z in zip(fs,bb)}
def xy(p):return p.x/1e6,p.y/1e6
def rot(x,y,a):t=math.radians(a);return x*math.cos(t)+y*math.sin(t),-x*math.sin(t)+y*math.cos(t)
def hit(a,c,g=.35):return a[0]<c[2]+g and a[2]+g>c[0] and a[1]<c[3]+g and a[3]+g>c[1]
def p(r,n):return next(q for q in pads if q.parent==F[r].id and q.number==str(n))
refs=[('C200','U1',11),('C201','U1',28),('C202','U1',50),('C203','U1',75),('C204','U1',100),('C212','U1',6),('C206','U1',22),('C208','U1',21),('C207','U1',22),('C213','U1',21),('C210','Y200',1),('C211','Y200',3),('C214','Y201',1),('C215','Y201',2)]
occupied={r:z for r,z in B.items() if r not in [v[0] for v in refs]};plans={}
for r,ar,pn in refs:
 f=F[r];ox,oy=xy(f.position);oldangle=f.orientation.degrees;anchor=p(ar,pn);tx,ty=xy(anchor.position);sp=next(q for q in pads if q.parent==f.id and q.net.name==anchor.net.name);sx,sy=xy(sp.position);opts=[]
 for a in [0,90,180,270]:
  dx,dy=rot(sx-ox,sy-oy,a-oldangle);corners=[rot(x-ox,y-oy,a-oldangle) for x in [B[r][0],B[r][2]] for y in [B[r][1],B[r][3]]]
  for ix in range(-40,41):
   for iy in range(-40,41):
    x=tx+ix*.25;y=ty+iy*.25;dist=math.hypot(x+dx-tx,y+dy-ty);opts.append((dist,x,y,a,corners))
 opts.sort(key=lambda z:z[0]);best=None
 for dist,x,y,a,cs in opts:
  z=(x+min(c[0] for c in cs),y+min(c[1] for c in cs),x+max(c[0] for c in cs),y+max(c[1] for c in cs))
  if z[0]<60 or z[2]>112 or z[1]<77 or z[3]>113:continue
  if not any(hit(z,v) for v in occupied.values()):best=(x,y,a,dist,z);break
 assert best,r
 x,y,a,dist,z=best;plans[r]=(x,y,a);occupied[r]=z;print(r,'to',ar,pn,round(dist,3),flush=True)
sig=sorted((str(q.id),str(q.parent),q.number,q.net.name) for q in pads);commit=b.begin_commit()
try:
 changed=[]
 for r,(x,y,a) in plans.items():f=F[r];f.position=Vector2.from_xy_mm(x,y);f.orientation=Angle.from_degrees(a);changed.append(f)
 assert len(b.update_items(changed))==len(changed)
 fresh=b.get_footprints();assert len(fresh)==532;assert sig==sorted((str(q.id),str(q.parent),q.number,q.net.name) for q in b.get_pads())
 boxes=b.get_item_bounding_box(fresh);boxes=[(v.pos.x/1e6,v.pos.y/1e6,(v.pos.x+v.size.x)/1e6,(v.pos.y+v.size.y)/1e6) for v in boxes];assert not any(hit(v,w,0) for i,v in enumerate(boxes) for w in boxes[i+1:])
 b.push_commit(commit,'Refine MCU decoupling and oscillator load capacitors')
except Exception:b.drop_commit(commit);raise
b.save()
for file in ['live-after.json','placement-coordinates.json']:
 path=Path('.layout-review')/file;data=json.loads(path.read_text())
 for r,(x,y,a) in plans.items():data['placements'][r].update(x_mm=x,y_mm=y,rotation_deg=a)
 path.write_text(json.dumps(data,indent=2))
print('Saved capacitor refinement, no actual bbox overlap, net identities unchanged')
