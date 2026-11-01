from pathlib import Path
import json,re,shutil,subprocess,xml.etree.ElementTree as E,copy
ns={};exec(Path('.review-gd32/crystal_work.py').read_text(encoding='utf8').split("s=P('MCU.kicad_sch')")[0],ns);parse,children,one=[ns[x] for x in ['parse','children','one']]
A=json.loads(Path('.layout-review/reference-testpoint-audit.json').read_text(encoding='utf8'));refs={r['ref'] for r in A['current_keystone']};assert len(refs)==52
backup=Path('.layout-review/testpoint-barepad-backup');backup.mkdir(exist_ok=True)
cli=r'D:\KiCad\HQ10.0\bin\kicad-cli.exe'
def export(name):
 p=Path('.layout-review')/name;subprocess.run([cli,'sch','export','netlist','--format','kicadxml','-o',str(p),'GD32F5_FOC.kicad_sch'],check=True);return p
def nets(p):
 t=E.parse(p);return sorted((n.get('name'),sorted((x.get('ref'),x.get('pin')) for x in n.findall('node'))) for n in t.findall('./nets/net'))
before=export('testpoint-before.xml');changes=[];seen=set()
def clean(node):
 if isinstance(node,list):
  if node and node[0]=='property' and node[1] in {'Value','Footprint','Manufacturer Part','Manufacturer','Supplier Part','Supplier','Datasheet'}:return [node[0],node[1],'<ALLOWED>']+node[3:]
  if node and node[0] in ['in_bom','in_pos_files']:return [node[0],'<ALLOWED>']
  return [clean(x) for x in node]
 return node
for filename in ['MCU.kicad_sch','power.kicad_sch','FOC_M1.kicad_sch','FOC_M2.kicad_sch']:
 p=Path(filename);text=p.read_text(encoding='utf8');orig=text;parts=list(re.finditer(r'\n\t\(symbol\s*\n\t\t\(lib_id ',text)); replacements=[]
 for m in parts:
  start=m.start()+1;depth=0;quote=False;escape=False;end=None
  for i in range(start,len(text)):
   c=text[i]
   if quote:
    if escape:escape=False
    elif c=='\\':escape=True
    elif c=='"':quote=False
   elif c=='"':quote=True
   elif c=='(':depth+=1
   elif c==')':
    depth-=1
    if depth==0:end=i+1;break
  block=text[start:end];tree=parse(block);pr={x[1]:x[2] for x in children(tree,'property')};r=pr.get('Reference')
  if r not in refs:continue
  assert r not in seen;seen.add(r);new=block
  values={'Value':'TestPoint','Footprint':'VerifiedParts:TestPoint_D1.27_Reference','Manufacturer Part':'','Manufacturer':'','Supplier Part':'','Supplier':'','Datasheet':''}
  for key,value in values.items():
   if key in pr:
    pat=r'(\(property '+re.escape(json.dumps(key))+r' )"(?:\\.|[^"\\])*"';new,n=re.subn(pat,lambda m:m[1]+json.dumps(value),new,count=1);assert n==1
  new,n=re.subn(r'\(in_bom yes\)','(in_bom no)',new,count=1);assert n==1
  new,n=re.subn(r'\(in_pos_files yes\)','(in_pos_files no)',new,count=1);assert n==1
  assert clean(tree)==clean(parse(new));assert one(parse(new),'on_board')[1]=='yes'
  replacements.append((start,end,new));changes.append(dict(ref=r,sheet=filename,old_properties=pr,new_properties=values,in_bom=False,in_pos_files=False,on_board=True))
 for start,end,new in reversed(replacements):text=text[:start]+new+text[end:]
 if text!=orig:
  shutil.copy2(p,backup/p.name);p.write_text(text,encoding='utf8')
assert seen==refs
# Compare entire sheets modulo allowed metadata only and verify all non-target blocks exactly unaffected structurally.
for filename in ['MCU.kicad_sch','power.kicad_sch','FOC_M1.kicad_sch','FOC_M2.kicad_sch']:
 old=parse((backup/filename).read_text(encoding='utf8'));new=parse(Path(filename).read_text(encoding='utf8'));assert clean(old)==clean(new)
after=export('testpoint-after.xml');assert nets(before)==nets(after)
result=dict(count=52,changed_sheets=sorted({r['sheet'] for r in changes}),connectivity_unchanged=True,only_approved_metadata_changed=True,footprint='VerifiedParts:TestPoint_D1.27_Reference',symbol_library_id_retained_for_pin_geometry=True,TP200_unchanged=True,changes=changes)
Path('.layout-review/reference-testpoint-fix-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print('PASS 52 metadata-only changes; whole project nets unchanged')
