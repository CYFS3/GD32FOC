from pathlib import Path as P
import re,json,shutil,hashlib
base=P('.layout-review');backup=base/'annotation-backup';backup.mkdir(exist_ok=True)
for p in P('.').glob('*.kicad_sch'):
 dest=backup/p.name
 if not dest.exists():shutil.copy2(p,dest)
a=json.loads((base/'annotation-audit-before.json').read_text(encoding='utf8'))
changes=[];nextref=12000
alltext='\n'.join(p.read_text(encoding='utf8') for p in P('.').glob('*.kicad_sch'))
def block_end(s,start):
 depth=0;quote=False;esc=False
 for i in range(start,len(s)):
  c=s[i]
  if quote:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c=='"':quote=False
  elif c=='"':quote=True
  elif c=='(':depth+=1
  elif c==')':
   depth-=1
   if depth==0:return i+1
 raise ValueError('Unclosed block')
for issue in a['issues']:
 assert issue[0]=='duplicate',issue
 old=issue[1];es=issue[2]
 assert old.startswith('#PWR') and len(es)==2
 entry=next(e for e in es if e['file'] in ['MCU.kicad_sch','Interface.kicad_sch'])
 while '"#PWR'+str(nextref)+'"' in alltext:nextref+=1
 new='#PWR'+str(nextref);nextref+=1
 p=P(entry['file']);raw=p.read_bytes();s=raw.decode('utf8')
 ident=s.index('"'+entry['uuid']+'"');start=s.rfind('(symbol',0,ident);end=block_end(s,start);part=s[start:end]
 assert '(lib_id' in part and entry['uuid'] in part
 patched,n1=re.subn(r'(\(property\s+"Reference"\s+)"'+re.escape(old)+'"',lambda m:m[1]+'"'+new+'"',part)
 patched,n2=re.subn(r'(\(reference\s+)"'+re.escape(old)+'"',lambda m:m[1]+'"'+new+'"',patched)
 assert (n1,n2)==(1,1),(entry,n1,n2)
 p.write_bytes((s[:start]+patched+s[end:]).encode('utf8'))
 changes.append(dict(file=p.name,uuid=entry['uuid'],old=old,new=new,property_changes=n1,instance_changes=n2))
(base/'annotation-changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(changes,ensure_ascii=False,indent=2))
