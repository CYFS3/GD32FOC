from pathlib import Path
import json
from kipy import KiCad
from kipy.board_types import PadType,BoardLayer
from kipy.geometry import Vector2
k=KiCad();assert k.check_version();b=k.get_board();ps=b.get_pads();cands=json.loads(Path('.layout-review/false-pth-candidates.json').read_text());ids={pid for c in cands for pid in c['pad_ids']};target=[p for p in ps if p.id.value in ids];assert len(target)==len(ids)
sig=lambda pp:sorted((p.id.value,p.parent.value,p.number,p.net.name,p.position.x,p.position.y) for p in pp)
before=sig(ps);fs=[f for f in b.get_footprints() if f.reference_field.text.value in {r['ref'] for r in cands}];target=[p for f in fs for p in f.definition.pads if p.id.value in ids];assert len(target)==len(ids)
c=b.begin_commit()
try:
 for p in target:
  assert 0<p.padstack.drill.diameter.x<10000
  p.pad_type=PadType.PT_SMD;p.padstack.layers=[BoardLayer.BL_F_Cu,BoardLayer.BL_F_Paste,BoardLayer.BL_F_Mask];p.padstack.drill.diameter=Vector2.from_xy_mm(0,0)
 assert len(b.update_items(fs))==len(fs)
 fresh=b.get_pads();assert sig(fresh)==before
 bad=[(p.number,p.pad_type,p.padstack.drill.diameter.x,list(p.padstack.layers)) for p in fresh if p.id.value in ids and not(p.pad_type==PadType.PT_SMD and p.padstack.drill.diameter.x==0 and BoardLayer.BL_B_Cu not in p.padstack.layers)];assert not bad,bad[:3]
 b.push_commit(c,'Correct definite FOC SMD microdrill import artifacts')
except Exception:b.drop_commit(c);raise
b.save();Path('.layout-review/module-smd-fix-validation.json').write_text(json.dumps(dict(footprints=len(cands),pads=len(ids),identity_net_geometry_preserved=True,refs=[r['ref'] for r in cands]),indent=2));print('Corrected',len(cands),'footprints',len(ids),'pads')
