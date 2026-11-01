from pathlib import Path as P
import re,json,uuid,copy,hashlib
exec(P('.review-gd32/crystal_work.py').read_text().split("s=P('MCU.kicad_sch')")[0])
exec(P('.review-gd32/apply_crystal.py').read_text().split("f=P('MCU.kicad_sch')")[0].split('def uid():')[1].join(['def uid():','']) if False else P('.review-gd32/apply_crystal.py').read_text().split("f=P('MCU.kicad_sch')")[0])
s=P('.review-fixes/MCU.before-fixes.kicad_sch').read_text(encoding='utf8'); tree=parse(s)
# Exact top-level blocks preserving original formatting outside edits.
def topblocks(text):
 out=[];i=text.index('(')+1
 while i<len(text):
  if text[i]=='(':
   b=block(text,i);out.append(b);i+=len(b)
  else:i+=1
 return out
def repl_node(node, transform):
 global s
 for b in topblocks(s):
  if parse(b)==node:s=s.replace(b,transform(b),1);return
 raise Exception('node not found')
for n in children(tree,'symbol'):
 ref=next(p[2] for p in children(n,'property') if p[1]=='Reference')
 if ref in ['C206','C208']:repl_node(n,lambda b:b.replace('(property "Value" "100nF"','(property "Value" "10nF"',1))
# Reposition existing note blocks to remove old crystal overlap, retaining semantics.
for n in children(tree,'text'):
 t=n[1]
 if t.startswith('MCU_VDDA ='):
  repl_node(n,lambda b: b.replace('(at 150 210 0)','(at 245 230 0)').replace('bypass C206..C208 to AGND.','bypass C206/C207 + C208/C213 to AGND.').replace('FAULT inputs use pullups; external open-drain HEALTH holds LOW only while healthy.','FAULT pullups: external open-drain HEALTH holds LOW while healthy.').replace('Configure each timer break polarity HIGH; unplugged defaults to brake. No autonomous trip comparator fitted.','Timer break polarity HIGH; unplugged defaults to brake.\\nNo autonomous trip comparator fitted.').replace('Current limits/thresholds and external fault source remain to be designed.','Current limits and external fault source remain to be designed.'))
 if t.startswith('M1 TIMER0:'):
  repl_node(n,lambda b:b.replace('(at 150 250 0)','(at 15 220 0)').replace('M1 TIMER0: PA8/9/10 AF1; PB13/14 AF2, PB15 AF1. BRKIN PB12 AF4.','M1 TIMER0: PA8/9/10 AF1; PB13/14 AF2, PB15 AF1.\\nBRKIN PB12 AF4.').replace('M2 TIMER7: PC6/7 AF3, PC8 AF2; PC0/1/2 AF0. BRKIN PA6 AF4.','M2 TIMER7: PC6/7 AF3, PC8 AF2; PC0/1/2 AF0.\\nBRKIN PA6 AF4.').replace('VA/VB/VC/COM and M2_VBUS stay on power-sheet testpoints, not MCU ADC.','VA/VB/VC/COM and M2_VBUS: power-sheet testpoints.'))
# Import a standard testpoint, no project library edits.
txt=P(r'D:\KiCad\HQ10.0\share\kicad\symbols\Connector.kicad_sym').read_text(encoding='utf8');b=block(txt,txt.index('(symbol "TestPoint"')).replace('(symbol "TestPoint"','(symbol "Connector:TestPoint"',1)
p=s.index('(lib_symbols')+len('(lib_symbols');s=s[:p]+'\n'+b+s[p:]
inst='/df410b35-b24b-4f8c-aaa2-f94e7558172b/023525dc-8b31-4272-8a5f-3c0381bf9655';add=[]
def prop(k,v,x,y,hide=False):return f'(property {json.dumps(k)} {json.dumps(v)} (at {x} {y} 0)'+(' (hide yes)' if hide else '')+' (effects (font (size 1 1))))'
def sym(lib,ref,val,x,y,pins,fp='',power=False):
 t=f'(symbol (lib_id "{lib}") (at {x} {y} 0) (unit 1) (in_bom {"no" if power else "yes"}) (on_board {"no" if power else "yes"}) (dnp no) (uuid "{uid()}")'
 t+=prop('Reference',ref,x+5,y-2,power)+prop('Value',val,x if power else x+6,(y+3.81 if val in ['GND','AGND'] else y-3.81) if power else y+2,False)+prop('Footprint',fp,x,y,True)
 t+=''.join(f'(pin "{p}" (uuid "{uid()}"))' for p in pins)
 t+=f'(instances (project "GD32F5_FOC" (path "{inst}" (reference "{ref}") (unit 1)))))';add.append(t)
def wire(x,y,a,b):add.append(f'(wire (pts (xy {x} {y}) (xy {a} {b})) (stroke (width 0) (type default)) (uuid "{uid()}"))')
def text(t,x,y):add.append(f'(text {json.dumps(t)} (at {x} {y} 0) (effects (font (size 1 1)) (justify left top)) (uuid "{uid()}"))')
def label(t,x,y):add.append(f'(global_label "{t}" (shape bidirectional) (at {x} {y} 0) (effects (font (size 1 1)) (justify left)) (uuid "{uid()}"))')
refs={p[2] for n in children(tree,'symbol') for p in children(n,'property') if p[1]=='Reference'}
assert not refs & {'C212','C213','TP200','#PWR9041','#PWR9042','#PWR9043','#PWR9044'}
for ref,val,x,net,ground,idx in [('C212','100nF',254,'VCC','GND',9041),('C213','1uF',292.1,'MCU_VDDA','AGND',9043)]:
 y=63.5;sym('Device:C',ref,val,x,y,['1','2'],'Capacitor_SMD:C_0603_1608Metric')
 sym('StylePower:'+net,'#PWR'+str(idx),net,x,y-3.81,['1'],power=True)
 sym('StylePower:'+ground,'#PWR'+str(idx+1),ground,x,y+3.81,['1'],power=True)
text('C212: place at U1.6 VBAT / GND.\nVBAT remains tied to VCC.',242.57,74.93)
text('U1.22 VDDA: C206 10nF + C207 1uF.\nU1.21 VREFP: C208 10nF + C213 1uF.\nPlace each pair at its pin, return to AGND.\nMCU_VDDA remains common (R203).',285.75,74.93)
sym('Connector:TestPoint','TP200','NRST',254,95.25,['1'],'TestPoint:TestPoint_Pad_D1.5mm')
wire(254,95.25,254,99.06);label('NRST',254,99.06)
text('TP200: external probe reset access (open-drain).\nUse J200 GND; J200 remains 4-pin.',264.16,91.44)
for x,y in [(201.93,59.69),(201.93,36.83)]:add.append(f'(no_connect (at {x} {y}) (uuid "{uid()}"))')
s=s[:s.rfind(')')]+'\n'+'\n'.join(add)+'\n'+s[s.rfind(')'):]
P('.review-fixes/MCU.candidate.kicad_sch').write_text(s,encoding='utf8')
print('Candidate written')
