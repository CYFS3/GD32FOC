from migrate_p2 import *
import math
OUT=W/'dual_review'
ROOT='/df410b35-b24b-4f8c-aaa2-f94e7558172b/023525dc-8b31-4272-8a5f-3c0381bf9655'
BASE=Path(r'C:\Users\RTT\AppData\Local\Programs\KiCad\10.0\share\kicad\symbols')
def standard(lib,name):
 t,r=load(BASE/(lib+'.kicad_sym'));n=next(n for n in r.kids('symbol') if n.items[1]==name)
 return t[n.start:n.end].replace('(symbol "'+name+'"','(symbol "'+lib+':'+name+'"',1),n
s,r=load(W/'MCU.kicad_sch');extra=[];ops=[]
# VDDA/VREFP and the three associated bypass caps now derive from MCU VDD.
for n in r.kids('global_label'):
 if n.items[1]=='AVCC':ops.append((n.start,n.end,s[n.start:n.end].replace('"AVCC"','"MCU_VDDA"',1)))
for n in r.kids('text'):ops.append((n.start,n.end,''))
cache={}
for lib,name in [('Device','R'),('Connector_Generic','Conn_01x04')]:cache[lib+':'+name]=standard(lib,name)[1]
def part(lib,ref,value,x,y,fp):
 n=cache[lib];t=f'(symbol (lib_id "{lib}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid()}")'
 for k,v,dy in [('Reference',ref,-2),('Value',value,2),('Footprint',fp,4)]:
  t+=f' (property "{k}" "{v}" (at {x+3} {y+dy} 0) (effects (font (size 1 1)) (justify left)'+(' (hide yes)' if k=='Footprint' else '')+'))'
 t+=f' (instances (project "GD32F5_FOC" (path "{ROOT}" (reference "{ref}") (unit 1)))))';extra.append(t)
 return {p.val('number'):(x+float(p.one('at').items[1]),y-float(p.one('at').items[2])) for u in n.kids('symbol') for p in u.kids('pin')}
def connect(p,net):extra.append(label(net,*p))
p=part('Device:R','R203','0R VDDA LINK',275,145,'Resistor_SMD:R_0603_1608Metric');connect(p['1'],'VCC');connect(p['2'],'MCU_VDDA')
# Dedicated externally driven active-low fault inputs. Pullups and jumper-test connector,
# explicitly not an autonomous overcurrent circuit.
p=part('Connector_Generic:Conn_01x04','J201','FAULT INPUTS: 3V3 GND M1 M2',300,105,'Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical')
for pin,net in {'1':'VCC','2':'GND','3':'M1_BRKIN','4':'M2_BRKIN'}.items():connect(p[pin],net)
for idx in (1,2):
 p=part('Device:R',f'R{203+idx}','10k',270+(idx-1)*30,180,'Resistor_SMD:R_0603_1608Metric');connect(p['1'],'VCC');connect(p['2'],f'M{idx}_BRKIN')
extra.append(note('MCU_VDDA = VCC through R203 (0R), bypass C206..C208 to AGND.\nAVCC LDO remains for external analog amplifiers only.\nJ201: 1=3V3, 2=GND, 3=M1_BRKIN, 4=M2_BRKIN.\nFAULT inputs use pullups; external open-drain fault asserts LOW.\nConfigure each timer break polarity LOW. No autonomous trip comparator fitted.\nCurrent limits/thresholds and external fault source remain to be designed.',150,210))
ops.append((len(s.rstrip())-1,len(s.rstrip())-1,'\n'+'\n'.join(extra)+'\n'))
(W/'MCU.kicad_sch').write_text(patches(s,ops),encoding='utf-8')
# Canonicalize electrically equivalent sense returns: avoid conflicting global labels.
for index in (1,2):
 p=W/f'FOC_M{index}.kicad_sch';s,r=load(p);ops=[]
 for n in r.kids('global_label'):
  name=n.items[1];new=name
  if name==f'M{index}_IBUS-':new='PGND'
  elif name in [f'M{index}_'+z for z in ('IA-','IB-','IC-','IBUS+')]:new=f'M{index}_SHUNT_RETURN'
  if name!=new:ops.append((n.start,n.end,s[n.start:n.end].replace(json.dumps(name),json.dumps(new),1)))
 ops.append((len(s.rstrip())-1,len(s.rstrip())-1,'\n'+note('VA/VB/VC, COM, IBUS, NTC and auxiliary PWM are retained reference interfaces.\nOnly nets explicitly connected on MCU sheet are MCU functions.\nFD6288Q has no dedicated EN pin: hardware gate-input pulldowns are provided.\nBRKIN requires external fault generation; software must initialize PWM disabled.',15,370)+'\n'))
 p.write_text(patches(s,ops),encoding='utf-8')
print('Added VDDA link, dedicated fault connector and pullups; canonicalized shunt returns.')
