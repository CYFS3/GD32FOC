from pathlib import Path
import json
from kipy import KiCad
from kipy.board_types import BoardLayer,PadType
from kipy.geometry import Vector2
load=lambda p:json.loads(Path(p).read_text(encoding='utf8'))
k=KiCad();assert k.check_version();b=k.get_board();fs=b.get_footprints();old=load('.layout-review/module-smd-library-fixes.json');ids={x['lib_id'] for x in old['files']};changed=[];refs=[]
for f in fs:
 if str(f.definition.id) not in ids:continue
 todo=[p for p in f.definition.pads if p.pad_type!=PadType.PT_SMD and 0<p.padstack.drill.diameter.x<10000]
 if not todo:continue
 for p in todo:p.pad_type=PadType.PT_SMD;p.padstack.layers=[BoardLayer.BL_F_Cu,BoardLayer.BL_F_Paste,BoardLayer.BL_F_Mask];p.padstack.drill.diameter=Vector2.from_xy_mm(0,0)
 changed.append(f);refs.append(f.reference_field.text.value)
if changed:
 c=b.begin_commit();assert len(b.update_items(changed))==len(changed);b.push_commit(c,'Correct shared instances of verified SMD definitions')
fs=b.get_footprints();power=load('.layout-review/power-reference-map.json')['rows'];back={r['current_ref'] for r in power if r['source_layer']=='B.Cu'}
flip=[f for f in fs if f.reference_field.text.value in back and f.layer!=BoardLayer.BL_B_Cu]
if flip:
 c=b.begin_commit();assert len(b.flip_items(flip))==len(flip);b.push_commit(c,'Restore reference power backside component placement')
fs=b.get_footprints();assert all(f.layer==BoardLayer.BL_B_Cu for f in fs if f.reference_field.text.value in back)
ps=b.get_pads();bb=b.get_item_bounding_box(fs);rows=[]
for f,v in zip(fs,bb):rows.append(dict(ref=f.reference_field.text.value,id=f.id.value,position=[f.position.x/1e6,f.position.y/1e6],angle=f.orientation.degrees,layer=int(f.layer),bbox=[v.pos.x/1e6,v.pos.y/1e6,v.size.x/1e6,v.size.y/1e6],pads=[dict(number=p.number,id=p.id.value,position=[p.position.x/1e6,p.position.y/1e6],net=p.net.name,layers=list(p.padstack.layers),type=int(p.pad_type)) for p in ps if p.parent==f.id]))
b.save();Path('.layout-review/power-integrated-ready.json').write_text(json.dumps(dict(footprints=rows,shared_smd_fixed=refs,power_back=sorted(back)),indent=2));print('shared SMD',len(refs),refs);print('power back',len(back));print('READY saved')
