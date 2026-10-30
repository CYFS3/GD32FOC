import sys,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from migrate_p2 import *
for m in (1,2):
 f=W/f'FOC_M{m}.kicad_sch';s,r=load(f);ops=[]
 for n in r.kids('wire'):
  if {tuple(map(float,p.items[1:3])) for p in n.one('pts').kids('xy')}=={(260.35,264.16),(260.35,267.97)}:ops.append((n.start,n.end,''))
 for n in r.kids('symbol'):
  rr=prop(n,'Reference');x,y=map(float,n.one('at').items[1:3])
  powerunit=rr==f'U{9100+m}' and n.val('unit')=='4'
  selector=rr in [f'R{9101+(m-1)*2}',f'R{9102+(m-1)*2}']
  if powerunit or selector:
   for p in n.kids('property'):
    if p.items[1] not in ('Reference','Value'):continue
    t=s[p.start:p.end]
    if powerunit and p.items[1]=='Value':t=t[:-1]+' (hide yes))'
    else:
     xx=x+10.16;yy=y+(-1.27 if p.items[1]=='Reference' else 1.27)
     t=re.sub(r'\(at [-\d.]+ [-\d.]+ [-\d.]+\)',f'(at {xx:.6f} {yy:.6f} 0)',t,count=1)
    ops.append((p.start,p.end,t))
 f.write_text(patches(s,ops),encoding='utf8')
