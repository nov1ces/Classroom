#!/usr/bin/env python3
"""汇总真实审读日志与问题状态，不替作者或大纲核验声明通过。"""
import json
import hashlib
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]

def main():
    reads=json.loads((HERE/'read_log.json').read_text())
    issues=json.loads((HERE/'issues.json').read_text())
    seen={r['path'] for r in reads}
    actual={str(f.relative_to(ROOT)):f for f in (ROOT/'manuscript').glob('*/*.md')}
    pending=[x for x in issues if x['status']!='已解决']
    counts=Counter(p.split('/')[1] for p in seen)
    lines=['# 四科独立技术审校记录','',f'更新：{datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}。内部材料。','',
           f'已实际审读 {len(seen)} 个分章文件：DS {counts["DS"]} 章、CO {counts["CO"]} 章、OS {counts["OS"]} 章、CN {counts["CN"]} 章。审读日志逐条记录路径、实际版本 SHA-256、字符数和行范围。首次全章阅读与后续改动段复核分别登记；早稿的阅读不自动认证后续新加段。',
           '', '本审校检查术语、成立条件、推理链、计算状态、跨科机制和题目呈现，已复算的范围另见 independent_calculations.json。大纲依据的正式发布身份、题源逐题图读和 PDF 视觉分别以对应台账为准；本报告不把分章内容审读自动扩大为这三类核验。',
           '', '## 跨科一致性', '',
           '- 计组与 OS 均区分 OS 维护映射与 MMU 运行时转换；TLB 缓存转换，Cache 缓存指令/数据，未命中与缺页分别处理。',
           '- 逻辑页/页框、Cache 块/行、文件逻辑块/磁盘块均按上下文定义；页偏移不变，地址单位、数据位宽和容量单位分开。',
           '- 系统调用和中断不必切进程，唤醒先变就绪；PIO/中断由 CPU 搬运的模型与 DMA 硬件搬运及 CPU 设置/收尾的解释相合。',
           '- 链接、装入、运行时重定位及调用返回位置按机制和 ISA 条件区分；返回地址未被无条件固定为主存栈。',
           '- 网络速率采用 SI 数量级，二进制容量单列；发送与传播、单向与往返、段号与字节序号、总窗口与剩余额度分别说明。',
           '- 正文短题源按【年份】/〖节号-三位题号〗；原作答与完整出处保留在内部材料，不进入学生正文。',
           '', '## 已发现问题与处理', '',
           f'累计记录 {len(issues)} 项，其中已解决 {len(issues)-len(pending)} 项，其余 {len(pending)} 项如下。具体原句、路径、行号、修复依据及复核版本见 issues.json；行号属于发现时版本，后续可随增补移动。','',
           '| 编号 | 位置 | 问题 | 当前状态 |','| --- | --- | --- | --- |']
    for x in pending:
        lines.append(f'| {x["id"]} | {x["path"]}:{x["line"]} | {x["issue"]} | {x["status"]} |')
    if not pending:lines.append('| — | — | 所列可修问题均已逐项复核关闭 | 已完成 |')
    lines+=['','## 审读文件与版本','','| 文件 | 实际全读版本数 | 最近全读/增补段复核 | 当前文件 SHA-256 |','| --- | --- | --- | --- |']
    for p,f in sorted(actual.items()):
        entries=[x for x in reads if x['path']==p]
        label='未读' if not entries else entries[-1]['scope']
        lines.append(f'| {p} | {sum(x.get("full_read",True) for x in entries)} | {label} | {hashlib.sha256(f.read_bytes()).hexdigest()} |')
    unread=sorted(set(actual)-seen)
    lines+=['','尚未审读文件：'+('、'.join(unread) if unread else '当前已落盘章节均有实际审读记录。'),
            '', '## 最终 PDF 视觉记录', '',
            '以下状态读取各科单独记录，并与当前 PDF 的 SHA-256 比对。独立审校员实际全页目验范围为 OS；其他科由各自记录所列审阅者负责，不能误称同一审校员重看了四科全部页。', '',
            '| 科目 | 实际页数 | 当前 SHA 对应状态 | 记录 |', '| --- | --- | --- | --- |']
    for sub in ['DS','CO','OS','CN']:
        visual=ROOT/'editorial/full/pdf'/sub/'visual_review.json'
        if not visual.exists():
            lines.append(f'| {sub} | — | 待该科最终记录 | {visual.relative_to(ROOT)} |')
            continue
        v=json.loads(visual.read_text())
        pdf=ROOT/v.get('pdf',{'DS':'dist/数据结构_讲义.pdf','CO':'dist/计算机组成原理_讲义.pdf','OS':'dist/操作系统_讲义.pdf','CN':'dist/计算机网络_讲义.pdf'}[sub])
        matches=pdf.exists() and hashlib.sha256(pdf.read_bytes()).hexdigest()==v.get('sha256')
        visual_status=v.get('status','未明') if matches else 'SHA不一致，待重审'
        lines.append(f'| {sub} | {len(v.get("reviewed_pages",[]))} | {visual_status} | {visual.relative_to(ROOT)} |')
    lines+=['','## 验证边界','',
            '机械检查只检查短标签格式、个人作答泄漏、代码围栏、锚点/链接与图片可达性。人工已排除“最高频率”中的高频与“等待补齐”中的待补等非问题词，未用词命中冒充内容结论。',
            '', '可计算核验按原题输入执行事件、算法或独立数值运算；其通过不代表全部题目核验完成。最后增补已另审 CO3-11 的 2023 年页/Cache 综合题改编、CO5-2 的 2022 年数据通路综合题，以及 DS1/DS3/DS8 自测题源恢复。CO3-11 已明确两处赋值式改为常量 10，不计作未改原真题。CO5-2 原创 ADD 轨迹已被可用真题替换；正文保留短题源，完整题型/卷题号/页码及替换理由在内部台账。',
            '', '本轮可取得的真题卷为社区复原或教材转载，已核图文及答案的记录不表示取得了考试机构发布的官方原卷或官方答案。可用大纲版本及其核验范围见范围台账；未取得下一年度正式全文的变化不能据现有讲义推断。PDF 视觉检查另绑定最终 PDF SHA、实际页面与图像清单，不以预览、结构检查或本文的内容审校代替。','']
    (HERE/'cross_subject_review.md').write_text('\n'.join(lines))
    print(json.dumps({'read_chapters':len(seen),'actual_chapters':len(actual),'pending_issues':len(pending)},ensure_ascii=False))

if __name__=='__main__':main()
