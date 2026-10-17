# 408 中文自学讲义

**当前为第三轮正文审阅阶段。** 本轮修汇编源转换、补RISC/CISC与OS比较、增加OS和计网综合题并重画中序线索图；尚未做新稿分页、裁切和逐页视觉检查。完整入口见[正文审阅说明](CONTENT_REVIEW.md)，具体定位见[本轮修改说明](dist/revision3/本轮修改说明.md)。

正文在第三轮内容审阅之后另做了一轮中文润色（第四轮，2026-10-17）：只调整行文、指代、句序与局部表述，未改知识点、公式、代码、表格、题目条件与答案；逐章记录、结构核对与疑似问题见[润色说明](editorial/polish/润色说明.md)。`dist/revision3` 的四科审阅PDF仍是润色前导出的，未重排。

四科29章，可编辑分章正文、合并稿与统一A4单栏PDF。题源按已确认标准缩写：真题【年份】，非真题〖原书节号-三位题号〗，置于题干首行并同行，该首行不缩进。普通正文段落（含标题后首段）首行缩进两个汉字。正文不展示个人原作答；详细题源与错题记录放在内部材料。

| 当前正文审阅稿 | 章数 | 编号例题 | 可编辑完整稿 |
| --- | ---: | ---: | --- |
| [数据结构](dist/revision3/数据结构_正文审阅稿.pdf) | 8 | 44 | [合并稿](manuscript/数据结构_合并稿.md) |
| [计算机组成原理](dist/revision3/计算机组成原理_正文审阅稿.pdf) | 8 | 54 | [合并稿](manuscript/计算机组成原理_合并稿.md) |
| [操作系统](dist/revision3/操作系统_正文审阅稿.pdf) | 7 | 45 | [合并稿](manuscript/操作系统_合并稿.md) |
| [计算机网络](dist/revision3/计算机网络_正文审阅稿.pdf) | 6 | 50 | [合并稿](manuscript/计算机网络_合并稿.md) |

四科共193道编号例题、81幅实际引用图，例题就近解析，章末自测给答案。分章正文在manuscript/DS、CO、OS、CN中；公式为可编辑文本源码，图保留SVG、PNG、绘图源及供构建引用的矢量PDF。导出程序生成目录、书签及题目与方法索引，本轮尚未检查新PDF的跳转与页面呈现。

GitHub 中的 `408_lecture_notes/` 即完整可编辑项目。正文、图稿、排版源码、构建脚本、审阅PDF及内部编辑材料按目录直接跟踪；[交付清单](dist/revision3/交付清单.json)记录成稿的实际计数和文件指纹。压缩归档、Python缓存、重复的构建PDF及临时页面渲染由 `.gitignore` 排除，可由源码重新生成。

## 项目目录

| 目录或文件 | 内容 |
| --- | --- |
| `manuscript/` | 29章正文与四科合并Markdown |
| `figures/` | SVG、PNG、矢量PDF及共享图数据 |
| `tools/` | 绘图、排版、索引、复算与编辑台账工具 |
| `editorial/` | 知识覆盖、选题、题源、错题去向、来源证据及审校记录 |
| `dist/revision3/` | 当前四科审阅PDF、目录、台账与修改说明 |
| `build/` | 保留的Markdown、LaTeX中间源码及构建指纹 |
| `build_review.sh`、`requirements.txt` | 审阅稿构建入口与Python依赖 |
| `PROJECT_STATE.json` | 可恢复进度及当前交付状态 |

## 核验范围

当前以[本轮独立内容审校](editorial/revision3/review/02_final_content_review.md)、[逐章状态](editorial/revision3/逐章状态.csv)及[剩余核验](editorial/未解决问题与后续任务.md)为准。13个改章实际独立复读；16个未改章只核与基线SHA相同。243个稳定知识组按已读本地266条细目组织，四科457条原始错题均有读取及逐条去向记录；这不表示457题都做过完整独立计算或官方真题认证。

2027正式大纲的出版书目已核，全文细目尚未取得，仍待正式年度逐条对照。入选真题与王道主书、完整社区复原卷交叉核验，并核对应答案和过程；社区卷是二手复原，官方原卷/官方答案发布未取得。具体版本分歧与勘误保留在来源记录，未编造考试频率或未来变动。

## 编辑材料入口

- [实际目录](editorial/full/四科实际目录.md)、[知识覆盖表](editorial/scope/coverage.csv)。
- [考法总表](editorial/full/考法总表.csv)、[入选题总台账](editorial/full/入选题总台账.csv)、[错题最终去向](editorial/full/错题最终去向.csv)。
- [原始读取总台账](editorial/errors/错误题总台账.csv)：保留实际原作答、可用批改、缺失推理说明和原题位置，不推测个人心理错因。
- 各科editorial/full/科目/chapter_records.json与results.json：知识位置、选题比较、来源核验、逐题去向、图稿及实际复算。
- [参考讲义分析与编写规范](editorial/reference/参考讲义分析与编写规范.md)、[本轮独立审校机器记录](editorial/revision3/review/final_content_review.json)。
- [实际图稿清单](editorial/full/figure_manifest.csv)：本轮只登记来源、引用与SHA，不认证PDF版式。各科editorial/full/pdf中的结构/视觉报告属于V1历史，不能套用到新稿。
- [V1独立目录重建验证](editorial/full/portable_build_verification.json)：历史副本的模型、图稿、排版及像素验证记录；不代表第三轮PDF已检查。
- [正式范围与资料续核](editorial/full/sources/正式范围与资料续核.md)、[当前来源清单](editorial/sources/当前来源与核验范围.md)。其中首轮未读状态的后续更新以full各科实际记录为准，不冒称整本课件或题库全读。

首轮样章、最初规划和首轮检查保留为历史证据，当前进度以[PROJECT_STATE.json](PROJECT_STATE.json)、实际分章文件和本次交付清单为准。

## 重新导出正文审阅稿

在项目根目录执行：

```bash
python -m pip install -r requirements.txt
bash build_review.sh
```

该入口运行各科计算与状态核验、源码转换检查、覆盖和选题台账更新，并生成合并Markdown、LaTeX及三遍XeLaTeX导出的四科审阅PDF；**不渲染讲义页面，也不运行排版检查**。重建不需联网或大型原书路径，使用项目内图稿即可；重新核查题源需要保留台账所指原资料。原书与课件仍按来源台账所指资料定位。

主要系统依赖：Pandoc、XeLaTeX、Inkscape、fontconfig与Noto Serif/Sans/Mono CJK SC。Debian/Ubuntu可安装texlive-xetex、texlive-latex-extra、fonts-noto-cjk、fontconfig、pandoc、inkscape；Python依赖见requirements.txt。已在Python3.12、Pandoc3.1.11.1、TeX Live2025/dev、Inkscape1.4上实际构建。

单科导出可用`bash build_review.sh --subjects DS`（或CO/OS/CN），输出在`dist/revision3`，不覆盖V1或第二轮PDF。重绘图稿的方法见分科修订记录。正文或图语义发生变化后，应重新核验受影响部分；构建不会自动授予内容或视觉通过。

持久编辑入口为manuscript下的Markdown；通用样式为tools/book_preamble.tex、tools/book_images.lua。绘图源在tools/draw_*_figures.py及tools/draw_figures.py，图稿在figures。build/revision3/科目/body.tex为中间输出，修改应回写Markdown或模板，避免重建覆盖。普通重建不运行历史样章同步器，不会把已完成章节重置为规划。

本轮定稿收束用`python tools/finalize_review.py --edition revision3`，核对当前正文、独立内容记录、导出指纹与台账；项目通过普通Git文件提交。该收束步骤不检查讲义排版。

V1的260页成稿、视觉报告及第二轮PDF单独保留。旧`build.sh`及最终版验收工具留待内容确认后的精排阶段使用，本轮不执行。
