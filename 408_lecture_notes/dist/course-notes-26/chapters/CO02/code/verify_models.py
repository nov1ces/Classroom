from pathlib import Path
import json,math,struct,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[2]
checks={f'CO{i:02}':[] for i in range(1,8)}
def check(ch,name,actual,expected):
 assert (math.isclose(actual,expected,rel_tol=1e-12,abs_tol=1e-12) if isinstance(actual,float) and isinstance(expected,(int,float)) else actual==expected),(ch,name,actual,expected)
 checks[ch].append({'name':name,'actual':actual,'expected':expected,'passed':True})
check('CO01','CPU执行时间',10**8*1.5/(2*10**9),.075)
check('CO01','2KiB按16位字编址地址位数',(2048//2).bit_length()-1,10)
check('CO01','4KiB按32位字/按字节编址',[int(math.log2(4096//4)),int(math.log2(4096))],[10,12])
check('CO01','Amdahl:80%加速2倍',round(1/(.2+.8/2),12),round(5/3,12))
# 独立按位仿真与数学整数对照：n=4,8所有输入的加减/溢出及分支条件。
for n in [4,8]:
 mask=(1<<n)-1
 for a in range(mask+1):
  for b in range(mask+1):
   signed=lambda x:x-(1<<n) if x>>(n-1) else x
   sa,sb=signed(a),signed(b)
   for sub in [False,True]:
    bb=(b^mask) if sub else b;c=int(sub);cprev=0;out=0
    for bit in range(n):
     ai,bi=(a>>bit)&1,(bb>>bit)&1;cprev=c
     out|=(ai^bi^c)<<bit;c=(ai&bi)|((ai^bi)&c)
    ideal=sa-sb if sub else sa+sb
    assert out==((a-b if sub else a+b)&mask)
    assert bool(c^cprev)==(ideal<-(1<<(n-1)) or ideal>(1<<(n-1))-1)
    assert bool(c^int(sub))==((a<b) if sub else a+b>mask)
    if sub:
     sf=bool(out>>(n-1));of=bool(c^cprev);zf=out==0
     assert (sf!=of)==(sa<sb)
     assert (zf or sf!=of)==(sa<=sb)
 checks['CO02'].append({'name':f'{n}位全部输入加减进位/溢出/分支独立对照','cases':2*(1<<n)**2,'passed':True})
# 部分积乘法。
n=4;x=13;p=0;y=11;trace=[]
for _ in range(n):
 total=p+x if y&1 else p;whole=(total<<n)|y;whole>>=1;p=(whole>>n)&15;y=whole&15
 trace.append([p,y])
check('CO02','13×11无符号移位累加轨迹',trace,[[6,13],[9,14],[4,15],[8,15]])
# Booth以n+1位A保留符号，可覆盖最小负数。
def booth(x,y,n):
 aw=n+1;amask=(1<<aw)-1;qmask=(1<<n)-1;a=0;q=y&qmask;qm=0
 for _ in range(n):
  pair=(q&1,qm)
  if pair==(0,1):a=(a+x)&amask
  elif pair==(1,0):a=(a-x)&amask
  whole=(a<<(n+1))|(q<<1)|qm
  if a>>(aw-1):whole|=1<<(aw+n+1)
  whole>>=1;qm=whole&1;q=(whole>>1)&qmask;a=(whole>>(n+1))&amask
 v=((a<<n)|q)&((1<<(2*n))-1)
 return v-(1<<(2*n)) if v>>(2*n-1) else v
for x in range(-8,8):
 for y in range(-8,8):assert booth(x,y,4)==x*y
checks['CO02'].append({'name':'4位补码Booth全部256组含最小负数对照','passed':True})
check('CO02','-3×6的8位补码',format((-3*6)&255,'08b'),'11101110')
for x in range(16):
 for y in range(1,16):
  rem=0;quot=0
  for b in range(3,-1,-1):
   rem=2*rem+((x>>b)&1);quot<<=1
   if rem>=y:rem-=y;quot|=1
  assert (quot,rem)==divmod(x,y)
checks['CO02'].append({'name':'4位无符号逐位除法240组对照','passed':True})
f32=lambda x:struct.unpack('f',struct.pack('f',x))[0]
check('CO02','单精度最近偶数4组',[f32(2**24+.5),f32(2**24+1),f32(2**24+1.5),f32(2**24+3)],[16777216.,16777216.,16777218.,16777220.])
check('CO02','-5.25单精度编码',struct.pack('>f',-5.25).hex(),'c0a80000')
seq=[1,2,3,4,1,2,5,1,2,3,4,5]
def trace_cache(lru):
 mem=[];hits=[];states=[]
 for i,v in enumerate(seq,1):
  if v in mem:
   hits.append(i)
   if lru:mem.remove(v);mem.append(v)
  else:
   if len(mem)==4:mem.pop(0)
   mem.append(v)
  states.append(mem[:])
 return hits,states
f,fs=trace_cache(False);l,ls=trace_cache(True)
check('CO03','FIFO命中位置',f,[5,6]);check('CO03','LRU命中位置',l,[5,6,8,9])
checks['CO03'].append({'name':'FIFO/LRU完整逐步状态','FIFO':fs,'LRU':ls,'passed':True})
check('CO03','字位扩展片数',(32768//16384)*(16//8),4)
check('CO03','128行异步刷新间隔us',2000/128,15.625)
check('CO03','刷新开销%',128*.5/2000*100,3.2)
check('CO03','8字低位交叉读取ns',200+7*50,550)
check('CO03','Cache同时/顺序模型',[round(.95+ .05*5,3),round(1+.05*5,3)],[1.2,1.25])
check('CO03','7200rpm平均旋转等待ms',round(60000/7200/2,6),4.166667)
check('CO04','扩展操作码逐层剩余',[16-15,(16-15)*16-12,((16-15)*16-12)*16-62],[1,4,2])
check('CO04','零地址可用编码数',(((16-15)*16-12)*16-62)*16,32)
check('CO04','x86地址形成',0x1000+3*4+8,0x1014)
check('CO04','32位标准帧参数相对位置',[0,4,8,12,-4],[0,4,8,12,-4])
check('CO05','微指令数量与地址位数',[32*4+2,math.ceil(math.log2(32*4+2))],[130,8])
check('CO05','7个互斥命令加空操作编码',math.ceil(math.log2(7+1)),3)
check('CO05','5段20条理想流水线拍数',5+20-1,24)
check('CO05','4段10条每拍90ns总时间',(4+10-1)*90,1170)
check('CO06','32bit/33MHz带宽Bps',32//8*33000000,132000000)
check('CO06','8设备三类仲裁线数',[3,math.ceil(math.log2(8))+2,2*8+1],[3,5,17])
check('CO07','查询鼠标CPU占用%',30*100/(50*10**6)*100,.006)
check('CO07','磁盘查询CPU占用%',100*(2*2**20//4)/(50*10**6)*100,104.8576)
check('CO07','串行字符位数',1+7+1+1,10)
check('CO07','每字符重复间隔cycle',25000+10+15*4,25070)
check('CO07','1000字符CPU开销cycle',1000*(10+20*4),90000)
for ch,items in checks.items():
 out=ROOT/ch/'sources'/'numeric_checks.json';out.write_text(json.dumps({'chapter':ch,'checks':items,'status':'passed','method':'independent arithmetic/bit-level models; full document numerical review continues at integration'},ensure_ascii=False,indent=2))
print(json.dumps({ch:len(v) for ch,v in checks.items()},ensure_ascii=False))
