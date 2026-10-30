"""Geometry-preserving split of the actual migrated reference, with auditable backup."""
from migrate_p2 import *
import hashlib
ROOT='/df410b35-b24b-4f8c-aaa2-f94e7558172b'
OUT=W/'dual_review';OUT.mkdir(exist_ok=True)
backup=W/'dual_backup'/datetime.datetime.now().strftime('%Y%m%d_%H%M%S');backup.mkdir(parents=True)
for f in W.iterdir():
 if f.is_file() and (f.suffix in ('.kicad_sch','.kicad_pro','.kicad_pcb','.kicad_sym') or f.name.endswith('lib-table')):shutil.copy2(f,backup/f.name)
(OUT/'backup_path.txt').write_text(str(backup),encoding='utf-8')
s,r=load(backup/'power.kicad_sch')
shared={'GND','AGND','PGND','PGND_IN','DCBUS','DCBUS_IN','12V','5V','VCC','AVCC','VREF'}
pageids={'POWER_SHARED':'49516b4f-d465-4b39-ae52-1de484ecc052','FOC_M1':uid(),'FOC_M2':uid()}
def region(x,y):
 x,y=float(x),float(y)
 if y<145:return 'POWER_SHARED'
 if 145<=y<318 and not (155<x<220 and 150<y<245):return 'MOTOR'
 return 'DISCARD'
def classify(n):
 if n.key=='symbol' and prop(n,'Reference')=='#FRAME1':return 'DISCARD'
 if n.key=='text':return 'DISCARD' # replace damaged source encoding annotations with explicit notes
 if n.one('at'):return region(*n.one('at').items[1:3])
 if n.key in ('wire','polyline') and n.one('pts'):
  regs={region(*p.items[1:3]) for p in n.one('pts').kids('xy')}
  if len(regs)!=1:raise RuntimeError(('boundary-crossing geometry',s[n.start:n.end]))
  return regs.pop()
 return 'DISCARD'
objects=[n for n in r.items if isinstance(n,Node) and n.key in ('symbol','wire','junction','label','global_label','no_connect','text','polyline')]
selected={k:[n for n in objects if classify(n)==k] for k in ('POWER_SHARED','MOTOR','DISCARD')}
manifest={'backup':str(backup),'sheets':{},'removed_refs':[prop(n,'Reference') for n in selected['DISCARD'] if n.key=='symbol']}
for page,index in [('POWER_SHARED',0),('FOC_M1',1),('FOC_M2',2)]:
 nodes=selected['POWER_SHARED' if index==0 else 'MOTOR']; chunks=[]; refs={}
 for n in nodes:
  t=s[n.start:n.end]
  if index==2:t=re.sub(r'\(uuid "[^"]+"\)',lambda m:'(uuid "'+uid()+'")',t)
  if n.key=='symbol':
   ref=prop(n,'Reference');newref=ref
   if index==2:
    mt=re.fullmatch(r'([A-Za-z#]+)(\d+)',ref);assert mt,ref
    newref=mt[1]+str(int(mt[2])+1000)
   refs[ref]=newref;t=reinstance(t,ROOT+'/'+pageids[page],{ref:newref})
   val=prop(n,'Value')
   if index and ref.startswith('#') and val not in shared:
    t=t.replace('(property "Value" '+json.dumps(val,ensure_ascii=False),'(property "Value" '+json.dumps(f'M{index}_'+val,ensure_ascii=False))
  if n.key in ('label','global_label'):
   name=n.items[1];newname=(f'M{index}_'+name) if index and name not in shared else name
   # All explicit labels global: source depends on power symbols and cross-block label joining.
   t=t.replace('('+n.key+' '+json.dumps(name),'(global_label '+json.dumps(newname),1)
   if n.key=='label':t=t[:-1]+' (shape bidirectional))'
  chunks.append(t)
 ids={n.val('lib_id') for n in nodes if n.key=='symbol'}
 defs=[s[n.start:n.end] for n in r.one('lib_symbols').kids('symbol') if n.items[1] in ids]
 text='Shared input protection, DCBUS capacitors, 12V / 5V regulators and analog VREF.\nOne common supply only; original ratings retained, not verified for two motors.' if not index else f'MOTOR {index}: independent gate drive, six MOSFETs, phase shunts and bus shunt.\nAll motor signals M{index}_*. Common DCBUS / 12V / 5V / VCC / AVCC / VREF.\nPGND is common AFTER the dedicated bus shunt; phase-shunt return remains local.\nReference values and footprints require engineering review; no rating verification.'
 chunks.append(note(text,15,335 if index else 160))
 out='(kicad_sch (version 20260306) (generator "eeschema") (uuid "'+(r.val('uuid') if not index else uid())+'") (paper "A2")\n(lib_symbols\n'+'\n'.join(defs)+')\n'+'\n'.join(chunks)+'\n(embedded_fonts no))\n'
 filename='power.kicad_sch' if not index else page+'.kicad_sch'
 (W/filename).write_text(out,encoding='utf-8');manifest['sheets'][page]={'file':filename,'refs':refs,'uuid':pageids[page]}
rs,rr=load(backup/'GD32F5_FOC.kicad_sch');ops=[]
old=next(n for n in rr.kids('sheet') if prop(n,'Sheetfile')=='power.kicad_sch')
ops.append((old.start,old.end,rs[old.start:old.end].replace('"FOC"','"POWER_SHARED"')))
extra=[]
for index in (1,2):
 page=f'FOC_M{index}';x=125+(index-1)*47
 extra.append(f'(sheet (at {x} 30.48) (size 38.1 36.83) (stroke (width 0.1524) (type solid)) (fill (color 0 0 0 0)) (uuid "{pageids[page]}") (property "Sheetname" "{page}" (at {x} 29.7684 0) (effects (font (size 1.27 1.27)) (justify left bottom))) (property "Sheetfile" "{page}.kicad_sch" (at {x} 68 0) (effects (font (size 1.27 1.27)) (justify left top))) (instances (project "GD32F5_FOC" (path "{ROOT}" (page "{index+3}")))))')
extra.append(note('Dual independent motor framework\nCommon input supply + GD32F505VxTx controller\nReview protection thresholds and ratings before energizing.',32,85))
ops.append((len(rs.rstrip())-1,len(rs.rstrip())-1,'\n'+'\n'.join(extra)+'\n'))
(W/'GD32F5_FOC.kicad_sch').write_text(patches(rs,ops),encoding='utf-8')
(OUT/'split_manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'backup':str(backup),'counts':{k:len(v) for k,v in selected.items()}},indent=2))
