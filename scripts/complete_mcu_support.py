from migrate_p2 import *
import copy
s,r=load(W/'MCU.kicad_sch');extra=[];defs=[];rootpath='/df410b35-b24b-4f8c-aaa2-f94e7558172b/023525dc-8b31-4272-8a5f-3c0381bf9655'
# Standard KiCad passive/connector definitions, preserving standard pin geometry.
BASE=Path(r'C:\Users\RTT\AppData\Local\Programs\KiCad\10.0\share\kicad\symbols')
cache={}
for lib,name in [('Device','R'),('Device','C'),('Connector_Generic','Conn_01x04')]:
 t,rr=load(BASE/(lib+'.kicad_sym'));n=next(n for n in rr.kids('symbol') if n.items[1]==name)
 raw=t[n.start:n.end].replace('(symbol "'+name+'"','(symbol "'+lib+':'+name+'"',1)
 defs.append(raw);cache[lib+':'+name]=n

def part(lib,ref,value,x,y,fp):
 n=cache[lib];text=f'(symbol (lib_id "{lib}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid()}")'
 for k,v,dy in [('Reference',ref,-2),('Value',value,2),('Footprint',fp,4)]:
  text+=f' (property "{k}" "{v}" (at {x+3} {y+dy} 0)'+(' (hide yes)' if k=='Footprint' else '')+' (effects (font (size 1.0 1.0)) (justify left)))'
 text+=f' (instances (project "GD32F5_FOC" (path "{rootpath}" (reference "{ref}") (unit 1)))))';extra.append(text)
 return {p.val('number'):(x+float(p.one('at').items[1]),y-float(p.one('at').items[2])) for u in n.kids('symbol') for p in u.kids('pin')}
def connect(p,net):
 x,y=p;extra.append(label(net,x,y))
for i in range(5):
 p=part('Device:C','C'+str(200+i),'100nF',155+i*18,130,'Capacitor_SMD:C_0603_1608Metric');connect(p['1'],'VCC');connect(p['2'],'GND')
for i,(value,top,bot) in enumerate([('4.7uF','VCC','GND'),('100nF','AVCC','AGND'),('1uF','AVCC','AGND'),('100nF','AVCC','AGND')]):
 p=part('Device:C','C'+str(205+i),value,155+i*23,150,'Capacitor_SMD:C_0603_1608Metric');connect(p['1'],top);connect(p['2'],bot)
p=part('Device:R','R200','10k',160,175,'Resistor_SMD:R_0603_1608Metric');connect(p['1'],'VCC');connect(p['2'],'NRST')
p=part('Device:C','C209','100nF',185,175,'Capacitor_SMD:C_0603_1608Metric');connect(p['1'],'NRST');connect(p['2'],'GND')
p=part('Device:R','R201','10k',210,175,'Resistor_SMD:R_0603_1608Metric');connect(p['1'],'BOOT0');connect(p['2'],'GND')
p=part('Device:R','R202','10k',235,175,'Resistor_SMD:R_0603_1608Metric');connect(p['1'],'BOOT1');connect(p['2'],'GND')
# U1 PB2/BOOT1 pin 37 endpoint from original library.
extra.extend([wire(55.88,81.28,48.26,81.28),label('BOOT1',48.26,81.28)])
p=part('Connector_Generic:Conn_01x04','J200','SWD 3V3 GND DIO CLK',245,105,'Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical')
for pin,net in {'1':'VCC','2':'GND','3':'SWDIO','4':'SWCLK'}.items():connect(p[pin],net)
extra.append(note('MCU local decoupling: C200..204 one per VDD; C205 bulk.\nC206..208 analog/reference decoupling. R200/C209 reset.\nR201/R202 boot pulldowns. J200 SWD. Internal clock startup.\nPlace decouplers beside respective supply pins during PCB design.',150,195))
s=patches(s,[(r.one('lib_symbols').end-1,r.one('lib_symbols').end-1,'\n'+'\n'.join(defs)),(len(s.rstrip())-1,len(s.rstrip())-1,'\n'+'\n'.join(extra)+'\n')])
(W/'MCU.kicad_sch').write_text(s,encoding='utf-8')
# Make imported power reference annotations unique, and decorative frame non-electrical.
count=1
for f in ['MCU.kicad_sch','power.kicad_sch']:
 t,rr=load(W/f);ops=[]
 for n in rr.kids('symbol'):
  ref=prop(n,'Reference');raw=t[n.start:n.end]
  if ref.startswith('#'):
   new=f'#PWR{count:04}';count+=1;raw=raw.replace('"'+ref+'"','"'+new+'"')
  elif ref=='?':raw=raw.replace('"?"','"#FRAME1"')
  if f=='MCU.kicad_sch' and ref in ('U20','U2'):
   raw=raw.replace('"ProDoc_Boa-easyedapro:"','"ProDoc_Board1v1_2026-10-26-import-fps:SOT-23-5_L3.0-W1.7-P0.95-LS2.8-BR"')
  if raw!=t[n.start:n.end]:ops.append((n.start,n.end,raw))
 if f=='power.kicad_sch':ops.append((len(t.rstrip())-1,len(t.rstrip())-1,'\n'+note('REFERENCE NOTES: U11/R56/R58/R143/R144 are an illustrative op-amp example.\nCN1 source pin names conflict with rail polarity: verify connector before PCB.\n10 imported Short-Symbol graphics replaced by electrical wires.\n24V and DCBUS remain distinct source nets; auxiliary PWM is pending.',35,385)+'\n'))
 (W/f).write_text(patches(t,ops),encoding='utf-8')
print('Added decoupling/reset/boot/SWD; annotated power symbols; retained all source components.')
