"""Shorten only isolated signal label leads; retain exact connectivity."""
from migrate_p2 import *
import math
s,r=load(W/'HSLink.kicad_sch');defs={n.items[1]:n for n in r.one('lib_symbols').kids('symbol')};pins=set();ends={};occ={};ops=[]
def xy(n):return tuple(round(float(v),5) for v in n.one('at').items[1:3])
for n in r.kids('symbol'):
 if prop(n,'Reference').startswith('#'):continue
 x,y=xy(n);a=math.radians(float(n.one('at').items[3]))
 for u in defs[n.val('lib_id')].kids('symbol'):
  for p in u.kids('pin'):
   px,py=map(float,p.one('at').items[1:3]);mir=n.val('mirror')
   if mir=='x':py=-py
   if mir=='y':px=-px
   pins.add((round(x+px*math.cos(a)-py*math.sin(a),5),round(y-px*math.sin(a)-py*math.cos(a),5)))
for n in r.kids('wire'):
 pts=[tuple(round(float(v),5) for v in q.items[1:3]) for q in n.one('pts').kids('xy')]
 for p in pts:ends.setdefault(p,[]).append((n,pts))
for k in ['symbol','label','global_label','junction','no_connect']:
 for n in r.kids(k):occ[xy(n)]=occ.get(xy(n),0)+1
for n in r.kids('global_label'):
 x,y=xy(n)
 if n.items[1]=='HSL_ISP_KEY':continue # Existing shared branch touches the wire interior.
 if len(ends.get((x,y),[]))!=1:continue
 w,pts=ends[(x,y)][0];other=pts[1] if pts[0]==(x,y) else pts[0]
 if other not in pins or len(ends.get(other,[]))!=1 or occ.get(other,0)!=0 or occ[(x,y)]!=1 or other[1]!=y:continue
 ops += [(w.start,w.end,''),(n.start,n.end,label(n.items[1],*other,0 if other[0]>x else 180))]
(W/'HSLink.kicad_sch').write_text(patches(s,ops),encoding='utf-8');print('Signal leads shortened',len(ops)//2)
