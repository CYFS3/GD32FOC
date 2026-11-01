from pathlib import Path as P
exec(P('.review-gd32/crystal_work.py').read_text(encoding='utf8').split("s=P('MCU.kicad_sch')")[0])
s=parse(P('MCU.kicad_sch').read_text(encoding='utf8'))
for n in children(s,'symbol'):
 ref=next(p[2] for p in children(n,'property') if p[1]=='Reference');print(ref,one(n,'at'))
 if ref=='U1':print('U1UNIT',one(n,'unit'))
for n in children(s,'no_connect'):print('NC',one(n,'at'),one(n,'uuid'))
for n in children(s,'text'):print('TEXT',n[1],one(n,'at'))
for l in children(one(s,'lib_symbols'),'symbol'):
 if l[1].startswith('MCU:'):
  for u in children(l,'symbol'):
   for p in children(u,'pin'):
    if one(p,'number')[1] in ['8','9']:print('PIN',p)
