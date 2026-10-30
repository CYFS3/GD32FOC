from migrate_p2 import *
import math
s,r=load(W/'hslink_cleanup/HSLink.before.kicad_sch'); defs={n.items[1]:n for n in r.one('lib_symbols').kids('symbol')}
def xy(n):return tuple(map(float,n.one('at').items[1:3]))
def moved(t,dx,dy):return re.sub(r'\((at|xy) (-?[\d.]+) (-?[\d.]+)',lambda m:f'({m[1]} {float(m[2])+dx:.6f} {float(m[3])+dy:.6f}',t)
def pins(n):
 x,y=xy(n);a=math.radians(float(n.one('at').items[3]));out=[]
 for u in defs[n.val('lib_id')].kids('symbol'):
  for p in u.kids('pin'):
   px,py=map(float,p.one('at').items[1:3]);mir=n.val('mirror')
   if mir=='x':py=-py
   if mir=='y':px=-px
   out.append((round(x+px*math.cos(a)-py*math.sin(a),5),round(y-px*math.sin(a)-py*math.cos(a),5)))
 return out
objs=[n for n in r.items if isinstance(n,Node) and n.key in ['symbol','wire','junction','global_label','label','no_connect']]
# Physically connected drawing islands; symbols union all their pins for layout only.
coords=[]
for n in objs:
 coords.append(pins(n) if n.key=='symbol' else [tuple(map(float,p.items[1:3])) for p in n.one('pts').kids('xy')] if n.key=='wire' else [xy(n)])
parent=list(range(len(objs)))
def find(i):
 while parent[i]!=i:i=parent[i]
 return i
def union(i,j):parent[find(i)]=find(j)
for i,pts in enumerate(coords):
 for j in range(i):
  if set(pts)&set(coords[j]):union(i,j)
  elif objs[j].key=='wire':
   a,b=coords[j]
   if any(abs((p[0]-a[0])*(b[1]-a[1])-(p[1]-a[1])*(b[0]-a[0]))<1e-5 and min(a[0],b[0])<=p[0]<=max(a[0],b[0]) and min(a[1],b[1])<=p[1]<=max(a[1],b[1]) for p in pts):union(i,j)
groups={}
for i,n in enumerate(objs):groups.setdefault(find(i),[]).append(i)
pieces=[];removed=[]
for k,ids in groups.items():
 refs=[prop(objs[i],'Reference') for i in ids if objs[i].key=='symbol' and not prop(objs[i],'Reference').startswith('#')]
 if 'U8008' in refs or 'U8010' in refs:
  removed+=refs;continue
 dx,dy=35,30
 if 'R8052' in refs:dx,dy=150,10
 if 'D8005' in refs:dx,dy=80,30
 if 'SW8005' in refs:dx,dy=80,30
 if 'H8001' in refs:dx,dy=360,-115
 if 'R8061' in refs:dx,dy=155,65
 for j,ref in enumerate(['R8063','R8064','R8065','R8066','R8068','R8070']):
  if ref in refs:dx,dy=60,210+j*10-xy(next(objs[i] for i in ids if objs[i].key=='symbol' and prop(objs[i],'Reference')==ref))[1]
 for j in range(5):
  if 'R'+str(8901+j) in refs:dx,dy=155,160+j*20-(100+j*15.24)
 for i in ids:
  n=objs[i];t=s[n.start:n.end]
  if n.key=='global_label':
   x,y=xy(n);a=float(n.one('at').items[3])
   # Labels at either end of series resistors must face away from body.
   if any(q in refs for q in ['R8063','R8064','R8065','R8066','R8068','R8070']):a=180 if x<39.37 else 0
   if 'R8061' in refs:a=180 if x<121.92 else 0
   if any(q in refs for q in ['R8901','R8902','R8903','R8904','R8905']):a=180 if x<285 else 0
   if (x,y) in [(93.98,88.9),(93.98,91.44),(73.66,184.15),(73.66,189.23)]:a=0
   if (x,y) in [(146.05,93.98),(203.2,20.32)]:a=180
   t=label(n.items[1],x,y,a)
  if n.key=='symbol' and prop(n,'Value')=='HSL_3V3':
   t=t.replace('StylePower:HSL_3V3','StylePower:VCC').replace('"HSL_3V3"','"VCC"')
  if n.key=='symbol':
   ref=prop(n,'Reference');value=prop(n,'Value')
   offsets={
    'R8901':(0,5),'R8902':(0,5),'R8903':(0,5),'R8904':(0,5),'R8905':(0,5),
    'H8001':(0,15),'R8070':(0,-3),'R8055':(6,3),'SW8005':(8,-4),'C8081':(-5,-3),
    '#PWR11043':(-17,-3),'#PWR11033':(-20,5)}
   if ref in offsets:
    ox,oy=offsets[ref];pr=n.kids('property');ed=[]
    for q in pr:
     if q.items[1] in ['Reference','Value'] and not (q.items[1]=='Reference' and ref.startswith('#')):
      qt=s[q.start:q.end];ed.append((q.start-n.start,q.end-n.start,moved(qt,ox,oy)))
    t=patches(t,ed)
  pieces.append(moved(t,dx,dy))
notes=[('HSLINK / HPM5301 - SHARED SYSTEM POWER',25,15),('HPM5301 + 24 MHz clock + on-chip VDD_SOC buck',45,170),('USB data / ESD; VBUS does not power board',275,30),('System 3.3 V -> R8052 -> HPM I/O rail',275,65),('ISP boot button',290,103),('JTAG series termination',60,195),('UART series termination',245,195),('Target reference header',395,35),('Target disconnect links (default DNP)',390,145),('POWER: VCC = existing system 3.3 V (U20 XC6210B332MR).\nR8052 0R supplies HSL_LINK_3V3; HPM on-chip VDD_SOC buck retained.\nUSB VBUS only reaches USB connector / ESD; no board-supply path.\nU20 load / thermal margin requires measurement; HPM load is unknown.',25,300),('R8901..R8905 remain DEFAULT DNP / OPEN. Fit only with target powered.\nNever drive target simultaneously from onboard debugger and J200 probe.\nH8001 pin 1 is target VCC reference; no separate power injection.\nNo validated ADC voltage sensing or firmware power-off tri-state.',265,300),('Reference GPIO mapping retained; firmware compatibility NOT verified.\nUSB footprint and firmware require validation before PCB fabrication.',25,345),('UART nets name target direction: TX = GD32 PD5 -> probe RX;\nRX = GD32 PD6 <- probe TX.',265,345)]
pieces += [note(line,x,y+j*3.5) for t,x,y in notes for j,line in enumerate(t.split('\n'))]
lib=s[r.one('lib_symbols').start:r.one('lib_symbols').end]
# VCC definition already present for H8001 target reference.
assert 'StylePower:VCC' in lib
out='(kicad_sch (version 20250114) (generator "hslink_cleanup") (uuid "'+r.val('uuid')+'") (paper "A2") '+lib+'\n'+'\n'.join(pieces)+'\n)'
(W/'HSLink.kicad_sch').write_text(out,encoding='utf-8')
(W/'hslink_cleanup/removed.json').write_text(json.dumps(sorted(removed),indent=2),encoding='utf-8')
print('Removed:',sorted(removed))
