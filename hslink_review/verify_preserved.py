import sys,json,xml.etree.ElementTree as E
old=E.parse(sys.argv[1]);new=E.parse(sys.argv[2]);parts=lambda r:{c.get('ref'):(c.findtext('value'),c.findtext('footprint')) for c in r.findall('./components/comp') if not c.get('ref','').startswith('#')}
a,b=parts(old),parts(new)
def nets(r):
 return {tuple(sorted((p.get('ref'),p.get('pin')) for p in n.findall('node') if p.get('ref') in a)) for n in r.findall('./nets/net')} - {()}
an,bn=nets(old),nets(new)
result={'old_components':len(a),'new_components':len(b),'existing_parts_unchanged':all(b.get(k)==v for k,v in a.items()),'original_pin_connectivity_preserved':an==bn,'lost_groups':[list(g) for g in sorted(an-bn)],'new_groups_of_original_pins':[list(g) for g in sorted(bn-an)],'changed_parts':[k for k in a if b.get(k)!=a[k]]}
result['pass']=result['existing_parts_unchanged'] and result['original_pin_connectivity_preserved']
print(json.dumps(result,ensure_ascii=False,indent=2))
