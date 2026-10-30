import sys
sys.path.insert(0,'scripts')
from migrate_p2 import load,prop,W
s,r=load(W/'FOC_M1.kicad_sch');u=next(n for n in r.kids('symbol') if prop(n,'Reference')=='U7');d=next(n for n in r.one('lib_symbols').kids('symbol') if n.items[1]==u.val('lib_id'));x,y,_=map(float,u.one('at').items[1:]);print('PINS')
for sub in d.kids('symbol'):
 for p in sub.kids('pin'):
  px,py,a=map(float,p.one('at').items[1:]);print(p.val('number'),p.val('name'),x+px,y-py,a)
print('LABELS')
for n in r.kids('global_label')+r.kids('label'):
 px,py,a=map(float,n.one('at').items[1:])
 if 250<px<305 and 190<py<230:print(n.items[1],px,py,a,n.one('effects').one('justify').items if n.one('effects').one('justify') else '')
print('WIRES')
for n in r.kids('wire'):
 ps=[tuple(map(float,p.items[1:3])) for p in n.one('pts').kids('xy')]
 if any(250<px<300 and 190<py<230 for px,py in ps):print(ps)
