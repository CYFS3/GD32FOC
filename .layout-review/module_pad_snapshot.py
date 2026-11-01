import json
from pathlib import Path
from kipy import KiCad
from kipy.board_types import BoardLayer
k=KiCad();assert k.check_version();b=k.get_board();ps=b.get_pads();polys=b.get_pad_shapes_as_polygons(ps,BoardLayer.BL_F_Cu)
rows=[]
for p,poly in zip(ps,polys):
 pts=[]
 for n in poly.outline.nodes:
  if n.has_point:pts.append([n.point.x/1e6,n.point.y/1e6])
  elif n.has_arc:
   for v in [n.arc.start,n.arc.mid,n.arc.end]:pts.append([v.x/1e6,v.y/1e6])
 rows.append(dict(id=p.id.value,parent=p.parent.value,number=p.number,net=p.net.name,points=pts))
Path('.layout-review/module-pad-polygons-before.json').write_text(json.dumps(rows))
print(len(rows),len(ps),rows[0])
