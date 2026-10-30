import sys,json,xml.etree.ElementTree as E
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from migrate_p2 import *
if '--fix-pwm' in sys.argv:
 for m in (1,2):
  f=W/f'FOC_M{m}.kicad_sch';s,r=load(f)
  n=next(n for n in r.kids('wire') if {tuple(map(float,p.items[1:3])) for p in n.one('pts').kids('xy')}=={(224.79,270.51),(231.14,270.51)})
  f.write_text(patches(s,[(n.start,n.end,label('5V',231.14,270.51))]),encoding='utf-8')
else:
 def nets(file):
  r=E.parse(file);return { (p.get('ref'),p.get('pin')):frozenset((q.get('ref'),q.get('pin')) for q in n.findall('node')) for n in r.findall('.//nets/net') for p in n.findall('node')}
 before=nets(W/'interface_review/hall_before.xml');after=nets(W/'interface_review/hall_after.xml')
 # Remove sanctioned Hall-related endpoints so added buffer and pullup changes cannot conceal unrelated changes.
 allowed=set()
 for m in (1,2):
  off=(m-1)*1000
  for ref,pins in [('CN'+str(5+off),['6']),('R'+str(49+off),['2']),('R'+str(54+off),['1'])]:allowed.update((ref,p) for p in pins)
  for i in (95,97,98,106,107,108):allowed.update(('R'+str(i+off),p) for p in ('1','2'))
  for i in (82,83,84):allowed.update(('C'+str(i+off),p) for p in ('1','2'))
  for i in (14,19,20):allowed.update(('D'+str(i+off),p) for p in ('1','2'))
  allowed.update(('U1',p) for p in (['90','91','35'] if m==1 else ['59','60','61']))
 allowed.update(p for p in after if p not in before)
 changes=[]
 focrefs=set()
 for m in (1,2):
  _,r=load(W/f'FOC_M{m}.kicad_sch');focrefs.update(prop(n,'Reference') for n in r.kids('symbol'))
 for p in before:
  if p[0] in focrefs and p not in allowed:
   b=before[p]-allowed;a=after.get(p,frozenset())-allowed
   if b!=a:changes.append({'pin':p,'removed':sorted(b-a),'added':sorted(a-b)})
 result={'unexpected_FOC_connectivity_changes':changes}
 for m in (1,2):
  u=f'U{9100+m}'
  for inp,out,ch in [('1','7','A'),('6','2','B'),('3','5','C')]:
   assert (u,inp) not in after[(u,out)]
   assert ('U1', ['90','91','35']['ABC'.index(ch)] if m==1 else ['59','60','61']['ABC'.index(ch)]) in after[(u,out)]
  assert ('U9101','8') in after[(u,'8')]
  assert ('U9101','4') in after[(u,'4')]
 for ref in ('CN47','CN1047'):
  for pin in ('1','2','3','4','5','6','7','8'):
   p=(ref,pin);assert before[p]-allowed==after[p]-allowed,(ref,pin)
 (W/'interface_review/hall_validation.json').write_text(json.dumps(result,indent=2),encoding='utf8')
 print(json.dumps(result,indent=2));assert not changes
