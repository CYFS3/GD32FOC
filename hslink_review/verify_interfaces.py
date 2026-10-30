import xml.etree.ElementTree as E,json
r=E.parse('hslink_review/after.xml'); ix={(p.get('ref'),p.get('pin')):n for n in r.findall('./nets/net') for p in n.findall('node')};checks=[]
def same(name,*pins):
 ns=[ix.get(p) for p in pins];checks.append({'name':name,'pass':ns[0] is not None and all(n is ns[0] for n in ns)})
def diff(name,a,b):checks.append({'name':name,'pass':ix.get(a) is not None and ix.get(b) is not None and ix[a] is not ix[b]})
for a,b,c,d in [('R8066','R8901','U1','72'),('R8065','R8902','U1','76'),('R8070','R8903','U1','14'),('R8067','R8904','U1','86'),('R8069','R8905','U1','87')]:
 same(b+' probe side',(a,'2'),(b,'1'));same(b+' target side',(b,'2'),(c,d));diff(b+' separated pins',(b,'1'),(b,'2'))
same('USB D+ to HPM',('USB8002','6'),('USB8002','8'),('U8006','44'))
same('USB D- to HPM',('USB8002','5'),('USB8002','7'),('U8006','43'))
same('Buck feedback',('U8010','4'),('R8075','1'),('R8077','1'),('C8089','1'))
same('Buck input and enable pullup',('U8010','3'),('U8008','2'),('R8076','2'))
same('Passive target voltage header',('H8001','1'),('U1','11'))
diff('Probe5V separate motor5V',('U8010','3'),('U20','1'))
diff('USBVBUS separate motor5V',('USB8002','2'),('U20','1'))
diff('Probe3V3 separate targetVCC',('U8006','6'),('U1','11'))
same('Shared ground',('U8006','49'),('U1','10'))
print(json.dumps({'pass':all(c['pass'] for c in checks),'checks':checks},indent=2))
