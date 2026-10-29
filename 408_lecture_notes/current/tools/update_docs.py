#!/usr/bin/env python3
"""Publish concise navigation with an explicit, evidence-based production stage."""
import argparse,json
from datetime import datetime
from zoneinfo import ZoneInfo
from build_notes import ROOT,read,jwrite
ap=argparse.ArgumentParser();ap.add_argument('--phase',choices=['ready_for_layout','completed'],required=True);a=ap.parse_args()
m=read(ROOT/'manifest.json');idx=read(ROOT/'sources/example_index.json');phase='已构建，待集中排版检查' if a.phase=='ready_for_layout' else '内容、索引与最终排版检查完成'
sub={'DS':'数据结构','CO':'计算机组成原理','OS':'操作系统','CN':'计算机网络'}
lines=['# 408强化笔记','',phase+'。','',f"四科26章，知识笔记{m['total_pages']}页，{len(idx['examples'])}道例题；解析独立成册。",'', '| 科目 | PDF | Markdown | 页数 |','| --- | --- | --- | ---: |']
for s,name in sub.items():
 pages=sum(x['pages'] for x in m['chapters'] if x['id'].startswith(s))
 lines.append(f'| {name} | [阅读](books/{name}_强化笔记.pdf) | [阅读](books/{name}_强化笔记.md) | {pages} |')
lines+=['','[四科合订本](books/408四科_强化笔记.pdf) · [独立解析册](books/408强化例题解析.pdf) · [解析Markdown](solutions/notes.md)','','正文例题题号可跳转解析，解析题号可返回合订本对应题目。解析册前部提供答案与页码速查。PDF相对链接适合将books目录整套下载后使用；浏览器是否支持跨文件跳转取决于阅读器。','','[章节正文与图源](chapters/) · [例题及原解析来源](sources/example_index.json) · [交付检查](sources/delivery_checks.json)','','## 重建','','依赖Python 3、Pandoc、XeLaTeX；Python依赖见requirements.txt，字体与模板位于common/。','','```bash','python3 -m pip install -r requirements.txt','python3 tools/build_project.py','```','','现有截图和图源随项目保存，使用已核对的索引重建不需要原始教材。改题后须在原资料可读时重新准备来源索引：`python3 tools/build_project.py --refresh-sources`。最终版面检查在完整构建推送GitHub后执行。','','代码按可核验的王道教材接口及下标约定；严蔚敏版本尚缺可核验原件。原课件逐帧及细小标签的历史核查范围保留在底稿记录中。']
(ROOT/'README.md').write_text('\n'.join(lines)+'\n')
now=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds')
jwrite(ROOT/'sources/workflow.json',{'phase':a.phase,'updated_at':now,'notes_pages':m['total_pages'],'examples':len(idx['examples']),'solution_modes':idx['summary'],'visual_review_after_github_push':True})
project=ROOT.parents[1]/'NOTES_PROJECT.md';text=project.read_text();cut=text.index('## 强化版制作检查点');text=text[:cut]
text=text.replace('尚未生成强化版正文与独立解析册','已制作强化版正文与独立解析册，实际检查状态见下方检查点').replace('该底稿尚未按本轮强化阶段要求整体精简，也尚未完成正文与解析分册。','该底稿作为历史来源保留，新强化版位于current/。')
text+='## 强化版制作检查点\n\n'+f'- 状态：{phase}。\n- 四科26章知识笔记{m["total_pages"]}页，195道例题；正文与解析独立。\n- 来源截图及原生解析的实际数量、理由与指纹见current/sources/example_index.json。\n- 页面审阅必须绑定实际PDF指纹；GitHub检查前快照见current/sources/github_pre_layout.json。\n- 目录入口：408_lecture_notes/current/README.md。\n'
project.write_text(text)
print(phase)
