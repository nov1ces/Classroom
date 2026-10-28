from pathlib import Path
from fractions import Fraction as F
import json,math,struct
ROOT=Path(__file__).resolve().parents[2]
checks={f'CO{i:02}':[] for i in range(1,8)}
def check(c,name,a,e):
 ok=math.isclose(a,e,rel_tol=1e-10,abs_tol=1e-10) if isinstance(a,float) else a==e
 assert ok,(c,name,a,e)
 checks[c].append({'case':name,'actual':str(a),'expected':str(e),'passed':True})
check('CO01','加权CPI与执行时间',(F(8,10)+F(2,10)*10)*10000/F(10**9),F(28,10**6))
check('CO01','CPU加速50%后总历时',F(90)/F(3,2)+10,70)
check('CO01','编译优化时间',F(20)*F(7,10)*F(12,10),F(168,10))
check('CO01','程序y=ab+c',2*3+1,7)
check('CO02','137.5八进制整数小数',(oct(137),int(.5*8)),('0o211',4))
check('CO02','65530零扩展',hex(65530),'0xfffa')
check('CO02','负short转unsigned32',hex((-32767)%(2**32)),'0xffff8001')
check('CO02','8位69-38加法器输入',[69,255^38,1,((69+(255^38)+1)&255)],[69,217,1,31])
check('CO02','-33-65补码',hex((-33-65)%(2**32)),'0xffffff9e')
check('CO02','-0.4375单精度',struct.pack('>f',-.4375).hex(),'bee00000')
check('CO02','两负单精度比较',struct.unpack('>f',bytes.fromhex('cc900000'))[0]<struct.unpack('>f',bytes.fromhex('b0c00000'))[0],True)
check('CO02','f(23)浮点编码',struct.pack('>f',2**24-1).hex(),'4b7fffff')
check('CO02','f(24)浮点舍入',struct.unpack('>f',struct.pack('>f',2**25-1))[0],float(2**25))
check('CO02','结构体填充c地址与最低字节',[0xC008+6,273&255],[0xC00E,0x11])
check('CO02','record数组中56H字节地址',0xA0B0+20+1,0xA0C5)
# Implement quotient registers directly, separate from the prose tables.
r=0;q=15;y=2;unsigned=[]
for i in range(4):
 r=(r<<1)|(q>>3);q=(q<<1)&15;shift=(r,q);trial=r-y
 if trial>=0:r=trial;q|=1
 unsigned.append([shift[0],shift[1],trial,r,q])
check('CO02','15除2四轮恢复余数状态',unsigned,[[1,14,-1,1,14],[3,12,1,1,13],[3,10,1,1,11],[3,6,1,1,7]])
r=-1;q=9;signed=[]
for i in range(4):
 r=2*r+(q>>3);q=(q<<1)&15;trial=r+3
 if trial<0:r=trial;q|=1
 signed.append([r,q])
check('CO02','-7除3四轮状态',signed,[[-1,2],[-2,4],[-1,9],[-1,2]])
check('CO02','-7除3商符号修正与回代',[(-q)&15,r,-2*3-1],[14,-1,-7])
check('CO02','双精度商溢出边界',[255//15,200//15,200%15],[17,13,5])
check('CO03','4M乘8位DRAM复用引脚',math.ceil(22/2)+8,19)
check('CO03','256MiB芯片数量',256//4,64)
check('CO03','交叉存储体序列',[a%4 for a in [8005,8006,8007,8008,8001,8002,8003,8004,8000]],[1,2,3,0,1,2,3,0,0])
check('CO03','ROM/RAM分区芯片数',[4//2,(60//4)*2],[2,30])
check('CO03','片选111的字地址范围',[7*32768,8*32768-1],[0x38000,0x3ffff])
check('CO03','7200rpm单扇区平均ms',8+60000/7200/2+60000/7200/1000,12.175)
check('CO03','读后写数组缺失率',F(1,8),F(125,1000))
check('CO03','32KiB8路64B块字段',[32768//64//8,32-6-6],[64,20])
check('CO03','4K字Cache总bit',1024*(128+18+1+1),148*1024)
check('CO03','018H页框与840H偏移',0x018*4096+0x840,0x018840)
check('CO03','TLB标记位数',32-10-3,19)
check('CO03','TLB/Cache串行实例物理地址',[0x0d*64+0x14,0x02*64+0x31],[0x354,0x0b1])
check('CO03','32bit物理标记行号偏移重组',((0x0d*16)+5)*4+0,0x354)
check('CO04','递归阶乘溢出',math.factorial(13)%(2**32),1932053504)
check('CO04','call rel32偏移',0x00401000-(0x00401025+5),-42)
check('CO04','call rel32小端位串',struct.pack('<i',-42).hex(),'d6ffffff')
check('CO05','互斥类控制字段位数',sum(math.ceil(math.log2(x+1)) for x in [7,3,12,5,6]),15)
check('CO05','5段20条加3气泡总ns',(5+20-1+3)*2,54)
check('CO05','16位-513算术右移',((-513)//2)&65535,0xfeff)
check('CO05','无转发关键链最早ID',[6,6+4,6+8],[6,10,14])
check('CO05','STORE五段完全流出',14+3,17)
check('CO06','4B两拍10MHz带宽',F(4)*10**7/2,20*10**6)
check('CO06','1333MT每次8B',1333*8,10664)
check('CO06','非突发64bit32B块ns',(32//8)*(1+6+1),32)
check('CO06','420MHz64bitDDR峰值GB',F(420*2*8,1000),F(672,100))
check('CO06','64B七周期有效GB',F(64*420,7*1000),F(384,100))
check('CO07','定时查询CPU百分比',F(500*200,50*10**6)*100,F(1,5))
check('CO07','中断100ns每400nsCPU比例',F(100,400),F(1,4))
check('CO07','512B32bitDMA次数',512//4,128)
check('CO07','2MB设备最长查询秒',F(4,2*10**6),F(2,10**6))
check('CO07','查询设备A CPU预算',F((2*10**6//4)*10*4,500*10**6),F(4,100))
check('CO07','40MB设备中断CPU预算',F((40*10**6//4)*400,500*10**6),8)
check('CO07','40MB设备DMA CPU预算',F((40*10**6//1000)*500,500*10**6),F(4,100))
check('CO07','1000字符完整启动排空周期',1000*25070+20,25070020)
for c,rows in checks.items():
 (ROOT/c/'sources/course_numeric_checks.json').write_text(json.dumps({'chapter':c,'status':'passed','method':'independent integer/fraction/IEEE and register-state calculations','checks':rows},ensure_ascii=False,indent=2))
print(json.dumps({c:len(x) for c,x in checks.items()}))
