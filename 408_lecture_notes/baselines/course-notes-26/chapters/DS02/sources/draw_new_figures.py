from pathlib import Path
import html,subprocess
root=Path('/workspace/Classroom/408_lecture_notes/dist/course-notes-26/chapters')
def text(x,y,s,size=18):return f'<text x="{x}" y="{y}" font-size="{size}">{html.escape(s)}</text>'
def rect(x,y,w,h,label,fill='#DDEFF5'):
 return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}" stroke="#7B9AAA"/>'+text(x+9,y+h/2+6,label)
def arrow(x,y,a,b):return f'<path d="M{x},{y} L{a},{b}" fill="none" stroke="#466C82" stroke-width="2" marker-end="url(#a)"/>'
def save(ch,name,w,h,parts):
 out=root/ch/'figures';s=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6" fill="none" stroke="#466C82"/></marker></defs><rect width="100%" height="100%" fill="white"/><g font-family="Noto Sans CJK SC, sans-serif" fill="#253F4B">'+''.join(parts)+'</g></svg>'
 p=out/(name+'.svg');p.write_text(s)
 for ext in ['png','pdf']:subprocess.run(['inkscape',str(p),'--export-type='+ext,'--export-filename='+str(out/(name+'.'+ext))],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
parts=[text(24,30,'递归从n到1：同时保留每个尚未返回的调用'),text(24,73,'每层常数空间'),text(370,73,'每层保留长度k的局部数组')]
for n in range(5):
 label=['n','n−1','⋮','2','1'][n];parts+=[rect(80,90+n*43,130,34,'调用 '+label),rect(410,90+n*43,230 if n<2 else (190 if n==2 else 90+n*-7),34,label+' 个单元','#F9E8EC')]
parts+=[text(24,350,'峰值 Θ(n)'),text(370,350,'n + (n−1) + ⋯ + 1 = Θ(n²)')]
save('DS01','DS01_recursion_space',740,380,parts)
parts=[text(24,28,'相同输入：a、b、c；L为有效头结点')]
for r,(title,states) in enumerate([('头插法',['a','b a','c b a']),('尾插法',['a','a b','a b c'])]):
 y=75+r*180;parts.append(text(24,y,title))
 for k,state in enumerate(states):
  yy=y+23+k*45;parts.append(text(24,yy+25,'读入'+['a','b','c'][k]));parts.append(rect(120,yy,65,34,'L','#EEE3E9'));x=220
  parts.append(arrow(185,yy+17,220,yy+17))
  for letter in state.split():parts.append(rect(x,yy,65,34,letter));parts.append(arrow(x+65,yy+17,x+100,yy+17));x+=100
  parts.append(text(x,yy+23,'NULL'))
parts.append(text(24,435,'头插：每次接到L后；尾插：r始终指最后一个结点'))
save('DS02','DS02_build_order',730,460,parts)
parts=[text(24,30,'扩容时，新旧两块连续区域会同时存在'),text(24,85,'旧区 p')]
for i,c in enumerate('abcd'):parts.append(rect(150+i*70,58,70,42,c))
parts+=[text(24,180,'新区 q')]
for i,c in enumerate(['a','b','c','d','空','空']):parts.append(rect(150+i*70,152,70,42,c,'#E4F0E5'))
for i in range(4):parts.append(arrow(185+i*70,105,185+i*70,145))
parts+=[text(24,245,'复制length个元素 → data=q → 增加容量 → free(p)'),text(24,285,'新数组仍连续；原来的元素地址和外部指针可能失效')]
save('DS02','DS02_dynamic_growth',720,315,parts)
parts=[text(24,30,'带头结点链队列：删除最后一个数据结点'),text(24,93,'删除前')]
parts +=[rect(160,65,110,48,'头结点','#EEE3E9'),arrow(270,89,350,89),rect(350,65,100,48,'x'),arrow(450,89,510,89),text(520,95,'NULL'),text(150,145,'front'),text(355,145,'rear')]
parts +=[text(24,224,'删除后'),rect(160,196,110,48,'头结点','#EEE3E9'),arrow(270,220,350,220),text(360,226,'NULL'),text(140,285,'front = rear'),text(24,340,'先接回front->next，再让rear=front，最后释放数据结点')]
save('DS03','DS03_linkqueue_last',720,370,parts)
parts=[text(24,30,'矩阵坐标1起始，压缩数组下标0起始'),text(24,70,'4阶下三角：行优先'),text(375,70,'4阶三对角：行优先')]
k1=k2=0
for i in range(1,5):
 for j in range(1,5):
  x=45+(j-1)*65;y=100+(i-1)*52
  if i>=j:parts.append(rect(x,y,61,47,str(k1)));k1+=1
  else:parts.append(rect(x,y,61,47,'·','#F5F5F5'))
  x=410+(j-1)*65
  if abs(i-j)<=1:parts.append(rect(x,y,61,47,str(k2),'#E4F0E5'));k2+=1
  else:parts.append(rect(x,y,61,47,'0','#F5F5F5'))
parts +=[text(24,355,'k = i(i−1)/2 + j−1'),text(375,355,'k = 2i + j−3'),text(24,400,'下三角共10位置；三对角共3×4−2=10位置')]
save('DS03','DS03_matrix_positions',740,430,parts)
