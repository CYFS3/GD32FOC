from pathlib import Path
import re,json,math,collections
base=Path(r'E:\MCU\GD32\GD32F5_FOC\data')
def parse(s):
 ts=re.findall(r'"(?:\\.|[^"\\])*"|[^\s()]+|[()]',s);stack=[];out=[]
 for t in ts:
  if t=='(':
   n=[]
   if stack:stack[-1].append(n)
   else:out.append(n)
   stack.append(n)
  elif t==')':stack.pop()
  else:stack[-1].append(json.loads(t) if t.startswith('"') else t)
 return out[0]
def ch(n,k):return [x for x in n if isinstance(x,list) and x and x[0]==k]
def one(n,k,default=None):return next(iter(ch(n,k)),default)
def xy(n,k):return [float(v) for v in one(n,k,['',0,0])[1:]]
allout={}
for key,filename in [('FOC','ProDoc_1.axdr_v1.3_2026-10-31'),('HPM','ProDoc_IPB-TINY_2026-10-31')]:
 p=base/key/(filename+'.kicad_pcb');tree=parse(p.read_text(encoding='utf8'));fps=[];edges=[]
 for n in ch(tree,'footprint'):
  props={x[1]:x[2] for x in ch(n,'property')};pads=[]
  for pad in ch(n,'pad'):
   net=one(pad,'net',['',0,'']);pads.append({'number':pad[1],'type':pad[2],'shape':pad[3],'local_at':xy(pad,'at'),'size':xy(pad,'size'),'net':net[-1],'pinfunction':one(pad,'pinfunction',['',''])[1]})
  fps.append({'reference':props.get('Reference'),'value':props.get('Value'),'footprint':n[1],'at':xy(n,'at'),'layer':one(n,'layer',['',''])[1],'pads':pads})
 for n in tree:
  if isinstance(n,list) and n[0].startswith('gr_') and one(n,'layer',['',''])[1]=='Edge.Cuts':edges.append({'type':n[0],'start':xy(n,'start'),'mid':xy(n,'mid') if one(n,'mid') else None,'end':xy(n,'end'),'center':xy(n,'center') if one(n,'center') else None,'pts':one(n,'pts')})
 coords=[pt[:2] for e in edges for pt in [e['start'],e['end'],e['mid']] if pt]
 bounds={'xmin':min(p[0] for p in coords),'xmax':max(p[0] for p in coords),'ymin':min(p[1] for p in coords),'ymax':max(p[1] for p in coords)} if coords else {}
 if bounds:bounds.update(width=bounds['xmax']-bounds['xmin'],height=bounds['ymax']-bounds['ymin'])
 allout[key]={'source':str(p),'thickness':one(one(tree,'general'),'thickness')[1],'copper_layers':[n[1] for n in one(tree,'layers')[1:] if isinstance(n,list) and n[1].endswith('.Cu')],'outline':edges,'outline_coordinate_bounds':bounds,'counts':dict(collections.Counter(n[0] for n in tree if isinstance(n,list))),'footprints':fps}
 print(key,bounds,'layers',allout[key]['copper_layers'],'fps',len(fps))
 for f in fps:
  if f['reference'] and (f['reference'].startswith(('U','Q','USB','X','CN')) or 'crystal' in f['footprint'].lower()):print(f['reference'],f['value'],f['at'],f['layer'])
Path('.layout-review/reference-coordinates.json').write_text(json.dumps(allout,ensure_ascii=False,indent=2),encoding='utf8')
