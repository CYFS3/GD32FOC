import sys,json,xml.etree.ElementTree as E

def load(path):
 r=E.parse(path)
 parts={c.get('ref'):{k:c.findtext(k) or '' for k in ['value','footprint']} for c in r.findall('./components/comp') if not c.get('ref','').startswith('#')}
 groups=[]
 for n in r.findall('./nets/net'):
  ps=tuple(sorted((p.get('ref'),p.get('pin')) for p in n.findall('node') if p.get('ref') in parts))
  if ps: groups.append(ps)
 return parts,set(groups)
a,an=load(sys.argv[1]);b,bn=load(sys.argv[2]);report={'physical_components_before':len(a),'physical_components_after':len(b),'component_values_and_footprints_identical':a==b,'physical_pin_connectivity_identical':an==bn,'removed_connections':[list(x) for x in sorted(an-bn)],'added_connections':[list(x) for x in sorted(bn-an)],'changed_components':[k for k in sorted(set(a)|set(b)) if a.get(k)!=b.get(k)]}
report['pass']=a==b and an==bn
print(json.dumps(report,ensure_ascii=False,indent=2))
