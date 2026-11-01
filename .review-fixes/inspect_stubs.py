from pin_types import *
exec(Path('.review-gd32/crystal_work.py').read_text(encoding='utf8').split("s=P('MCU.kicad_sch')")[0])
e=json.loads(Path('.review-gd32/erc-after.json').read_text(encoding='utf8'));ids={i['uuid'] for sh in e['sheets'] for v in sh['violations'] if v['type']=='unconnected_wire_endpoint' for i in v['items']}
for f in Path('.').glob('*.kicad_sch'):
 s=parse(f.read_text(encoding='utf8'))
 for w in children(s,'wire'):
  if one(w,'uuid')[1] not in ids:continue
  print('\n',f,w)
  pts=children(one(w,'pts'),'xy'); coords=[tuple(map(float,p[1:])) for p in pts]
  for n in s[1:]:
   if not isinstance(n,list) or n[0] not in ['wire','junction','label','global_label','no_connect','symbol']:continue
   positions=children(one(n,'pts'),'xy') if one(n,'pts') else children(n,'at')
   if any(abs(float(p[1])-x)<3 and abs(float(p[2])-y)<3 for p in positions for x,y in coords):print('NEAR',str(n)[:450])
