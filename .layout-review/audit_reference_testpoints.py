from pathlib import Path
import json,collections
ns={};exec(Path('.review-gd32/crystal_work.py').read_text(encoding='utf8').split("s=P('MCU.kicad_sch')")[0],ns)
parse,children,one=[ns[x] for x in ['parse','children','one']]
base=Path(r'E:\MCU\GD32\GD32F5_FOC\data\FOC'); stem='ProDoc_1.axdr_v1.3_2026-10-31'
def props(n):return {p[1]:p[2] for p in children(n,'property')}
def field(n,k):
 a=one(n,k);return a[1:] if a else None
def geo(f):
 return dict(libid=f[1],properties=props(f),layer=field(f,'layer'),at=field(f,'at'),pads=[dict(number=p[1],type=p[2],shape=p[3],at=field(p,'at'),size=field(p,'size'),drill=field(p,'drill'),layers=field(p,'layers'),net=field(p,'net')) for p in children(f,'pad')],graphics=[p for p in f if isinstance(p,list) and p[0].startswith('fp_') and p[0]!='fp_text'],models=children(f,'model'))
sch=parse((base/(stem+'.kicad_sch')).read_text(encoding='utf8')); board=parse((base/(stem+'.kicad_pcb')).read_text(encoding='utf8')); fps={props(f).get('Reference'):f for f in children(board,'footprint')}
syms={props(s).get('Reference'):props(s) for s in children(sch,'symbol') if props(s).get('Value')=='5012' or props(s).get('Manufacturer Part')=='5012'}
cb=parse(Path('GD32F5_FOC.kicad_pcb').read_text(encoding='utf8')); current={props(f).get('Reference'):f for f in children(cb,'footprint') if 'Keystone THM' in str(field(f,'descr'))}
cs={}
for p in Path('.').glob('*.kicad_sch'):
 for s in children(parse(p.read_text(encoding='utf8')),'symbol'):
  pr=props(s)
  if pr.get('Reference') in current:cs[pr['Reference']]=dict(sheet=p.name,properties=pr)
mp=json.loads(Path('.layout-review/foc-reuse-map.json').read_text(encoding='utf8'))['rows']; bysrc={r['source_ref']:r for r in mp if r.get('source_ref')}
rows=[]; libs={}
for ref,pr in sorted(syms.items()):
 f=fps.get(ref);g=geo(f) if f else None;mapping=[]
 if ref in bysrc:
  rr=bysrc[ref];mapping=[dict(ref=rr['m1_ref'],role='M1'),dict(ref=rr['m2_ref'],role='M2')]
 elif ref in current and ref not in {x['m1_ref'] for x in mp} and ref not in {x['m2_ref'] for x in mp}:
  mapping=[dict(ref=ref,role='shared_same_ref_candidate_requires_net_verification')]
 if g:
  name=g['libid'].split(':')[-1];p=base/(stem+'-import-fps.pretty')/(name+'.kicad_mod')
  if name not in libs:libs[name]=dict(path=str(p),exists=p.exists(),geometry=geo(parse(p.read_text(encoding='utf8'))) if p.exists() else None)
 rows.append(dict(source_ref=ref,schematic_properties=pr,board=g,current_mapping=mapping))
# establish shared candidates by exact pin-net correspondence, explicit power renames only
aliases={'DCBUS_IN':'DCBUS_IN','PGND_IN':'PGND_IN','DCBUS':'DCBUS','PGND':'PGND','12V':'12V','5V':'5V','VCC':'VCC','GND':'GND','AGND':'AGND'}
def netname(p):
 a=field(p,'net');return a[-1] if a else ''
for row in rows:
 for m in row['current_mapping']:
  r=m['ref'];f=current.get(r);m['current_exists_as_keystone']=f is not None
  if f is not None:
   m['source_nets']=[netname(p) for p in children(fps[row['source_ref']],'pad')];m['current_nets']=[netname(p) for p in children(f,'pad')]
   if m['role'].startswith('shared'):
    m['same_net']=m['source_nets']==m['current_nets'];m['role']='shared_same_ref_net_verified' if m['same_net'] else 'shared_unconfirmed'
# Shared refs were renumbered: map by explicit network and pin-neighbor evidence, not same-ref alone.
shared_map={'CN5':'CN2','CN6':'CN3','CN8':'CN6','CN2':'CN9','CN4':'CN4','CN7':'CN7','CN13':'CN13','CN16':'CN16'}
for row in rows:
 row['current_mapping']=[m for m in row['current_mapping'] if m['role'] in ['M1','M2']]
 if row['source_ref'] in shared_map:
  r=shared_map[row['source_ref']]; sf=fps[row['source_ref']];cf=current[r];sn=netname(children(sf,'pad')[0]);cn=netname(children(cf,'pad')[0]);sneighbors=sorted((rr,p[1]) for rr,ff in fps.items() for p in children(ff,'pad') if netname(p)==sn);cneighbors=sorted((props(ff).get('Reference'),p[1]) for ff in children(cb,'footprint') for p in children(ff,'pad') if netname(p)==cn)
  row['current_mapping'].append(dict(ref=r,role='shared',source_nets=[sn],current_nets=[cn],source_neighbors=sneighbors,current_neighbors=cneighbors,evidence='same named net' if sn==cn else 'same ref and shared R57.2, but source/current neighbor sets differ; position equivalence unresolved',position_mapping_verified=(sn==cn),current_exists_as_keystone=True))
covered={m['ref'] for r in rows for m in r['current_mapping']}
result=dict(source_paths=dict(pcb=str(base/(stem+'.kicad_pcb')),schematic=str(base/(stem+'.kicad_sch'))),source_5012_symbol_count=len(syms),source_5012_board_count=sum(r['board'] is not None for r in rows),current_keystone_count=len(current),source_library_variants=libs,rows=rows,current_keystone=[dict(ref=r,schematic=cs.get(r),board=geo(f),covered_by_source_mapping=r in covered) for r,f in sorted(current.items())],unmapped_current=sorted(set(current)-covered),decision='Reference copper geometry and source 5012 BOM identity conflict. Prefer restoring reference-sized bare test pads under explicit design intent, with value TestPoint, no Keystone 5012 MPN/supplier/datasheet; do not call the source a proven SMD test pad: TH model name/User.1 hole-like graphic and 0.001 drill leave lost original drill ambiguous. If actual Keystone 5012 is required retain official mechanical footprint and do not claim reference replication.')
Path('.layout-review/reference-testpoint-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print('counts',len(syms),result['source_5012_board_count'],len(current),'libs',list(libs),'unmapped',result['unmapped_current'])
for r in rows:
 print(r['source_ref'],r['board']['libid'].split(':')[-1] if r['board'] else 'NO PCB',[(m['ref'],m['role'],m.get('source_nets'),m.get('current_nets')) for m in r['current_mapping']])
