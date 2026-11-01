from pathlib import Path
import json,math,shutil
from kipy import KiCad
from kipy.geometry import Vector2
load=lambda p:json.loads(Path(p).read_text(encoding='utf8'))
M=load('.layout-review/foc-reuse-map.json'); oldcoords=load('.layout-review/module-reuse-coordinates.json')
k=KiCad();assert k.check_version();b=k.get_board();fs=b.get_footprints();ps=b.get_pads();fd={f.reference_field.text.value:f for f in fs}
a={r['m1_ref'] for r in M['rows']};d={r['m2_ref'] for r in M['rows']};shared=set(fd)-a-d
assert len(fs)==532 and len(a)==len(d)==162 and len(shared)==208
assert not any(f.locked for f in fs)
def counts():return [len(b.get_tracks()),len(b.get_vias()),len(b.get_zones()),len(b.get_shapes()),b.get_copper_layer_count()]
cc=counts();assert cc==[0,0,0,0,2]
def gs():
 return sorted((g.id.value,g.name,tuple(sorted(i.id.value for i in g.items))) for g in b.get_groups())
groups=gs();assert len(groups)==2 and all(len(x[2])==162 for x in groups)
def signature(ff,pp):
 return [sorted((f.id.value,f.reference_field.text.value,f.orientation.degrees,int(f.layer),f.locked) for f in ff),sorted((p.id.value,p.parent.value,p.number,p.net.name,int(p.pad_type),tuple(p.padstack.layers)) for p in pp)]
sig=signature(fs,ps);pos={r:(f.position.x,f.position.y) for r,f in fd.items()}
for row in M['rows']:
 x,y=pos[row['m1_ref']];xx,yy=pos[row['m2_ref']];assert abs(xx-x-66396000)<=2 and abs(yy-y)<=2
bbs=b.get_item_bounding_box(fs);assert len(bbs)==532
boxes={f.reference_field.text.value:[v.pos.x/1e6,v.pos.y/1e6,(v.pos.x+v.size.x)/1e6,(v.pos.y+v.size.y)/1e6] for f,v in zip(fs,bbs)}
def union(refs,bb):return [min(bb[r][0] for r in refs),min(bb[r][1] for r in refs),max(bb[r][2] for r in refs),max(bb[r][3] for r in refs)]
ab=union(a,boxes);db=union(d,boxes);sb=union(shared,boxes)
pitch=math.ceil((ab[3]-ab[1]+8)*2)/2
projected_d=[db[0]-66.396,db[1]+pitch,db[2]-66.396,db[3]+pitch]
shift_shared=max(0,math.ceil((projected_d[3]+8-sb[1])*2)/2)
target=dict(pos)
for row in M['rows']:
 x,y=pos[row['m1_ref']];target[row['m2_ref']]=(x,y+round(pitch*1e6))
for r in shared:target[r]=(pos[r][0],pos[r][1]+round(shift_shared*1e6))
b.save();shutil.copy2('GD32F5_FOC.kicad_pcb','.layout-review/before-vertical-stack.kicad_pcb')
Path('.layout-review/vertical-stack-before.json').write_text(json.dumps(dict(positions_nm=pos,signature=sig,groups=groups,bbox=dict(M1=ab,M2=db,shared=sb)),indent=2),encoding='utf8')
print('Plan pitch',pitch,'shared shift',shift_shared,'M1',ab,'oldM2',db,flush=True)
c=b.begin_commit()
try:
 changed=[]
 for r,f in fd.items():
  if target[r]!=pos[r]:f.position=Vector2.from_xy_mm(target[r][0]/1e6,target[r][1]/1e6);changed.append(f)
 assert len(b.update_items(changed))==len(changed)
 fresh=b.get_footprints();freshpads=b.get_pads();assert signature(fresh,freshpads)==sig and gs()==groups and counts()==cc
 ff={f.reference_field.text.value:f for f in fresh}
 assert all((f.position.x,f.position.y)==target[r] for r,f in ff.items())
 for row in M['rows']:
  f,g=ff[row['m1_ref']],ff[row['m2_ref']];assert g.position.x==f.position.x and g.position.y-f.position.y==round(pitch*1e6)
 freshbb=b.get_item_bounding_box(fresh);bb={f.reference_field.text.value:[v.pos.x/1e6,v.pos.y/1e6,(v.pos.x+v.size.x)/1e6,(v.pos.y+v.size.y)/1e6] for f,v in zip(fresh,freshbb)}
 aa,dd,ss=union(a,bb),union(d,bb),union(shared,bb)
 assert dd[1]-aa[3]>=8-2e-6 and ss[1]-dd[3]>=8-2e-6
 b.push_commit(c,'Stack FOC M1 above M2 with identical X positions')
except Exception:b.drop_commit(c);raise
b.save()
validation=dict(status='saved',pitch_mm=pitch,M2_translation_mm=[-66.396,pitch],shared_translation_mm=[0,shift_shared],M1_unchanged=True,counts=dict(M1=162,M2=162,shared=208,total=532,moved=len(changed)),bbox=dict(M1=aa,M2=dd,shared=ss),gaps_mm=dict(M1_to_M2=dd[1]-aa[3],M2_to_shared=ss[1]-dd[3]),pair_dx_mm=0,pair_dy_mm=pitch,maximum_pair_error_nm=0,identity_network_angle_layer_groups_preserved=True,groups=groups,copper_counts=cc)
Path('.layout-review/vertical-stack-validation.json').write_text(json.dumps(validation,indent=2),encoding='utf8')
Path('.layout-review/vertical-stack-coordinates.json').write_text(json.dumps({r:dict(x_mm=f.position.x/1e6,y_mm=f.position.y/1e6,rotation_deg=f.orientation.degrees,layer=int(f.layer)) for r,f in ff.items()},indent=2),encoding='utf8')
print(json.dumps(validation,ensure_ascii=False),flush=True)
