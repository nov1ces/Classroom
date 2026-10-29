# 408强化笔记

已构建，待集中排版检查。

四科26章，知识笔记187页，195道例题；解析独立成册。

| 科目 | PDF | Markdown | 页数 |
| --- | --- | --- | ---: |
| 数据结构 | [阅读](books/数据结构_强化笔记.pdf) | [阅读](books/数据结构_强化笔记.md) | 57 |
| 计算机组成原理 | [阅读](books/计算机组成原理_强化笔记.pdf) | [阅读](books/计算机组成原理_强化笔记.md) | 52 |
| 操作系统 | [阅读](books/操作系统_强化笔记.pdf) | [阅读](books/操作系统_强化笔记.md) | 39 |
| 计算机网络 | [阅读](books/计算机网络_强化笔记.pdf) | [阅读](books/计算机网络_强化笔记.md) | 39 |

[四科合订本](books/408四科_强化笔记.pdf) · [独立解析册](books/408强化例题解析.pdf) · [解析Markdown](solutions/notes.md)

正文例题题号可跳转解析，解析题号可返回合订本对应题目。解析册前部提供答案与页码速查。PDF相对链接适合将books目录整套下载后使用；浏览器是否支持跨文件跳转取决于阅读器。

[章节正文与图源](chapters/) · [例题及原解析来源](sources/example_index.json) · [交付检查](sources/delivery_checks.json)

## 重建

依赖Python 3、Pandoc、XeLaTeX；Python依赖见requirements.txt，字体与模板位于common/。

```bash
python3 -m pip install -r requirements.txt
python3 tools/build_project.py
```

现有截图和图源随项目保存，使用已核对的索引重建不需要原始教材。改题后须在原资料可读时重新准备来源索引：`python3 tools/build_project.py --refresh-sources`。最终版面检查在完整构建推送GitHub后执行。

代码按可核验的王道教材接口及下标约定；严蔚敏版本尚缺可核验原件。原课件逐帧及细小标签的历史核查范围保留在底稿记录中。
