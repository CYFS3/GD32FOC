from migrate_p2 import *
# Snap only newly added devices and their pin labels to the existing 1.27-mm grid.
for file in ['MCU.kicad_sch','FOC_M1.kicad_sch','FOC_M2.kicad_sch']:
 s,r=load(W/file);ops=[]
 targets={'R203','R204','R205','J201'} if file=='MCU.kicad_sch' else {f'R{i}' for i in list(range(300,306))+list(range(1300,1306))}
 for n in r.kids('symbol'):
  if prop(n,'Reference') not in targets:continue
  x,y=map(float,n.one('at').items[1:3]);dx=round(x/1.27)*1.27-x;dy=round(y/1.27)*1.27-y
  raw=s[n.start:n.end]
  def shift(m):return f'(at {float(m[1])+dx:g} {float(m[2])+dy:g}'
  raw=re.sub(r'\(at ([\d.-]+) ([\d.-]+)',shift,raw);ops.append((n.start,n.end,raw))
  points=[(x,y-3.81),(x,y+3.81)] if prop(n,'Reference')!='J201' else [(x-5.08,y-2.54),(x-5.08,y),(x-5.08,y+2.54),(x-5.08,y+5.08)]
  for lab in r.kids('global_label'):
   a,b=map(float,lab.one('at').items[1:3])
   if any(abs(a-p)<0.001 and abs(b-q)<0.001 for p,q in points):ops.append((lab.start,lab.end,re.sub(r'\(at ([\d.-]+) ([\d.-]+)',shift,s[lab.start:lab.end])))
 (W/file).write_text(patches(s,ops),encoding='utf-8')
