import sys,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from migrate_p2 import *
K=Path(r'C:\Users\RTT\AppData\Local\Programs\KiCad\10.0\share\kicad')
ls,lr=load(K/'symbols/74xGxx.kicad_sym');bn=next(n for n in lr.kids('symbol') if n.items[1]=='74LVC3G17')
bdef=ls[bn.start:bn.end].replace('(symbol "74LVC3G17"','(symbol "74xGxx:74LVC3G17"',1)
assert (K/'footprints/Package_SO.pretty/VSSOP-8_2.3x2mm_P0.5mm.kicad_mod').exists()
def pp(k,v,x,y,hide=False):return f'(property {json.dumps(k)} {json.dumps(v)} (at {x:.6f} {y:.6f} 0)'+(' (hide yes)' if hide else '')+' (effects (font (size 1 1))))'
def inst(lib,ref,val,x,y,path,unit=1,fp='',dnp=False):
 return f'(symbol (lib_id "{lib}") (at {x:.6f} {y:.6f} 0) (unit {unit}) (in_bom yes) (on_board yes) (dnp {"yes" if dnp else "no"}) (uuid "{uid()}")'+pp('Reference',ref,x,y-8)+pp('Value',val,x,y+8)+pp('Footprint',fp,x,y,True)+f'(instances (project "GD32F5_FOC" (path "{path}" (reference "{ref}") (unit {unit})))))'
def clean(s,n,value=None,dnp=None,desc=None):
 ops=[]
 for p in n.kids('property'):
  k=p.items[1]
  if k not in ('Reference','Value','Footprint'):ops.append((p.start-n.start,p.end-n.start,''))
  elif k=='Value' and value is not None:
   t=s[p.start:p.end];t=t.replace(json.dumps(p.items[2],ensure_ascii=False),json.dumps(value),1);ops.append((p.start-n.start,p.end-n.start,t))
 t=patches(s[n.start:n.end],ops)
 if dnp is not None:t=t.replace('(dnp no)',f'(dnp {"yes" if dnp else "no"})')
 if desc:t=t[:-1]+pp('Description',desc,*map(float,n.one('at').items[1:3]),True)+')'
 return t
for motor in (1,2):
 f=W/f'FOC_M{motor}.kicad_sch';s,r=load(f);ops=[];extra=[];offset=(motor-1)*1000
 ref=lambda prefix,i:prefix+str(i+offset)
 syms={prop(n,'Reference'):n for n in r.kids('symbol')}
 path=syms[ref('R',49)].one('instances').one('project').one('path').items[1]
 # Retain every unrelated connection, including auxiliary PWM and SPI.
 changes={**{ref('R',i):('100R',False) for i in (95,97,98)},**{ref('R',i):('10k',True) for i in (88,89,90)},**{ref('R',i):('1k',True) for i in (106,107,108)},**{ref('C',i):('100pF',True) for i in (82,83,84)}}
 for rr,(val,dnp) in changes.items():
  n=syms[rr];ops.append((n.start,n.end,clean(s,n,val,dnp,'Generic value; procurement MPN pending. DNP options require bandwidth review.' if dnp else 'Generic 100 ohm series resistor; procurement MPN pending.')))
 shunts=[]
 for rr,n in syms.items():
  if prop(n,'Value') and prop(n,'Value').startswith('1m') and rr.startswith('R'):
   ops.append((n.start,n.end,clean(s,n,desc='TBD 1mR power rating pending; incorrect 5mR procurement metadata removed.')));shunts.append(rr)
 for n in r.kids('global_label'):
  for ch in 'ABC':
   if n.items[1]==f'M{motor}_HALL_{ch}':ops.append((n.start,n.end,s[n.start:n.end].replace(f'M{motor}_HALL_{ch}',f'M{motor}_ENC_{ch}_IN')))
 def remove_wire(a,b):
  match=[n for n in r.kids('wire') if {tuple(map(float,p.items[1:3])) for p in n.one('pts').kids('xy')}=={a,b}];assert len(match)==1,(a,b)
  n=match[0];ops.append((n.start,n.end,''))
 remove_wire((238.76,264.16),(260.35,264.16));extra.append(label('VCC',238.76,264.16))
 remove_wire((208.28,267.97),(208.28,278.13));extra.append(label(f'M{motor}_ENC_VSUP',208.28,278.13))
 # Standard library buffer, with its exact unit pin definitions preserved.
 ops.append((r.one('lib_symbols').end-1,r.one('lib_symbols').end-1,'\n'+bdef+'\n'))
 u=f'U{9100+motor}'
 for unit,ch,x in [(1,'A',245.11),(2,'B',346.71),(3,'C',448.31)]:
  y=335.28;extra.append(inst('74xGxx:74LVC3G17',u,'SN74LVC3G17DCUR',x,y,path,unit,'Package_SO:VSSOP-8_2.3x2mm_P0.5mm'))
  extra.extend([wire(x-20.32,y,x-15.24,y),label(f'M{motor}_ENC_{ch}_IN',x-20.32,y),wire(x+12.7,y,x+17.78,y),label(f'M{motor}_HALL_{ch}',x+17.78,y,180)])
 x,y=546.1,340.36;extra.append(inst('74xGxx:74LVC3G17',u,'SN74LVC3G17DCUR',x,y,path,4,'Package_SO:VSSOP-8_2.3x2mm_P0.5mm'))
 extra.extend([label('VCC',x,y-10.16),label('GND',x,y+10.16)])
 # Reuse embedded imported capacitor symbol with verified local pin geometry.
 cap=next(n for n in r.one('lib_symbols').kids('symbol') if n.items[1]=='ProDoc_Boa-easyedapro:C0603_S')
 cap_pins=[p for sub in cap.kids('symbol') for p in sub.kids('pin')]
 for j,val in enumerate(('100nF','1uF')):
  cx,cy=520.7+j*43.18,370.84;cr=f'C{9101+(motor-1)*2+j}'
  extra.append(inst(cap.items[1],cr,val,cx,cy,path,fp='ProDoc_Board1v1_2026-10-26-import-fps:C0603_S'))
  for pin in cap_pins:
   px,py=map(float,pin.one('at').items[1:3]);extra.append(label('VCC' if pin.val('number')=='1' else 'GND',cx+px,cy-py))
 # Two mutually exclusive supply straps, 3.3V default. Device:R pin ends +/-3.81mm vertically.
 for j,rail in enumerate(('VCC','5V')):
  rx,ry=405.13+j*43.18,389.89;rr=f'R{9101+(motor-1)*2+j}'
  extra.append(inst('Device:R',rr,'0R' if not j else '0R (5V option)',rx,ry,path,fp='Resistor_SMD:R_0603_1608Metric',dnp=bool(j)))
  extra.extend([label(rail,rx,ry-3.81),label(f'M{motor}_ENC_VSUP',rx,ry+3.81)])
 extra.append(note(f'CN{5+offset}: Hall / single-ended ABZ (one mode at a time)\n1 GND; 2 C / Z; 3 B; 4 A; 5 auxiliary PWM (unused); 6 VSUP; 7/8 shield GND.\nDefault: 3.3V power and 3.3V push-pull signals. VCC = 3.3V.\n10k pullups, 1k pulldowns and 100pF EMI capacitors DNP.\nFit pullups only for open-drain after cable / edge-rate review.\nPin 6 supply: fit ONE 0R selector only; 5V option DNP.\n5V Hall / encoder operation pending TI datasheet validation.\nBuffer pinout from KiCad library; silicon / footprint review required before fabrication.',195.58,353.06))
 extra.append(note('Buffer decoupling: 100nF + 1uF close to pins 8 / 4.\nExisting 5V input clamps retained; power sequencing not validated.',485.14,396.24))
 ops.append((len(s.rstrip())-1,len(s.rstrip())-1,'\n'+'\n'.join(extra)+'\n'))
 f.write_text(patches(s,ops),encoding='utf-8');print(f.name,'modified',sorted(changes),'shunts',shunts)
