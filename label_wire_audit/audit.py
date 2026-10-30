from pathlib import Path
import sys,json,math
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W/'scripts'))
from migrate_p2 import parse,prop,patches
def xy(n):return tuple(map(float,n.one('at').items[1:3]))
def ends(n):return [tuple(map(float,p.items[1:])) for p in n.one('pts').kids('xy')]
def pins(r):
 out=[]
 for n in r.kids('symbol'):
  sx,sy,ang=map(float,n.one('at').items[1:]); lib=next(z for z in r.one('lib_symbols').kids('symbol') if z.items[1]==n.val('lib_id'))
  for sub in lib.kids('symbol'):
   unit=int(sub.items[1].rsplit('_',2)[-2])
   if unit not in (0,int(n.val('unit') or 1)):continue
   for p in sub.kids('pin'):
    px,py=map(float,p.one('at').items[1:3]);mir=n.val('mirror')
    if mir=='x':py=-py
    if mir=='y':px=-px
    a=math.radians(ang);out.append((round(sx+px*math.cos(a)-py*math.sin(a),6),round(sy-px*math.sin(a)-py*math.cos(a),6),prop(n,'Reference'),p.val('number')))
 return out
if __name__=='__main__':
 reports=[]
 for f in W.glob('*.kicad_sch'):
  s=f.read_text(encoding='utf-8');r=parse(s);ps=pins(r);ls=r.kids('global_label');ws=r.kids('wire');cs=[]
  for l in ls:
   x,y=xy(l);ang=float(l.one('at').items[3]);d=1 if ang==0 else -1 if ang==180 else 0
   if not d:continue
   for w in ws:
    a,b=ends(w)
    if a[1]!=y or b[1]!=y or not min(a[0],b[0])<=x<=max(a[0],b[0]):continue
    end=max(a[0],b[0]) if d==1 else min(a[0],b[0])
    if (end-x)*d<0.000001:continue
    def on(xx,yy):return abs(yy-y)<1e-6 and (xx-x)*d>1e-6 and (xx-end)*d<=1e-6
    blockers=[]
    for xx,yy,ref,pin in ps:
     if on(xx,yy):blockers.append(['pin',ref,pin,xx,yy])
    for kind in ['label','global_label','hierarchical_label','junction','no_connect']:
     for n in r.kids(kind):
      if on(*xy(n)):blockers.append([kind,n.items[1] if kind.endswith('label') else '',*xy(n)])
    for ow in ws:
     if ow is w:continue
     aa,bb=ends(ow)
     if aa[1]==bb[1]:
      if aa[1]==y and (on(*aa) or on(*bb) or min(aa[0],bb[0])<min(x,end) and max(aa[0],bb[0])>max(x,end)):blockers.append(['wire',aa,bb])
     elif min(aa[1],bb[1])<=y<=max(aa[1],bb[1]):
      xx=aa[0]+(y-aa[1])*(bb[0]-aa[0])/(bb[1]-aa[1])
      if on(xx,y):blockers.append(['wire',aa,bb])
    cs.append(dict(label=l.items[1],anchor=[x,y,ang],wire=ends(w),uuid=w.val('uuid'),blockers=blockers))
  reports.append(dict(file=f.name,labels=len(ls),candidates=cs))
 (W/'label_wire_audit/candidates.json').write_text(json.dumps(reports,indent=2),encoding='utf-8')
 for f in reports:
  print(f['file'],f['labels'],len(f['candidates']))
  for c in f['candidates']:print(c)
