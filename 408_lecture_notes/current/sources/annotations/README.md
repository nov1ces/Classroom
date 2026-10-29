# 用户侧栏批注

输入为用户上传的 `annotations.json`，原文件逐字节保存在 `input.json`。本次只添加侧栏；正文 Markdown、LaTeX、例题、图源、原有侧栏及独立解析册保持不变。

- `sidebars.md`：198条侧栏文字及对应位置，独立于正文。
- `diagram_specs/`：17幅图的完整原始说明；`tex/`：文字和图示的可编辑 LaTeX 分块。
- `placement.json`：每一块的原文锚点、合订本页码及实际侧栏坐标。
- `baseline.json`、`baseline/`：修改前的文件指纹和 PDF，用于幂等重建及正文不变的核验。
- `checks.json`：输入/输出指纹、受保护源码指纹、原 PDF 内容流与144 dpi像素对比。视觉检查另附实际输出指纹。

文字批注放在原锚点同页；图示保持8.5 pt字号，按阅读顺序分块放入同章空余侧栏，页码均指合订本。保留全部原始图示说明，窄栏图按需要分块或转置，数值、状态、方向和条件保持对应。

直接重新应用侧栏（使用保存的修改前底本，不重复叠加）：

```bash
python3 tools/import_annotations.py
```

常规 `python3 tools/build_project.py` 会在正文、解析和原有链接构建完毕后重新应用侧栏。`--refresh-baseline`仅用于刚生成的干净 PDF，会拒绝把已叠加的成品当作底本。仅检查排版而不写入阅读版时用 `--typeset-only`。
