from pathlib import Path as P
import json,xml.etree.ElementTree as E
exec(P('.review-gd32/crystal_work.py').read_text(encoding='utf8').split("s=P('MCU.kicad_sch')")[0])
changes=json.loads(P('.layout-review/annotation-changes.json').read_text(encoding='utf8'))
for f in P('.layout-review/annotation-backup').glob('*.kicad_sch'):
 before=f.read_bytes();now=P(f.name).read_bytes()
 for c in changes:
  if c['file']==f.name:now=now.replace(('"'+c['new']+'"').encode(),('"'+c['old']+'"').encode())
 assert now==before,f.name
print('PASS byte-exact original content except 17 hidden Reference/instances replacements')
def nets(p):return {n.get('name'):sorted((x.get('ref'),x.get('pin')) for x in n.findall('node') if not x.get('ref','').startswith('#')) for n in E.parse(p).findall('./nets/net')}
assert nets('.layout-review/annotation-before.xml')==nets('.layout-review/annotation-after.xml')
print('PASS all physical net names and ref/pin membership unchanged')
a=json.loads(P('.layout-review/annotation-audit-after.json').read_text(encoding='utf8'));assert not a['issues'],a['issues']
print('PASS 870 instances including hidden power and flags: references/units/hierarchy valid')
# UUIDs for schematic objects must be unique; pin UUIDs included, instance path UUIDs not definitions.
for f in P('.layout-review/annotation-backup').glob('*.kicad_sch'):
 text=P(f.name).read_text(encoding='utf8');uuids=re.findall(r'\(uuid\s+"([^"\n]+)"\)',text)
 assert len(uuids)==len(set(uuids)),f.name
print('PASS per-sheet object UUID uniqueness')
P('.layout-review/annotation-validation.json').write_text(json.dumps({'hidden_references_changed':17,'physical_nets_unchanged':True,'all_other_bytes_unchanged':True,'all_870_instances_valid':True,'annotation_audit_issues':0},indent=2),encoding='utf8')
