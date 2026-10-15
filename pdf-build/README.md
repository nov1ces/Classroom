# PDF 核心构建源码

这份目录保存《408 薄弱点精读与练习册 · 第二版》的排版与拼版流程。内容包括 41 个知识主题、571 道题的放置索引、完整题目与集中解析的拼版、目录书签，以及问答旁 3.4pt 淡色圆点的双向链接。

参考书、课件、上传的笔记和试题册、OCR 文本与模型、裁切图像缓存、构建产物均不在此目录的提交范围。题目索引只保存编号、页码、裁切坐标及编者提示；构建完整练习册时，从本地配置的原 PDF 中取出题目和解析。

## 环境

使用 Python 3.11 或更新版本，以及 XeLaTeX。在 Debian / Ubuntu 上安装：

```bash
sudo apt-get install texlive-xetex texlive-latex-extra fonts-noto-cjk fonts-dejavu-core
cd pdf-build
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

## 完整构建

```bash
cp sources.example.json sources.local.json
```

编辑 `sources.local.json` 中的十个 PDF 路径。相对路径以该配置文件所在目录为起点，也可使用绝对路径或 `~`。四科横版做题本的示例路径直接指向仓库已有文件；四科王道 2027 教材和 relax 题目、解析两册自行放到外部目录，再填写路径。仓库中的分卷压缩包须先解包。

```bash
python build.py --check
python build.py
```

也可传入其他位置的配置：

```bash
python build.py --sources /path/to/sources.json
```

输出位于 `build/408_薄弱点精读与练习册_第二版.pdf`。构建会先核对原 PDF 的 SHA-256、页数及裁切边界，防止版本或页码不匹配；完成后检查 571 对问答链接、目录、书签，并渲染所有页面检查空白页。日志、导航映射和校验报告也在 `build/`，这个目录已忽略。

## 只构建知识部分

无需准备题目或教材 PDF：

```bash
python build.py --review-only
```

生成 `build/review.pdf`，包含封面、复习说明、知识正文及来源附录。只检查已构建的完整练习册可运行 `python build.py --verify-only`。

## 文件分工

| 文件 | 用途 |
| --- | --- |
| `build.py` | 构建入口，调用 XeLaTeX、拼版和成品校验 |
| `topics.py`、`build_review.py`、`templates/preamble.tex` | 知识内容、前言与版式 |
| `compose_book.py`、`pdf_sources.py` | 原页裁切拼版、集中解析、目录与双向圆点 |
| `subset_header_font.py` | 从 PyMuPDF 自带 CJK 字体生成页眉字体，无需提交字体文件 |
| `verify_pdf.py` | 问答链接、目录、书签及页面渲染检查 |
| `config.py`、`sources.example.json` | 输出目录与外部 PDF 路径配置 |
| `data/items.json`、`data/sources.json` | 当前第二版的精简放置索引、原 PDF 版本指纹 |

题目索引对应已发布的第二版，题目与解析的坐标已经核验。修改知识内容可编辑 `topics.py`；更换 PDF 版本或增删题目时，需要同步更新索引、版本指纹及对应的册内说明。这里保存最终构建流程，选题和 OCR 定位产生的中间数据无需参与重建。
