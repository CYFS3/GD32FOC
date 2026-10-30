import sys
sys.path.insert(0,'scripts')
from migrate_p2 import load,prop,W
s,r=load(W/'FOC_M1.kicad_sch')
for n in r.kids('wire'):
 ps=[tuple(map(float,p.items[1:3])) for p in n.one('pts').kids('xy')]
 if any(335<x<390 and 190<y<230 for x,y in ps):print('WIRE',ps)
for n in r.kids('global_label')+r.kids('label'):
 x,y,a=map(float,n.one('at').items[1:])
 if 335<x<390 and 190<y<230:print('LABEL',n.items[1],x,y,a)
