from audit import *
f=W/'HSLink.kicad_sch';s=f.read_text(encoding='utf-8');r=parse(s);ops=[]
for n in r.kids('global_label'):
 if n.items[1]=='HSL_ISP_KEY' and xy(n)==(128.98,106.2):nx,ny,ang=132.79,106.2,270
 elif n.items[1]=='HSL_LINK_DP' and xy(n)==(167.08,126.52):nx,ny,ang=160.73,126.52,90
 else:continue
 for at in [n.one('at')]+[p.one('at') for p in n.kids('property')]:
  ops.append((at.start,at.end,f'(at {nx:.6f} {ny:.6f} {ang})'))
 j=n.one('effects').one('justify');ops.append((j.start,j.end,'(justify left)' if ang==90 else '(justify right)'))
f.write_bytes(patches(s,ops).encode())
