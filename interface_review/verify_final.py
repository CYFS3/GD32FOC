import json,xml.etree.ElementTree as E
r=E.parse('interface_review/final.xml');cs={c.get('ref'):c for c in r.findall('./components/comp')}; nets={n.get('name'):{(p.get('ref'),p.get('pin'))for p in n.findall('node')}for n in r.findall('./nets/net')};pn={p:n for n,ps in nets.items()for p in ps};checks={}
for ref,expected in {'J300':{'1':'VCC','2':'GND','3':'LCD_SCK','4':'LCD_MOSI','5':'LCD_CS_N','6':'LCD_DC','7':'LCD_RST_N','8':'LCD_BL_CTRL'},'U9101':{'1':'M1_ENC_A_IN','6':'M1_ENC_B_IN','3':'M1_ENC_C_IN','7':'M1_HALL_A','2':'M1_HALL_B','5':'M1_HALL_C','8':'VCC','4':'GND'},'U9102':{'1':'M2_ENC_A_IN','6':'M2_ENC_B_IN','3':'M2_ENC_C_IN','7':'M2_HALL_A','2':'M2_HALL_B','5':'M2_HALL_C','8':'VCC','4':'GND'}}.items():checks[ref+'_pins']=all(pn.get((ref,p))==n for p,n in expected.items())
for ref in ['R312','R314','R316','R318']:checks[ref+'_not_bypassed']=pn[(ref,'1')]!=pn[(ref,'2')]
for motor in (1,2):
 off=(motor-1)*1000
 for rr in [88,89,90,106,107,108]:checks[f'R{rr+off}_DNP']='dnp' in [p.get('name')for p in cs[f'R{rr+off}'].findall('property')]
 for rr in [9101+(motor-1)*2,9102+(motor-1)*2]:checks[f'R{rr}_selector_DNP']=('dnp'in[p.get('name')for p in cs[f'R{rr}'].findall('property')])==(rr%2==0)
 checks[f'M{motor}_headerpower']=pn[(f'CN{5+off}','6')]==f'M{motor}_ENC_VSUP'
 checks[f'M{motor}_PWMpullup']=pn[(f'R{54+off}','1')]=='5V'
checks['all']=all(checks.values());print(json.dumps(checks,indent=2))
