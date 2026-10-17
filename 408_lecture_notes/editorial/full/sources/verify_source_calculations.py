#!/usr/bin/env python3
"""Independent arithmetic checks for four inspected CN questions and one relax sample."""
from pathlib import Path
import json,math
out=Path(__file__).with_name('source_calculation_results.json')
records=[]
# 2025 q38: compute from byte sets, not from an asserted packet count.
mss=1000;ssthresh=8000;cwnd0=2000;rcvwnd=4000
segments=[set(range(2001,3001)),set(range(3001,4001))]
ack=3001
sent=set().union(*segments);confirmed={b for b in sent if b<ack};outstanding=sent-confirmed
cwnd1=cwnd0+mss if cwnd0<ssthresh else cwnd0+mss*mss//cwnd0
window=min(cwnd1,rcvwnd);credit=max(0,window-len(outstanding));new_segments=credit//mss
assert (len(confirmed),len(outstanding),cwnd1,credit,new_segments)==(1000,1000,3000,2000,2)
records.append({'question':'2025 CN38','inputs':{'sent_sequence_intervals':[[2001,3000],[3001,4000]],'ack':ack,'cwnd0':cwnd0,'ssthresh':ssthresh,'rcvwnd':rcvwnd,'MSS':mss},'actual':{'confirmed_bytes':len(confirmed),'outstanding_bytes':len(outstanding),'cwnd_after_ACK':cwnd1,'effective_window':window,'new_credit_bytes':credit,'new_segments':new_segments},'answer':'A','check':'PASS'})
# 2020 q40: graph has root -> com -> abc.com, each DNS exchange one remote RTT.
dns_chain=['root','com','abc.com'];rtt_ms=10;web_rtts=2
shortest=(0+web_rtts)*rtt_ms;longest=(len(dns_chain)+web_rtts)*rtt_ms
assert (shortest,longest)==(20,50)
records.append({'question':'2020 CN40','actual':{'remote_dns_hops':dns_chain,'cache_hit_DNS_RTT':0,'cache_miss_DNS_RTT':len(dns_chain),'TCP_and_HTTP_RTT':web_rtts,'shortest_ms':shortest,'longest_ms':longest},'answer':'D','check':'PASS'})
# 2016 q40: iterative query chain for www.abc.xyz.com, all DNS servers iterative.
name='www.abc.xyz.com';labels=name.split('.')
servers=['root']+['.'.join(labels[i:]) for i in range(len(labels)-1,0,-1)]
assert servers==['root','com','xyz.com','abc.xyz.com']
records.append({'question':'2016 CN40','actual':{'query_servers':servers,'minimum_queries_with_cache':0,'maximum_queries_without_cache':len(servers)},'answer':'C','check':'PASS'})
# relax DS chapter1 q11: sum is strictly greater than n on exit.
cases=[]
for n in [0,1,2,3,5,6,9,10,99,100,999,1000,9999,10000]:
 count=0;total=0;next_value=1
 while total<=n:
  total+=next_value;next_value+=1;count+=1
 expected=(math.isqrt(8*n+1)-1)//2+1
 assert count==expected and total>n and (count-1)*count//2<=n
 cases.append({'n':n,'iterations':count,'exit_sum':total,'previous_sum':(count-1)*count//2})
records.append({'question':'relax DS chapter1 q11','actual':cases,'answer':'C，Theta(sqrt(n))；按算法分析的精确整数模型，忽略机器int溢出','check':'PASS'})
out.write_text(json.dumps({'date':'2026-10-16','scope':'实际数值/状态复算；不替代真题身份、原题图或大纲核验','checks':records,'result':'PASS'},ensure_ascii=False,indent=2),encoding='utf8')
print(out)
