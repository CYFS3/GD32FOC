from pathlib import Path
import sys,json,shutil
from decimal import Decimal
W=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(W/'scripts'))
from migrate_p2 import load,patches,prop,Node
files=[W/(n+'.kicad_sch') for n in ['GD32F5_FOC','MCU','power','FOC_M1','FOC_M2','HSLink']]
apply='--apply' in sys.argv
report={'pages':{},'different_names_same_anchor':[]}
if apply:
 b=W/'power_review/baseline';b.mkdir(exist_ok=True)
 for f in files:
  assert not (b/f.name).exists(), 'Refuse overwrite baseline'
  shutil.copy2(f,b/f.name)
for f in files:
 s,r=load(f);defs={n.items[1]:n for n in r.one('lib_symbols').kids('symbol')};groups={};anchors={}
 for n in r.kids('symbol'):
  d=defs[n.val('lib_id')]
  if d.one('power') is None:continue
  if d.one('power').items[1:] not in ([],['global']):continue
  at=tuple(str(Decimal(x).normalize()) for x in n.one('at').items[1:3]);value=prop(n,'Value')
  groups.setdefault((at,value),[]).append(n);anchors.setdefault(at,set()).add(value)
 for at,values in anchors.items():
  if len(values)>1:report['different_names_same_anchor'].append({'page':f.name,'at':at,'values':sorted(values)})
 ops=[];removed=[]
 for (at,value),ns in groups.items():
  if len(ns)<2:continue
  # Prefer converted StylePower glyph; original counterpart alone is removed.
  ns.sort(key=lambda n:(not n.val('lib_id').startswith('StylePower:'),prop(n,'Reference')))
  keep=ns[0]
  for n in ns[1:]:
   ops.append((n.start,n.end,''));removed.append({'at':at,'value':value,'keep':prop(keep,'Reference'),'remove':prop(n,'Reference'),'removed_lib':n.val('lib_id')})
 if apply and ops:
  new=patches(s,ops)
  with f.open('w',encoding='utf-8',newline='') as out:out.write(new)
 report['pages'][f.name]={'removed_count':len(removed),'duplicates':removed}
report['total_removed']=sum(p['removed_count'] for p in report['pages'].values())
print(json.dumps(report,indent=2))
if apply:(W/'power_review/duplicates.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
