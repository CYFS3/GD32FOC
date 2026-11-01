from pathlib import Path
import json,math,collections,time
from kipy import KiCad
from kipy.geometry import Vector2,Angle
S=json.loads(Path('.layout-review/live-before.json').read_text());P=json.loads(Path('.layout-review/placement-groups.json').read_text())
D={f['ref']:f for f in S['footprints']};targets={};placed={};boxes={};notes=[]
def rot(x,y,a):
 t=math.radians(a);return (x*math.cos(t)+y*math.sin(t),-x*math.sin(t)+y*math.cos(t))
def box(r,x,y,a):
 f=D[r];bx,by,w,h=f['bbox'];px,py=f['position'];pts=[rot(u-px,v-py,a-f['angle']) for u in [bx,bx+w] for v in [by,by+h]]
 return (x+min(t[0] for t in pts),y+min(t[1] for t in pts),x+max(t[0] for t in pts),y+max(t[1] for t in pts))
def hit(a,b,gap=.35):return a[0]<b[2]+gap and a[2]+gap>b[0] and a[1]<b[3]+gap and a[3]+gap>b[1]
def padxy(r,p,x=None,y=None,a=None):
 f=D[r];q=next((q for q in f['pads'] if q['number']==str(p)),None)
 if q is None:return None
 if x is None:x,y,a=placed[r]
 dx,dy=rot(q['position'][0]-f['position'][0],q['position'][1]-f['position'][1],a-f['angle']);return x+dx,y+dy
regions={g:dict(v['rect_mm']) for g,v in P['groups'].items()}
for g in ['m1_sense','m2_sense']:regions[g]['y_max']=75
regions['analog_reference'].update(x_min=39,x_max=62,y_min=64,y_max=76)
regions['mcu_debug']['y_max']=120
# Permit all tightly linked MCU components around the LQFP.
regions['mcu'].update(x_min=62,x_max=112,y_min=77,y_max=113)
def inside(bb,reg):return bb[0]>=reg['x_min'] and bb[1]>=reg['y_min'] and bb[2]<=reg['x_max'] and bb[3]<=reg['y_max']
def place(r,target,angles=(0,90),reg=None,limit=70):
 if r in placed:return
 tx,ty=target;reg=reg or regions[P['ref_to_group'][r]]
 # Search radial 0.5mm lattice, closest to the electrical attraction target first.
 candidates=[]
 for a in angles:
  for ix in range(-limit,limit+1):
   for iy in range(-limit,limit+1):
    ds=ix*ix+iy*iy
    candidates.append((ds+.03*angles.index(a),tx+ix*.5,ty+iy*.5,a))
 candidates.sort(key=lambda z:z[0])
 for _,x,y,a in candidates:
  bb=box(r,x,y,a)
  if inside(bb,reg) and not any(hit(bb,b) for b in boxes.values()):
   placed[r]=(round(x,4),round(y,4),a);boxes[r]=bb;return
 # Soft regions may expand locally, whole envelope still enforced.
 whole=dict(x_min=0,y_min=0,x_max=170,y_max=120)
 for _,x,y,a in candidates:
  bb=box(r,x,y,a)
  if inside(bb,whole) and not any(hit(bb,b) for b in boxes.values()):
   placed[r]=(round(x,4),round(y,4),a);boxes[r]=bb;notes.append(f'{r}: expanded beyond nominal {P["ref_to_group"][r]} region');return
 raise RuntimeError('No free position '+r)
# Key mechanical and active anchors. Clocks get dedicated pad-based placement below.
keys=P['key_targets']; clocks={'Y200','Y201','X8002'}
order=sorted((r for r in keys if r not in clocks),key=lambda r:(0 if r in ['U1','USB8002','CN1','CN41','CN1041'] else 1,-D[r]['bbox'][2]*D[r]['bbox'][3]))
for r in order:
 t=keys[r];a=270 if r=='USB8002' else 0
 place(r,(t['x_mm'],t['y_mm']),(a,))
# MCU crystal and supply anchor pin coordinates are actual footprint pads.
for r,p,dx,dy,a in [('Y201',8,-4.2,-1,90),('Y200',12,-4.2,2,90),('C200',11,-1.8,0,0),('C201',28,0,2,90),('C202',50,0,2,90),('C203',75,2,0,0),('C204',100,0,-2,90),('C212',6,-2,-1,0),('C206',22,-2,1,0),('C208',21,-2,0,0),('C207',22,-4,2,0),('C213',21,-4,0,0)]:
 q=padxy('U1',p);place(r,(q[0]+dx,q[1]+dy),(a,))
for c,y,p in [('C214','Y201',1),('C215','Y201',2),('C210','Y200',1),('C211','Y200',3)]:
 q=padxy(y,p);place(c,(q[0]-2,q[1]),(0,90))
q=padxy('U8006',35);place('X8002',(q[0]+3,q[1]),(0,90))
# Known gate/boot/local clusters: anchor to actual relevant pin for nearest components.
cluster_refs=set()
for c in P['local_clusters']:
 ar=c.get('anchor_ref');rs=c['refs'];cid=c['id']
 if ar not in placed:continue
 q=placed[ar][:2]
 if 'gate_' in cid:q=padxy(ar,1) or q
 elif 'bootstrap' in cid:
  phase=int(cid[-1]);q=padxy(ar,{1:20,2:17,3:14}[phase]) or q
 elif ar=='U1':
  continue
 for i,r in enumerate(rs):
  if r not in D or r in placed:continue
  place(r,q,(0,90));cluster_refs.add(r)
# Weighted small-net adjacency; global supplies are deliberately excluded from attraction.
netrefs=collections.defaultdict(list)
for r,f in D.items():
 for q in f['pads']:
  if q['net']:netrefs[q['net']].append((r,q['number']))
def attraction(r):
 pts=[]
 for q in D[r]['pads']:
  links=netrefs[q['net']]
  if len(links)>14 or q['net'] in ['GND','PGND','VCC','AGND','12V','5V','DCBUS']:continue
  for ar,pn in links:
   if ar in placed and P['ref_to_group'][ar].split('_')[0]==P['ref_to_group'][r].split('_')[0]:
    xy=padxy(ar,pn);pts.append((xy,1/max(1,len(links)-1)))
 if pts:
  w=sum(w for _,w in pts);return (sum(p[0]*w for p,w in pts)/w,sum(p[1]*w for p,w in pts)/w),len(pts)
 rg=regions[P['ref_to_group'][r]];return ((rg['x_min']+rg['x_max'])/2,(rg['y_min']+rg['y_max'])/2),0
# Remaining all 532; prioritize strongly connected passives, not a distant generic grid.
while len(placed)<len(D):
 rem=[r for r in D if r not in placed];scores={r:attraction(r) for r in rem}
 r=max(rem,key=lambda r:(scores[r][1],D[r]['bbox'][2]*D[r]['bbox'][3]));xy,n=scores[r]
 # Identical M2 counterpart follows M1 exact relative arrangement when collision permits.
 if P['ref_to_group'][r].startswith('m2'):
  import re
  m=re.match(r'([A-Z]+)(\d+)$',r)
  if m and 1000<=int(m[2])<2000:
   other=m[1]+str(int(m[2])-1000)
   if other in placed and P['ref_to_group'].get(other,'').startswith('m1'):
    ox,oy,oa=placed[other];xy=(ox+66,oy)
    place(r,xy,(oa,));continue
 place(r,xy,(0,90))
assert len(placed)==532
collisions=[(a,b) for i,a in enumerate(placed) for b in list(placed)[i+1:] if hit(boxes[a],boxes[b],0)]
assert not collisions
out=dict(placements={r:dict(x_mm=p[0],y_mm=p[1],rotation_deg=p[2],group=P['ref_to_group'][r]) for r,p in placed.items()},bbox_collisions=collisions,notes=notes,bounds=[min(b[0] for b in boxes.values()),min(b[1] for b in boxes.values()),max(b[2] for b in boxes.values()),max(b[3] for b in boxes.values())])
Path('.layout-review/placement-coordinates.json').write_text(json.dumps(out,indent=2));print('Planned',len(placed),'bounds',out['bounds'],'expanded',len(notes),flush=True)
# Fresh live objects only, single undo transaction, preserve identities/net mappings/layers.
k=KiCad();assert k.check_version();board=k.get_board();fs=board.get_footprints();assert len(fs)==532 and not any(f.locked for f in fs)
def signature(fs,ps):return (sorted((str(f.id),f.reference_field.text.value,str(f.layer),f.locked) for f in fs),sorted((str(p.id),str(p.parent),p.number,p.net.name) for p in ps))
base=signature(fs,board.get_pads());assert {f.reference_field.text.value for f in fs}==set(placed)
assert all(str(f.id)==D[f.reference_field.text.value]['id'] for f in fs)
commit=board.begin_commit()
try:
 for f in fs:
  x,y,a=placed[f.reference_field.text.value];f.position=Vector2.from_xy_mm(x,y);f.orientation=Angle.from_degrees(a)
 result=board.update_items(fs);assert len(result)==532
 fresh=board.get_footprints();assert signature(fresh,board.get_pads())==base
 for f in fresh:
  x,y,a=placed[f.reference_field.text.value];assert abs(f.position.x/1e6-x)<1e-5 and abs(f.position.y/1e6-y)<1e-5
 bb=board.get_item_bounding_box(fresh);actual={f.reference_field.text.value:(v.pos.x/1e6,v.pos.y/1e6,(v.pos.x+v.size.x)/1e6,(v.pos.y+v.size.y)/1e6) for f,v in zip(fresh,bb)}
 actual_collisions=[(a,b) for i,a in enumerate(actual) for b in list(actual)[i+1:] if hit(actual[a],actual[b],0)]
 assert not actual_collisions,actual_collisions[:20]
 assert board.get_copper_layer_count()==2 and len(board.get_tracks())==len(board.get_vias())==len(board.get_zones())==len(board.get_shapes())==0
 board.push_commit(commit,'Initial functional placement of all 532 imported footprints')
except Exception:
 board.drop_commit(commit);raise
board.save()
Path('.layout-review/live-after.json').write_text(json.dumps(dict(count=len(fresh),bbox_collisions=actual_collisions,identity_net_signature_preserved=True,bounds=out['bounds'],placements=out['placements'],copper_layers=2,tracks=0,vias=0,zones=0,shapes=0),indent=2))
print('SAVED: 532 placements; UUID/ref/pad/net/layer unchanged; actual IPC bbox overlap zero',flush=True)
