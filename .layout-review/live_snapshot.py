from kipy import KiCad
from pathlib import Path
import json,shutil
k=KiCad();assert k.check_version();b=k.get_board();fs=b.get_footprints();ps=b.get_pads();bbs=b.get_item_bounding_box(fs)
def xy(p):return [p.x/1e6,p.y/1e6]
rows=[]
for f,bb in zip(fs,bbs):
 pads=[p for p in ps if p.parent==f.id]
 rows.append(dict(ref=f.reference_field.text.value,id=str(f.id),position=xy(f.position),angle=f.orientation.degrees,locked=f.locked,bbox=[*xy(bb.pos),*xy(bb.size)],pads=[dict(number=p.number,id=str(p.id),position=xy(p.position),net=p.net.name) for p in pads]))
s=dict(board=b.name,footprints=rows,count=len(fs),copper_layers=b.get_copper_layer_count(),tracks=len(b.get_tracks()),vias=len(b.get_vias()),zones=len(b.get_zones()),shapes=len(b.get_shapes()))
Path('.layout-review/live-before.json').write_text(json.dumps(s,indent=2));b.save();shutil.copy2(b.name,'.layout-review/board-before-placement.kicad_pcb')
p=json.load(open('.layout-review/placement-groups.json'));print([(n,len(g['refs']),g['rect_mm']) for n,g in p['groups'].items()]);print('keys',list(p['key_targets'].items())[:5]);print('sample',rows[0]);print('U1',next(x for x in rows if x['ref']=='U1'));print('USB',next(x for x in rows if x['ref']=='USB8002'))
