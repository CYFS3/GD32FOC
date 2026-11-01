from pathlib import Path
import json,re,copy,hashlib,shutil,collections
exec(Path('.review-gd32/crystal_work.py').read_text(encoding='utf8').split("s=P('MCU.kicad_sch')")[0])
root=Path.cwd()
candidates=json.loads(Path('.layout-review/false-pth-candidates.json').read_text(encoding='utf8'))
components=json.loads(Path('.layout-review/placement-groups.json').read_text(encoding='utf8'))['components']
table=parse(Path('fp-lib-table').read_text(encoding='utf8'))
libs={one(n,'name')[1]:Path(one(n,'uri')[1].replace('${KIPRJMOD}',str(root))) for n in children(table,'lib')}
groups=collections.defaultdict(list)
for c in candidates:
 libid=c['definition'].split('id=')[1].split(', items=')[0]
 groups[libid].append(c['ref'])
evidence={
'C0603_S':'Library JLC_3D_Size=1.6 0.8 and C0603_L1.6-W0.8-H0.8 model; 0603 chip capacitor.',
'R0603_S':'0603 chip resistor/NTC package, rectangular 0.8065x0.864 lands and 1.6x0.8 body graphics; populated R/NTC component metadata uses this package.',
'SOD-323_L1.8-W1.3-LS2.5-RD_2':'SOD-323 surface-mount diode package, JLC model and dimension metadata; two rectangular leads.',
'CONN-SMD_6P-P1.25_XUNPU_WAFER-GH1.25-6PWB':'Explicit CONN-SMD library and model for WAFER-GH1.25-6PWB; six solder tails and two rectangular surface mounting tabs, all 0.001mm imported drill.',
'QFN-24_L4.0-W4.0-P0.50-BL-EP2.6':'FD6288Q QFN24 with exposed pad25; QFN-24_L4.0-W4.0-H0.9-P0.50 model and existing F.Paste pad polygons.'}
def block(s,start):
 depth=0;quoted=False;escaped=False
 for i in range(start,len(s)):
  c=s[i]
  if quoted:
   if escaped:escaped=False
   elif c=='\\':escaped=True
   elif c=='"':quoted=False
  elif c=='"':quoted=True
  elif c=='(':depth+=1
  elif c==')':
   depth-=1
   if not depth:return s[start:i+1]
 raise ValueError('unclosed')
report=[]
for libid,refs in groups.items():
 lib,name=libid.split(':',1); assert name in evidence
 path=libs[lib]/(name+'.kicad_mod'); raw=path.read_bytes();text=raw.decode('utf8');before=parse(text)
 pads=children(before,'pad');expected=copy.deepcopy(before);epads=children(expected,'pad')
 count=0
 for pad,ep in zip(pads,epads):
  drill=one(pad,'drill');layers=one(pad,'layers')
  if pad[2]!='thru_hole' or drill!=['drill','0.001'] or layers!=['layers','*.Cu','*.Mask']:continue
  ep[2]='smd';ep[:]=[n for n in ep if not(isinstance(n,list) and n[0] in ('drill','remove_unused_layers'))]
  one(ep,'layers')[:]=['layers','F.Cu','F.Paste','F.Mask'];count+=1
 assert count==len(pads),'Unexpected real or mixed pads: '+libid
 # No true through-hole/NPTH remain. Preserve any other attributes.
 attr=one(expected,'attr')
 if attr:
  attr[:]=[x for x in attr if x!='through_hole']
  if 'smd' not in attr:attr.append('smd')
 else:expected.append(['attr','smd'])
 changes=[]
 for m in re.finditer(r'\(pad\s',text):
  old=block(text,m.start());p=parse(old)
  if p[2]=='thru_hole' and one(p,'drill')==['drill','0.001'] and one(p,'layers')==['layers','*.Cu','*.Mask']:
   new=old.replace('thru_hole','smd',1)
   new=re.sub(r'\s*\(drill 0\.001\)','',new)
   new=re.sub(r'\s*\(remove_unused_layers [^)]*\)','',new)
   new=new.replace('(layers "*.Cu" "*.Mask")','(layers "F.Cu" "F.Paste" "F.Mask")')
   changes.append((m.start(),m.start()+len(old),new))
 for a,b,new in reversed(changes):text=text[:a]+new+text[b:]
 oldattr=one(before,'attr')
 if oldattr:
  m=re.search(r'\(attr\s',text);old=block(text,m.start());new='(attr '+' '.join(one(expected,'attr')[1:])+')';text=text[:m.start()]+new+text[m.start()+len(old):]
 else:text=text[:text.rfind(')')]+'\t(attr smd)\n'+text[text.rfind(')'):]
 after=parse(text)
 # Ignore only top-level ordering of newly added attr; all other AST nodes must be identical to whitelist transformation.
 assert [n for n in after if n!=one(after,'attr')]==[n for n in expected if n!=one(expected,'attr')]
 assert one(after,'attr')==one(expected,'attr')
 rel=path.relative_to(root);backup=root/'.layout-review/module-smd-library-backup'/rel
 backup.parent.mkdir(parents=True,exist_ok=True)
 if backup.exists():assert backup.read_bytes()==raw,'Backup exists with another original; stop'
 else:shutil.copy2(path,backup)
 path.write_text(text,encoding='utf8')
 assert parse(path.read_text(encoding='utf8'))==after
 shared=[]
 for ref,c in components.items():
  fp=c.get('footprint','')
  if ':' in fp:
   a,b=fp.split(':',1)
   if a in libs and libs[a]/(b+'.kicad_mod')==path:shared.append(ref)
 report.append(dict(path=str(rel),backup=str(backup.relative_to(root)),lib_id=libid,evidence=evidence[name],candidate_refs=refs,all_project_refs_using_library=shared,other_shared_refs=sorted(set(shared)-set(refs)),padcount_changed=count,pad_numbers=[p[1] for p in pads],geometry_numbering_uuid_and_graphics_unchanged=True,ast_whitelist_validation='PASS',before_sha256=hashlib.sha256(raw).hexdigest(),after_sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
out={'candidate_instance_count':len(candidates),'library_file_count':len(report),'definition_pads_changed':sum(x['padcount_changed'] for x in report),'files':report,'pcb_modified':False,'schematic_modified':False,'library_table_modified':False,'notes':['Existing F.Paste graphics retained exactly; exposed-pad paste process remains to be reviewed.','True 5012 PTH and power/motor connector files not selected and not changed.','Only exact five candidate library paths changed; shared references listed for future library updates.']}
Path('.layout-review/module-smd-library-fixes.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(out,ensure_ascii=False,indent=2))
