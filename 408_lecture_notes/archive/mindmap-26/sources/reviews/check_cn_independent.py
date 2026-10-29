import math,json,hashlib
from pathlib import Path
p=Path(__file__).resolve().parent
results={}
Td=128*8/16000;Ta=Td;twoway=.5
w=math.ceil((Td+Ta+twoway)/Td)
results['GBN-long-ACK']={'Td_ms':Td*1000,'cycle_ms':(Td+Ta+twoway)*1000,'Ws_min':w,'k_min':math.ceil(math.log2(w+1))}
assert w==10 and math.ceil(math.log2(w+1))==4
results['SR-window-space']={'k3_symmetric_max':2**2,'k4_Wr7_Wsmax':2**4-7,'asymmetric_common_config_ok':7<=9}
assert results['SR-window-space']['k4_Wr7_Wsmax']==9
cwnd=2000+1000;rwnd=4000;flight=1000
results['TCP-new-data']={'cwnd_after_ACK':cwnd,'rwnd':rwnd,'flight':flight,'new_bytes':max(0,min(cwnd,rwnd)-flight),'full_MSS_segments':max(0,min(cwnd,rwnd)-flight)//1000}
assert results['TCP-new-data']['new_bytes']==2000
results['TCP-SYN-FIN']={'SYN_seq':100,'data_bytes':500,'data_first':101,'data_last':600,'FIN_seq':100+1+500,'ACK_of_FIN':100+1+500+1}
assert results['TCP-SYN-FIN']['FIN_seq']==601 and results['TCP-SYN-FIN']['ACK_of_FIN']==602
results['TCP-full-buffer']={'round_KB':[1,2,4,8,5],'total_B':20*1024,'next_seq':101+20*1024,'time_s':5*.2,'rate_bit_s':20*1024*8/(5*.2)}
assert sum(results['TCP-full-buffer']['round_KB'])==20 and results['TCP-full-buffer']['next_seq']==20581
assert results['TCP-full-buffer']['rate_bit_s']==163840
results['normal-plus-dupACK']={'same_ACK_total_3':'1 normal + 2 duplicate: insufficient','same_ACK_total_4':'1 normal + 3 duplicate: threshold in simplified model'}
results['SRTT']=(1-1/8)*100+1/8*140
assert results['SRTT']==105
results['reviewed_notes']={cid:hashlib.sha256((Path(__file__).resolve().parents[2]/'chapters'/cid/'content.md').read_bytes()).hexdigest() for cid in ['CN03','CN05']}
(p/'CN-independent-numeric.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print(json.dumps(results,ensure_ascii=False,indent=2))
