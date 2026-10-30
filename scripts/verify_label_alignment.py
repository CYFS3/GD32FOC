from align_labels import *
import xml.etree.ElementTree as ET
sys.path.insert(0,str(W/'.pdf-review-tools'));import fitz

def netdata(p):
 r=ET.parse(p).getroot();return sorted((n.attrib['name'],sorted(tuple(sorted(v.attrib.items())) for v in n.findall('node'))) for n in r.findall('./nets/net')),sorted((c.attrib['ref'],c.findtext('value'),c.findtext('footprint')) for c in r.findall('./components/comp'))
a,b=netdata(OUT/'before.xml'),netdata(OUT/'after.xml');assert a==b
print('NETLIST EQUIVALENT',len(a[0]),'nets',len(a[1]),'components')
changes=json.loads((OUT/'changes.json').read_text());print('CHANGES',{p:sum(c['page']==p for c in changes) for p in ['MCU','HSLink','FOC_M1','FOC_M2','power']})
doc=fitz.open(OUT/'after.pdf');report=[]
for f,idx in [('MCU',1),('HSLink',5),('FOC_M1',3),('FOC_M2',4),('power',2)]:
 s,r=load(W/(f+'.kicad_sch')); words=doc[idx].get_text('words');scale=72/25.4
 # page order discovered by distinctive text below rather than assumed.
 print(idx,doc[idx].get_text()[:70].replace('\n',' '))
 for n in r.kids('global_label'):
  x,y,a=map(float,n.one('at').items[1:]);x*=scale;y*=scale
  matches=[w for w in words if w[4]==n.items[1]]
  if not matches:continue
  w=min(matches,key=lambda w:abs((w[1]+w[3])/2-y)+min(abs(w[0]-x),abs(w[2]-x)))
  outward=(w[2]<x if a==180 else w[0]>x)
  collisions=[v[4] for v in words if v is not w and min(w[2],v[2])-max(w[0],v[0])>.4 and min(w[3],v[3])-max(w[1],v[1])>.4]
  report.append(dict(page=f,name=n.items[1],x=x,y=y,angle=a,bbox=list(w[:4]),outward=outward,collisions=collisions))
(OUT/'pdf_geometry.json').write_text(json.dumps(report,indent=2));print('geometry',len(report),'wrongside',sum(not v['outward'] for v in report),'collisions',[v for v in report if v['collisions']])
