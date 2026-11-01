from pathlib import Path
import re,json,hashlib
src=Path(r'E:\MCU\GD32\GD32F5_FOC\data\FOC\ProDoc_1.axdr_v1.3_2026-10-31-import-fps.pretty\DFN-8_L5.8-W4.9-P1.27-LS6.0-BL-1.kicad_mod')
out=Path('VerifiedParts.pretty/WSD90P06DN56_GDS123.kicad_mod')
assert not out.exists(),'Do not overwrite existing model'
s=src.read_text(encoding='utf8')
def parse(text):
 stack=[];root=None
 for t in re.findall(r'"(?:\\.|[^"\\])*"|[^\s()]+|[()]',text):
  if t=='(':
   n=[]
   if stack:stack[-1].append(n)
   else:root=n
   stack.append(n)
  elif t==')':stack.pop()
  else:stack[-1].append(json.loads(t) if t.startswith('"') else t)
 return root
def child(n,k):return next((x for x in n if isinstance(x,list) and x[0]==k),None)
def children(n,k):return [x for x in n if isinstance(x,list) and x[0]==k]
a=parse(s);pads=children(a,'pad');assert len(pads)==9
for p in pads:
 assert p[2]=='thru_hole' and child(p,'drill')==['drill','0.001']
 assert child(p,'layers')==['layers','*.Cu','*.Mask']
t=s.replace('(footprint "DFN-8_L5.8-W4.9-P1.27-LS6.0-BL-1"','(footprint "WSD90P06DN56_GDS123"',1)
t=t.replace('(layer "F.Cu")','(layer "F.Cu")\n\t(attr smd)\n\t(descr "WSD90P06DN56 reference Q1 C719104; G=1 D=2 incl EP S=3; corrected imported 0.001mm thru-hole pads to SMD. Reference geometry adopted; manufacturer drawing visual verification pending.")',1)
t=t.replace('(property "Value" ""','(property "Value" "WSD90P06DN56"',1)
t=re.sub(r'(\(pad "[123]") thru_hole rect',r'\1 smd rect',t)
t=t.replace('\n\t\t(drill 0.001)','').replace('(layers "*.Cu" "*.Mask")','(layers "F.Cu" "F.Paste" "F.Mask")').replace('\n\t\t(remove_unused_layers no)','')
b=parse(t);np=children(b,'pad')
assert len(np)==9
for p,q in zip(pads,np):
 assert q[2]=='smd' and child(q,'drill') is None
 assert child(q,'layers')==['layers','F.Cu','F.Paste','F.Mask']
 def core(x):return [x[0],x[1],x[3]]+[i for i in x[4:] if not(isinstance(i,list) and i[0] in ['drill','layers','remove_unused_layers'])]
 assert core(p)==core(q)
for k in ['fp_line','fp_poly','fp_circle','fp_rect','fp_text']:
 assert children(a,k)==children(b,k),k
counts={k:sum(p[1]==k for p in np) for k in ['1','2','3']};assert counts=={'1':1,'2':5,'3':3}
out.write_text(t,encoding='utf8')
report={'source':str(src),'output':str(out),'source_sha256':hashlib.sha256(s.encode()).hexdigest(),'output_sha256':hashlib.sha256(t.encode()).hexdigest(),'electrodes':{'1':'G','2':'D including EP','3':'S'},'pad_counts':counts,'pads':[{'number':p[1],'at':child(p,'at')[1:],'size':child(p,'size')[1:],'type':p[2],'layers':child(p,'layers')[1:]} for p in np],'unchanged':'all pad number/position/size/rotation/shape/uuid and all graphics including existing F.Paste','changes':['footprint name and value','attr smd and source description','9 pad types thru_hole -> smd','9 drill=0.001 removed','9 layer sets *.Cu/*.Mask -> F.Cu/F.Paste/F.Mask','9 remove_unused_layers removed'],'limitations':['Reference exact MPN evidence, not manufacturer visual pin/land pattern certification','Existing paste polygons retained; EP stencil coverage requires manufacturing review','No schematic or PCB modified']}
Path('.layout-review/q1-footprint-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False,indent=2))
