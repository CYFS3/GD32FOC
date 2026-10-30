from migrate_p2 import *
s,r=load(W/'MCU.kicad_sch');n=next(n for n in r.kids('symbol') if prop(n,'Reference')=='R3');old=n.val('lib_id');d=next(d for d in r.one('lib_symbols').kids('symbol') if d.items[1]==old)
def fixed(t):
 q=parse(t);ops=[]
 for p in q.kids('property'):
  k=p.items[1];v=p.items[2]
  if k in ['Supplier Part','Supplier','LCSC Part Name']:ops.append((p.start,p.end,''))
  elif k in ['Manufacturer Part','Manufacturer','Datasheet','Value','Description']:
   nv={'Manufacturer Part':'0402WGF0000TCE','Manufacturer':'Royal Electronic Factory','Datasheet':'','Value':'0R','Description':'0 ohm 0402 1/16W; HQ catalog HQG0063276'}[k]
   ops.append((p.start,p.end,t[p.start:p.end].replace(json.dumps(v,ensure_ascii=False),json.dumps(nv),1)))
 return patches(t,ops)
dt=fixed(s[d.start:d.end]).replace(old,'Interface:0402WGF0000TCE').replace('0402WGF1002TCE_','0402WGF0000TCE_')
nt=fixed(s[n.start:n.end]).replace(old,'Interface:0402WGF0000TCE')
s=patches(s,[(n.start,n.end,nt),(r.one('lib_symbols').end-1,r.one('lib_symbols').end-1,'\n'+dt+'\n')]);(W/'MCU.kicad_sch').write_text(s,encoding='utf-8')
(W/'Interface.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor")\n'+dt.replace('Interface:0402WGF0000TCE','0402WGF0000TCE',1)+'\n)',encoding='utf-8')
f=W/'sym-lib-table';t=f.read_text(encoding='utf-8');f.write_text(t.rstrip()[:-1]+'\n(lib (name "Interface") (type "KiCad") (uri "${KIPRJMOD}/Interface.kicad_sym") (options "") (descr "Corrected catalog metadata preserving R3 symbol geometry"))\n)',encoding='utf-8')
print('R3 corrected; original geometry, pins, UUID and footprint retained.')
