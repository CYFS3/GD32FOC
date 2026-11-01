from pathlib import Path as P
import re
src=P('VerifiedParts.pretty/WSD80120DN56.kicad_mod').read_text(encoding='utf8')
dst=P('VerifiedParts.pretty/WSD80120DN56_GDS123.kicad_mod')
assert not dst.exists()
mapping={'1':'3','2':'3','3':'3','4':'1','5':'2','6':'2','7':'2','8':'2','9':'2'}
s=re.sub(r'\(pad "([1-9])"',lambda m:'(pad "'+mapping[m[1]]+'"',src)
s=s.replace('"7e2c5954dcee4b73b60a624e483743bd"','"WSD80120DN56_GDS123"',1)
dst.write_text(s,encoding='utf8')
assert re.sub(r'\(pad "[1-9]"','(pad "X"',src.split('\n',1)[1])==re.sub(r'\(pad "[1-9]"','(pad "X"',s.split('\n',1)[1])
print('Verified geometry unchanged; original package S1/2/3 to schematic3, G4 to schematic1, D5/6/7/8/9 to schematic2')
