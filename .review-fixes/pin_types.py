from pathlib import Path
import re,json,shutil
# Lossless s-expression spans; only electrical type token replaced.
def nodes(text):
 stack=[]; roots=[]
 for m in re.finditer(r'"(?:\\.|[^"\\])*"|[^\s()]+|[()]',text):
  t=m.group()
  if t=='(':
   n={'start':m.start(),'tokens':[],'children':[]}
   if stack:stack[-1]['children'].append(n)
   else:roots.append(n)
   stack.append(n)
  elif t==')':stack.pop()['end']=m.end()
  else:stack[-1]['tokens'].append((json.loads(t) if t.startswith('"') else t,m.start(),m.end()))
 return roots

def val(n,k):
 return next((x['tokens'][1][0] for x in n['children'] if x['tokens'][0][0]==k),None)
def kind(n):return n['tokens'][0][0]
def walk(n):
 yield n
 for c in n['children']:yield from walk(c)
PASSIVE={'5012','B16WS','B5819WS_C305446','C0603_S','C0603_S_1','C1206_S_1','CGA0603X5R105K500JT','MR30PW-F','R0603_S','R0603_S_1','R2512_S','WAFER-GH1.25-6PWB','BLM18KG121TN1D','CapAcitance','DZ127S-22-10-55','FTC252010S4R7MBCA','PRTR5V0U2X_C5158049','TS-1088-AR02016','TYPE-C 16PIN 2MD(073)','XL7EL89CKI-111YLC-24M','PTS815SJK250SMTRLFS','0402WGF1002TCE','0402WGF0000TCE','1N4148WS T4','AFC07-S16ECA-00','CL05A106MQ5NUNC','1.5SMC30CAHE3/57T','100nF','10K','2.2uH','52.3K','LED-0603_R_1','SMNR6045-470MT','VKME1001K820MV','XT30PW-M','ZMM15V','ZMM62','c1206_s','C0402'}
MAP={
'LP5907QMFX-3.3Q1':{'1':'power_in','2':'power_in','3':'input','4':'no_connect','5':'power_out'},
'XC6210B332MR':{'1':'power_in','2':'power_in','3':'input','4':'no_connect','5':'power_out'},
'FD6288Q_C328453':{**{str(x):'power_in' for x in [4,6,12,14,15,17,18,20,25]},**{str(x):'output' for x in [9,10,11,13,16,19]},**{str(x):'no_connect' for x in [5,7,8,21]}},
'LM5164DDAR':{'1':'power_in','2':'power_in','6':'open_collector','7':'power_in','8':'power_out','9':'passive'},
'TD1466':{'1':'power_in','2':'power_in','5':'power_in','6':'power_out'},
'TPS563201DDCR':{'1':'power_in','2':'power_out','3':'power_in','4':'input','5':'input','6':'power_in'},
'CH213K':{'1':'power_in','2':'power_out','3':'power_in'},
'LM321MF/NOPB':{'2':'power_in','5':'power_in'},
}
def desired(sym,p):
 name=sym.split(':')[-1]; pn=val(p,'number'); nm=val(p,'name')
 if name in PASSIVE or name=='电阻':return 'passive'
 if name=='RS6334XQ':return 'output' if nm.startswith('OUT') else 'power_in' if nm in ['V+','V-'] else 'input'
 if name in ['KCD3008A','WSD80120DN56_1','WSD90P06DN56_1','FMMT593']:return 'passive'
 if name=='HPM5301IEG1':
  if re.match(r'P[ABY]\d',nm):return 'bidirectional'
  if nm in ['VDD_SOC','VIO_B00','VIO_B01','VPMC','VREFL','VREFH','VANA','VSS']:return 'power_in'
  if nm in ['RESETN','WAKEUP','XTALI']:return 'input'
  if nm=='XTALO':return 'output'
 return MAP.get(name,{}).get(pn)
def patch(text):
 root=nodes(text)[0]; edits=[]; changes=[]
 lib=next((c for c in root['children'] if kind(c)=='lib_symbols'),root)
 for sym in lib['children']:
  if kind(sym)!='symbol':continue
  sid=sym['tokens'][1][0]
  # Garbled resistor import identified by reference R and exactly two numbered pins.
  ref=next((c['tokens'][2][0] for c in sym['children'] if kind(c)=='property' and c['tokens'][1][0]=='Reference'),None)
  for pin in walk(sym):
   if kind(pin)!='pin' or len(pin['tokens'])<3:continue
   new=desired(sid,pin)
   if ref=='R':new='passive'
   if new and new!=pin['tokens'][1][0]:
    old,a,b=pin['tokens'][1];edits.append((a,b,new));changes.append((sid,val(pin,'number'),old,new))
 for a,b,s in sorted(edits,reverse=True):text=text[:a]+s+text[b:]
 return text,changes
if __name__=='__main__':
 files=['FOC_M1.kicad_sch','FOC_M2.kicad_sch','HSLink.kicad_sch','Interface.kicad_sch','power.kicad_sch','ProDoc_Boa-easyedapro.kicad_sym','ProDoc_IPB-easyedapro.kicad_sym','Interface.kicad_sym']
 logs={}
 for name in files:
  p=Path(name);s=p.read_text(encoding='utf8');out,changes=patch(s)
  if changes:
   dest=Path('.review-fixes')/name
   if not dest.exists():shutil.copy2(p,dest)
   p.write_text(out,encoding='utf8');logs[name]=changes
 Path('.review-fixes/type-changes.json').write_text(json.dumps(logs,indent=2,ensure_ascii=False),encoding='utf8')
 print({k:len(v) for k,v in logs.items()})
