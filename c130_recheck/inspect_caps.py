from pathlib import Path
import sys
sys.path.insert(0,str(Path.cwd()/'scripts'))
from migrate_p2 import load,prop
for fname in ['FOC_M1.kicad_sch','FOC_M2.kicad_sch','_autosave-FOC_M1.kicad_sch']:
 p=Path(fname)
 if not p.exists(): print(fname,'ABSENT');continue
 s,r=load(p)
 print('\nFILE',fname)
 for n in r.items:
  if not hasattr(n,'key'):continue
  at=n.one('at')
  if at and 330<float(at.items[1])<380 and 180<float(at.items[2])<230 and n.key in ['symbol','label','global_label']:
   print(n.key,prop(n,'Reference') if n.key=='symbol' else n.items[1],at.items)
   if n.key=='symbol':
    print([(x.items[1:3],x.one('at').items if x.one('at') else '') for x in n.kids('property')][:2])
  if n.key=='wire':
   pts=[x.items[1:] for x in n.one('pts').kids('xy')]
   if all(330<float(x)<380 and 180<float(y)<230 for x,y in pts): print('WIRE',pts)
