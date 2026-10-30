from migrate_p2 import *
# Only new Interface and MCU annotation objects; no electrical changes.
s,r=load(W/'Interface.kicad_sch');ops=[]
for n in r.kids('symbol'):
 if (prop(n,'Reference') or '').startswith('SW30'):
  x,y=map(float,n.one('at').items[1:3])
  for p in n.kids('property'):
   if p.items[1] in ['Reference','Value']:
    a=p.one('at');yy=y-8.89 if p.items[1]=='Reference' else y+10.16
    ops.append((a.start,a.end,f'(at {x:g} {yy:g} 0)'))
for n in r.kids('text'):
 if '\n' in n.items[1]:
  x,y=map(float,n.one('at').items[1:3]);ops.append((n.start,n.end,'\n'.join(note(line,x,y+i*3.5) for i,line in enumerate(n.items[1].splitlines()))))
(W/'Interface.kicad_sch').write_text(patches(s,ops),encoding='utf-8')
s,r=load(W/'MCU.kicad_sch');ops=[];extras=[]
names={'LCD_SCK','LCD_MOSI','LCD_CS_N','LCD_DC','LCD_RST_N','LCD_BL_GPIO','BTN_1_N','BTN_2_N','BTN_3_N'}
for n in r.kids('global_label'):
 if n.items[1] in names:
  x,y,a=map(float,n.one('at').items[1:]);left=x<80;xx=x
  ops.append((n.start,n.end,label(n.items[1],xx,y,180 if left else 0)))
for n in r.kids('text'):
 if n.items[1].startswith('LCD on Interface page:'):
  lines=['LCD: SPI0 SCK PB3 AF2 / MOSI PA7 AF0, TX only.','CS PB6 / DC PB7 / RST PE4 / BL PE5.','BL: GPIO or TIMER15_CH0 AF3; logic only, not LED power.','Release PB3 JTDO/TRACESWO; keep SWD PA13/PA14.','Buttons PD2/PD3/PD4 active-low. See Interface page.']
  ops.append((n.start,n.end,'\n'.join(note(t,285,210+i*3.5) for i,t in enumerate(lines))))
ops.append((len(s.rstrip())-1,len(s.rstrip())-1,'\n'+'\n'.join(extras)+'\n'));(W/'MCU.kicad_sch').write_text(patches(s,ops),encoding='utf-8')
print('Moved nine MCU labels outward, note into free right region; switch fields and note line spacing adjusted')
