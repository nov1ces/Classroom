from pathlib import Path
import json,math,struct,itertools
rows=[]
def add(q,data,expected):
 assert data==expected,(q,data,expected)
 rows.append({'question':q,'actual':data,'expected':expected,'status':'PASS'})
add('CO3-1',{'address_pins':22//2,'data_pins':8,'total':22//2+8},{'address_pins':11,'data_pins':8,'total':19})
add('CO3-2',int(math.log2(64*2**20)),26)
a=[8005,8006,8007,8008,8001,8002,8003,8004,8000];add('CO3-3',[x%4 for x in a],[1,2,3,0,1,2,3,0,0])
add('CO3-4',{'ROM':4//2,'RAM':(64-4)//4*(8//4)},{'ROM':2,'RAM':30})
rotation_ms=60/7200*1000;disk=8+rotation_ms/2+rotation_ms/1000
assert abs(disk-12.175)<1e-9;rows.append({'question':'CO3-5','actual_ms':disk,'check':'PASS'})
for offset in [0,4,8,12]:
 tags=[None]*64;miss=access=0
 for k in range(1000):
  address=offset+k*4;block=address//16;line=block%64;tag=block//64
  for op in ['read','write']:
   access+=1
   if tags[line]!=tag:miss+=1;tags[line]=tag
 expected=250 if offset==0 else 251
 assert miss==expected and access==2000
 rows.append({'question':'CO3-6','start_offset':offset,'misses':miss,'accesses':access,'miss_rate':miss/access,'status':'PASS'})
add('CO3-7',{'lines':32768//64,'sets':32768//64//8,'tag':32-6-6,'comparators':8},{'lines':512,'sets':64,'tag':20,'comparators':8})
add('CO3-8',(128+18+1+1)*1024,148*1024)
va=0x00082840;vpn=va//4096;offset=va%4096;page_table={82:(0x024,0),129:(0x180,1),130:(0x018,1)};frame,pres=page_table[vpn]
add('CO3-9',{'vpn':vpn,'offset':offset,'present':pres,'physical':frame*4096+offset},{'vpn':130,'offset':0x840,'present':1,'physical':0x018840})
add('CO3-10',32-int(math.log2(1024))-int(math.log2(32//4)),19)
add('CO2-7',struct.pack('>f',-0.4375).hex().upper(),'BEE00000')
x=struct.unpack('>f',bytes.fromhex('CC900000'))[0];y=struct.unpack('>f',bytes.fromhex('B0C00000'))[0]
add('CO2-8',{'x_negative':x<0,'y_negative':y<0,'x_lt_y':x<y,'x_exponent':((0xCC900000>>23)&255)-127,'y_exponent':((0xB0C00000>>23)&255)-127},{'x_negative':True,'y_negative':True,'x_lt_y':True,'x_exponent':26,'y_exponent':-30})
def stuff(data):
 out='';ones=0
 for b in data:
  out+=b;ones=ones+1 if b=='1' else 0
  if ones==5:out+='0';ones=0
 return out
add('CN3-1',stuff('0111110001111110'),'011111000011111010')
def mod2(a,b):
 while a.bit_length()>=b.bit_length():a^=b<<(a.bit_length()-b.bit_length())
 return a
add('CN3-2',[format(mod2(int(x,2),0b10011),'04b') for x in ['101110000','101110100','101111000','101111100']],['1100','1000','0100','0000'])
words=['10011010','01011100','11110000','00001111'];ds=[sum(a!=b for a,b in zip(x,y)) for x,y in itertools.combinations(words,2)]
add('CN3-3',ds,[4,4,4,4,4,8])
add('CN3-4',1000*8/10000/(1000*8/10000+0.4+1000*8/10000),0.4)
add('CN3-5',list(range(max([0,2,3])+1,8)),[4,5,6,7])
chips=[2,0,2,0,0,-2,0,-2,0,2,0,2];symbols=[sum(chips[i:i+4])/4 for i in range(0,12,4)];add('CN3-7',symbols,[1,-1,1])
add('CN3-8',2e8*(800/1e9/2),80.0)
add('CN3-9',1998*8/54+28+28+2,354.0)
add('CN3-11',6*8/(100*1e6)*1e6,0.48)
Path(__file__).with_name('review_calculation_results.json').write_text(json.dumps({'scope':'独立算式/执行轨迹；不代替题源身份与图文核验','results':rows},ensure_ascii=False,indent=2))
print('PASS',len(rows),'actual calculation records')
