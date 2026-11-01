import json,collections,pathlib
P=pathlib.Path
def load(n):return [v for s in json.loads(P(n).read_text(encoding='utf-8'))['sheets'] for v in s['violations']]
def key(v):return (v['type'],v['severity'],v['description'],tuple(sorted(i['uuid'] for i in v.get('items',[]))))
b=load('.review-gd32/erc-before.json');a=load('.review-gd32/erc-after.json');bk={key(v) for v in b};ak={key(v) for v in a}
print('before',len(b),collections.Counter(v['severity'] for v in b));print('after',len(a),collections.Counter(v['severity'] for v in a))
for v in a:
 if key(v) not in bk:print('ADDED',json.dumps(v,ensure_ascii=False))
for v in b:
 if key(v) not in ak:print('REMOVED',json.dumps(v,ensure_ascii=False))
