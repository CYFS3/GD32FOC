from pathlib import Path
import json,shutil
from kipy import KiCad
from kipy.board_types import PadType,BoardLayer
from kipy.geometry import Vector2
path=Path('ProDoc_Board1v1_2026-10-26-import-fps.pretty/SMC_L6.8-W5.9-LS7.8-BI.kicad_mod');text=path.read_text(encoding='utf8');backup=Path('.layout-review/SMC.before-smd.kicad_mod');shutil.copy2(path,backup)
assert text.count('thru_hole')==2 and text.count('(drill 0.001)')==2
text=text.replace('thru_hole rect','smd rect').replace('\n\t\t(drill 0.001)','').replace('(layers "*.Cu" "*.Mask")','(layers "F.Cu" "F.Paste" "F.Mask")').replace('\n\t\t(remove_unused_layers no)','').replace('\t(layer "F.Cu")','\t(layer "F.Cu")\n\t(attr smd)',1);path.write_text(text,encoding='utf8')
k=KiCad();assert k.check_version();b=k.get_board();f=next(f for f in b.get_footprints() if f.reference_field.text.value=='D22');before=[(p.id.value,p.number,p.net.name) for p in f.definition.pads];c=b.begin_commit()
for p in f.definition.pads:p.pad_type=PadType.PT_SMD;p.padstack.layers=[BoardLayer.BL_B_Cu,BoardLayer.BL_B_Paste,BoardLayer.BL_B_Mask];p.padstack.drill.diameter=Vector2.from_xy_mm(0,0)
f.position=Vector2.from_xy_mm(f.position.x/1e6+1,f.position.y/1e6)
assert len(b.update_items([f]))==1
ff=next(x for x in b.get_footprints() if x.reference_field.text.value=='D22');assert before==[(p.id.value,p.number,p.net.name) for p in ff.definition.pads];assert all(p.pad_type==PadType.PT_SMD and p.padstack.drill.diameter.x==0 and BoardLayer.BL_F_Cu not in p.padstack.layers for p in ff.definition.pads)
b.push_commit(c,'Correct SMC TVS pad import and clear XT30 mechanical pins');b.save()
planpath=Path('.layout-review/power-integrated-plan.json');plan=json.loads(planpath.read_text());plan['placements']['D22']['x_mm']=ff.position.x/1e6;plan['placements']['D22']['y_mm']=ff.position.y/1e6;plan['power_compatibility_exception']=dict(ref='D22',delta_mm=[1,0],reason='XT30PW-M mechanical PTH pads differ from reference XT30PW-F');planpath.write_text(json.dumps(plan,indent=2));print('D22 saved',ff.position)
