# 数据结构前两章 · 基础重点笔记

[下载 12 页 PDF](数据结构前两章_基础重点笔记.pdf?raw=true) · [阅读 Markdown](notes.md) · [LaTeX 正文](chapter.tex) · [项目档案](../../../NOTES_PROJECT.md)

主文件：main.tex；正文：chapter.tex；同内容Markdown：notes.md。

正文以408前两章的重点基础知识为主，包括概念、算法特性、时间/辅助空间复杂度、线性表定义、顺序表、单链表基本操作、双链表/循环链表/静态链表，以及批量删除和逆置两个基础巩固算法。复杂综合题按本次要求压缩。

使用通用章节笔记模板，A4单面，正文固定左侧，边栏和页码固定右侧，无封面或附加空白笔记页。

## 构建

需要XeLaTeX、常见TeX宏包以及Python的PyMuPDF与Pillow。

在本目录运行：

    python tools/build_chapter.py .

也可直接运行两遍：

    xelatex -no-shell-escape -interaction=nonstopmode -halt-on-error main.tex

当前字体已包含在fonts/，无需另找字体包。本次采用系统Noto CJK SC宋体/黑体和DejaVu代码字体，与原技能指定的字体文件版本不同；中文字体从系统TTC的SC字体面提取，版本与SHA-256见sources/font-selection.json。模板的页面尺寸、边栏位置与组件样式未改变。字体授权文件也已包含。

## 图示与核验

figures/中含四张重新绘制的图示及TikZ、PNG、SVG源文件；code/中是正文实际使用的代码片段。

sources/coverage.json保留内容映射和按本次要求压缩的算法题记录；sources/qa.json记录12页逐页视觉检查、原生文字与字体嵌入检查、代码对照和内存检查。

NOTES_PROJECT.md是本次交付时的项目档案快照，权威档案继续保存在资料项目根目录。压缩包不包含原教材、整套做题本等母本。
