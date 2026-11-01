exec(open('.layout-review/build_foc_reuse.py',encoding='utf8').read().split('# Same reference')[0])
w=json.loads(Path('.layout-review/foc-reuse-working.json').read_text(encoding='utf8'));mp=w['map'];mp.pop('C9101',None) # new buffer bypass must not steal unrelated reference decoupling
for r,s in [('C130','C66'),('C131','C70'),('C132','C71'),('CN5','U8')]:mp[r]=s
special={'C9101':'C9103','C9102':'C9104','R9101':'R9103','R9102':'R9104','U9101':'U9102'}
def pair(r):
 if r in special:return special[r]
 m=re.fullmatch(r'([A-Z]+)(\d+)',r);return m[1]+str(int(m[2])+1000)
rows=[];exceptions=[]
for r in sorted(m1):
 p=pair(r);assert p in m2,(r,p)
 if r not in mp:
  rows.append({'source_ref':None,'m1_ref':r,'m2_ref':p,'classification':'new_no_reference','confidence':'confirmed_new_or_changed_interface','evidence':'No equivalent source footprint/function; preserve as identical peripheral additions on M1/M2','current_value':m1[r]['value']});continue
 s=mp[r];f=S[s];sw=r in ['C130','C131','C132'];same=r==s
 evidence=['source and target pin-network neighborhood checked after stripping M1/M2 prefix','functional aliases SHUNT_RETURN=source IA-, NTC=NTC1, ENC inputs=source HALL inputs']
 conf='high_functional_topology'
 if same:
  evidence.append('same inherited reference plus compatible per-pin networks; repeated power-only passives are provenance-based, not mathematically unique');conf='high_provenance_function' if len(cn[r])>2 else 'medium_provenance_topology'
 else:evidence.append('cross-reference topology match; do not infer from number')
 if sw:evidence.append('bootstrap pair exact VB1/2/3 and MA/MB/MC; capacitor pin numbering reversed');conf='high_exact_two_net_match'
 if r=='CN5':
  conf='functional_replacement_geometry_differs';evidence=['reference U8 is 5P Hall connector; current CN5 is 6P Hall+PWM connector','pins1GND and2/3/4 C/B/A preserved; former5=5V now5=PWM and6=ENC_VSUP','reuse connector center/function only; package dimensions and access must be checked'];exceptions.append(r)
 row={'source_ref':s,'m1_ref':r,'m2_ref':p,'source_x_mm':f['at'][0],'source_y_mm':f['at'][1],'source_rotation_deg':f['rotation_deg'],'source_layer':f['layer'],'source_pads':f['pads'],'source_value':f['value'],'current_value':m1[r]['value'],'classification':'reference_mapped','confidence':conf,'evidence':evidence,'pad_number_mapping_current_to_source':{'1':'2','2':'1'} if sw else 'identity unless package geometry demands origin alignment','rotation_adjustment_for_pin_numbering_deg':180 if sw else 0}
 rows.append(row)
# verify pairing graph equivalence using module-qualified net names, tolerate anonymous ref text renamed
mapping={r:pair(r) for r in m1};rev={v:k for k,v in mapping.items()}
def partition(refs,reverse={}):
 bins=collections.defaultdict(set)
 for r in refs:
  for pin,n in cn[r].items():bins[n].add((reverse.get(r,r),pin))
 return {frozenset(v) for v in bins.values()}
assert partition(m1)==partition(m2,rev),'module topology asymmetry'
used=set(mp.values());mapped=[x for x in rows if x['source_ref']];xs=[x['source_x_mm'] for x in mapped];ys=[x['source_y_mm'] for x in mapped]
res={'status':'mapping_only_no_board_changes','source':'data/FOC reference PCB','counts':{'m1':len(m1),'m2':len(m2),'mapped_each':len(mapped),'new_each':len(rows)-len(mapped)},'module_graph_pairing_equivalent':True,'rows':rows,'reference_not_reused':[{'source_ref':r,'value':f['value'],'reason':'outside current FOC module or removed source function'} for r,f in S.items() if r not in used],'mapped_center_bbox_mm':[min(xs),min(ys),max(xs),max(ys)],'suggested_translation':{'same_rotation':True,'no_mirror':True,'m2_minus_m1_mm':[max(xs)-min(xs)+20,0],'note':'center bbox only; execution must expand to actual source/target courtyard and append identical new interface parts; no origin/rotation changes per part except package pad alignment'},'functional_replacement_exceptions':exceptions}
Path('.layout-review/foc-reuse-map.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf8')
print(res['counts']);print('bbox',res['mapped_center_bbox_mm']);print('new',[x['m1_ref'] for x in rows if not x['source_ref']]);print('cross',[(x['m1_ref'],x['source_ref']) for x in rows if x['source_ref'] and x['m1_ref']!=x['source_ref']])
