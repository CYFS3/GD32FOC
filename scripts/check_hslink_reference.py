from migrate_p2 import *
import xml.etree.ElementTree as E
O=W/'hslink_review'; mp=json.loads((O/'reference_map.json').read_text()); orig=E.parse(W/'hslink_source.xml'); new=E.parse(O/'after.xml')
def groups(tree,lookup):
 out={}
 for n in tree.findall('.//net'):
  pins=frozenset((lookup[x.attrib['ref']],x.attrib['pin']) for x in n.findall('node') if x.attrib['ref'] in lookup)
  for p in pins:out[p]=(n.attrib['name'],pins)
 return out
a=groups(orig,mp);b=groups(new,{v:v for v in mp.values()});bad=[]
for pin,(name,pins) in a.items():
 if pin not in b or b[pin][1]!=pins:bad.append((pin,name,sorted(pins),b.get(pin)))
for x in bad:print(x)
print('DIFFERENCES',len(bad),'source pins',len(a))
