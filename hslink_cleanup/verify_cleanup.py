import json,xml.etree.ElementTree as E,sys
before=E.parse('hslink_cleanup/before.xml');after=E.parse(sys.argv[1]);parts=lambda r:{c.get('ref'):(c.findtext('value'),c.findtext('footprint')) for c in r.findall('./components/comp') if not c.get('ref','').startswith('#')}
a,b=parts(before),parts(after);keep=set(a)&set(b)
def groups(r):
 out=set()
 for n in r.findall('./nets/net'):
  ps=frozenset((p.get('ref'),p.get('pin')) for p in n.findall('node') if p.get('ref') in keep)
  if ps:out.add(ps)
 return out
old,new=groups(before),groups(after)
# Intentional merge: former HSL_3V3 supply side joins existing system VCC.
def pinmap(r):return {(p.get('ref'),p.get('pin')):n for n in r.findall('./nets/net') for p in n.findall('node')}
ix=pinmap(after)
expected=[]
for g in old:
 if ('R8052','2') in g or ('U20','5') in g:expected.append(g)
allowed=(old-set(expected))|{frozenset().union(*expected)}
checks={}
def same(name,*pins):
 ns=[ix.get(p) for p in pins];checks[name]=ns[0] is not None and all(n is ns[0] for n in ns)
same('system_VCC_to_debugger_feed',('U20','5'),('R8052','2'),('R8071','1'),('R8072','1'))
same('debugger_after_feed',('R8052','1'),('U8006','6'),('U8006','34'))
same('preserved_core_supply',('U8007','1'),('U8006','5'),('U8006','9'))
checks['USB_VBUS_not_system_supply']=ix[('USB8002','2')] is not ix[('U20','5')] and ix[('USB8002','2')] is not ix[('U20','1')]
checks['TPS_removed']='U8010' not in b
checks['USB_power_bridge_removed']='U8008' not in b
checks['all_other_connectivity_preserved']=allowed==new
checks['retained_parts_unchanged']=all(a[k]==b[k] for k in keep)
print(json.dumps({'pass':all(checks.values()),'checks':checks,'removed_parts':sorted(set(a)-set(b)),'new_parts':sorted(set(b)-set(a)),'unexpected_lost_groups':[sorted(x) for x in allowed-new],'unexpected_added_groups':[sorted(x) for x in new-allowed]},indent=2))
