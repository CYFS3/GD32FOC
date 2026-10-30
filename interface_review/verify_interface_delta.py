import xml.etree.ElementTree as E,json,sys
from pathlib import Path
def read(p):
 r=E.parse(p);cs={c.get('ref'):(c.findtext('value'),c.findtext('footprint'))for c in r.findall('./components/comp')};ns={n.get('name'):set((p.get('ref'),p.get('pin'))for p in n.findall('node'))for n in r.findall('./nets/net')};return cs,ns
b,bn=read('interface_review/audit_netlist.xml');a,an=read(sys.argv[1]);old=set(b);allowed_refs={f'R{x+k}'for k in (0,1000)for x in [49,54,88,89,90,95,97,98,106,107,108]}|{f'C{x+k}'for k in(0,1000)for x in[82,83,84]}|{f'D{x+k}'for k in(0,1000)for x in[14,19,20]}|{'CN5','CN1005'};mcupins={'32','89','92','93','3','4','83','84','85'}
def keep(p):return p[0] in old and p[0] not in allowed_refs and not(p[0]=='U1'and p[1]in mcupins)
def groups(ns):return {frozenset(p for p in v if keep(p))for v in ns.values()if any(keep(p)for p in v)}
x,y=groups(bn),groups(an)
report={'physical_before':len(b),'physical_after':len(a),'added_refs':sorted(set(a)-old),'removed_refs':sorted(old-set(a)),'unrelated_connectivity_unchanged':x==y,'unexpected_removed_groups':[sorted(z)for z in x-y],'unexpected_added_groups':[sorted(z)for z in y-x],'changed_values_or_footprints':{r:[b[r],a[r]]for r in old&set(a)if b[r]!=a[r]},'mcu_new_pins':{pin:next((n for n,v in an.items()if ('U1',pin)in v),None)for pin in sorted(mcupins)}}
print(json.dumps(report,ensure_ascii=False,indent=2))
