from migrate_p2 import *
s,r=load(W/'Interface.kicad_sch');ops=[]
for n in r.kids('global_label'):
 x,y,a=map(float,n.one('at').items[1:])
 for w in r.kids('wire'):
  pts=[list(map(float,p.items[1:3])) for p in w.one('pts').kids('xy')]
  if [x,y] in pts:
   other=pts[1] if pts[0]==[x,y] else pts[0]
   if abs(other[1]-y)<.001 and abs(other[0]-x)>.01:
    ops.append((n.start,n.end,label(n.items[1],x,y,180 if x<other[0] else 0)))
   break
for n in r.kids('symbol'):
 if prop(n,'Reference')=='J300':
  for p in n.kids('property'):
   if p.items[1]=='Value':
    a=p.one('at');ops.append((a.start,a.end,'(at 83.82 33.02 0)'))
(W/'Interface.kicad_sch').write_text(patches(s,ops),encoding='utf-8');print('All horizontal endpoint labels point outward; header value above connector')
