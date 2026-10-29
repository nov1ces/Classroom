"""Native, editable 48 mm vector diagrams for the uploaded annotation specs.

Wide figures are divided into named panels instead of reducing their font size.
All source numbers, states, directions, assumptions and complete specs are retained.
"""
from __future__ import annotations

import re
from import_annotations import prose, esc


def table(headers, rows, weights=None):
    n = len(headers)
    weights = weights or [1]*n
    available = 136.05 - (n-1)*2.4
    spec = '@{}' + ''.join(r'>{\raggedright\arraybackslash}p{' + f'{available*w/sum(weights):.3f}bp' + '}' for w in weights) + '@{}'
    result = [r'{\setlength{\tabcolsep}{1.2bp}\renewcommand{\arraystretch}{1.18}\begin{tabular}{' + spec + '}', r'\toprule',
              ' & '.join(r'\textbf{' + prose(h) + '}' for h in headers) + r'\\\midrule']
    for row in rows:
        result.append(' & '.join(prose(str(c)) for c in row) + r'\\')
    return '\n'.join(result + [r'\bottomrule\end{tabular}}'])


def tikz(commands):
    return (r'\begin{tikzpicture}[x=1bp,y=-1bp,>=Stealth,font=\fontsize{8.5}{10.7}\selectfont,'
            r'every node/.style={inner sep=1bp},line width=.45bp]' + '\n' + '\n'.join(commands) + '\n' + r'\end{tikzpicture}')


def node(x, y, text, width=None, style=''):
    opts = 'anchor=north west,align=left'
    if width:
        opts += f',text width={width}bp'
    if style:
        opts += ',' + style
    return r'\node[' + opts + f'] at ({x},{y})' + '{' + prose(text) + '};'


def sequence(labels):
    """Full-width boxes connected by arrows; prose retains its native typesetting."""
    output = []
    for i, label in enumerate(labels):
        if i:
            output.append(r'\par\vspace{1bp}\centerline{\(\downarrow\)}\par\vspace{1bp}')
        output.append(r'{\setlength{\fboxsep}{3bp}\color{ink}\fbox{\parbox{128bp}{\color{black}' + prose(label) + '}}}')
    return '\n'.join(output)


def figure_pieces(item, context):
    spec = item['annotation'].get('diagram_spec')
    if not spec:
        return []
    ident = item['id']
    panels = []

    def add(title, body):
        panels.append((title, body))

    if ident == 'ch02-005':
        cmds, y = [], 0
        for i, state in enumerate(spec['nodes']):
            cmds.append(node(0, y, state['label']))
            for j, value in enumerate(state['values']):
                x = 3+j*26
                cmds.append(node(x+7, y+14, str(j)))
                color = 'blue' if (i == 0 and j < 2) or (i == 3 and j >= 3) else 'green'
                cmds.append(fr'\draw[fill={color}] ({x},{y+27}) rectangle ++(24,16);')
                cmds.append(node(x+7, y+29, str(value)))
            if i < 3:
                label = spec['edges'][i]['label']
                cmds += [fr'\draw[->] (13,{y+47}) -- (13,{y+64});', node(24,y+47,label)]
            y += 70
        add('三次逆置，A为前2项、B为后3项', tikz(cmds) + r'\par ' + prose('所有区间均含两端；首尾双指针交换。'))

    elif ident == 'ch03-002':
        cmds, y = [], 0
        for state in spec['nodes']:
            cmds += [node(0,y,state['label']), node(0,y+15,' '.join(state['operations']),52),
                     node(62,y,'峰值'), node(101,y,'结束')]
            for x, key in [(64,'peak_stack'),(105,'stack_after')]:
                values=state[key]
                h=max(1,len(values))*14
                cmds += [fr'\draw ({x},{y+15}) -- ({x},{y+15+h}) -- ({x+23},{y+15+h}) -- ({x+23},{y+15});']
                for j,value in enumerate(reversed(values)):
                    cmds += [node(x+8,y+16+j*14,value),fr'\draw ({x},{y+29+j*14}) -- ({x+23},{y+29+j*14});']
                if not values:
                    cmds.append(node(x+7,y+16,'空'))
            y += 76
        add('栈顶在上；↑入栈、↓出栈', tikz(cmds)+r'\par '+prose('最大深度3，最小容量3（C）；每段结束仅余a，最终为空。'))

    elif ident == 'ch05-008':
        coords={'root':(83,8),'n0':(52,42),'n1':(115,42),'n00':(34,78),'n01':(77,78),
                'n000':(24,114),'n001':(91,114),'n0000':(13,150),'n0001':(46,150),'n0010':(79,150),'n0011':(113,150)}
        cmds=[]
        for edge in spec['edges']:
            x,y=coords[edge['from']];u,v=coords[edge['to']]
            cmds += [fr'\draw[->] ({x},{y+7}) -- ({u},{v-7});',node((x+u)/2-4,(y+v)/2-8,edge['label'])]
        for n in spec['nodes']:
            x,y=coords[n['id']]
            label='∅' if n['id']=='root' else n['id'][1:]
            if n['id']=='root':label='根'
            color='pink' if n['status']=='fixed_leaf' else ('green' if n['status']=='new_leaf' else 'white')
            cmds.append(fr'\node[fill={color},draw,anchor=center] at ({x},{y})'+'{'+prose(label)+'};')
        add('前缀码树，粉色为已占用叶',tikz(cmds)+r'\par '+prose(spec['caption']))

    elif ident == 'ch07-005':
        for i, frame in enumerate(spec['frames']):
            nodes={n['id']:n for n in frame['nodes']}
            children={n:{} for n in nodes}
            for edge in frame['edges']:children[edge['from']][edge['label']]=edge['to']
            order=[];depths={}
            def inorder(n,depth):
                depths[n]=depth
                if 'left' in children[n]:inorder(children[n]['left'],depth+1)
                order.append(n)
                if 'right' in children[n]:inorder(children[n]['right'],depth+1)
            inorder(frame['root'],0)
            # Reserve 32 bp per leaf label. Balanced keys occupy fixed inorder positions.
            coords={n:(12+j*(110/max(1,len(order)-1)), depths[n]*39+12) for j,n in enumerate(order)}
            cmds=[]
            for edge in frame['edges']:
                x,y=coords[edge['from']];u,v=coords[edge['to']]
                cmds.append(fr'\draw[->] ({x},{y+12}) -- ({u},{v-8});')
            for nid,n in nodes.items():
                x,y=coords[nid]
                bf=re.search(r'BF=([+-]?\d+)',n['label'])[1]
                fill='blue' if n['highlight_new_node'] else 'white'
                cmds.append(fr'\node[draw,fill={fill},anchor=center,align=center] at ({x},{y})'+'{'+str(n['key'])+r'\\'+prose('('+bf.replace('+0','0')+')')+'};')
            rotation='；'.join(frame['rotations_in_order']) or '无需旋转'
            add(frame['label']+'；'+rotation,tikz(cmds))
        add('AVL图示约定',prose('浅蓝为本步新插入结点；括号内为BF，BF=左高−右高，空树高0。各图均为完成旋转后的整树，中序从左向右递增。'))

    elif ident == 'ch08-011':
        order=spec['layout']['sibling_order']
        labels={n['id']:str(n['weight']) for n in spec['nodes']}
        for parent in ['N413','N64','N17','N196']:
            cmds=[fr'\node[draw,fill=blue] at (67,9)'+'{'+labels[parent]+'};']
            for j,child in enumerate(order[parent]):
                x=14+j*35
                cmds += [fr'\draw[->] (67,17) -- ({x},41);',
                         fr'\node[draw,anchor=center'+(',dashed' if child=='L0' else '')+fr'] at ({x},50)'+'{'+labels[child]+'};']
            add(('根结点' if parent=='N413' else '展开权为'+labels[parent]+'的子树'),tikz(cmds))
        add('归并层数与I/O',prose('虚线叶0不产生读写。根深度0；3、6、8深度3，9、18、20、30、44、60、62深度2，68、85深度1。')+r'\par '+prose(spec['results']['WPL_by_leaf_depths'])+r'\par '+prose(spec['results']['conditional_IO']))

    elif ident == 'ch11-017':
        nodes={n['id']:n for n in spec['nodes']}
        for order in spec['execution_order']:
            column=nodes[order[0]]['column']
            labels=[nodes[n]['label'] for n in order]
            add(f'独立读访问{column}：'+labels[0].split('\n')[0],sequence(labels))
        add('三条访问路径的初态',prose('每次均从原题初态开始，回填互不影响；先完成地址转换，再查物理地址Cache。缺页路径在P=0处停止，不推演调页后的重试。H后缀表示十六进制。'))

    elif ident == 'ch13-013':
        rows=spec['state_table']
        for start,end in [(1,6),(7,12),(13,17)]:
            # At most six cycle columns keeps every 8.5 pt stage label readable.
            headers=['拍']+[str(i) for i in range(start,end+1)]
            states=[[r['instruction']]+[{'ID等':'等','IF禁':'禁'}.get(s,s or '·') for s in r['states'][start-1:end]] for r in rows]
            add(f'五段流水：第{start}～{end}拍',table(headers,states,[1]+[1.35]*(end-start+1)))
        add('指令、等待与依赖',prose('\n'.join(n['id']+'：'+n['label'] for n in spec['nodes']))+r'\par '+
            prose('等＝ID等待；禁＝IF冻结；·＝未进入或已离开。无旁路，同寄存器读须晚于写1拍。')+r'\par '+
            prose('I1.WB5→I3.ID6；I2.WB6→I4.ID10；I3.WB9→I4.ID10；I4.WB13→I5.ID14。')+r'\par '+
            prose('5+5−1+2+3+3=17拍；第16拍M写入[x]，按题设流出WB的口径第17拍完成。'))

    elif ident == 'ch15-001':
        add('屏蔽字，位序固定A、B、C',table(['服务','屏蔽字','可打断者'],[[r[0],''.join(r[1:4]),r[4]] for r in spec['mask_table']['rows']],[1,1.2,1.6])+r'\par '+prose('硬件响应A>B>C；处理优先级C>B>A；1禁、0允许。'))
        labels=[]
        for n in spec['nodes']:
            labels.append('　'*n['indent_level']+n['label'])
        add('中断嵌套与返回',sequence(labels))

    elif ident == 'ch17-005':
        cmds=[]
        for lane,y in [('SRTF',19),('RR',84)]:
            cmds.append(node(0,y-20,'SRTF' if lane=='SRTF' else 'RR，q=2'))
            intervals=[n for n in spec['nodes'] if n['lane']==lane]
            for n in intervals:
                a,b=8+n['start']*4.6,8+n['end']*4.6
                color={'P1':'blue','P2':'pink','P3':'green','P4':'orange'}[n['label']]
                cmds.append(fr'\draw[fill={color}] ({a},{y}) rectangle ({b},{y+14});')
                cmds.append(fr'\node[anchor=center,inner sep=0pt] at ({(a+b)/2},{y+7})'+'{'+n['label'][1:]+'};')
            boundaries=sorted({n[k] for n in intervals for k in ['start','end']})
            for t in boundaries:
                offset=14 if (lane=='SRTF' and t==0) or (lane=='RR' and t==25) else 0
                cmds.append(fr'\node[anchor=north,inner sep=0pt] at ({8+t*4.6},{y+18+offset})'+'{'+str(t)+'};')
        add('SRTF与RR执行区间',tikz(cmds)+r'\par '+prose('条内1～4代表P1～P4；时间单位为题设配额。RR在t=25仍保留片界。'))
        add('到达、服务与周转',table(['进程','到达/服务','SRTF周转','RR周转'],[[r['process'],str(r['arrival'])+'/'+str(r['service']),spec['summary_table'][i]['SRTF_turnaround'],spec['summary_table'][i]['RR_turnaround']] for i,r in enumerate(spec['input_table'])],[1,1.4,1.35,1.25])+r'\par '+prose('同刻新到达者先入队；平均周转SRTF为13、RR为19.25。t=2若先回队P1，RR平均改为18.75。'))

    elif ident == 'ch18-005':
        nodes={n['id']:n for n in spec['nodes']}
        for i,order in enumerate(spec['execution_order']):
            row=spec['rows'][i]
            add(row['label'],sequence([nodes[n]['label'] for n in order])+r'\par '+prose(spec['display_equations'][i]))
        states=[]
        for s in spec['state_table'][1:]:
            mappings='，'.join(p+'→'+f for p,f in s['resident_page_to_frame'].items())
            tlb='，'.join(p+'→'+f for p,f in s['tlb_page_to_frame'].items())
            states.append([s['point'][0],mappings+'\nTLB：'+tlb,'→'.join(map(str,s['lru_oldest_to_newest']))])
        add('访问完成后的映射与LRU',table(['访问','页→页框','最久→最近'],states,[.65,2.5,1.3])+r'\par '+prose('10⁸ ns含缺页处理中的页表与TLB更新，失败查询与重试另计；页2的TLB项保留。')+r'\par '+prose(spec['display_equations'][3]))

    elif ident == 'ch20-001':
        for panel in spec['panels']:
            cmds=[]
            for lane,y in [('device',24),('cpu',48)]:
                cmds.append(node(0,y-12,'设备输入' if lane=='device' else 'CPU复制、分析'))
                for n in panel['nodes']:
                    if n['lane']!=lane:continue
                    x,z=5+n['start']*.25,5+n['end']*.25
                    color={'input':'blue','copy':'orange','analysis':'green'}[n['stage']]
                    cmds += [fr'\draw[fill={color}] ({x},{y}) rectangle ({z},{y+14});',fr'\node[anchor=center,inner sep=0pt] at ({(x+z)/2},{y+7})'+'{'+str(n['block'])+'};']
            for t in range(0,501,100):cmds.append(fr'\node[anchor=north,inner sep=0pt] at ({5+t*.25},68)'+'{'+str(t)+'};')
            add(panel['title']+'（μs）',tikz(cmds)+r'\par '+prose('蓝＝输入，黄＝复制，绿＝分析；数字为块号。')+r'\par '+prose('前3块分析完成：'+str(panel['prefix_completion'])+' μs。'))
        add('缓冲复用与第10块',prose('输入100、复制50、分析50 μs；同一缓冲复制完才可复用。复制和分析共用CPU，设备输入可与CPU重叠。')+r'\par '+prose('单缓冲第2块输入150～250；双缓冲100～200。第10块的输入/复制/分析分别为：')+r'\par '+prose('单：1350～1450／1450～1500／1500～1550；双：900～1000／1000～1050／1050～1100 μs。'))

    elif ident == 'ch20-003':
        for start,end in [(0,4),(4,7)]:
            labels=[]
            for n in spec['nodes'][start:end]:
                labels.append(n['step']+' '+n['event']+'\n'+n['executor']+'\nP：'+n['P_state']+'；'+n['CPU_mode'])
            add('键盘输入：'+('阻塞至驱动读入' if start==0 else '唤醒、调度与返回'),sequence(labels))
        add('①之后等待重新调度',prose('①仅将P由阻塞改为就绪；调度到P后才继续系统调用并执行⑤。③属于键盘驱动；②之后CPU可运行其他进程。六个编号的次序：②→⑥→④→③→①→⑤。'))

    elif ident == 'ch24-010':
        for key,label in [('net_210_2_3','210.2.3.0/24，直连R14'),('net_210_2_4','210.2.4.0/24，直连R16')]:
            # Six router columns are narrow; transpose into one router per row.
            states=spec['state_tables'][key]
            rows=[]
            for j in range(6):rows.append(['R'+str(j+11)]+['∞' if s['distances'][j]==16 else s['distances'][j] for s in states])
            add(label,table(['路由器','初始','0 s','30 s','60 s'],rows,[1.8,1,1,1,1])+r'\par '+prose('∞表示RIP不可达（16）；直连网距离1。首次全体获知：'+('30 s。' if key=='net_210_2_3' else '60 s。')))
        add('同步交换的时间原点',prose('t=0完成首轮初始向量交换；每轮只用轮初邻居距离。R13与R16无直接边；不加入触发更新。'))

    elif ident == 'ch25-002':
        cmds=[node(22,0,'C'),node(114,0,'S'),fr'\draw[dashed] (27,17)--(27,183);',fr'\draw[dashed] (118,17)--(118,122);']
        for t,y in [(0,28),(25,61),(50,94),(75,127),(1650,178)]:cmds.append(node(0,y-5,str(t)))
        for x,y,u,v,label in [(27,28,118,61,'FIN'),(118,61,27,94,'FIN+ACK'),(27,94,118,127,'最后ACK')]:
            cmds += [fr'\draw[->] ({x},{y})--({u},{v});',node(44,(y+v)/2-15,label)]
        cmds += [node(35,139,'省略中间时间',94),node(35,155,'2MSL从50 ms开始',94)]
        add('两端关闭的时序（ms）',tikz(cmds))
        add('各端状态与关闭时刻',table(['时刻','状态变化'],[['0','C发FIN，FIN-WAIT-1'],['25','S：CLOSE-WAIT→立即发FIN+ACK→LAST-ACK'],['50','C发最后ACK，进入TIME-WAIT'],['75','S收ACK，CLOSED'],['1650','C等待2MSL结束，CLOSED']],[.8,4])+r'\par '+prose('RTT=50 ms，单向25 ms；MSL=800 ms。服务器收到FIN后立即关闭并合并FIN+ACK；忽略发送、处理和丢失。'))

    elif ident == 'ch25-010':
        add('每轮发送和缓存，单位KB',table(['轮','发','累计收','cwnd','rwnd'],[[r['round'],r['sent_KB'],r['received_total_KB'],r['cwnd_KB'],r['rwnd_KB']] for r in spec['rows']],[.7,.7,1.3,1.4,1.4])+r'\par '+prose('表中窗口为该轮ACK处理后。初始cwnd=1 MSS、ssthresh=32 KB，1 MSS=1 KB=1024 B。'))
        add('下一轮额度与计时终点',table(['轮末','时间ms','下轮发送KB'],[[r['round'],r['elapsed_ms'],r['next_window_KB']] for r in spec['rows']],[.8,1.4,1.8])+r'\par '+prose('每个新ACK使cwnd加1 MSS；接收缓存20 KB只存不取。发送量=min(cwnd,rwnd)。第4轮后rwnd仅5 KB；第5轮零窗口通告返回时结束，5 RTT=1000 ms。'))

    elif ident == 'ch26-006':
        for first,last in [(0,3),(3,5)]:
            rows=[]
            for r in spec['state_table'][first:last]:
                rows.append([str(r['round']),f"发{r['H_send_time_ms']} ms；收末ACK {r['H_receives_final_ACK_time_ms']} ms\n窗口{r['cwnd_before_send_MSS']} MSS，发送{r['segments_sent']}段\nseq {r['first_byte_seq']}～{r['last_byte_seq']}\nACK："+'、'.join(map(str,r['ACKs_in_order']))])
            add(f'FTP数据连接：第{first+1}～{last}轮',table(['轮','时刻、序号和逐段ACK'],rows,[.5,4.5]))
        # Keep all 12 grouped message arrows from the spec, in narrow stacked panels.
        edges=spec['edges']
        for first,last in [(0,3),(3,6),(6,9),(9,len(edges))]:
            labels=[]
            for e in edges[first:last]:
                direction=str(e.get('from',e.get('source','')))+'→'+str(e.get('to',e.get('target','')))
                labels.append(direction+'（'+str(e['send_time_ms'])+'→'+str(e['receive_time_ms'])+' ms）：'+e.get('label',''))
            add('FTP消息方向与时序'+str(first+1)+'～'+str(last),sequence(labels))
        add('30、40、55、60 ms的观察点',prose('0 ms发SYN，5 ms收SYN，10 ms握手完成并发首段。30 ms处理ACK2101后cwnd=3，再处理ACK3101后为4。40 ms收ACK7101后为5。55 ms数据到齐S，60 ms H收ACK18101才全部获确认。')+r'\par '+prose('初始cwnd补定1 MSS；门限4 MSS，之后每完整轮加1 MSS；RTT=10 ms，单向5 ms，无差错且rwnd充足，逐段及时确认。'))

    elif ident == 'ch26-007':
        # A compact cross preserves the original port orientation. Full addresses
        # appear in an adjacent legend, avoiding tiny topology labels.
        cmds=[node(53,0,'R'),node(0,42,'DNS'),node(113,42,'H2'),node(54,88,'H1'),node(57,42,'S')]
        cmds += [r'\draw (58,17)--(58,39);',r'\draw (27,49)--(52,49);',r'\draw (73,49)--(112,49);',r'\draw (63,60)--(63,85);',
                 node(61,25,'2'),node(36,34,'1'),node(93,34,'3'),node(65,69,'4')]
        add('LAN端口拓扑',tikz(cmds))
        add('设备的完整IP和MAC',table(['端口','设备、完整IP与MAC'],[[n['switch_port'],n['id']+'\n'+n['ip']+'\n'+n['mac']] for n in spec['nodes'] if n.get('switch_port')],[.5,4.5]))
        for start,end in [(0,3),(3,6),(6,9)]:
            rows=[]
            for state in spec['state_table'][start:end]:
                src=state['frame_source_mac'][-2:];dst=state['frame_destination_mac'][-2:]
                mac=src+'→'+('广播' if dst=='ff' else dst)
                info=state['event']+'\n'+mac+'；入'+str(state['ingress_port'])+'，出'+','.join(map(str,state['egress_ports']))
                info+='\n学习：'+state['new_learning']+'；H2'+('收到' if state['H2_receives'] else '未收到')
                rows.append([state['order'],info])
            add(f'帧事件{start+1}～{end}',table(['序','帧、学习与转发'],rows,[.45,4.55]))
        add('t1交换机转发表',table(['完整MAC','端口'],[[r['mac'],r['port']] for r in spec['state_table'][-1]['switch_table_after_event']],[4.5,.5]))
        add('MAC缩写与广播',prose('MAC缩写aa、bb、cc均补前缀00-11-22-33-44；广播完整目的MAC为ff-ff-ff-ff-ff-ff。H2未发帧，无dd记录。'))
        add('DNS封装与HTTP下一跳',
            prose('DNS查询：DNS→UDP→IPv4→以太网；UDP目的端口53。IP从192.168.1.2到192.168.1.126；MAC从cc到bb。')+r'\par '+
            prose('t1的HTTP帧：IP从192.168.1.2到外网Web地址，题未给具体值；MAC从cc到aa，入4出2。假设DNS已有有效缓存，整个过程表项不老化。'))
    else:
        raise ValueError('Unsupported diagram: '+ident)

    result=[]
    for i,(title,body) in enumerate(panels,1):
        tex=(r'{\color{ink}\bfseries '+prose(f"{context['title']} · 合订本{context['anchor_page']} · 图{i}")+r'}\par '+
             r'\textbf{'+prose(title)+r'}\par\vspace{2bp}'+body)
        result.append(dict(context,key=f'{ident}-fig{i:02}',annotation_id=ident,kind='figure',tex=tex))
    return result
