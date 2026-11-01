from pathlib import Path
import json
from kipy import KiCad
from kipy.board_types import BoardLayer,PadType,BoardCircle,BoardRectangle
from kipy.geometry import Vector2
from kipy.common_types import LibraryIdentifier
load=lambda p:json.loads(Path(p).read_text(encoding='utf8'))
refs={r['ref'] for r in load('.layout-review/reference-testpoint-audit.json')['current_keystone']};assert len(refs)==52 and 'TP200' not in refs
k=KiCad();assert k.check_version();b=k.get_board();fs=b.get_footprints();sel=[f for f in fs if f.reference_field.text.value in refs];assert len(sel)==52
sig=lambda pp:sorted((p.id.value,p.parent.value,p.number,p.net.name) for p in pp)
before=sig(b.get_pads());positions={f.reference_field.text.value:(f.position.x,f.position.y,f.orientation.degrees,int(f.layer)) for f in fs};groups=sorted((g.id.value,tuple(sorted(x.id.value for x in g.items))) for g in b.get_groups());smdstyle=next(f.attributes.mounting_style for f in fs if f.reference_field.text.value=='C200');c=b.begin_commit()
try:
 for f in sel:
  definition=f.definition;pp=definition.pads;assert len(pp)==1;p=pp[0];assert p.number=='1'
  p.pad_type=PadType.PT_SMD;p.position=Vector2.from_xy_mm(f.position.x/1e6,f.position.y/1e6);p.padstack.drill.diameter=Vector2.from_xy_mm(0,0);p.padstack.layers=[BoardLayer.BL_F_Cu,BoardLayer.BL_F_Mask]
  for cl in p.padstack.copper_layers:
   cl.size=Vector2.from_xy_mm(1.27,1.27);cl.offset=Vector2.from_xy_mm(0,0)
  # Existing pad is circular; preserve circular shape enum rather than inventing one.
  x,y=f.position.x/1e6,f.position.y/1e6
  fab=BoardCircle();fab.layer=BoardLayer.BL_F_Fab;fab.center=Vector2.from_xy_mm(x,y);fab.radius_point=Vector2.from_xy_mm(x+.762,y);fab.attributes.stroke.width=51000
  court=BoardRectangle();court.layer=BoardLayer.BL_F_CrtYd;court.top_left=Vector2.from_xy_mm(x-1.0375,y-1.0375);court.bottom_right=Vector2.from_xy_mm(x+1.0375,y+1.0375);court.attributes.stroke.width=50000
  definition.items=[p,fab,court]
  lid=LibraryIdentifier();lid.library='VerifiedParts';lid.name='TestPoint_D1.27_Reference';definition.id=lid
  f.value_field.text.value='TestPoint';f.datasheet_field.text.value='';f.description_field.text.value='Reference bare copper test pad D1.27mm'
  # Identity supplier fields disappear with old definition text; reference/value instance fields retained.
  f.attributes.exclude_from_bill_of_materials=True;f.attributes.exclude_from_position_files=True;f.attributes.mounting_style=smdstyle
 assert len(b.update_items(sel))==52
 fresh=b.get_footprints();fp={f.reference_field.text.value:f for f in fresh};assert sig(b.get_pads())==before;assert positions=={f.reference_field.text.value:(f.position.x,f.position.y,f.orientation.degrees,int(f.layer)) for f in fresh};assert groups==sorted((g.id.value,tuple(sorted(x.id.value for x in g.items))) for g in b.get_groups())
 for r in refs:
  f=fp[r];p=f.definition.pads[0];assert p.pad_type==PadType.PT_SMD and p.padstack.drill.diameter.x==0;assert p.padstack.layers==[BoardLayer.BL_F_Cu,BoardLayer.BL_F_Mask];assert all(cl.size.x==1270000 and cl.size.y==1270000 for cl in p.padstack.copper_layers);assert f.definition.id.name=='TestPoint_D1.27_Reference'
 b.push_commit(c,'Restore 52 reference bare copper test pads')
except Exception:b.drop_commit(c);raise
b.save();Path('.layout-review/reference-tp-ipc-validation.json').write_text(json.dumps(dict(count=52,refs=sorted(refs),pad_id_net_preserved=True,diameter_mm=1.27,library='VerifiedParts:TestPoint_D1.27_Reference'),indent=2));print('SAVED 52 reference test pads')
