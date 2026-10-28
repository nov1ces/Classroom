# 408四科26章完整课程笔记

以项目四科【课件】目录中的王道课件为主线，王道2027教材核验，参考博客的知识分级与图文讲解方式；独立导图用于辅助查漏。

## 阅读入口

**制作中：**以下分册和合订本为阶段性工作稿，操作系统内容和部分课件源图仍在核对；当前进度见项目档案。

- [四科合订PDF](408四科26章_完整笔记.pdf)
- [数据结构PDF](books/数据结构_完整笔记.pdf) · [Markdown](books/数据结构_完整笔记.md)
- [计算机组成原理PDF](books/计算机组成原理_完整笔记.pdf) · [Markdown](books/计算机组成原理_完整笔记.md)
- [操作系统PDF](books/操作系统_完整笔记.pdf) · [Markdown](books/操作系统_完整笔记.md)
- [计算机网络PDF](books/计算机网络_完整笔记.pdf) · [Markdown](books/计算机网络_完整笔记.md)
- [章节正文与图源](chapters/) · [项目档案](NOTES_PROJECT.md)

当前制作状态和检查结果见项目档案、各章`sources/`及[交付检查](sources/delivery_checks.json)。文件入口在相应产物生成后生效，完成状态以实际检查记录为准。

## 代码约定

正文代码采用王道教材式C／C++描述，保留结构体、函数接口、引用参数、存储模型与算法下标。顺序表数组下标与操作位序分别说明；链表区分头结点模型；串采用`SString`、`ch[1..length]`，KMP采用`next[1]=0`、失败返回0。所有图、表、轨迹与代码使用对应的同一套约定。

严蔚敏教材的差异对照以可核验版次和实际来源为依据。当前可读主教材为项目王道2027四本，具体来源身份见`sources/textbook_inventory.json`。

## 排版与编辑

A4单面边栏版式，正文固定左侧，旁注固定右侧。章节`content.md`为正文编辑入口，`sidebars.json`保存旁注，`map.json`保存知识导航，`figures/`保存PNG、SVG与矢量PDF。`notes.md`是包含实际排入PDF的导图和旁注的阅读版本。各章`code/`保存验证程序。

制作记录、来源页码、纠错和检查范围均在`sources/`中。来源自动提取、作者内容复核、数值验证和PDF视觉检查分别登记。

## 重建

依赖：Python 3、PyMuPDF、Pillow、Pandoc、XeLaTeX、Inkscape、fontconfig及模板所需TeX包。必要字体和许可位于`common/fonts/`。

```bash
python3 -m pip install -r requirements.txt
python3 tools/build_all.py --jobs 2
```

重建单章及汇编：

```bash
python3 tools/build_notes.py DS04
python3 tools/release.py assemble
python3 tools/release.py audit
python3 tools/release.py package
```

构建与阅读不需要原始教材。新构建的PDF须重新视觉复核，既有视觉记录仅适用于绑定的PDF指纹。素材包保存可编辑正文、图源、字体、构建及核验记录，原始课件和教材仍保留在项目资料目录。

## 参考来源

- [努力的clz：考研408王道计算机考研网课笔记总结](https://blog.csdn.net/qq_43468008/article/details/129418769)。该博客声明采用CC BY-SA 4.0，章节链接和访问记录见`sources/blog_index.json`。
- 项目四科基础考点课件、精讲课导图、王道2027教材及配套题目。具体文件指纹和引用映射见`sources/`与各章覆盖清单。
- 字体及模板代码沿用各自许可，见`common/fonts/`与章节许可说明。
