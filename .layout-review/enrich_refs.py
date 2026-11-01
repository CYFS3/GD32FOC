exec(open('.layout-review/parse_references.py',encoding='utf8').read().split('allout={}')[0])
out=json.loads(Path('.layout-review/reference-coordinates.json').read_text(encoding='utf8'))
for key in out:
 sm={}
 for p in (base/key).glob('*.kicad_sch'):
  tree=parse(p.read_text(encoding='utf8'))
  libs={n[1]:n for n in ch(one(tree,'lib_symbols',[]),'symbol')}
  for n in ch(tree,'symbol'):
   props={x[1]:x[2] for x in ch(n,'property')};ref=props.get('Reference');lib=one(n,'lib_id',['',''])[1]
   if not ref:continue
   item=sm.setdefault(ref,{'sheet':p.name,'properties':props,'lib_id':lib,'pins':[]})
   for unit in ch(libs.get(lib,[]),'symbol'):
    for pin in ch(unit,'pin'):item['pins'].append({'number':one(pin,'number',['',''])[1],'name':one(pin,'name',['',''])[1]})
 for fp in out[key]['footprints']:
  if fp['reference'] in sm:fp['schematic']=sm[fp['reference']];fp['value']=sm[fp['reference']]['properties'].get('Value','')
 print('\n',key)
 for f in out[key]['footprints']:
  r=f['reference'] or ''
  if r.startswith(('U','Q','X','USB')) or r in ['CN1','CN41']:
   print(r,f['value'],f['at'],f['footprint'])
Path('.layout-review/reference-coordinates.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
