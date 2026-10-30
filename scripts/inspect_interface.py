from migrate_p2 import *
import xml.etree.ElementTree as ET
s,r=load(W/'MCU.kicad_sch')
u=next(n for n in r.kids('symbol') if prop(n,'Reference')=='U1'); d=next(n for n in r.one('lib_symbols').kids('symbol') if n.items[1]==u.val('lib_id'))
print('MCU at',u.one('at').items)
for sub in d.kids('symbol'):
 for p in sub.kids('pin'):
  if p.val('number') in ['89','32','92','93','3','4','83','84','85']:print('PIN',p.val('number'),p.val('name'),p.one('at').items)
print('NOTES',[(n.items[1],n.one('at').items) for n in r.kids('text')])
s,r=load(W.parent/'test/2_P1.kicad_sch')
for ref in ['SW5','R1','C1']:
 n=next(n for n in r.kids('symbol') if prop(n,'Reference')==ref);d=next(d for d in r.one('lib_symbols').kids('symbol') if d.items[1]==n.val('lib_id'))
 print('REF',ref,'lib',n.val('lib_id'),'fp',prop(n,'Footprint'),'at',n.one('at').items)
 print(s[d.start:d.end])
x=ET.parse(W/'interface_review/audit_netlist.xml')
print('existing 300 refs',[c.attrib['ref'] for c in x.findall('.//components/comp') if '30' in c.attrib['ref']])
