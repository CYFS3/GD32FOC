import xml.etree.ElementTree as E,json
from pathlib import Path
r=E.parse('.review-fixes/after-types-final.xml'); comps={c.get('ref'):c.findtext('value') for c in r.findall('./components/comp')}
targets=['DCBUS_IN','PGND_IN','DCBUS','PGND','12V','VREF','HSL_LINK_3V3','HSL_VDD_SOC','HSL_USB_VBUS','HSL_SHIELD']
for n in r.findall('./nets/net'):
 name=n.get('name')
 if any(name==x or name.endswith('/'+x) for x in targets) or any(x in name.upper() for x in ['BST','VB1','VB2','VB3','OTPCAP','PMCCAP','DCDC_LP']):
  print('\nNET',name)
  for p in n.findall('node'): print(p.attrib,comps.get(p.get('ref')))
e=json.loads(Path('.review-fixes/erc-current.json').read_text(encoding='utf-8'))
for s in e['sheets']:
 for v in s['violations']:
  if v['type']=='power_pin_not_driven': print('ERC',s['path'],[i['description'] for i in v['items']])
