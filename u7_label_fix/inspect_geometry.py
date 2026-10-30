import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from migrate_p2 import load,prop
W=Path(__file__).resolve().parents[1]
for file,ref in [('FOC_M1.kicad_sch','U7'),('FOC_M2.kicad_sch','U1007')]:
 s,r=load(W/file); n=next(n for n in r.kids('symbol') if prop(n,'Reference')==ref)
 print(file,s[n.start:n.end][:1800]); sx,sy,ang=map(float,n.one('at').items[1:]);assert ang==0
 lib=next(x for x in r.one('lib_symbols').kids('symbol') if x.items[1]==n.val('lib_id'))
 for sub in lib.kids('symbol'):
  for p in sub.kids('pin'):
   px,py,a=map(float,p.one('at').items[1:]); x,y=sx+px,sy-py
   print('PIN',p.val('number'),p.val('name'),x,y,a)
 for kind in ['wire','label','global_label','junction','symbol']:
  for q in r.kids(kind):
   pts=q.one('pts').kids('xy') if kind=='wire' else ([q.one('at')] if q.one('at') else [])
   if any(abs(float(p.items[1])-sx)<50 and abs(float(p.items[2])-sy)<28 for p in pts):
    print(kind,prop(q,'Reference') if kind=='symbol' else q.items[1] if 'label' in kind else '',[p.items[1:] for p in pts],q.val('uuid'))
