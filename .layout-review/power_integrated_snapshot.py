from pathlib import Path
import json,shutil
from kipy import KiCad
k=KiCad();assert k.check_version();b=k.get_board();fs=b.get_footprints();ps=b.get_pads();bb=b.get_item_bounding_box(fs)
rows=[]
for f,v in zip(fs,bb):
 rows.append(dict(ref=f.reference_field.text.value,id=f.id.value,position=[f.position.x/1e6,f.position.y/1e6],angle=f.orientation.degrees,layer=int(f.layer),locked=f.locked,bbox=[v.pos.x/1e6,v.pos.y/1e6,v.size.x/1e6,v.size.y/1e6],definition=str(f.definition.id),pads=[dict(number=p.number,id=p.id.value,position=[p.position.x/1e6,p.position.y/1e6],net=p.net.name,pad_type=int(p.pad_type),layers=list(p.padstack.layers),drill=[p.padstack.drill.diameter.x/1e6,p.padstack.drill.diameter.y/1e6]) for p in ps if p.parent==f.id]))
groups=[dict(id=g.id.value,name=g.name,refs=[next(f.reference_field.text.value for f in fs if f.id==i.id) for i in g.items]) for g in b.get_groups()]
out=dict(footprints=rows,layers=b.get_copper_layer_count(),groups=groups,counts=dict(footprints=len(fs),pads=len(ps),tracks=len(b.get_tracks()),vias=len(b.get_vias()),zones=len(b.get_zones()),shapes=len(b.get_shapes())))
Path('.layout-review/power-integrated-before.json').write_text(json.dumps(out,indent=2),encoding='utf8')
b.save();shutil.copy2('GD32F5_FOC.kicad_pcb','.layout-review/power-integrated-before.kicad_pcb')
print(out['counts']);print('back',len([f for f in rows if f['layer']==34]));print('groups',[len(g['refs']) for g in groups]);print('locked',sum(f['locked'] for f in rows))
