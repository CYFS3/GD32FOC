from pin_types import *
import uuid,math,copy
uid=lambda:str(uuid.uuid4())
exec(Path('.review-gd32/crystal_work.py').read_text(encoding='utf8').split("s=P('MCU.kicad_sch')")[0])
def block(s,i):
 depth=0
 for m in re.finditer(r'"(?:\\.|[^"\\])*"|[()]',s[i:]):
  if m.group()=='(':depth+=1
  elif m.group()==')':
   depth-=1
   if depth==0:return s[i:i+m.end()]
def q(s):return json.dumps(s,ensure_ascii=False)
root=parse(Path('GD32F5_FOC.kicad_sch').read_text(encoding='utf8'));rootid=one(root,'uuid')[1]
paths={next(x[2] for x in children(sh,'property') if x[1]=='Sheetfile'):rootid+'/'+one(sh,'uuid')[1] for sh in children(root,'sheet')}
std=Path(r'D:\KiCad\HQ10.0\share\kicad\symbols\power.kicad_sym').read_text(encoding='utf8'); flaglib=block(std,std.index('(symbol "PWR_FLAG"')).replace('(symbol "PWR_FLAG"','(symbol "power:PWR_FLAG"',1)
plans={
'power.kicad_sch':[('DCBUS_IN','CN1.1 external input; polarity marking requires verification'),('PGND_IN','CN1.2 external supply return'),('DCBUS','DCBUS_IN via Q1 protection MOSFET'),('PGND','PGND_IN via Q3 protection MOSFET'),('12V','U6 LM5164 SW via L6'),('PWR_BST_U6','U6 internal VCC/bootstrap diode; C67 to SW'),('PWR_BST_U19','U19 RY8411 internal bootstrap driver; C172 to SW')],
'FOC_M1.kicad_sch':[(f'M1_VB{i}',f'12V via D{7+i}; C{129+i} to VS{i}') for i in range(1,4)],
'FOC_M2.kicad_sch':[(f'M2_VB{i}',f'12V via D{1007+i}; C{1129+i} to VS{i}') for i in range(1,4)],
'HSLink.kicad_sch':[('HSL_LINK_3V3','VCC via R8052 0R'),('HSL_USB_VBUS','USB8002 VBUS host supply')],
}
logs=[];count=9700
for fn,plan in plans.items():
 p=Path(fn);s=p.read_text(encoding='utf8');Path('.review-fixes/'+fn+'.before-power-model').write_text(s,encoding='utf8');tree=parse(s);edits=[];add=[]
 for n in nodes(s)[0]['children']:
  if kind(n)!='symbol':continue
  props={c['tokens'][1][0]:c for c in n['children'] if kind(c)=='property'}
  ref=props['Reference']['tokens'][2][0];value=props['Value']['tokens'][2][0]
  if ref.startswith('#PWR') and value in ['VREF','HSL_SHIELD']:
   at=next(c for c in n['children'] if kind(c)=='at');x,y=at['tokens'][1][0],at['tokens'][2][0]
   edits.append((n['start'],n['end'],f'(global_label {q(value)} (shape bidirectional) (at {x} {y} 0) (effects (font (size 1 1)) (justify left)) (uuid "{val(n,"uuid")}"))'))
  if ref in ['D8','D9','D10','D1008','D1009','D1010']:
   for k,c in props.items():
    if k=='Description':
     _,a,b=c['tokens'][2];edits.append((a,b,q('B16WS; see manufacturer datasheet; legacy B5819WS metadata removed')))
    elif k not in ['Reference','Value','Footprint','Datasheet'] and any(t in str(c['tokens'][2][0]) for t in ['40V','40 V','B5819']):edits.append((c['start'],c['end'],''))
 for a,b,new in sorted(edits,reverse=True):s=s[:a]+new+s[b:]
 if not any(x[1]=='power:PWR_FLAG' for x in children(one(tree,'lib_symbols'),'symbol')):
  ix=s.index('(lib_symbols')+len('(lib_symbols');s=s[:ix]+'\n'+flaglib+s[ix:]
 # Anonymous bootstrap labels directly at capacitor pin1, transformed from library geometry.
 for cref,net in [('C67','PWR_BST_U6'),('C172','PWR_BST_U19')]:
  if fn!='power.kicad_sch':continue
  ins=next(n for n in children(tree,'symbol') if any(x[1]=='Reference' and x[2]==cref for x in children(n,'property')))
  lib=next(n for n in children(one(tree,'lib_symbols'),'symbol') if n[1]==one(ins,'lib_id')[1]);pin=next(pn for sub in children(lib,'symbol') for pn in children(sub,'pin') if one(pn,'number')[1]=='1')
  at=one(ins,'at');pa=one(pin,'at');a=math.radians(float(at[3]));xx=float(pa[1]);yy=-float(pa[2]);x=float(at[1])+xx*math.cos(a)+yy*math.sin(a);y=float(at[2])-xx*math.sin(a)+yy*math.cos(a)
  add.append(f'(label "{net}" (at {x:.6f} {y:.6f} 0) (effects (font (size 1 1)) (justify left bottom)) (uuid "{uid()}"))')
 for i,(net,source) in enumerate(plan):
  x=25.4+(i%3)*83.82;y=260.35+(i//3)*12.7;ref='#FLG'+str(count);count+=1
  add.append(f'(symbol (lib_id "power:PWR_FLAG") (at {x} {y} 0) (unit 1) (in_bom no) (on_board yes) (dnp no) (uuid "{uid()}") (property "Reference" "{ref}" (at {x} {y} 0) (hide yes) (effects (font (size 1 1)))) (property "Value" "PWR_FLAG" (at {x} {y-3.81} 0) (effects (font (size 1 1)))) (pin "1" (uuid "{uid()}")) (instances (project "GD32F5_FOC" (path "/{paths[fn]}" (reference "{ref}") (unit 1)))))')
  typ='label' if net.startswith('PWR_BST') else 'global_label';shape='' if typ=='label' else '(shape bidirectional)'
  add.append(f'({typ} "{net}" {shape} (at {x} {y} 0) (effects (font (size 1 1)) (justify left bottom)) (uuid "{uid()}"))')
  add.append(f'(text {q(source)} (at {x} {y+3.81} 0) (effects (font (size 0.85 0.85)) (justify left top)) (uuid "{uid()}"))')
  logs.append((fn,ref,net,source))
 s=s[:s.rfind(')')]+'\n'+'\n'.join(add)+'\n'+s[s.rfind(')'):];p.write_text(s,encoding='utf8')
Path('.review-fixes/power-model-changes.json').write_text(json.dumps(logs,ensure_ascii=False,indent=2),encoding='utf8')
print(logs)
