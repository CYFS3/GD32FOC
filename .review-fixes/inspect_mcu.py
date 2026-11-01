from pathlib import Path as P
exec(P('.review-gd32/crystal_work.py').read_text().split("s=P('MCU.kicad_sch')")[0])
s=parse(P('MCU.kicad_sch').read_text(encoding='utf8'))
for n in children(s,'symbol'):
 print(next(p[2] for p in children(n,'property') if p[1]=='Reference'),one(n,'at'),one(n,'lib_id'))
for n in children(s,'text'):print(n)
for n in children(s,'global_label')+children(s,'label'):
 if 'RST' in n[1]:print(n)
