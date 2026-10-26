# 408 中文自学讲义

## 导图核心新版：26章单面边栏笔记

[四科合订PDF（369页）](dist/mindmap-26/408四科26章_导图核心笔记.pdf) · [26章与分科入口](dist/mindmap-26/) · [项目档案](../NOTES_PROJECT.md)

以课件导图为核心，教材框架查漏；自学详解，每页配置高价值旁注，附重绘导图、最小反例微图、Markdown与LaTeX。旧版独立保留。


四科最终稿共 **316 页、29 章、193 道编号例题**。基于 DeepSeek 润色稿，包含数据结构第 5 章自测第 1 题、计组例 3-13 的内容优化，以及例 2-4、例 2-9 等同类选项排版修订。

[下载四科合订本](dist/final/408四科讲义_最终稿_合订本.pdf?raw=true) · [交付清单与 SHA256](dist/final/最终稿交付清单.json) · [版本说明](dist/final/最终稿说明.md)

| 分科最终版 | 页数 | 章数 | 编号例题 | 正文 |
| --- | ---: | ---: | ---: | --- |
| [数据结构 PDF](dist/final/数据结构_最终稿.pdf?raw=true) | 76 | 8 | 44 | [分章](manuscript/DS/) · [合并稿](manuscript/数据结构_合并稿.md) |
| [计算机组成原理 PDF](dist/final/计算机组成原理_最终稿.pdf?raw=true) | 74 | 8 | 54 | [分章](manuscript/CO/) · [合并稿](manuscript/计算机组成原理_合并稿.md) |
| [操作系统 PDF](dist/final/操作系统_最终稿.pdf?raw=true) | 86 | 7 | 45 | [分章](manuscript/OS/) · [合并稿](manuscript/操作系统_合并稿.md) |
| [计算机网络 PDF](dist/final/计算机网络_最终稿.pdf?raw=true) | 80 | 6 | 50 | [分章](manuscript/CN/) · [合并稿](manuscript/计算机网络_合并稿.md) |

## 双面打印

以上页数包含空白页。每本封面后均留一张纯空白页，总页数补齐为偶数；末尾按实际页数补空白页。合订本各科封面都从奇数物理页开始。打印时选择双面、长边翻转，并保留 PDF 中的空白页。

计组补充 IEEE 754 单、双精度参数及特殊编码对照表。四科 104 张表格均按实际字体宽度重新分配列宽，保持正文满宽；短字段尽量单行显示，长说明允许必要换行。例 3-12 的六列表头及数据均为单行。

## 数据结构前两章基础重点

[下载 12 页 PDF](dist/basic-foundations/数据结构前两章_基础重点笔记.pdf?raw=true) · [Markdown 正文](dist/basic-foundations/notes.md) · [LaTeX 源码与重建说明](dist/basic-foundations/) · [项目档案](../NOTES_PROJECT.md)

范围为绪论与线性表，重点整理基本概念、时间与辅助空间复杂度、顺序表及链表的基本操作，保留必要 C++ 代码与四张重绘图示。使用通用章节笔记的 A4 单面边栏模板，正文与边栏在所有页面保持同侧。该目录内含实际使用的字体、图源、内容映射和检查记录，可独立重建。

## 项目目录

- `dist/final/`：合订本、四科 PDF、交付清单和版本说明。
- `dist/basic-foundations/`：数据结构前两章基础重点 PDF、Markdown、LaTeX、字体与图源。
- `manuscript/`：29 章 Markdown 及四科合并稿。
- `figures/`：81 幅引用图的 SVG、PNG、矢量 PDF 与绘图数据。
- `tools/`：当前排版、绘图和核验源码。
- `editorial/final/`：当前版本的源码、选项坐标、PDF 结构及视觉检查记录。
- `editorial/provenance/`：必要的题源、覆盖、错题去向与内容核验记录，见[台账说明](editorial/provenance/README.md)。

旧版 PDF、样章、历轮正文快照、重复打包和旧流程脚本已移除。编译中间文件、页面预览和提取文本统一生成到 `build/`，由 Git 忽略，可随时删除。

## 重新构建

依赖 Python 3、Pandoc 3.1（本版使用 3.1.11.1）、XeLaTeX、fontconfig，以及 Noto Serif/Sans/Mono CJK SC 字体。在本目录执行：

```bash
python -m pip install -r requirements.txt
bash build_final.sh
```

该入口检查 29 章源码与转换结果，编译四科、渲染全部页面，检查缺字、文本边界、全部表格列宽与换行、选项坐标、题源标记、内部链接及打印留白，然后导出五份最终 PDF 与交付清单。构建不需要原教材或网络。视觉阅图记录仅对绑定的文件指纹有效，构建不会自动授予新的人工视觉结论。

仅排版单科可运行 `python tools/build_books.py --subjects DS`（或 CO、OS、CN），中间 PDF 位于 `build/科目/`；完整交付请运行 `bash build_final.sh`。

持久编辑应修改 `manuscript/`、`tools/book_preamble.tex`、`tools/book_choices.py` 或 `tools/book_images.lua`。表格列宽由 `tools/book_tables.py` 用实际 XeLaTeX 字体测量后分配。重绘图稿另需 Inkscape，绘图入口为 `tools/draw_figures.py` 和四个 `tools/draw_*_figures.py`；通常可直接使用已有图稿。

## 核验范围

164 组 A—D 选项与 15 组罗马数字题组已统一排版，另 1 组程序代码选项保留等宽格式。全部 316 页已查看版面总览，并逐表查看 104 张表格的版面；IEEE 表、例 3-12 和密集表格另作细看。所有选项均有坐标检查，封面背面和末尾所加空白页均核验为纯白。合订本保留四科书签及 798 个内部链接，页面文字与渲染像素逐页对照分科稿。

[源码与选项保全](editorial/final/choice_source_checks.json) · [PDF 选项坐标](editorial/final/choice_pdf_checks.json) · [全部表格核验](editorial/final/table_pdf_checks.json) · [IEEE 编码核对](editorial/final/ieee754_checks.json) · [视觉记录](editorial/final/visual_review.json) · [交付检查](editorial/final/delivery_checks.json)

题源简标为真题【年份】、王道习题〖节号-题号〗；原创或改编另行说明。243 个稳定知识组按本地 266 条细目组织，457 条原始错题有读取和去向记录。正式 2027 大纲全文逐条对照、官方原卷和官方答案认证仍受原资料条件限制；不以排版验收替代独立知识审校，也不据教学重点推断考频。
