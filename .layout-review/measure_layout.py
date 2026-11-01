from kipy import KiCad
from pathlib import Path
import json,math
k=KiCad();assert k.check_version();b=k.get_board();fs=b.get_footprints();ps=b.get_pads();f={x.reference_field.text.value:x for x in fs};pd={r:[p for p in ps if p.parent==x.id] for r,x in f.items()}
def p(r,n):return next(q for q in pd[r] if q.number==str(n))
def dist(a,c):return math.hypot(a.position.x-c.position.x,a.position.y-c.position.y)/1e6
pairs=[('U1',8,'Y201',1),('U1',9,'Y201',2),('U1',12,'Y200',1),('U1',13,'Y200',3),('Y201',1,'C214',1),('Y201',2,'C215',1),('Y200',1,'C210',1),('Y200',3,'C211',1)]
for pin,r in [(11,'C200'),(28,'C201'),(50,'C202'),(75,'C203'),(100,'C204'),(6,'C212'),(22,'C206'),(22,'C207'),(21,'C208'),(21,'C213')]:
 a=p('U1',pin);same=[q for q in pd[r] if q.net.name==a.net.name];q=min(same,key=lambda q:dist(a,q));pairs.append(('U1',pin,r,q.number))
rows=[dict(a=f'{a}.{an}',b=f'{c}.{cn}',pad_center_distance_mm=round(dist(p(a,an),p(c,cn)),3)) for a,an,c,cn in pairs]
for r,mos in [('R59','Q5'),('R60','Q6'),('R61','Q7'),('R75','Q8'),('R76','Q9'),('R77','Q10')]:
 a=p(mos,1);q=min(pd[r],key=lambda q:dist(a,q));rows.append(dict(a=mos+'.1',b=r+'.'+q.number,pad_center_distance_mm=round(dist(a,q),3)))
Path('.layout-review/critical-pad-distances.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
