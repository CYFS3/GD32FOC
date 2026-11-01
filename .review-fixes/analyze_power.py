import json,re,xml.etree.ElementTree as E
from pathlib import Path as P
j=json.loads(P('.review-fixes/erc-current.json').read_text(encoding='utf8'));r=E.parse('.review-fixes/after-types-final.xml'); nets=r.findall('./nets/net'); index={(p.get('ref'),p.get('pin')):n for n in nets for p in n.findall('node')}; comps={x.get('ref'):x for x in r.findall('./components/comp')}
lines=[]
for s in j['sheets']:
 for v in s['violations']:
  if v['type']!='power_pin_not_driven':continue
  for it in v['items']:
   desc=it['description'];m=re.search(r'(?:Symbol|符号)\s+(\S+)\s+(?:引脚|Pin)\s+(\S+)',desc)
   line={'sheet':s['path'],'description':desc,'pos':it.get('pos')}
   if m:
    ref,pin=m.groups();n=index.get((ref,pin));line['net']=n.get('name') if n is not None else None
    if n is not None:line['connections']=[dict(x.attrib,value=comps.get(x.get('ref')).findtext('value') if comps.get(x.get('ref')) is not None else '') for x in n.findall('node')]
   lines.append(line)
P('.review-fixes/power-source-analysis.json').write_text(json.dumps(lines,ensure_ascii=False,indent=2),encoding='utf8')
for l in lines:print(l['sheet'],l['description'],l.get('net'))
