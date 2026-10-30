from migrate_p2 import *
import fitz,json
p=fitz.open(W/'interface_review/final.pdf')
for idx in [1,6]:
 pg=p[idx]; words=pg.get_text('words'); print('PAGE',idx+1,'size',pg.rect)
 lines=[]
 for b in pg.get_text('dict')['blocks']:
  for l in b.get('lines',[]):
   for sp in l['spans']:
    lines.append((sp['text'],sp['bbox']))
 hits=[]
 for i,(a,ab) in enumerate(lines):
  ar=fitz.Rect(ab)
  for b,bb in lines[i+1:]:
   inter=ar&fitz.Rect(bb)
   if inter.width>.8 and inter.height>.8:hits.append((a,b,list(inter)))
 print('TEXT INTERSECTIONS',json.dumps(hits,ensure_ascii=False))
 (W/f'interface_review/text_bounds_page{idx+1}.json').write_text(json.dumps(lines,ensure_ascii=False,indent=2),encoding='utf-8')
