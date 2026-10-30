import sys,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from migrate_p2 import *
for m in (1,2):
 f=W/f'FOC_M{m}.kicad_sch';s,r=load(f);ops=[];extra=[]
 # New content follows first new U instance. Move this self-contained block into unused sheet top.
 newstart=next(n.start for n in r.kids('symbol') if prop(n,'Reference')==f'U{9100+m}')
 path=next(n for n in r.kids('symbol') if prop(n,'Reference')==f'U{9100+m}').one('instances').one('project').one('path').items[1]
 pc=0
 def pwr(rail,x,y):
  global pc
  pc+=1;ref=f'#PWR{9200+m*100+pc}'
  return f'(symbol (lib_id "StylePower:{rail}") (at {x:.6f} {y:.6f} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid()}") (property "Reference" "{ref}" (at {x:.6f} {y:.6f} 0) (hide yes) (effects (font (size 1 1)))) (property "Value" "{rail}" (at {x:.6f} {y+(-3 if rail!="GND" else 3):.6f} 0) (effects (font (size 1 1)))) (instances (project "GD32F5_FOC" (path "{path}" (reference "{ref}") (unit 1)))))'
 for n in r.items:
  if not isinstance(n,Node):continue
  if n.start>=newstart and n.key in ('symbol','wire','global_label','text'):
   t=s[n.start:n.end]
   t=re.sub(r'\((at|xy) ([-\d.]+) ([-\d.]+)',lambda mt:f'({mt[1]} {float(mt[2]):.6f} {float(mt[3])-300:.6f}',t)
   if n.key=='global_label':
    name=n.items[1];x,y,a=map(float,n.one('at').items[1:]);y-=300
    if name in ('VCC','GND','5V'):t=pwr(name,x,y)
    elif '_ENC_' in name and '_VSUP' not in name:t=label(name,x,y,180)
    elif '_HALL_' in name:t=label(name,x,y,0)
   if n.key=='text':
    x,y=map(float,n.one('at').items[1:3]);y-=300
    t='\n'.join(note(line,x,y+i*3.5) for i,line in enumerate(n.items[1].split('\n')))
   ops.append((n.start,n.end,t))
  elif n.key=='global_label' and n.items[1] in ('VCC','5V') and tuple(map(float,n.one('at').items[1:3])) in [(238.76,264.16),(231.14,270.51)]:
   x,y=map(float,n.one('at').items[1:3]);ops.append((n.start,n.end,pwr(n.items[1],x,y)))
 f.write_text(patches(s,ops),encoding='utf8')
