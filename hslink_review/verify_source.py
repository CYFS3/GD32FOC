import xml.etree.ElementTree as E,json
m=json.load(open('hslink_review/reference_map.json',encoding='utf8'));inv={v:k for k,v in m.items()}
def groups(path,convert):
 r=E.parse(path);out=set()
 for n in r.findall('./nets/net'):
  ps=tuple(sorted((convert[p.get('ref')],p.get('pin')) for p in n.findall('node') if p.get('ref') in convert and (convert[p.get('ref')],p.get('pin'))!=('H1','1')))
  if ps:out.add(ps)
 return out
a=groups('hslink_review/reference.xml',{k:k for k in m});b=groups('hslink_review/after.xml',inv)
print(json.dumps({'pass':a==b,'lost':[list(x) for x in sorted(a-b)],'added':[list(x) for x in sorted(b-a)]},ensure_ascii=False,indent=2))
