from migrate_p2 import *
from math import *
ROOT='/df410b35-b24b-4f8c-aaa2-f94e7558172b'
s,r=load(W/'MCU.kicad_sch');u=next(n for n in r.kids('symbol') if prop(n,'Reference')=='U1');lib=next(n for n in r.one('lib_symbols').kids('symbol') if n.items[1]==u.val('lib_id'))
mapping={'23':'M1_IA','24':'M1_IB','25':'M1_IC','26':'M2_IA','29':'M2_IB','30':'M2_IC','18':'M1_IBUS','34':'M2_IBUS','33':'M1_VBUS','38':'M1_NTC','39':'M2_NTC','90':'M1_QEI1_A','91':'M1_QEI1_B','35':'M1_QEI1_Z','59':'M2_QEI1_A','60':'M2_QEI1_B','61':'M2_QEI1_Z','78':'SPI2_SCK','79':'SPI2_MISO','80':'SPI2_MOSI','1':'M1_SPI1_CS0','2':'M2_SPI1_CS0','51':'M1_BRKIN','31':'M2_BRKIN','67':'M1_HIN1','68':'M1_HIN2','69':'M1_HIN3','52':'M1_LIN1','53':'M1_LIN2','54':'M1_LIN3','63':'M2_HIN1','64':'M2_HIN2','65':'M2_HIN3','15':'M2_LIN1','16':'M2_LIN2','17':'M2_LIN3','72':'SWDIO','76':'SWCLK','14':'NRST','94':'BOOT0','37':'BOOT1'}
ops=[];extra=[];sx,sy,_=map(float,u.one('at').items[1:])
# Replace only old U1 pin stubs and their labels, preserving all support circuits.
pins=[p for b in lib.kids('symbol') for p in b.kids('pin')];ends=[]
for pin in pins:
 num,name=pin.val('number'),pin.val('name');px,py,pa=map(float,pin.one('at').items[1:]);x,y=sx+px,sy-py;xx=x+(-7.62 if pa==0 else 7.62);ends.append(((x,y),(xx,y)))
 net=mapping.get(num)
 if name in ('VDD','VBAT'):net='VCC'
 if name in ('VDDA','VREFP'):net='MCU_VDDA'
 if name=='VSS':net='GND'
 if name in ('VSSA','VREFN'):net='AGND'
 if net:extra.extend([wire(x,y,xx,y),label(net,xx,y,0 if pa==0 else 180)])
 elif name!='NC':extra.append(f'(no_connect (at {x:g} {y:g}) (uuid "{uid()}"))')
def near(a,b):return abs(a[0]-b[0])<0.001 and abs(a[1]-b[1])<0.001
for n in r.kids('wire'):
 ps=[tuple(map(float,p.items[1:3])) for p in n.one('pts').kids('xy')]
 if any((near(ps[0],a) and near(ps[1],b)) or (near(ps[0],b) and near(ps[1],a)) for a,b in ends):ops.append((n.start,n.end,''))
for n in r.kids('global_label'):
 pos=tuple(map(float,n.one('at').items[1:3]))
 if any(near(pos,b) for a,b in ends):ops.append((n.start,n.end,''))
extra.append(note('M1 TIMER0: PA8/9/10 AF1; PB13/14 AF2, PB15 AF1. BRKIN PB12 AF4.\nM2 TIMER7: PC6/7 AF3, PC8 AF2; PC0/1/2 AF0. BRKIN PA6 AF4.\nM1 currents PA0/1/2; M2 currents PA3/4/5 (ADC0/ADC1).\nIBUS: PC3 / PC5; VBUS PC4; NTC PE7 / PE8 (ADC2).\nHall M1 PB4/5/0 TIMER2; M2 PD12/13/14 TIMER3. Release PB4 JTAG, keep SWD.\nShared SPI2 PC10/11/12 AF2; GPIO chip selects PE2 / PE3.\nVA/VB/VC/COM and M2_VBUS stay on power-sheet testpoints, not MCU ADC.',150,250))
ops.append((len(s.rstrip())-1,len(s.rstrip())-1,'\n'+'\n'.join(extra)+'\n'))
(W/'MCU.kicad_sch').write_text(patches(s,ops),encoding='utf-8')
# Fault contract: active HIGH break, externally held LOW only while healthy.
s,r=load(W/'MCU.kicad_sch')
s=s.replace('external open-drain fault asserts LOW.','external open-drain HEALTH holds LOW only while healthy.').replace('Configure each timer break polarity LOW.','Configure each timer break polarity HIGH; unplugged defaults to brake.')
(W/'MCU.kicad_sch').write_text(s,encoding='utf-8')
# Pull all six logic inputs LOW if MCU resets or is disconnected.
base=Path(r'C:\Users\RTT\AppData\Local\Programs\KiCad\10.0\share\kicad\symbols\Device.kicad_sym');ts,rr=load(base);rn=next(n for n in rr.kids('symbol') if n.items[1]=='R');definition=ts[rn.start:rn.end].replace('(symbol "R"','(symbol "Device:R"',1)
manifest=json.loads((W/'dual_review/split_manifest.json').read_text(encoding='utf-8'))
for index in (1,2):
 f=W/f'FOC_M{index}.kicad_sch';s,r=load(f);ops=[];extra=[];path=ROOT+'/'+manifest['sheets'][f'FOC_M{index}']['uuid']
 for n in r.kids('global_label'):
  name=n.items[1]
  for signal in ('SCK','MISO','MOSI'):
   if name==f'M{index}_SPI1_{signal}':ops.append((n.start,n.end,s[n.start:n.end].replace(json.dumps(name),json.dumps('SPI2_'+signal),1)))
 for j,signal in enumerate(('HIN1','HIN2','HIN3','LIN1','LIN2','LIN3')):
  x,y=270+j*28,345;ref=f'R{300+j+(index-1)*1000}'
  extra.append(f'(symbol (lib_id "Device:R") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (uuid "{uid()}") (property "Reference" "{ref}" (at {x+3} {y-1} 0) (effects (font (size 1 1)) (justify left))) (property "Value" "10k" (at {x+3} {y+1} 0) (effects (font (size 1 1)) (justify left))) (property "Footprint" "Resistor_SMD:R_0603_1608Metric" (at {x} {y} 0) (effects (font (size 1 1)) (hide yes))) (instances (project "GD32F5_FOC" (path "{path}" (reference "{ref}") (unit 1)))))')
  extra.extend([label(f'M{index}_{signal}',x,y-3.81),label('GND',x,y+3.81)])
 ops.extend([(r.one('lib_symbols').end-1,r.one('lib_symbols').end-1,'\n'+definition+'\n'),(len(s.rstrip())-1,len(s.rstrip())-1,'\n'+'\n'.join(extra)+'\n')]);f.write_text(patches(s,ops),encoding='utf-8')
(W/'dual_review/pin_mapping.json').write_text(json.dumps(mapping,indent=2),encoding='utf-8')
print('Mapped dual PWM/ADC/Hall/SPI/fault interfaces; fitted 12 gate logic pulldowns.')
