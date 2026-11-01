import xml.etree.ElementTree as E
from pathlib import Path
r=E.parse('.layout-review/annotation-final.xml')
nets={}
for n in r.findall('./nets/net'):
 for x in n.findall('node'): nets.setdefault(x.get('ref'),[]).append((x.get('pin'),n.get('name')))
lines=[]
for c in r.findall('./components/comp'):
 lines.append(f"{c.get('ref')} | {c.findtext('value')} | {c.findtext('footprint')} | {c.find('sheetpath').get('names')} | {nets.get(c.get('ref'),[])}")
Path('.layout-review/current-placement-inventory.txt').write_text('\n'.join(lines),encoding='utf8')
print(len(lines))
