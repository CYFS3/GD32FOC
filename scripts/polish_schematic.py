"""Visual-only rail-symbol conversion and isolated MCU lead shortening.
Always rebuild from style_review/baseline; validate native netlist independently.
"""
from migrate_p2 import *
import math, hashlib
OUT=W/'style_review'
FILES=['GD32F5_FOC.kicad_sch','MCU.kicad_sch','power.kicad_sch','FOC_M1.kicad_sch','FOC_M2.kicad_sch']
RAILS=set('VCC GND AGND AVCC MCU_VDDA 5V 12V DCBUS DCBUS_IN PGND PGND_IN VREF 24V'.split())
BASE=Path(r'C:\Users\RTT\AppData\Local\Programs\KiCad\10.0\share\kicad\symbols\power.kicad_sym')
ps,pr=load(BASE)
def definition(name):
 base='GND' if 'GND' in name else 'VCC'
 n=next(n for n in pr.kids('symbol') if n.items[1]==base)
 t=ps[n.start:n.end].replace('"'+base+'"','"'+name+'"').replace('"'+base+'_','"'+name+'_')
 return t
names=sorted(RAILS)
lib='(kicad_symbol_lib (version 20250114) (generator "visual_polish")\n'+'\n'.join(definition(n) for n in names)+'\n)\n'
(W/'StylePower.kicad_sym').write_text(lib,encoding='utf-8')
count=9000;stats=[]
def xy(n):return tuple(round(float(v),5) for v in n.one('at').items[1:3])
def power(name,x,y,path,angle=0):
 global count
 count+=1;ref=f'#PWR{count}';ground='GND' in name
 dy=3.81 if ground else -3.81
 return f'''(symbol (lib_id "StylePower:{name}") (at {x:.6f} {y:.6f} {angle}) (unit 1) (in_bom no) (on_board no) (dnp no) (uuid "{uid()}")
 (property "Reference" "{ref}" (at {x:.6f} {y:.6f} 0) (effects (font (size 1 1)) (hide yes)))
 (property "Value" "{name}" (at {x:.6f} {y+dy:g} 0) (effects (font (size 1 1))))
 (instances (project "GD32F5_FOC" (path "{path}" (reference "{ref}") (unit 1)))))'''
for fn in FILES:
 s,r=load(OUT/'baseline'/fn);ops=[];used=set();short=0;converted=0
 syms=r.kids('symbol');path=None
 for n in syms:
  inst=n.one('instances')
  if inst:path=inst.one('project').one('path').items[1];break
 # Physical pin endpoints, accounting for symbol rotation and mirroring.
 pins={}
 defs={n.items[1]:n for n in r.one('lib_symbols').kids('symbol')}
 for n in syms:
  if (prop(n,'Reference') or '').startswith('#'):continue
  x,y=xy(n);a=math.radians(float(n.one('at').items[3]));d=defs[n.val('lib_id')]
  for u in d.kids('symbol'):
   for p in u.kids('pin'):
    px,py=map(float,p.one('at').items[1:3]);mir=n.val('mirror')
    if mir=='x':py=-py
    if mir=='y':px=-px
    pt=(round(x+px*math.cos(a)-py*math.sin(a),5),round(y-px*math.sin(a)-py*math.cos(a),5))
    pins[pt]=(n,p)
 wires=r.kids('wire');ends={}
 for w in wires:
  pts=[tuple(round(float(v),5) for v in q.items[1:3]) for q in w.one('pts').kids('xy')]
  for p in pts:ends.setdefault(p,[]).append((w,pts))
 labels=r.kids('label')+r.kids('global_label');atcounts={}
 for n in labels+r.kids('junction')+r.kids('no_connect')+syms:
  if n.one('at'):atcounts[xy(n)]=atcounts.get(xy(n),0)+1
 # Consolidate dense MCU supply rows into shared buses on their existing nets.
 bus_vcc=[];bus_gnd=[]
 if fn=='MCU.kicad_sch':
  bus_vcc=[n for n in labels if n.items[1]=='VCC' and xy(n)[0]==48.26]
  bus_gnd=[n for n in labels if n.items[1]=='GND' and xy(n)[0]==124.46]
  for group,bx in [(bus_vcc,48.26),(bus_gnd,132.08)]:
   ys=sorted(xy(n)[1] for n in group)
   if ys:
    extra=[wire(bx,a,bx,b) for a,b in zip(ys,ys[1:])]
    if bx==132.08:extra += [wire(124.46,y,bx,y) for y in ys]
    extra += [f'(junction (at {bx} {y}) (diameter 0) (color 0 0 0 0) (uuid "{uid()}"))' for y in ys[1:-1]]
    ops.append((len(s.rstrip())-1,len(s.rstrip())-1,'\n'+'\n'.join(extra)+'\n'))
 for n in labels:
  name=n.items[1];x,y=xy(n);raw=s[n.start:n.end]
  if n in bus_vcc and y!=min(xy(q)[1] for q in bus_vcc):
   ops.append((n.start,n.end,''));converted+=1;continue
  if n in bus_gnd:
   if y!=max(xy(q)[1] for q in bus_gnd):
    ops.append((n.start,n.end,''));converted+=1;continue
   x=132.08
  if fn=='MCU.kicad_sch' and name not in RAILS and len(ends.get((x,y),[]))==1:
   w,pts=ends[(x,y)][0];other=pts[1] if pts[0]==(x,y) else pts[0]
   if other in pins and len(ends.get(other,[]))==1 and atcounts.get(other,0)==0 and atcounts.get((x,y))==1:
    # Only isolated horizontal signal leads, excluding shared branches and functional chains.
    if other[1]==y:
     ops.append((w.start,w.end,''));at=n.one('at');angle=0 if other[0]>x else 180
     raw=patches(raw,[(at.start-n.start,at.end-n.start,f'(at {other[0]:g} {other[1]:g} {angle})')]);short+=1
  if name in RAILS:
   # Imported labels can attach with KiCad's label tolerance despite 0.1016 mm
   # offset; power pins need the actual endpoint, not the label anchor.
   candidates=list(ends)+list(pins)
   nearest=min(candidates,key=lambda p:(p[0]-x)**2+(p[1]-y)**2) if candidates else (x,y)
   if math.dist(nearest,(x,y))<0.15:x,y=nearest
   else:
    # Power pins require a segment endpoint; labels also attach along interiors.
    for w in wires:
     a,b=[tuple(float(v) for v in q.items[1:3]) for q in w.one('pts').kids('xy')]
     if abs((x-a[0])*(b[1]-a[1])-(y-a[1])*(b[0]-a[0]))<1e-7 and min(a[0],b[0])<=x<=max(a[0],b[0]) and min(a[1],b[1])<=y<=max(a[1],b[1]):
      x,y=a;break
   raw=power(name,x,y,path);used.add(name);converted+=1
  if raw!=s[n.start:n.end]:ops.append((n.start,n.end,raw))
 if used:
  at=r.one('lib_symbols').end-1
  ops.append((at,at,'\n'+'\n'.join(definition(n).replace('(symbol "'+n+'"','(symbol "StylePower:'+n+'"',1) for n in sorted(used))+'\n'))
 result=patches(s,ops);(W/fn).write_text(result,encoding='utf-8')
 stats.append(dict(file=fn,rail_labels_converted=converted,isolated_signal_leads_removed=short,before_sha256=hashlib.sha256(s.encode()).hexdigest(),after_sha256=hashlib.sha256(result.encode()).hexdigest()))
(OUT/'changes.json').write_text(json.dumps(stats,indent=2),encoding='utf-8')
print(json.dumps(stats,indent=2))
