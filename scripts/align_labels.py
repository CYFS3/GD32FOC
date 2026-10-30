from migrate_p2 import *
import math, subprocess,sys
OUT=W/'label_alignment'; OUT.mkdir(exist_ok=True)
CLI=r'C:\Users\RTT\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe'
def export(tag):
 for kind,opts,ext in [('netlist',['--format','kicadxml'],'xml'),('pdf',[],'pdf')]:
  subprocess.run([CLI,'sch','export',kind,*opts,'-o',str(OUT/(tag+'.'+ext)),str(W/'GD32F5_FOC.kicad_sch')],check=True)
def pinlist(r):
 defs={n.items[1]:n for n in r.one('lib_symbols').kids('symbol')};out=[]
 for n in r.kids('symbol'):
  x,y,a=map(float,n.one('at').items[1:]);a=math.radians(a)
  for u in defs[n.val('lib_id')].kids('symbol'):
   for p in u.kids('pin'):
    px,py,pa=map(float,p.one('at').items[1:]);vx,vy=math.cos(math.radians(pa)),math.sin(math.radians(pa))
    if n.val('mirror')=='x':py=-py;vy=-vy
    if n.val('mirror')=='y':px=-px;vx=-vx
    out.append(dict(ref=prop(n,'Reference'),name=p.val('name'),x=round(x+px*math.cos(a)-py*math.sin(a),5),y=round(y-px*math.sin(a)-py*math.cos(a),5),vx=round(vx*math.cos(a)-vy*math.sin(a),5),vy=round(-vx*math.sin(a)-vy*math.cos(a),5)))
 return out
if __name__=='__main__':
 if sys.argv[1]=='before':
  b=OUT/'backup';b.mkdir(exist_ok=True)
  for p in W.glob('*.kicad_sch'):
   assert not (b/p.name).exists();shutil.copy2(p,b/p.name)
  export('before')
 if sys.argv[1]=='clear-note':
  path=W/'MCU.kicad_sch';s,r=load(path);ops=[]
  for n in r.kids('text'):
   if n.items[1].startswith('Onboard debugger:'):
    at=n.one('at');ops.append((at.start,at.end,'(at 150 195 0)'))
  path.write_text(patches(s,ops),encoding='utf-8');export('after')
 if sys.argv[1]=='clear-connectors':
  path=W/'MCU.kicad_sch';s,r=load(path);ops=[]
  for n in r.kids('symbol'):
   if prop(n,'Reference') in ['#PWR9007','#PWR9013']:
    p=next(p for p in n.kids('property') if p.items[1]=='Value');at=p.one('at');ops.append((at.start,at.end,f'(at {at.items[1]} {float(at.items[2])+6:g} {at.items[3]})'))
  path.write_text(patches(s,ops),encoding='utf-8');export('after')
 if sys.argv[1]=='restore-anchors':
  for path in W.glob('*.kicad_sch'):
   s,r=load(path);_,old=load(OUT/'backup'/path.name);orig={n.val('uuid'):n for n in old.kids('global_label')};ops=[]
   for n in r.kids('global_label'):
    at=n.one('at');o=orig[n.val('uuid')].one('at')
    if at.items[1:3]!=o.items[1:3]:ops.append((at.start,at.end,f'(at {o.items[1]} {o.items[2]} {at.items[3]})'))
   if ops:path.write_text(patches(s,ops),encoding='utf-8');print('Restored exact anchors',path.name,len(ops))
  export('after')
 if sys.argv[1]=='apply':
  report=[]
  for f in ['MCU','HSLink','FOC_M1','FOC_M2','power']:
   path=W/(f+'.kicad_sch');s,r=load(path);pins=pinlist(r);ops=[]
   for n in r.kids('global_label'):
    x,y,a=map(float,n.one('at').items[1:]);newa=a;reason='existing direction'
    exact=[p for p in pins if abs(p['x']-x)<1e-5 and abs(p['y']-y)<1e-5 and abs(p['vx'])>.9]
    if exact and len(set(p['vx'] for p in exact))==1:
     newa=180 if exact[0]['vx']>0 else 0;reason='outward from '+exact[0]['ref']+' '+exact[0]['name']
    elif not exact:
     dirs=set()
     for w in r.kids('wire'):
      pts=[tuple(map(float,q.items[1:3])) for q in w.one('pts').kids('xy')]
      for i,p in enumerate(pts):
       q=pts[1-i]
       if abs(p[0]-x)<1e-5 and abs(p[1]-y)<1e-5 and abs(q[1]-y)<1e-5 and abs(q[0]-x)>1e-5:dirs.add(1 if q[0]>x else -1)
     if len(dirs)==1:newa=180 if 1 in dirs else 0;reason='outward from horizontal wire endpoint'
    just=n.one('effects').one('justify');desired='right' if newa==180 else 'left'
    changed=a!=newa or (just and just.items[1:]!=[desired])
    if changed:
     at=n.one('at');ops.append((at.start,at.end,f'(at {at.items[1]} {at.items[2]} {newa:g})'))
     if just:ops.append((just.start,just.end,f'(justify {desired})'))
     report.append(dict(page=f,name=n.items[1],x=x,y=y,before_angle=a,after_angle=newa,before_justify=just.items[1:] if just else [],after_justify=desired,reason=reason))
   if ops:path.write_text(patches(s,ops),encoding='utf-8')
  (OUT/'changes.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('CHANGED',len(report))
  export('after')
 if sys.argv[1]=='inspect':
  for f in ['MCU','HSLink','FOC_M1','FOC_M2','power']:
   s,r=load(W/(f+'.kicad_sch'));pins=pinlist(r)
   print('\nPAGE',f)
   for p in pins:
    if p['name'] in ['PA0','PA00']:print('EXEMPLAR',p)
   for n in r.kids('global_label'):
    x,y,a=map(float,n.one('at').items[1:]);ps=sorted(pins,key=lambda p:abs(p['x']-x)+abs(p['y']-y))[:1]
    print(n.items[1],x,y,a,n.one('effects').one('justify').items if n.one('effects').one('justify') else '',ps)
