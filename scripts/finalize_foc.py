from migrate_p2 import *
for file in ['MCU.kicad_sch','power.kicad_sch']:
 s,r=load(W/file);ops=[]
 for n in r.kids('symbol'):
  if prop(n,'Reference').startswith('#'):
   for p in n.kids('property'):
    if p.items[1]=='Footprint' and p.items[2]:
     raw=s[p.start:p.end].replace(json.dumps(p.items[2],ensure_ascii=False),'""',1);ops.append((p.start,p.end,raw))
 if file=='MCU.kicad_sch':
  ops.append((len(s.rstrip())-1,len(s.rstrip())-1,'\n'+note('Alternate functions: PA8/9/10 AF1; PB13/14 AF2; PB15 AF1.\nSPI0 PA4..7 AF0. TIMER2 PC6..8 AF0.\nReference: official GD32EB F505VxT7.xml and AFIO GD32F505.xml.',150,218)+'\n'))
  ops.append((r.one('paper').start,r.one('paper').end,'(paper "A3")'))
 (W/file).write_text(patches(s,ops),encoding='utf-8')
print('Cleared meaningless power/graphics footprints; MCU sheet A3; AF mapping notes added.')
