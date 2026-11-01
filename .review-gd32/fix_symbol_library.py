from pathlib import Path as P
exec(P('.review-gd32/crystal_work.py').read_text(encoding='utf-8').split("s=P('MCU.kicad_sch')")[0])
s=P('MCU.kicad_sch').read_text(encoding='utf-8')
start=s.index('(symbol "HXTAL:ABM3B"');depth=0;quoted=False;esc=False
for i in range(start,len(s)):
 c=s[i]
 if quoted:
  if esc:esc=False
  elif c=='\\':esc=True
  elif c=='"':quoted=False
 elif c=='"':quoted=True
 elif c=='(':depth+=1
 elif c==')':
  depth-=1
  if depth==0:break
b=s[start:i+1].replace('"HXTAL:ABM3B"','"ABM3B"',1)
old=parse(P('HXTAL.kicad_sym').read_text(encoding='utf-8'));new=parse('(kicad_symbol_lib '+b+')')
print('Existing library AST equal:',children(old,'symbol')==children(new,'symbol'))
P('HXTAL.kicad_sym').write_text('(kicad_symbol_lib (version 20260306) (generator "kicad_symbol_editor")\n'+b+'\n)',encoding='utf-8')
