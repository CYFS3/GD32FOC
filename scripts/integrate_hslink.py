"""Reference-preserving standalone HPM5301 debugger migration. Rebuild from backup."""
from migrate_p2 import *
import math
S=W.parent/'HPM'; B=W/'hslink_backup_20261026_155454'; O=W/'hslink_review';O.mkdir(exist_ok=True)
rootpath='/df410b35-b24b-4f8c-aaa2-f94e7558172b'; sheetid='92cc594b-d885-4848-b864-91d378b546ef'; path=rootpath+'/'+sheetid
ps,pr=load(B/'StylePower.kicad_sym'); defs={}; pieces=[]; refs={}; count=11000
rails={'GND':'GND','GND2':'HSL_SHIELD','VBUS2':'HSL_USB_VBUS','+5V':'HSL_5V','+3.3V':'HSL_3V3','+3.3V-T':'HSL_3V3_RAW','LINK_3.3V':'HSL_LINK_3V3','LINK_VDD_SOC':'HSL_VDD_SOC'}
sig=lambda n:'HSL_'+n.replace('.','_').replace('/','_')
def powerdef(name):
 base='GND' if name=='GND' or name=='HSL_SHIELD' else 'VCC';n=next(x for x in pr.kids('symbol') if x.items[1]==base)
 return ps[n.start:n.end].replace('"'+base+'"','"'+name+'"').replace('"'+base+'_','"'+name+'_')
def power(name,x,y,angle=0):
 global count
 count+=1;ref=f'#PWR{count}';defs['StylePower:'+name]=powerdef(name).replace('(symbol "'+name+'"','(symbol "StylePower:'+name+'"',1)
 return f'''(symbol (lib_id "StylePower:{name}") (at {x:g} {y:g} 0) (unit 1) (in_bom no) (on_board no) (dnp no) (uuid "{uid()}") (property "Reference" "{ref}" (at {x:g} {y:g} 0) (effects (font (size 1 1)) (hide yes))) (property "Value" "{name}" (at {x:g} {y+ (3.81 if name in ['GND','HSL_SHIELD'] else -3.81):g} 0) (effects (font (size 1 1)))) (instances (project "GD32F5_FOC" (path "{path}" (reference "{ref}") (unit 1)))))'''
def moved(t,dx,dy):
 return re.sub(r'\((at|xy) (-?[\d.]+) (-?[\d.]+)',lambda m:f'({m[1]} {float(m[2])+dx:g} {float(m[3])+dy:g}',t)
def renamed(t,old,new):
 return t.replace(f'(property "Reference" "{old}"',f'(property "Reference" "{new}"').replace(f'(reference "{old}")',f'(reference "{new}")')
for fn,dx,dy in [('4_DAP.kicad_sch',0,0),('3_POWER.kicad_sch',220,0)]:
 s,r=load(S/fn);ld={n.items[1]:s[n.start:n.end] for n in r.one('lib_symbols').kids('symbol')}
 def inside(x,y):return 44<=float(x)<=165 and 27<=float(y)<=65
 for n in r.items:
  if not isinstance(n,Node) or n.key not in ['symbol','wire','junction','label','global_label','no_connect']:continue
  if fn=='3_POWER.kicad_sch':
   if n.key=='wire':
    if not all(inside(*p.items[1:3]) for p in n.one('pts').kids('xy')):continue
   elif not n.one('at') or not inside(*n.one('at').items[1:3]):continue
  t=s[n.start:n.end]
  if n.key=='symbol':
   lid=n.val('lib_id');old=prop(n,'Reference');value=prop(n,'Value')
   if 'Drawing-Symbol' in lid:continue
   if old.startswith('#'):
    name=rails[value]
    if fn=='4_DAP.kicad_sch' and n.one('at').items[1:3]==['55.88','179.07']:name='VCC'
    x,y=map(float,n.one('at').items[1:3]);pieces.append(power(name,x+dx,y+dy));continue
   m=re.match(r'([A-Za-z]+)(\d+)',old);new=m[1]+str(int(m[2])+8000);refs[old]=new
   t=renamed(t,old,new);t=reinstance(t,path)
   if value=='':t=t.replace('(property "Value" ""',f'(property "Value" {json.dumps(lid.split(":",1)[1],ensure_ascii=False)}')
   defs[lid]=ld[lid]
  elif n.key in ['label','global_label']:
   name=sig(n.items[1]);x,y,a=map(float,n.one('at').items[1:]);t=label(name,x,y,a)
  t=re.sub(r'\(uuid "[^"]+"\)',lambda m:'(uuid "'+uid()+'")',t)
  pieces.append(moved(t,dx,dy))
# Five 0-ohm assembly links reuse validated reference resistor definition and footprint.
s,r=load(S/'4_DAP.kicad_sch');template=next(n for n in r.kids('symbol') if prop(n,'Reference')=='R52');raw=s[template.start:template.end]
connections=[('HSL_JTAG_TMS','SWDIO'),('HSL_JTAG_TCK','SWCLK'),('HSL_D_RESETN','NRST'),('HSL_PA00_UART0_TXD','HSL_TARGET_UART_TX'),('HSL_PA01_UART0_RXD','HSL_TARGET_UART_RX')]
for i,(a,b) in enumerate(connections):
 x,y=285,100+i*15.24;ref='R'+str(8901+i);t=moved(raw,x-158.75,y-68.58);t=renamed(t,'R52',ref);t=reinstance(t,path);t=t.replace('(dnp no)','(dnp yes)');t=t.replace('(property "Value" "0R"','(property "Value" "0R DNP / CLOSE TO ENABLE"');t=re.sub(r'\(uuid "[^"]+"\)',lambda m:'(uuid "'+uid()+'")',t);pieces += [t,label(a,x-5.08,y,0),label(b,x+5.08,y,180)]
pieces += [note('HPM5301 REFERENCE DEBUGGER / HSLink-style hardware\nUSB-powered debugger; target remains powered by board supply.\nReference GPIO mapping retained. Firmware compatibility NOT verified.',255,65),note('TARGET LINKS R8901..R8905: DEFAULT DNP / OPEN\nFit 0R only with target VCC present. Remove before external J200 probe\nor debugging with target unpowered. NO automatic backfeed isolation.\nSWDIO / SWCLK / NRST / target TX / target RX (top to bottom).\nJ200 and onboard debugger must never drive target simultaneously.',255,183),note('H8001 pin1 = target VCC reference ONLY; no target power injection.\nNo validated ADC voltage sensing or firmware power-off tri-state.\nH8001 other signals remain debugger side of target disconnect links.\nHSL_TARGET_UART_TX = GD32 PD5 USART1_TX AF0 -> probe RX.\nHSL_TARGET_UART_RX = GD32 PD6 USART1_RX AF0 <- probe TX.',255,224),note('Reference: HPM 4_DAP + isolated 3_POWER 5V/3.3V block.\nUSB1 / EtherCAT / HPM main-controller circuit intentionally excluded.\nUSB footprint and firmware require validation before PCB fabrication.',15,230)]
text='(kicad_sch (version 20250114) (generator "hslink_migration") (uuid "'+uid()+'") (paper "A3") (lib_symbols\n'+'\n'.join(defs.values())+')\n'+'\n'.join(pieces)+'\n)'
(W/'HSLink.kicad_sch').write_text(text,encoding='utf-8')
# Add hierarchical page without disturbing prior pages.
s,r=load(B/'GD32F5_FOC.kicad_sch');n=r.kids('sheet')[0];t=s[n.start:n.end];t=moved(t,0,90);t=t.replace(n.val('uuid'),sheetid).replace('"MCU"','"HSL_DEBUGGER"').replace('"MCU.kicad_sch"','"HSLink.kicad_sch"').replace('(page "2")','(page "6")');s=s.rstrip()[:-1]+'\n'+t+'\n)';(W/'GD32F5_FOC.kicad_sch').write_text(s,encoding='utf-8')
# Target USART1 PD5/PD6 confirmed free by parent datasheet/pin audit.
s,r=load(B/'MCU.kicad_sch');u=next(n for n in r.kids('symbol') if prop(n,'Reference')=='U1');d=next(n for n in r.one('lib_symbols').kids('symbol') if n.items[1]==u.val('lib_id'));x,y,ang=map(float,u.one('at').items[1:]);assert ang==0
extra=[];ops=[]
for sub in d.kids('symbol'):
 for p in sub.kids('pin'):
  if p.val('number') not in ['86','87']:continue
  px,py,a=map(float,p.one('at').items[1:]);xx,yy=x+px,y-py
  extra.append(label('HSL_TARGET_UART_TX' if p.val('number')=='86' else 'HSL_TARGET_UART_RX',xx,yy,0 if a==0 else 180))
  for nc in r.kids('no_connect'):
   if abs(float(nc.one('at').items[1])-xx)<.01 and abs(float(nc.one('at').items[2])-yy)<.01:ops.append((nc.start,nc.end,''))
extra.append(note('Onboard debugger: HSLink page; R8901..R8905 are default-open.\nJ200 external probe: never use simultaneously with onboard probe.\nUSART1 bridge PD5/TX, PD6/RX; target must be powered before enabling links.',150,175))
ops.append((len(s.rstrip())-1,len(s.rstrip())-1,'\n'+'\n'.join(extra)+'\n'));(W/'MCU.kicad_sch').write_text(patches(s,ops),encoding='utf-8')
# Local libraries; source remains untouched.
shutil.copy2(S/'ProDoc_IPB-easyedapro.kicad_sym',W/'ProDoc_IPB-easyedapro.kicad_sym');fp='ProDoc_IPB-TINY_2026-10-26-import-fps';shutil.copytree(S/(fp+'.pretty'),W/(fp+'.pretty'),dirs_exist_ok=True)
for fn,name,ext in [('sym-lib-table','ProDoc_IPB-easyedapro','kicad_sym'),('fp-lib-table',fp,'pretty')]:
 s=(B/fn).read_text(encoding='utf-8');s=s.rstrip()[:-1]+f'\n(lib (name "{name}") (type "KiCad") (uri "${{KIPRJMOD}}/{name}.{ext}") (options "") (descr "HPM debugger reference"))\n)';
 if fn=='fp-lib-table':s=s.rstrip()[:-1]+f'\n(lib (name "ProDoc_IPB-easyedapro") (type "KiCad") (uri "${{KIPRJMOD}}/{fp}.pretty") (options "") (descr "HPM imported footprint alias"))\n)'
 (W/fn).write_text(s,encoding='utf-8')
names=set(rails.values())-{'GND'};s=ps.rstrip()[:-1]+'\n'+'\n'.join(powerdef(n) for n in sorted(names))+'\n)';(W/'StylePower.kicad_sym').write_text(s,encoding='utf-8')
(O/'reference_map.json').write_text(json.dumps(refs,indent=2),encoding='utf-8');print('Migrated',len(pieces),'objects',len(refs),'reference components')
