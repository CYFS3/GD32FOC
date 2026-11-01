import json
from pathlib import Path
from kipy import KiCad
from kipy.geometry import Vector2,Angle
from kipy.board_types import BoardLayer
k=KiCad();k.check_version();b=k.get_board();p=json.loads(Path('.layout-review/module-reuse-plan-final.json').read_text());back=set(p['back_refs']);fs=b.get_footprints();targets=[f for f in fs if f.reference_field.text.value in back and f.layer==BoardLayer.BL_F_Cu];c=b.begin_commit();out=b.flip_items(targets);print('flip returned',[(f.reference_field.text.value,f.layer) for f in out]);b.push_commit(c,'Restore reference backside capacitor mounting');fs=[f for f in b.get_footprints() if f.reference_field.text.value in back];print('fresh',[(f.reference_field.text.value,f.layer) for f in fs]);assert all(f.layer==BoardLayer.BL_B_Cu for f in fs)
c=b.begin_commit()
for f in fs:
 q=p['placements'][f.reference_field.text.value];f.position=Vector2.from_xy_mm(q['x_mm'],q['y_mm']);f.orientation=Angle.from_degrees(q['rotation_deg'])
b.update_items(fs);b.push_commit(c,'Align backside module capacitors to source electrodes');print('aligned',[(f.reference_field.text.value,f.layer) for f in b.get_footprints() if f.reference_field.text.value in back])
