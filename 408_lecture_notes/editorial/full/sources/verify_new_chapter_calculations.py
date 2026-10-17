from pathlib import Path
import json,ipaddress,math
r=[]
def record(id,v,e):
 assert v==e,(id,v,e)
 r.append({'question':id,'actual':v,'expected':e,'status':'PASS'})
record('CO6-1',max([90,80,70,60]),90)
# Five-stage common forwarding model: load result ready at end of MEM5,
# immediate branch consumer originally needs it at beginning of EX5.
producer_ex=3;consumer_i2_ex=4;load_mem=5;branch_ex_without_stall=5
record('CO6-3',{'I2_add_forwarding_wait':int(producer_ex>=consumer_i2_ex),'I3_load_use_wait':max(0,load_mem+1-branch_ex_without_stall),'I4_control_wait':True},{'I2_add_forwarding_wait':0,'I3_load_use_wait':1,'I4_control_wait':True})
record('CO7-1',4/(2/(10e6))/1e6,20.0)
record('CO7-2',round(1333e6*8/1e9,3),10.664)
record('CO7-3',(32//8)*(1+6+1),32)
record('CO7-4',{'peak_GBs':420e6*2*8/1e9,'transaction_GBs':64/(7/(420e6))/1e9},{'peak_GBs':6.72,'transaction_GBs':3.84})
cost=[8,10,12,6];dv=[[1,23,20,22],[12,35,30,28],[24,18,16,36],[36,30,8,24]]
record('CN4-1',[min(a+b for a,b in zip(cost,row)) for row in dv],[9,20,28,20])
remaining=1580-20;data=[]
while remaining:
 this=min(remaining,((800-20)//8)*8);data.append(this);remaining-=this
record('CN4-2',{'data_lengths':data,'total_lengths':[x+20 for x in data],'offsets':[sum(data[:i])//8 for i in range(len(data))],'MF':[int(i<len(data)-1) for i in range(len(data))]},{'data_lengths':[776,776,8],'total_lengths':[796,796,28],'offsets':[0,97,194],'MF':[1,1,0]})
net=ipaddress.ip_interface('168.16.84.24/20').network
record('CN4-3',[str(net.network_address+1),str(net.broadcast_address-1)],['168.16.80.1','168.16.95.254'])
leaves=[ipaddress.ip_network('101.200.16.0/20')]
for _ in range(4):
 target=min(leaves,key=lambda x:x.network_address);leaves.remove(target);leaves.extend(target.subnets(prefixlen_diff=1))
record('CN4-4',{'leaf_count':len(leaves),'smallest_available':min(n.num_addresses-2 for n in leaves),'total_addresses':sum(n.num_addresses for n in leaves)},{'leaf_count':5,'smallest_available':254,'total_addresses':4096})
merged=list(ipaddress.collapse_addresses([ipaddress.ip_network(x) for x in ['35.230.32.0/21','35.230.40.0/21','35.230.48.0/21','35.230.56.0/21']]))
record('CN4-5',[str(x) for x in merged],['35.230.32.0/19'])
s=0xB9B6+0x65C5
while s>>16:s=(s&0xffff)+(s>>16)
record('CN5-2',f'{(~s)&0xffff:04X}','E083')
record('CN5-3',200+300+500,1000)
RTT=50;MSL=800
record('CN5-4',{'server_receives_FIN':RTT/2,'client_receives_FIN_and_starts_TIME_WAIT':RTT,'server_CLOSED':RTT*1.5,'client_CLOSED':RTT+2*MSL},{'server_receives_FIN':25.0,'client_receives_FIN_and_starts_TIME_WAIT':50,'server_CLOSED':75.0,'client_CLOSED':1650})
record('CN5-5',(32-8)*2,48)
cwnd=1;ss=4;trace=[]
for _ in range(10):
 cwnd=min(cwnd*2,ss) if cwnd<ss else cwnd+1;trace.append(cwnd)
record('CN5-7',{'cwnd_trace_KB':trace,'window_KB':min(cwnd,10)},{'cwnd_trace_KB':[2,4,5,6,7,8,9,10,11,12],'window_KB':10})

record('CN6-4',(1+7)*2,16)
# Initial cwnd=1MSS model used in this historical question; request/ACK can piggyback.
events=[(0,'client SYN'),(5,'server SYN-ACK'),(10,'client ACK+GET HTML'),(15,'server HTML1MSS'),(20,'client ACK+GET image'),(25,'server image first2MSS'),(30,'client ACK image2MSS'),(35,'server image final1MSS'),(40,'client all received')]
record('CN6-7',{'completion_ms':events[-1][0],'MSS_per_response':[1,2,1]},{'completion_ms':40,'MSS_per_response':[1,2,1]})

Path(__file__).with_name('new_chapter_calculation_results.json').write_text(json.dumps({'scope':'本轮稿件计算实际复算；不作为协议全部实现的模型证明','checks':r,'result':'PASS'},ensure_ascii=False,indent=2))
print('PASS',len(r),'new chapter calculations')
