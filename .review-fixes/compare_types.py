from pathlib import Path
import json,collections,xml.etree.ElementTree as ET
def nets(f):
 t=ET.parse(f);return {frozenset((n.get('ref'),n.get('pin')) for n in net.findall('node') if n.get('ref') not in {'U1','C210','C211','Y200'}):net.get('name') for net in t.findall('./nets/net')}
a=nets('.review-fixes/before.xml');b=nets('.review-fixes/after-types.xml')
print('LOST',[(v,sorted(k)) for k,v in a.items() if k not in b]);print('NEW',[(v,sorted(k)) for k,v in b.items() if k not in a])
e=json.loads(Path('.review-fixes/erc-types.json').read_text(encoding='utf8'));vs=[v for s in e['sheets'] for v in s['violations']];print(collections.Counter((v['severity'],v['type']) for v in vs))
for v in vs:
 if v['severity']=='error' or v['type'] in ['lib_symbol_mismatch','lib_symbol_issues','pin_to_pin']:
  print(v['type'],v['description'],[(i['description']) for i in v['items']])
