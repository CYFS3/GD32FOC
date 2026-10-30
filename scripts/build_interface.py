"""Build LCD/buttons using verified installed KiCad symbols and reference switch."""
from migrate_p2 import *
import math, xml.etree.ElementTree as ET
K=Path(r'C:\Users\RTT\AppData\Local\Programs\KiCad\10.0\share\kicad')
O=W/'interface_review';B=O/'baseline'
sheetid='b0b9e672-d7fc-4b99-999e-0258311f2764';rootpath='/df410b35-b24b-4f8c-aaa2-f94e7558172b';path=rootpath+'/'+sheetid
pieces=[];defs={};placements={};used=set()
existing={c.attrib['ref'] for c in ET.parse(B/'audit_netlist.xml').findall('.//components/comp')}
def definition(lib,name):
 s,r=load(K/'symbols'/(lib+'.kicad_sym'));n=next(n for n in r.kids('symbol') if n.items[1]==name)
 t=s[n.start:n.end].replace('(symbol "'+name+'"','(symbol "'+lib+':'+name+'"',1);defs[lib+':'+name]=t;return lib+':'+name
R=definition('Device','R');C=definition('Device','C');J=definition('Connector_Generic','Conn_01x08')
s,r=load(W.parent/'test/2_P1.kicad_sch');sw=next(n for n in r.kids('symbol') if prop(n,'Reference')=='SW5');SW=sw.val('lib_id');sd=next(n for n in r.one('lib_symbols').kids('symbol') if n.items[1]==SW);defs[SW]=s[sd.start:sd.end]
def copyfp(lib,name):
 src=K/'footprints'/(lib+'.pretty')/(name+'.kicad_mod');assert src.is_file();dst=W/'Interface.pretty';dst.mkdir(exist_ok=True)
 if not (dst/src.name).exists():shutil.copy2(src,dst/src.name)
 return 'Interface:'+name
rfp=copyfp('Resistor_SMD','R_0603_1608Metric');cfp=copyfp('Capacitor_SMD','C_0603_1608Metric');jfp=copyfp('Connector_PinHeader_2.54mm','PinHeader_1x08_P2.54mm_Vertical')
def field(k,v,x,y,hide=False):return f'(property {json.dumps(k)} {json.dumps(v)} (at {x:g} {y:g} 0) (effects (font (size 1 1))'+(' (hide yes)' if hide else '')+'))'
def add(lid,ref,value,fp,x,y,ang=0):
 assert ref not in existing|used,ref
 used.add(ref)
 extra=''
 if lid==SW:
  extra=field('Manufacturer','C&K',x,y,True)+field('Manufacturer Part','PTS815SJK250SMTRLFS',x,y,True)+field('Datasheet',prop(sw,'Datasheet') or '',x,y,True)
 pieces.append(f'(symbol (lib_id "{lid}") (at {x:g} {y:g} {ang}) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid()}")'+field('Reference',ref,x+6.35,y-3.81)+field('Value',value,x+6.35,y+3.81)+field('Footprint',fp,x,y,True)+extra+f'(instances (project "GD32F5_FOC" (path "{path}" (reference "{ref}") (unit 1)))))')
 pins={};d=parse(defs[lid]);a=math.radians(ang)
 for sub in d.kids('symbol'):
  for p in sub.kids('pin'):
   px,py,pa=map(float,p.one('at').items[1:]);pins[p.val('number')]=(round(x+px*math.cos(a)-py*math.sin(a),4),round(y-px*math.sin(a)-py*math.cos(a),4),int((pa+ang)%360))
 placements[ref]=pins;return pins
def endpoint(ref,pin,net,length=7.62):
 x,y,a=placements[ref][str(pin)];dx,dy={0:(-length,0),180:(length,0),90:(0,length),270:(0,-length)}[a];xx,yy=x+dx,y+dy
 pieces.extend([wire(x,y,xx,yy),label(net,xx,yy,0 if a in (0,270) else 180)])
def nc(ref,pin):
 x,y,_=placements[ref][str(pin)];pieces.append(f'(no_connect (at {x:g} {y:g}) (uuid "{uid()}"))')
add(J,'J300','LCD_3V3_WRITE_ONLY',jfp,76.2,55.88)
for i,net in enumerate(['VCC','GND','LCD_SCK','LCD_MOSI','LCD_CS_N','LCD_DC','LCD_RST_N','LCD_BL_CTRL'],1):endpoint('J300',i,net,12.7)
# Separate bias and bypass branches keep labels clear and expose every net.
for ref,value,x,net in [('R310','10k',124.46,'LCD_CS_N'),('R311','10k',162.56,'LCD_RST_N')]:
 add(R,ref,value,rfp,x,50.8);endpoint(ref,1,'VCC');endpoint(ref,2,net)
for ref,value,x in [('C300','100nF',218.44),('C301','10uF / 10V',256.54)]:
 add(C,ref,value,cfp,x,50.8);endpoint(ref,1,'VCC');endpoint(ref,2,'GND')
add(R,'R312','100R',rfp,124.46,93.98,90);endpoint('R312',1,'LCD_BL_GPIO');endpoint('R312',2,'LCD_BL_CTRL')
add(R,'R313','100k',rfp,218.44,93.98);endpoint('R313',1,'LCD_BL_CTRL');endpoint('R313',2,'GND')
pieces += [note('LCD MODULE / 3.3V LOGIC ONLY / WRITE-ONLY SPI0',25.4,20.32),note('J300 is a board-defined 1x8 2.54mm header, not a module pinout standard.\nUse a verified cable adapter. No MISO, SD card, touch or readback support.\nVCC = board 3.3V; check module current + board regulator thermal budget.\nPlace C300/C301 near J300; select effective bulk capacitance under DC bias.',25.4,116.84),note('BL_CTRL is a logic enable/PWM signal ONLY.\nNot a backlight LED power driver. Module must provide its own driver.\nR313 holds BL off at reset; verify the module active-high enable polarity.',190.5,116.84)]
for i,x in enumerate([50.8,152.4,254.0]):
 ref=f'SW{300+i}';net=f'BTN_{i+1}_N';raw=f'BTN_{i+1}_SW'
 add(SW,ref,'PTS815SJK250SMTRLFS',prop(sw,'Footprint'),x,193.04)
 endpoint(ref,1,'GND');endpoint(ref,4,raw);nc(ref,2);nc(ref,3)
 rr=f'R{314+i*2}';rp=f'R{315+i*2}';cc=f'C{302+i}'
 add(R,rr,'1k',rfp,x,160.02,90);endpoint(rr,1,raw);endpoint(rr,2,net)
 add(R,rp,'10k',rfp,x+27.94,228.6);endpoint(rp,1,'VCC');endpoint(rp,2,net)
 add(C,cc,'100nF',cfp,x-10.16,228.6);endpoint(cc,1,net);endpoint(cc,2,'GND')
pieces += [note('THREE ACTIVE-LOW LOCAL BUTTONS: PD2 / PD3 / PD4',25.4,142.24),note('SW300..302 reuse reference SW5/SW6 C&K symbol and footprint; pins 2/3 left NC as reference.\n10k pull-up + 100nF at GPIO; 1k switch-series resistor limits capacitor discharge.\nPressed level approximately 0.30V with 3.3V supply. Apply firmware debounce. No external button cable.',25.4,261.62)]
text='(kicad_sch (version 20250114) (generator "interface_builder") (uuid "'+uid()+'") (paper "A3") (lib_symbols\n'+'\n'.join(defs.values())+')\n'+'\n'.join(pieces)+'\n)'
# Complete all precondition checks before touching existing schematic files.
s,r=load(W/'MCU.kicad_sch');u=next(n for n in r.kids('symbol') if prop(n,'Reference')=='U1');d=next(n for n in r.one('lib_symbols').kids('symbol') if n.items[1]==u.val('lib_id'));x,y,a=map(float,u.one('at').items[1:]);assert a==0
mapping={'89':'LCD_SCK','32':'LCD_MOSI','92':'LCD_CS_N','93':'LCD_DC','3':'LCD_RST_N','4':'LCD_BL_GPIO','83':'BTN_1_N','84':'BTN_2_N','85':'BTN_3_N'}
ops=[];extra=[];audit={}
for sub in d.kids('symbol'):
 for p in sub.kids('pin'):
  num=p.val('number')
  if num not in mapping:continue
  px,py,pa=map(float,p.one('at').items[1:]);xx,yy=round(x+px,4),round(y-py,4)
  ncs=[n for n in r.kids('no_connect') if abs(float(n.one('at').items[1])-xx)<.01 and abs(float(n.one('at').items[2])-yy)<.01];assert len(ncs)==1,(num,ncs)
  ops.append((ncs[0].start,ncs[0].end,''));extra.append(label(mapping[num],xx,yy,0 if pa==0 else 180));audit[num]={'gpio':p.val('name'),'net':mapping[num],'position':[xx,yy]}
extra.append(note('LCD on Interface page: SPI0 SCK PB3 AF2 / MOSI PA7 AF0, TX only.\nCS PB6 / DC PB7 / RST PE4 / BL PE5 (GPIO or TIMER15_CH0 AF3).\nRelease PB3 JTDO/TRACESWO; SWD PA13/PA14 preserved.\nButtons PD2/PD3/PD4 are active-low. BL is logic only, not LED power.',150,174.0))
ops.append((len(s.rstrip())-1,len(s.rstrip())-1,'\n'+'\n'.join(extra)+'\n'))
ms=patches(s,ops)
rs,rr=load(W/'GD32F5_FOC.kicad_sch');n=rr.kids('sheet')[0];t=rs[n.start:n.end];t=re.sub(r'\((at) (-?[\d.]+) (-?[\d.]+)',lambda m:f'(at {float(m[2])+46.99:g} {float(m[3])+90:g}',t);t=t.replace(n.val('uuid'),sheetid).replace('"MCU"','"INTERFACE"').replace('"MCU.kicad_sch"','"Interface.kicad_sch"').replace('(page "2")','(page "7")');rs=rs.rstrip()[:-1]+'\n'+t+'\n)'
(W/'Interface.kicad_sch').write_text(text,encoding='utf-8');(W/'MCU.kicad_sch').write_text(ms,encoding='utf-8');(W/'GD32F5_FOC.kicad_sch').write_text(rs,encoding='utf-8')
f=W/'fp-lib-table';t=f.read_text(encoding='utf-8');assert '(name "Interface")' not in t;f.write_text(t.rstrip()[:-1]+'\n(lib (name "Interface") (type "KiCad") (uri "${KIPRJMOD}/Interface.pretty") (options "") (descr "Verified standard footprints for LCD and buttons"))\n)',encoding='utf-8')
(O/'interface_pinmap.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
print('Created Interface:',len(used),'components',sorted(used));print(json.dumps(audit,indent=2))
