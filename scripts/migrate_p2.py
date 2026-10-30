from pathlib import Path
import re,json,uuid,shutil,datetime
W=Path(__file__).resolve().parents[1]
SRC=W.parent/'test'
class Node:
 def __init__(self,items,start,end): self.items,self.start,self.end=items,start,end
 @property
 def key(self): return self.items[0] if self.items else ''
 def kids(self,k): return [x for x in self.items if isinstance(x,Node) and x.key==k]
 def one(self,k): return next(iter(self.kids(k)),None)
 def val(self,k):
  n=self.one(k);return n.items[1] if n else None

def parse(s):
 ts=list(re.finditer(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+',s)); i=0
 def node():
  nonlocal i
  start=ts[i].start();i+=1;items=[]
  while ts[i].group()!=')':
   if ts[i].group()=='(': items.append(node())
   else:
    t=ts[i].group();items.append(json.loads(t) if t.startswith('"') else t);i+=1
  end=ts[i].end();i+=1;return Node(items,start,end)
 return node()
def prop(n,k):return next((x.items[2] for x in n.kids('property') if x.items[1]==k),None)
def load(p):
 s=p.read_text(encoding='utf-8');return s,parse(s)
def patches(s,ops):
 for a,b,t in sorted(ops,reverse=True):s=s[:a]+t+s[b:]
 return s

def inspect():
 for f in [W/'MCU.kicad_sch',SRC/'1_P2.kicad_sch']:
  s,r=load(f);syms=r.kids('symbol')
  print(f.name,'symbols',len(syms),'refs',[(prop(x,'Reference'),prop(x,'Value')) for x in syms if not prop(x,'Reference').startswith('#')])
  print('local labels',sorted(set(x.items[1] for x in r.kids('label'))))
  if f.name=='MCU.kicad_sch':
   for n in r.one('lib_symbols').kids('symbol'):
    for u in n.kids('symbol'):
     for p in u.kids('pin'):print('PIN',p.val('number'),p.val('name'),p.one('at').items[1:])
   print('placement',syms[0].one('at').items)
  print('footprints',sorted(set(prop(x,'Footprint') for x in syms if prop(x,'Footprint'))))
def uid():return str(uuid.uuid4())
def wire(x,y,xx,yy):return f'(wire (pts (xy {x:g} {y:g}) (xy {xx:g} {yy:g})) (stroke (width 0) (type default)) (uuid "{uid()}"))'
def label(name,x,y,angle=0):return f'(global_label "{name}" (shape bidirectional) (at {x:g} {y:g} {angle}) (effects (font (size 1.0 1.0)) (justify {"left" if angle==0 else "right"})) (uuid "{uid()}"))'
def note(text,x,y):return '(text '+json.dumps(text)+' (at '+str(x)+' '+str(y)+' 0) (effects (font (size 1.27 1.27)) (justify left top)) (uuid "'+uid()+'"))'
def reinstance(text,rootpath,rename=None):
 text=re.sub(r'\(project "[^"]+"','(project "GD32F5_FOC"',text)
 text=re.sub(r'\(path "/[^"\n]+"','(path "'+rootpath+'"',text)
 if rename:
  for a,b in rename.items():
   text=text.replace('(property "Reference" "'+a+'"','(property "Reference" "'+b+'"').replace('(reference "'+a+'")','(reference "'+b+'")')
 return text

def migrate():
 backup=W/'migration_backup'/datetime.datetime.now().strftime('%Y%m%d_%H%M%S');backup.mkdir(parents=True)
 for f in ['GD32F5_FOC.kicad_sch','GD32F5_FOC.kicad_pro','MCU.kicad_sch','power.kicad_sch','fp-lib-table','sym-lib-table']:
  if (W/f).exists():shutil.copy2(W/f,backup/f)
 rootpath='/df410b35-b24b-4f8c-aaa2-f94e7558172b'
 s,r=load(SRC/'1_P2.kicad_sch');ops=[]
 ops.append((r.one('uuid').start,r.one('uuid').end,'(uuid "3271627e-84a4-4fb5-94ee-1de1e259061e")'))
 interfaces=set('HIN1 HIN2 HIN3 LIN1 LIN2 LIN3 IA IB IC IBUS VBUS COM NTC SPI1_MISO SPI1_MOSI SPI1_SCK SPI1_CS0 QEI1_A QEI1_B QEI1_Z PWM'.split())
 for n in r.kids('label'):
  if n.items[1] in interfaces:
   t=s[n.start:n.end].replace('(label ','(global_label ',1);t=t[:-1]+' (shape bidirectional))';ops.append((n.start,n.end,t))
 shorts=[]
 import math
 for n in r.kids('symbol'):
  if n.val('lib_id').endswith(':Short-Symbol'):
   a=n.one('at').items;x,y,ang=map(float,a[1:]);dx=2.54*math.cos(math.radians(ang));dy=-2.54*math.sin(math.radians(ang))
   ops.append((n.start,n.end,wire(x-dx,y-dy,x+dx,y+dy)));shorts.append([x,y,ang])
  elif n.val('lib_id').endswith(':Sheet-Symbol_A2'):
   # Imported decorative frame: no pins, exclude from electrical/BOM/board.
   t=s[n.start:n.end].replace('(in_bom yes)','(in_bom no)').replace('(on_board yes)','(on_board no)');ops.append((n.start,n.end,t))
 p=patches(s,ops);p=reinstance(p,rootpath+'/49516b4f-d465-4b39-ae52-1de484ecc052')
 (W/'power.kicad_sch').write_text(p,encoding='utf-8')
 rs=(W/'GD32F5_FOC.kicad_sch').read_text(encoding='utf-8').replace('(property "Sheetname" "power"','(property "Sheetname" "FOC"')
 (W/'GD32F5_FOC.kicad_sch').write_text(rs,encoding='utf-8')
 # Import only the two 3.3 V supply blocks and analog ground link from P1.
 ms,m=load(W/'MCU.kicad_sch');ps,pr=load(SRC/'2_P1.kicad_sch');chosen=[]
 def inside(x,y):return 160<=float(x)<=225 and 20<=float(y)<=75
 for n in pr.items:
  if not isinstance(n,Node):continue
  if n.key in ('symbol','junction','label','global_label','no_connect') and n.one('at') and inside(*n.one('at').items[1:3]):chosen.append(n)
  elif n.key=='wire' and all(inside(*q.items[1:3]) for q in n.one('pts').kids('xy')):chosen.append(n)
 ids={n.val('lib_id') for n in chosen if n.key=='symbol'}
 defs=[ps[n.start:n.end] for n in pr.one('lib_symbols').kids('symbol') if n.items[1] in ids]
 extra=[reinstance(ps[n.start:n.end],rootpath+'/023525dc-8b31-4272-8a5f-3c0381bf9655',{'U1':'U20'}) for n in chosen]
 mappings={'67':'HIN1','68':'HIN2','69':'HIN3','52':'LIN1','53':'LIN2','54':'LIN3','15':'IA','16':'IB','17':'IC','18':'IBUS','33':'VBUS','34':'COM','23':'VA','24':'VB','25':'VC','26':'NTC','29':'SPI1_CS0','30':'SPI1_SCK','31':'SPI1_MISO','32':'SPI1_MOSI','63':'QEI1_A','64':'QEI1_B','65':'QEI1_Z','72':'SWDIO','76':'SWCLK','14':'NRST','94':'BOOT0'}
 sym=m.kids('symbol')[0];sx,sy,angle=map(float,sym.one('at').items[1:]);assert angle==0
 pins=[p for u in m.one('lib_symbols').kids('symbol')[0].kids('symbol') for p in u.kids('pin')]
 for pin in pins:
  num,name=pin.val('number'),pin.val('name');net=mappings.get(num)
  if name in ('VDD','VBAT'):net='VCC'
  if name in ('VDDA','VREFP'):net='AVCC'
  if name=='VSS':net='GND'
  if name in ('VSSA','VREFN'):net='AGND'
  px,py,pa=map(float,pin.one('at').items[1:]);x,y=sx+px,sy-py
  if net:
   xx=x+(-7.62 if pa==0 else 7.62);extra.extend([wire(x,y,xx,y),label(net,xx,y,0 if pa==0 else 180)])
  elif name=='NC':extra.append(f'(no_connect (at {x:g} {y:g}) (uuid "{uid()}"))')
 extra.extend([note('GD32F505VxTx / official GD32EB F505VxT7.xml pin mapping',150,85),note('HIN/LIN: TIMER0 CH0/1/2 and complementary outputs.\nSPI1_* connector nets use GD32 SPI0 on PA4..PA7.\nQEI1_*: TIMER2 on PC6..PC8. ADC inputs on PA0..3, PC0..5.\nVCC=3.3V; AVCC=3.3V analog; AGND linked to GND by R3.\nExternal crystal and application-specific PWM auxiliary net: pending.',150,92)])
 ms=patches(ms,[(m.one('lib_symbols').end-1,m.one('lib_symbols').end-1,'\n'+'\n'.join(defs)+'\n'),(len(ms.rstrip())-1,len(ms.rstrip())-1,'\n'+'\n'.join(extra)+'\n')])
 (W/'MCU.kicad_sch').write_text(ms,encoding='utf-8')
 shutil.copy2(SRC/'ProDoc_Boa-easyedapro.kicad_sym',W/'ProDoc_Boa-easyedapro.kicad_sym')
 lib='ProDoc_Board1v1_2026-10-26-import-fps';shutil.copytree(SRC/(lib+'.pretty'),W/(lib+'.pretty'),dirs_exist_ok=True)
 (W/'fp-lib-table').write_text('(fp_lib_table (version 7)\n'+''.join(f'(lib (name "{name}") (type "KiCad") (uri "${{KIPRJMOD}}/{lib}.pretty") (options "") (descr "Reference P2 footprint library"))\n' for name in [lib,'ProDoc_Boa-easyedapro'])+')\n',encoding='utf-8')
 # Recover the existing MCU embedded library as a local library without altering its pinout.
 _,mr=load(W/'MCU.kicad_sch');mt=(W/'MCU.kicad_sch').read_text(encoding='utf-8');mn=mr.one('lib_symbols').kids('symbol')[0];md=mt[mn.start:mn.end].replace('"MCU:GD32F505VxTx (Altium Display 1)"','"GD32F505VxTx (Altium Display 1)"',1)
 (W/'MCU.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor")\n'+md+'\n)',encoding='utf-8')
 (W/'sym-lib-table').write_text('(sym_lib_table (version 7)\n'+''.join(f'(lib (name "{n}") (type "KiCad") (uri "${{KIPRJMOD}}/{n}.kicad_sym") (options "") (descr ""))\n' for n in ['MCU','ProDoc_Boa-easyedapro'])+')\n',encoding='utf-8')
 print(json.dumps({'backup':str(backup),'short_symbols_replaced':shorts,'regulator_symbols':[prop(n,'Reference') for n in chosen if n.key=='symbol'],'interfaces':mappings},indent=2))
if __name__=='__main__':
 import sys
 migrate() if '--apply' in sys.argv else inspect()
