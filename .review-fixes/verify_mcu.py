from pathlib import Path as P
import json,collections
exec(P('.review-gd32/crystal_work.py').read_text().split("s=P('MCU.kicad_sch')")[0])
def nets(f):
 t=parse(P(f).read_text(encoding='utf8'));return {one(n,'name')[1]:{(one(x,'ref')[1],one(x,'pin')[1]) for x in children(n,'node')} for n in children(one(t,'nets'),'net')}
b=nets('.review-fixes/mcu-before.net');a=nets('.review-fixes/mcu-after.net')
expected={'VCC':{('C212','1')},'GND':{('C212','2')},'MCU_VDDA':{('C213','1')},'AGND':{('C213','2')},'NRST':{('TP200','1')}}
assert set(a)==set(b),(set(a)-set(b),set(b)-set(a))
for k in b:assert a[k]==b[k]|expected.get(k,set()),(k,a[k]-b[k],b[k]-a[k])
print('PASS exact netlist delta: only C212 VCC/GND, C213 MCU_VDDA/AGND, TP200 NRST')
for f in ['mcu-before-erc.json','mcu-after-erc.json']:
 e=json.loads(P('.review-fixes/'+f).read_text(encoding='utf8'));v=[v for sh in e['sheets'] for v in sh['violations']]
 print(f,len(v),collections.Counter((x['severity'],x['type']) for x in v))
 if f.startswith('mcu-candidate'):
  for x in v:
   if any(any(ref in i['description'] for ref in ['C212','C213','TP200','#PWR904']) for i in x['items']):print(x)
