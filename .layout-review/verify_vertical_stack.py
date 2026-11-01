from pathlib import Path
import json
from kipy import KiCad
load=lambda p:json.loads(Path(p).read_text(encoding='utf8'))
M=load('.layout-review/foc-reuse-map.json');S=load('.layout-review/vertical-stack-before.json');pos=S['positions_nm'];a={r['m1_ref'] for r in M['rows']};d={r['m2_ref'] for r in M['rows']};shared=set(pos)-a-d
k=KiCad();assert k.check_version();b=k.get_board();fs=b.get_footprints();ps=b.get_pads();fd={f.reference_field.text.value:f for f in fs}
sig=[sorted((f.id.value,f.reference_field.text.value,f.orientation.degrees,int(f.layer),f.locked) for f in fs),sorted((p.id.value,p.parent.value,p.number,p.net.name,int(p.pad_type),tuple(p.padstack.layers)) for p in ps)]
assert json.loads(json.dumps(sig))==S['signature']
groups=sorted((g.id.value,g.name,tuple(sorted(i.id.value for i in g.items))) for g in b.get_groups());assert json.loads(json.dumps(groups))==S['groups']
target={r:tuple(p) for r,p in pos.items()}
for row in M['rows']:
 x,y=pos[row['m1_ref']];target[row['m2_ref']]=(x,y+78500000)
for r in shared:target[r]=(pos[r][0],pos[r][1]+80500000)
err=max(max(abs(f.position.x-target[r][0]),abs(f.position.y-target[r][1])) for r,f in fd.items());assert err<=2
pairerr=max(max(abs(fd[row['m2_ref']].position.x-fd[row['m1_ref']].position.x),abs(fd[row['m2_ref']].position.y-fd[row['m1_ref']].position.y-78500000)) for row in M['rows']);assert pairerr<=2
for r in a:assert (fd[r].position.x,fd[r].position.y)==tuple(pos[r])
bbs=b.get_item_bounding_box(fs);bb={f.reference_field.text.value:[v.pos.x/1e6,v.pos.y/1e6,(v.pos.x+v.size.x)/1e6,(v.pos.y+v.size.y)/1e6] for f,v in zip(fs,bbs)}
def union(refs):return [min(bb[r][0] for r in refs),min(bb[r][1] for r in refs),max(bb[r][2] for r in refs),max(bb[r][3] for r in refs)]
aa,dd,ss=union(a),union(d),union(shared);assert dd[1]-aa[3]>=8 and ss[1]-dd[3]>=8
cc=[len(b.get_tracks()),len(b.get_vias()),len(b.get_zones()),len(b.get_shapes()),b.get_copper_layer_count()];assert cc==[0,0,0,0,2]
b.save()
v=dict(status='saved',pitch_mm=78.5,M2_translation_mm=[-66.396,78.5],shared_translation_mm=[0,80.5],M1_unchanged=True,counts=dict(M1=162,M2=162,shared=208,total=532,moved=370),bbox=dict(M1=aa,M2=dd,shared=ss),gaps_mm=dict(M1_to_M2=dd[1]-aa[3],M2_to_shared=ss[1]-dd[3]),maximum_target_error_nm=err,maximum_pair_error_nm=pairerr,identity_network_angle_layer_groups_preserved=True,groups=groups,copper_counts=cc,note='Position update took effect despite transaction drop after strict zero-tolerance verification; fresh state verified with <=2nm tolerance then saved. No repeated translation.')
Path('.layout-review/vertical-stack-validation.json').write_text(json.dumps(v,indent=2),encoding='utf8')
Path('.layout-review/vertical-stack-coordinates.json').write_text(json.dumps({r:dict(x_mm=f.position.x/1e6,y_mm=f.position.y/1e6,rotation_deg=f.orientation.degrees,layer=int(f.layer)) for r,f in fd.items()},indent=2),encoding='utf8')
print(json.dumps(v,ensure_ascii=False))
