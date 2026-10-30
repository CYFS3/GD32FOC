from migrate_p2 import *
import math,xml.etree.ElementTree as ET,hashlib
O=W/'oled_review';O.mkdir(exist_ok=True)
B=W/'interface_review/oled_baseline'
ss,sr=load(SRC/'2_P1.kicad_sch');ms,mr=load(B/'MCU.kicad_sch');s,r=load(B/'Interface.kicad_sch')
path='/df410b35-b24b-4f8c-aaa2-f94e7558172b/b0b9e672-d7fc-4b99-999e-0258311f2764'
refs=dict(zip('FPC1 C56 C57 C58 C59 C63 C65 R27 R30 R29 R31 R34 D3'.split(),'FPC300 C320 C321 C322 C323 C324 C325 R320 R321 R322 R323 R324 D300'.split()))
(O/'reference_mapping.json').write_text(json.dumps(refs,indent=2))
sources={prop(n,'Reference'):n for n in sr.kids('symbol') if prop(n,'Reference') in refs}
canonical={};netmap={'VCC':'VCC','GND':'GND','/P1/OLED_SCL':'OLED_SCL','/P1/OLED_SDA':'OLED_SDA'}
for n in ET.parse(W/'interface_review/reference_full.xml').findall('.//nets/net'):
 nodes=[(v.attrib['ref'],v.attrib['pin']) for v in n.findall('node') if v.attrib['ref'] in refs]
 if nodes:
  net=n.attrib['name'];netmap.setdefault(net,'OLED_N'+str(len(netmap)));canonical[net]=nodes
pin_nets={node:netmap[net] for net,nodes in canonical.items() for node in nodes}
def field(k,v,x,y,hide=False):return f'(property {json.dumps(k)} {json.dumps(v)} (at {x:.6f} {y:.6f} 0) (effects (font (size 1 1)) (justify left)'+(' (hide yes)' if hide else '')+'))'
def wire6(x,y,xx,yy):return f'(wire (pts (xy {x:.6f} {y:.6f}) (xy {xx:.6f} {yy:.6f})) (stroke (width 0) (type default)) (uuid "{uid()}"))'
def lab(net,x,y,ang):return f'(global_label "{net}" (shape bidirectional) (at {x:.6f} {y:.6f} {ang}) (effects (font (size 1 1)) (justify {"left" if ang==0 else "right"})) (uuid "{uid()}"))'
defs={n.items[1]:s[n.start:n.end] for n in r.one('lib_symbols').kids('symbol') if not n.items[1].endswith('Conn_01x08')}
for n in sr.one('lib_symbols').kids('symbol'):
 if n.items[1] in {v.val('lib_id') for v in sources.values()}:defs[n.items[1]]=ss[n.start:n.end]
for n in mr.one('lib_symbols').kids('symbol'):
 if n.items[1] in ['StylePower:VCC','StylePower:GND']:defs[n.items[1]]=ms[n.start:n.end]
pieces=[];pcount=9300
# Preserve complete button drawing, identifiers and placement byte-for-byte.
for n in r.items:
 if not isinstance(n,Node) or n.key in ['lib_symbols','uuid','paper','version','generator']:continue
 ys=[]
 if n.one('at'):ys=[float(n.one('at').items[2])]
 elif n.key=='wire':ys=[float(p.items[2]) for p in n.one('pts').kids('xy')]
 if ys and min(ys)>=140:pieces.append(s[n.start:n.end])
def power(net,x,y,ang=0):
 global pcount
 pcount+=1;ref=f'#PWR{pcount}'
 # horizontal power glyphs on dense connector have labels placed to their left
 tx,ty=(x-13,y) if ang else (x+2,y-2 if net=='VCC' else y+3)
 pieces.append(f'(symbol (lib_id "StylePower:{net}") (at {x:.6f} {y:.6f} {ang}) (unit 1) (in_bom no) (on_board yes) (uuid "{uid()}")'+field('Reference',ref,x,y,True)+field('Value',net,tx,ty)+f'(instances (project "GD32F5_FOC" (path "{path}" (reference "{ref}") (unit 1)))))')
positions={'FPC1':(85.09,68.58,0)}
for old,x,y in [('C56',145,43),('C57',205,43),('C58',265,43),('C59',325,43),('C63',145,83),('R27',205,83),('R30',265,83),('R29',325,83),('C65',145,121),('D3',205,121),('R31',265,121),('R34',325,121)]:positions[old]=(x,y,0)
placements={};proc=[]
for old,new in refs.items():
 n=sources[old];x,y,angle=positions[old];lid=n.val('lib_id');fp=prop(n,'Footprint')
 if old.startswith(('C','R')):
  name='c0402-无丝印-全尺寸_2' if old.startswith('C') else 'r0402-无丝印-全尺寸_1'
  source=SRC/'ProDoc_Board1v1_2026-10-26-import-fps.pretty'/(name+'.kicad_mod')
  _,fr=load(source);assert {p.items[1] for p in fr.kids('pad')}=={'1','2'}
  shutil.copy2(source,W/'Interface.pretty'/source.name);fp='Interface:'+name
 if old=='FPC1':
  name=fp.split(':')[1];source=SRC/'ProDoc_Board1v1_2026-10-26-import-fps.pretty'/(name+'.kicad_mod');dest=W/'Interface.pretty'/source.name;shutil.copy2(source,dest);fp='Interface:'+name
 t=f'(symbol (lib_id {json.dumps(lid)}) (at {x:.6f} {y:.6f} {angle}) (unit 1) (in_bom yes) (on_board yes) (uuid "{uid()}")'
 for p in n.kids('property'):
  k,v=p.items[1:3]
  if k=='Reference':v=new
  if k=='Footprint':v=fp
  t+=field(k,v,x+10 if old=='FPC1' else x-6,y-8 if k=='Reference' else y-5,k not in ['Reference','Value'])
 t+=f'(instances (project "GD32F5_FOC" (path "{path}" (reference "{new}") (unit 1)))))';pieces.append(t)
 d=parse(defs[lid]);placements[new]={}
 for sub in d.kids('symbol'):
  for p in sub.kids('pin'):
   px,py,a=map(float,p.one('at').items[1:]);xx,yy=x+px,y-py;net=pin_nets[(old,p.val('number'))];placements[new][p.val('number')]=[xx,yy,net]
   if net in ['VCC','GND']:
    if old=='FPC1':ex,ey=xx-(20.32 if p.val('number')=='12' else 12.7),yy;pieces.append(wire6(xx,yy,ex,ey));power(net,ex,ey,90)
    else:ex,ey=xx,yy+(-7.62 if a==90 else 7.62 if a==270 else 0);ex+=-7.62 if a==0 else 7.62 if a==180 else 0;pieces.append(wire6(xx,yy,ex,ey));power(net,ex,ey)
   else:
    # Direct anchors face away from body, no text through symbol.
    pieces.append(lab(net,xx,yy,180 if a==0 else 0))
 proc.append({'reference':new,'source':old,'value':prop(n,'Value'),'mpn':prop(n,'Manufacturer Part'),'supplier_part':prop(n,'Supplier Part'),'footprint':fp,'position':[x,y,angle]})
pieces += [note('OLED1.29 REFERENCE / 16-PIN 0.5mm FPC / 3.3V',25.4,15.24),note('FPC300: AFC07-S16ECA-00; mounting pads 17/18 grounded.',25.4,20.32),note('I2C0: PB6 AF1 = SCL; PB7 AF1 = SDA. Original hardware straps + RC reset retained.',25.4,25.4)]
# Convert remaining button power labels to the same StylePower glyphs.
newpieces=[]
for t in pieces:
 n=parse(t)
 if n.key=='global_label' and n.items[1] in ['VCC','GND']:
  x,y,a=map(float,n.one('at').items[1:]);before=len(pieces);power(n.items[1],x,y);newpieces.append(pieces.pop())
 else:newpieces.append(t)
pieces=newpieces
text=f'(kicad_sch (version 20250114) (generator "oled_reference_migration") (uuid "{r.val("uuid")}") (paper "A3") (lib_symbols\n'+ '\n'.join(defs.values())+')\n'+'\n'.join(pieces)+'\n)'
(W/'Interface.kicad_sch').write_text(text,encoding='utf-8')
ops=[]
for n in mr.kids('global_label'):
 net=n.items[1]
 if net in ['LCD_CS_N','LCD_DC']:ops.append((n.start,n.end,ms[n.start:n.end].replace(net,{'LCD_CS_N':'OLED_SCL','LCD_DC':'OLED_SDA'}[net])))
 elif net in ['LCD_MOSI','LCD_SCK','LCD_RST_N','LCD_BL_GPIO']:
  x,y=map(float,n.one('at').items[1:3]);ops.append((n.start,n.end,f'(no_connect (at {x:.6f} {y:.6f}) (uuid "{uid()}"))'))
for n in mr.kids('text'):
 if any(k in n.items[1] for k in ['LCD:','CS PB6','PE5 may','Release PB3','BL is logic','BL: GPIO']):ops.append((n.start,n.end,''))
ops.append((len(ms.rstrip())-1,len(ms.rstrip())-1,note('OLED1.29: I2C0 PB6 AF1 SCL / PB7 AF1 SDA.',285,210)+note('Reference RC reset; PA7/PB3/PE4/PE5 unused (NC).',285,213.5)))
(W/'MCU.kicad_sch').write_text(patches(ms,ops),encoding='utf-8')
(O/'procurement.json').write_text(json.dumps(proc,indent=2),encoding='utf-8')
(O/'canonical_nodes.json').write_text(json.dumps({'reference_mapping':refs,'net_mapping':netmap,'reference_nodes':canonical,'placements':placements},indent=2),encoding='utf-8')
print('Installed',len(refs),'OLED components; mapping written',O/'reference_mapping.json')
