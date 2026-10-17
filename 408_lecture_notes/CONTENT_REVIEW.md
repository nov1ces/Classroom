# 第三轮正文审阅稿

本轮修复计组汇编表格的源码转换问题、补RISC/CISC对比，扩充OS非同步章节与计网的完整综合题，并重画中序线索图。四科仍为29章；新增内容以实际分章Markdown为准，审阅PDF只供阅读内容。**本轮未做分页、裁切、逐页视觉或精排检查**，待用户再次审阅后执行。旧版260页及其视觉通过记录属于V1，不适用于本轮新稿。

## 阅读入口

| 科目 | 正文审阅PDF | 可编辑完整稿 |
| --- | --- | --- |
| 数据结构 | [审阅稿](dist/revision3/数据结构_正文审阅稿.pdf) | [合并稿](manuscript/数据结构_合并稿.md) |
| 计算机组成原理 | [审阅稿](dist/revision3/计算机组成原理_正文审阅稿.pdf) | [合并稿](manuscript/计算机组成原理_合并稿.md) |
| 操作系统 | [审阅稿](dist/revision3/操作系统_正文审阅稿.pdf) | [合并稿](manuscript/操作系统_合并稿.md) |
| 计算机网络 | [审阅稿](dist/revision3/计算机网络_正文审阅稿.pdf) | [合并稿](manuscript/计算机网络_合并稿.md) |

分章稿在`manuscript/DS`、`CO`、`OS`、`CN`。主要改动及定位见[本轮修改说明](dist/revision3/本轮修改说明.md)；PDF文件指纹、正文指纹和实际计数见[审阅交付清单](dist/revision3/交付清单.json)。

题源标注继续沿用用户确认的规则：真题【年份】，原书习题〖节号-题号〗，放在题干首行且同行，该行不缩进；普通段落含标题后首段保留两个汉字的首行缩进。没有习题号的教材教学示例只写真实书节，不虚构年份或题号。个人原作答与完整追溯信息只放内部编辑材料。

## 本轮内容与核验记录

- [数据结构修订](editorial/revision3/DS_revision.md)：图5.2的左右域、孩子边、线索及首尾空端点；此前AVL/B树/排序修改保留。
- [计组修订](editorial/revision3/CO_revision.md)：汇编字符与行序保全、RISC/CISC同维比较，原有完整大题保留。
- [操作系统同类修订](editorial/revision3/OS_revision.md)：非同步章节的调度、内存、文件、输入与磁盘综合题，以及必要同维比较。
- [计网修订](editorial/revision3/CN_revision.md)：九道完整综合题、协议事件链与原始题源分歧；原有四格式及比较保留。
- [独立内容审校](editorial/revision3/review/final_content_review.json)：本轮实际阅读范围与SHA、已修问题和边界，不能代替排版验收。
- [知识覆盖](editorial/scope/coverage.csv)、[考法](editorial/full/考法总表.csv)、[入选题](editorial/full/入选题总台账.csv)、[错题去向](editorial/full/错题最终去向.csv)、[图稿](editorial/full/figure_manifest.csv)：均从当前正文及分科台账回填。

243个稳定知识组的定位沿用本地266条细目；457条实际已读错题保留逐条记录。本轮不因新增综合题而虚增个人错题数量，也不以错题数量决定知识深度。2027正式大纲全文细目仍待取得；真题使用主书和社区完整复原卷交叉，官方原卷与答案发布尚未取得；未统计考试频率。这些限制均不表示已有错题未提供。

## 重新导出审阅稿

依赖与V1相同：Python、Pandoc、XeLaTeX、Inkscape、Noto CJK字体；Python依赖见`requirements.txt`。包含的SVG、PNG和图用PDF均可编辑或由脚本再生。无需原书或网络即可重建讲义；重新核查题源仍需台账所指用户资料。

```bash
bash build_review.sh
```

该入口运行实际计算与状态验证、更新台账并导出四科正文审阅PDF，**不渲染讲义页面，也不运行排版检查**。只重新导出某科可用`python tools/build_books.py --review --review-edition revision3 --subjects DS`；科目代码也可选CO、OS、CN。输出在`dist/revision3`，不覆盖V1及第二轮四科PDF。

绘图源为`tools/draw_*_figures.py`及`tools/draw_figures.py`，数据及图稿在`figures`；通用样式在`tools/book_preamble.tex`和`tools/book_images.lua`；本轮生成的LaTeX中间源码在`build/revision3/科目`。持久修改应回写Markdown或绘图代码。

`build.sh`及旧版视觉报告保留供之后精排阶段使用，本轮不执行该全量排版验收入口。内容确认后，再检查全部新PDF页面、目录跳转、图表、公式与代码的分页及裁切，并以新文件指纹记录结果。
