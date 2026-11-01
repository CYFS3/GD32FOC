import math

def rot(p,a):
 t=math.radians(a);x,y=p;return (x*math.cos(t)+y*math.sin(t),-x*math.sin(t)+y*math.cos(t))
def bounds(poly):return [min(p[0] for p in poly),min(p[1] for p in poly),max(p[0] for p in poly),max(p[1] for p in poly)]
def hit(a,b,gap=0):return a[0]<b[2]+gap and a[2]+gap>b[0] and a[1]<b[3]+gap and a[3]+gap>b[1]
def polygon_overlap(a,b,margin=0):
 # Convex separation test; native round/rect pad polygons are convex.
 if not a or not b or not hit(bounds(a),bounds(b),margin):return False
 for poly in (a,b):
  for p,q in zip(poly,poly[1:]+poly[:1]):
   axis=(q[1]-p[1],p[0]-q[0]);n=math.hypot(*axis)
   if n<1e-10:continue
   pa=[x*axis[0]+y*axis[1] for x,y in a];pb=[x*axis[0]+y*axis[1] for x,y in b]
   if max(pa)+margin*n<=min(pb)+1e-7*n or max(pb)+margin*n<=min(pa)+1e-7*n:return False
 return True

def fit(current,source,pinmap=None):
 pinmap=pinmap or {}; cp={};sp={}
 for p in current['pads']:
  q=rot((p['position'][0]-current['position'][0],p['position'][1]-current['position'][1]),-current['angle']);cp.setdefault(p['number'],[]).append(q)
 for p in source['pads']:
  q=rot(p['local_at'][:2],source['rotation_deg']);q=(q[0]+source['at'][0],q[1]+source['at'][1]);sp.setdefault(p['number'],[]).append(q)
 pairs=[]
 for n,pts in cp.items():
  sn=str(pinmap.get(n,n))
  if sn not in sp:continue
  pairs.append((tuple(sum(p[j] for p in pts)/len(pts) for j in (0,1)),tuple(sum(p[j] for p in sp[sn])/len(sp[sn]) for j in (0,1))))
 assert pairs,(current['ref'],source['reference'])
 ca=tuple(sum(p[0][j] for p in pairs)/len(pairs) for j in (0,1));sa=tuple(sum(p[1][j] for p in pairs)/len(pairs) for j in (0,1))
 if len(pairs)>1:
  dot=sum((a[0]-ca[0])*(b[0]-sa[0])+(a[1]-ca[1])*(b[1]-sa[1]) for a,b in pairs)
  cross=sum((a[0]-ca[0])*(b[1]-sa[1])-(a[1]-ca[1])*(b[0]-sa[0]) for a,b in pairs)
  angle=-math.degrees(math.atan2(cross,dot));angle=round(angle/90)*90
 else:angle=source['rotation_deg']
 rc=rot(ca,angle);xy=(sa[0]-rc[0],sa[1]-rc[1]);errs=[math.hypot(rot(a,angle)[0]+xy[0]-b[0],rot(a,angle)[1]+xy[1]-b[1]) for a,b in pairs]
 return dict(x=xy[0],y=xy[1],angle=angle,max_pad_center_error_mm=max(errs),origin_offset_mm=[xy[0]-source['at'][0],xy[1]-source['at'][1]],matched_pins=len(pairs))
