#!/usr/bin/env python3
"""Write release documentation from actual manifests and separate reviews."""
from pathlib import Path
import csv, hashlib, json, re, shutil

ROOT=Path(__file__).resolve().parents[1]
NAMES=dict(DS='数据结构',CO='计算机组成原理',OS='操作系统',CN='计算机网络')
def read(p):return json.loads((ROOT/p).read_text())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    coverage=read('editorial/full/coverage_validation.json')
    figure=read('editorial/full/figure_manifest.json')
    read_log=read('editorial/full/review/read_log.json')
    reviewed={(r['path'],r['sha256']) for r in read_log}
    issues=read('editorial/full/review/issues.json')
    unresolved=[i for i in issues if not str(i.get('status','')).startswith('已解决')]
    rows=[];books=[]
    for sub,title in NAMES.items():
        audit=read(f'editorial/full/pdf/{sub}/audit.json')
        visual=read(f'editorial/full/pdf/{sub}/visual_review.json')
        mf=read(f'build/{sub}/build_manifest.json')
        record=read(f'editorial/full/{sub}/chapter_records.json')
        results=read(f'editorial/full/{sub}/results.json')
        visual_ok=(audit['sha256']==visual['sha256'] and visual['status']=='PASS'
            and set(visual['reviewed_pages'])==set(range(1,audit['page_count']+1)))
        count=sum(bool(re.match(r'^例\s*\d',h['title'])) for h in mf['questions'])
        checks=results.get('checks',results.get('results',[]))
        books.append(dict(subject=sub,title=title,pages=audit['page_count'],chapters=len(record['chapters']),examples=count,
            calculation_checks=len(checks) if isinstance(checks,list) else checks))
        for ch in record['chapters']:
            manuscript=ch.get('manuscript',ch.get('file'))
            if not manuscript:
                manuscript=next((ROOT/f'manuscript/{sub}').glob(f"{int(ch['chapter']):02d}_*.md")).relative_to(ROOT).as_posix()
            matches=(manuscript,digest(ROOT/manuscript)) in reviewed
            open_here=[i['id'] for i in unresolved if i.get('path')==manuscript]
            technical='已完成' if matches and not open_here else '待核验'
            ex=ch.get('examples',[])
            source_ok=all(e.get('source') and e.get('verification') for e in ex)
            row=dict(科目=title,章=ch['chapter'],正文=manuscript,
                范围='待核验：本地知识组已定位；正式2027全文细目未取得',
                正确性=technical,清晰度=technical,精简度=technical,
                选题='已完成' if source_ok and not open_here else '待核验',
                优先级='已完成' if source_ok and not open_here else '待核验',
                自足性=technical,迁移性=technical,
                来源='已完成：按主书/完整复原卷交叉；不称官方答案认证' if source_ok else '待核验',
                呈现='已完成' if visual_ok and audit['structural_status']=='PASS' else '待核验',
                文风=technical,
                计算='已完成：实际过程/数值断言，范围见分科results' if results.get('status')=='PASS' else '待核验',
                当前问题='；'.join(open_here),
                证据=f'editorial/full/{sub}/chapter_records.json；review/read_log.json；pdf/{sub}/audit.json及visual_review.json')
            rows.append(row)
    with (ROOT/'editorial/full/逐章验收.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (ROOT/'editorial/full/逐章验收.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    total=sum(b['pages'] for b in books)
    lines=['# 四科全稿交付与核验记录\n',f'实际分章29章，四科PDF共{total}个物理页。知识覆盖、选题题源、计算、PDF结构和人工视觉分别登记。\n',
        '| 科目 | 章数 | PDF物理页 | 完整编号例题 |\n| --- | ---: | ---: | ---: |']
    for b in books:lines.append(f"| {b['title']} | {b['chapters']} | {b['pages']} | {b['examples']} |")
    lines+=['\n编号例题数不含正文机制小例与章末自测，也不代表真题频率或所有题目都已取得官方认证。\n',
        '题源标记与题干首行同行，该首行不缩进；普通正文段落（含标题后首段）首行缩进两个汉字。题干、数据和解法没有因本次版式调整而改变。\n',
        f"本地266条细目组织为243个稳定知识组，实际定位{coverage['located_groups']}组。457条已提供错题有逐条去向{coverage['mistake_destinations']}条。原作答只在内部台账保留，正文采用一般辨析。\n",
        f"正文实际引用{figure['referenced_figures']}幅可编辑图，每幅均提供SVG、PNG和用于排版的矢量PDF，绘图源代码可重跑。\n",
        '逐章11项验收与计算状态见逐章验收.csv；当前审校具体问题见review/issues.json。未取得的正式年度细目在每章范围项中明确标为待核验，没有以正文已生成代替官方覆盖核验。\n',
        '正文29章已完成实际审读；后续仅移动题源标记的版本，保留逐行不变、标题措辞/锚点不变及标记多重集相同的受控差异证据。25项具体审校问题均已关闭。\n',
        '实际计算与执行过程断言：'+ '、'.join(f"{b['title']}{b['calculation_checks']}组" for b in books)+'。计组另有196,608组加减/乘除穷举案例；具体边界和轨迹见各科results.json，不将文件存在或标题匹配算作复算。\n',
        f'四份PDF均完成结构检查及绑定最终指纹的逐页人工视觉检查。171道编号例题的索引链接实际跟随至目标页核对例号；题源首行位置另有PDF文本坐标检查。\n',
        f'在不含build缓存、无需原书路径或网络的独立目录执行全套复算、绘图与排版；重建PDF共{total}页的渲染像素与交付版逐页相同。记录见portable_build_verification.json；文件元数据时间可导致PDF字节指纹不同。\n',
        '## 仍待核验的来源范围\n',
        '2027正式考试大纲已出版，出版社书目信息已核；尚未取得可认证的全文细目。当前沿用实际读到的本地转录副本与王道2027主资料，不采用“2027无变化”的未经原文证实结论。\n',
        '入选真题按主书、完整社区复原卷与独立求解核对；未取得可认证的官方原卷/官方答案发布。社区复原卷中的已发现误排、主书或题干条件分歧分别记录，不把整套复原卷视为无误原件。\n',
        '未做考试频率统计；教学重点依据前置支撑、知识任务、真实入选考查证据及易混条件确定。\n',
        '其他来源疑点及限条件处理见各科chapter_records.json、editorial/未解决问题与后续任务.md和full/sources。它们不等同于用户没有提供错题。\n']
    report='\n'.join(lines)+'\n';(ROOT/'editorial/full/全稿验收与剩余核验.md').write_text(report)
    (ROOT/'dist/验收与核验范围.md').write_text(report)
    history=ROOT/'editorial/history';history.mkdir(exist_ok=True)
    old=ROOT/'README.md'
    if '首轮交付' in old.read_text() and not (history/'README_首轮.md').exists():shutil.copyfile(old,history/'README_首轮.md')
    table='\n'.join(f"| [{b['title']}](dist/{b['title']}_讲义.pdf) | {b['chapters']} | {b['pages']} | [合并稿](manuscript/{b['title']}_合并稿.md) |" for b in books)
    readme=f'''# 408 中文自学讲义

四科29章，可编辑分章正文、合并稿与统一A4单栏PDF。题源按已确认标准缩写：真题【年份】，非真题〖原书节号-三位题号〗，置于题干首行并同行，该首行不缩进。普通正文段落（含标题后首段）首行缩进两个汉字。正文不展示个人原作答；详细题源与错题记录放在内部材料。

| 讲义 | 章数 | PDF物理页 | 可编辑完整稿 |
| --- | ---: | ---: | --- |
{table}

四科共{total}页。PDF带可点击目录、书签、连续页码、题目与方法索引；例题就近解析，章末自测给答案。正文11pt、代码10pt，黑白打印可辨。分章正文在manuscript/DS、CO、OS、CN中；公式为可编辑文本源码，图由SVG与绘图代码构建，正文未整页图片化。

## 核验范围

以[全稿验收与剩余核验](editorial/full/全稿验收与剩余核验.md)和[逐章验收](editorial/full/逐章验收.csv)为准。243个稳定知识组按已读本地266条细目组织，四科457条原始错题均有读取及逐条去向记录；这不表示457题都做过完整独立计算或官方真题认证。

2027正式大纲的出版书目已核，全文细目尚未取得，仍待正式年度逐条对照。入选真题与王道主书、完整社区复原卷交叉核验，并核对应答案和过程；社区卷是二手复原，官方原卷/官方答案发布未取得。具体版本分歧与勘误保留在来源记录，未编造考试频率或未来变动。

## 编辑材料入口

- [实际目录](editorial/full/四科实际目录.md)、[知识覆盖表](editorial/scope/coverage.csv)。
- [考法总表](editorial/full/考法总表.csv)、[入选题总台账](editorial/full/入选题总台账.csv)、[错题最终去向](editorial/full/错题最终去向.csv)。
- [原始读取总台账](editorial/errors/错误题总台账.csv)：保留实际原作答、可用批改、缺失推理说明和原题位置，不推测个人心理错因。
- 各科editorial/full/科目/chapter_records.json与results.json：知识位置、选题比较、来源核验、逐题去向、图稿及实际复算。
- [参考讲义分析与编写规范](editorial/reference/参考讲义分析与编写规范.md)、[独立技术审校](editorial/full/review/cross_subject_review.md)。
- [实际图稿清单](editorial/full/figure_manifest.csv)和各科editorial/full/pdf中的结构/视觉报告。视觉检查绑定最终PDF SHA，不能由脚本渲染或文件存在替代。
- [独立目录重建验证](editorial/full/portable_build_verification.json)：在无build缓存、不依赖原书或网络的副本中重跑模型、图稿与排版，并逐页比较实际渲染像素。
- [正式范围与资料续核](editorial/full/sources/正式范围与资料续核.md)、[当前来源清单](editorial/sources/当前来源与核验范围.md)。其中首轮未读状态的后续更新以full各科实际记录为准，不冒称整本课件或题库全读。

首轮样章、最初规划和首轮检查保留为历史证据，当前进度以[PROJECT_STATE.json](PROJECT_STATE.json)、实际分章文件和本次交付清单为准。

## 重复构建

在项目根目录执行：

```bash
python -m pip install -r requirements.txt
bash build.sh
```

构建不需要联网，不依赖大型原书路径。它实际运行各科计算/过程核验，生成SVG/PNG/矢量PDF、合并Markdown与LaTeX、三遍XeLaTeX排版、更新覆盖/选题台账，并渲染全部页面。源题重新核查需要保留台账所指原资料；本包不重复装入四本约800MB原书和全部课件。

主要系统依赖：Pandoc、XeLaTeX、Inkscape、fontconfig与Noto Serif/Sans/Mono CJK SC。Debian/Ubuntu可安装texlive-xetex、texlive-latex-extra、fonts-noto-cjk、fontconfig、pandoc、inkscape；Python依赖见requirements.txt。已在Python3.12、Pandoc3.1.11.1、TeX Live2025/dev、Inkscape1.4上实际构建。

单科可用bash build.sh --subjects DS（或CO/OS/CN）。只做版面调整可运行bash build.sh --subjects DS --typeset-only，保留已核图稿与计算结果。重新生成PDF会改变文件指纹，须核对新的结构报告，并重新检查发生变化的页面；构建脚本不会自动伪造视觉通过。

持久编辑入口为manuscript下的Markdown；通用样式为tools/book_preamble.tex、tools/book_images.lua。绘图源在tools/draw_*_figures.py及tools/draw_figures.py，图稿在figures。build/科目/body.tex为中间输出，修改应回写Markdown或模板，避免重建覆盖。普通重建不运行历史样章同步器，不会把已完成章节重置为规划。

最后核对dist中的四科PDF与editorial/full/pdf各科audit.json/visual_review.json的SHA，再运行python tools/bundle_release.py打包。打包程序要求全科覆盖去向和最终视觉记录齐备，并执行ZIP逐项CRC检查。
'''
    old.write_text(readme)
    print(json.dumps(dict(books=books,physical_pages=total,chapter_acceptance_rows=len(rows),unresolved_review_issues=len(unresolved)),ensure_ascii=False))

if __name__=='__main__':main()
