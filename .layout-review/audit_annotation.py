from pathlib import Path as P
import json,re,collections
exec(P('.review-gd32/crystal_work.py').read_text(encoding='utf8').split("s=P('MCU.kicad_sch')")[0])
files={p.name:parse(p.read_text(encoding='utf8')) for p in P('.').glob('*.kicad_sch')}
r=files['GD32F5_FOC.kicad_sch'];root=one(r,'uuid')[1]
paths={'GD32F5_FOC.kicad_sch':'/'+root}
for s in children(r,'sheet'):
 props={p[1]:p[2] for p in children(s,'property')};paths[props['Sheetfile']]='/'+root+'/'+one(s,'uuid')[1]
refs=collections.defaultdict(list);issues=[]
for f,t in files.items():
 libs={l[1]:l for l in children(one(t,'lib_symbols'),'symbol')}
 for s in children(t,'symbol'):
  props={p[1]:p[2] for p in children(s,'property')};ref=props['Reference'];unit=one(s,'unit')[1];lib=one(s,'lib_id')[1]
  units=sorted(set(int(m.group(1)) for c in children(libs[lib],'symbol') if (m:=re.search(r'_(\d+)_\d+$',c[1])) and int(m.group(1))>0))
  entry={'file':f,'ref':ref,'unit':unit,'lib':lib,'uuid':one(s,'uuid')[1],'available_units':units}
  refs[ref].append(entry)
  inst=one(s,'instances')
  if '?' in ref:issues.append(['unannotated',entry])
  if not inst:issues.append(['missing instances',entry]);continue
  matched=0
  for pr in children(inst,'project'):
   for path in children(pr,'path'):
    if pr[1]=='GD32F5_FOC':
     matched+=1
     if path[1]!=paths[f]:issues.append(['bad path',entry,path[1],paths[f]])
     if one(path,'reference')[1]!=ref or one(path,'unit')[1]!=unit:issues.append(['instance mismatch',entry,path])
  if matched!=1:issues.append(['project instances count',entry,matched])
for ref,es in refs.items():
 if len(es)>1 and (len(set(e['unit'] for e in es))!=len(es) or len(set(e['lib'] for e in es))!=1):issues.append(['duplicate',ref,es])
 if not ref.startswith('#') and set(int(e['unit']) for e in es)!=set(es[0]['available_units']):issues.append(['units incomplete',ref,es])
result={'sheets':paths,'symbols':sum(map(len,refs.values())),'issues':issues}
import sys
P(sys.argv[1] if len(sys.argv)>1 else '.layout-review/annotation-audit-before.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(result,ensure_ascii=False,indent=2))
