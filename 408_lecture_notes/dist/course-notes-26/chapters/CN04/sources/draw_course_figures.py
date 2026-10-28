from pathlib import Path
import html,subprocess
R=Path(__file__).resolve().parents[2]
def T(x,y,s,size=18):return f'<text x="{x}" y="{y}" font-size="{size}">{html.escape(s)}</text>'
def save(ch,stem,body,w=960,h=500):
 p=R/ch/'figures'/f'{stem}.svg';p.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="100%" height="100%" fill="white"/><defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6" fill="#466c82"/></marker></defs><g font-family="Noto Sans CJK SC,sans-serif" fill="#243743">'+''.join(body)+'</g></svg>')
 for ext in ['png','pdf']:subprocess.run(['inkscape',str(p),f'--export-type={ext}',f'--export-filename={p.with_suffix("."+ext)}'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def box(x,y,w,h,s,color='#e1edf1'):
 return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{color}" stroke="#7395a5"/>'+T(x+12,y+h/2+7,s)
def arrow(x,y,xx,yy):return f'<path d="M{x},{y} L{xx},{yy}" fill="none" stroke="#466c82" stroke-width="2" marker-end="url(#a)"/>'
b=[T(25,30,'128.14.32.128/27：32个地址，按边界二分')]
b += [box(320,55,300,45,'.128～.159 /27'),arrow(390,100,240,145),arrow(550,100,700,145),box(70,145,340,55,'.128～.143 /28：网吧'),box(550,145,340,55,'.144～.159 /28')]
b += [arrow(630,200,540,245),arrow(810,200,820,245),box(330,245,320,55,'.144～.151 /29：家庭'),box(680,245,250,55,'.152～.159 /29')]
b += [arrow(750,300,620,345),arrow(860,300,850,345),box(420,345,330,55,'.152～.155 /30：点对点'),box(765,345,185,55,'.156～.159 /30')]
b += [T(65,435,'网吧可用 .129～.142；家庭可用 .145～.150；点对点可用 .153、.154',17),T(65,470,'每块地址数含网络地址和广播地址；上级可用 /27 聚合，本地保留不同出口的具体项',16)]
save('CN04','CN_course_vlsm',b)
b=[T(25,28,'经典三重复ACK：先有原ACK，再逐个数重复ACK'),T(115,65,'发送方'),T(725,65,'接收方')]
for x in [170,780]:b.append(f'<line x1="{x}" y1="80" x2="{x}" y2="625" stroke="#9aacb5"/>')
for y,label,back in [(95,'seq=622，1 B','ACK623：首次，推进确认'),(205,'seq=624，1 B（623丢失）','ACK623：重复1'),(315,'seq=625，1 B','ACK623：重复2'),(425,'seq=626，1 B','ACK623：重复3，触发重传')]:
 b += [arrow(170,y,780,y+30),T(260,y-5,label),arrow(780,y+40,170,y+70),T(270,y+83,back,17)]
b += [arrow(170,580,780,610),T(270,570,'立即重传seq=623；补齐后累计ACK627',18)]
save('CN05','CN_course_duplicate_acks',b,960,650)
b=[T(25,30,'偶校验海明码：各组由位号的二进制位决定')]
for j in range(7):
 pos=j+1;x=140+j*105
 b += [box(x,65,90,48,f'H{pos}'),T(x+35,135,str(['0','1','0','0','1','0','1'][j]))]
for k,(name,ps) in enumerate([('P1：最低位为1',[1,3,5,7]),('P2：次低位为1',[2,3,6,7]),('P3：第3位为1',[4,5,6,7])]):
 y=185+k*80;b += [T(15,y+25,name,17)]
 for pos in ps:b.append(box(140+(pos-1)*105,y,90,40,f'H{pos}', ['#e7e0ef','#dcebdc','#f0e2cb'][k]))
b += [T(30,455,'按H7→H1书写得到1010010；第2位翻转后，综合征S3S2S1=010₂，定位H2',18)]
save('CN03','CN_course_hamming_groups',b,960,485)
b=[T(25,35,'邮件系统：提交、服务器间转送、用户读取')]
for x,s in [(30,'发件用户代理'),(270,'发送邮件服务器'),(520,'接收邮件服务器'),(770,'收件用户代理')]:b.append(box(x,100,175,70,s))
b += [arrow(205,135,270,135),arrow(445,135,520,135),arrow(695,135,770,135)]
b += [T(206,100,'SMTP',15),T(446,100,'SMTP',15),T(697,100,'POP3',15),T(690,225,'由用户代理发起读取请求',16),arrow(850,190,605,190)]
b += [T(40,285,'邮件投递：用户代理提交 → 发送服务器排队 → 接收服务器邮箱',18),T(40,330,'邮件读取：收件用户代理向服务器发起请求；Web邮箱浏览器侧可用HTTP',17),T(40,375,'MIME描述邮件内容及编码，SMTP负责投递，POP3负责读取',18)]
save('CN06','CN_course_mail_flow',b,960,405)
