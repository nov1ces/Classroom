# 第三方素材与代码

本模板原创部分见 `LICENSE`。以下文件继续使用各自的原始许可。

## 用户参考图

模板外观依据用户提供的七张 JPEG 重建。技能与章节目录不附带这些参考照片；它们不属于模板 MIT 授权范围。已编译 PDF 不使用这些 JPEG 作为背景或内容。

## 中文字体

- `fonts/NotoSerifSC-Regular.ttf` / `NotoSerifSC-Bold.ttf`：Noto Serif SC。粗体为 Noto Serif SC 可变字体的 700 字重静态实例。
- `fonts/NotoSansSC-Regular.ttf` / `NotoSansSC-Bold.ttf`：Noto Sans SC。
- 许可：SIL Open Font License 1.1。完整文本见 `fonts/OFL-Serif.txt` 和 `fonts/OFL-Sans.txt`。
- 项目：[Noto CJK](https://github.com/notofonts/noto-cjk)。本次直接复用本地已有的完整字体文件，没有对字符集做子集化；用户添加其他中文内容时仍可使用完整字符集。

## 西文字体

- Nimbus Roman / Nimbus Sans：URW Base 35；许可及字体嵌入例外见 `fonts/LICENSE-URW.txt`。
- DejaVu Sans Mono：DejaVu；许可见 `fonts/LICENSE-DejaVu.txt`。
- 公式由本地 TeX 发行版的 Computer Modern / AMS 数学字体排版并嵌入 PDF，受对应发行许可约束。

## xeCJK / ctexhook

为兼容精简 TeX 安装，附带以下支持文件：

```text
xeCJK.sty
xeCJK.cfg
xeCJK-listings.sty
xunicode-addon.sty
xunicode-extra.def
ctexhook.sty
```

它们分别由未修改的上游文档化源码生成：

- xeCJK v3.9.1：[原始 dtx](https://raw.githubusercontent.com/CTeX-org/ctex-kit/xeCJK-v3.9.1/xeCJK/xeCJK.dtx)
- ctex v2.5.10：[原始 dtx](https://raw.githubusercontent.com/CTeX-org/ctex-kit/ctex-v2.5.10/ctex/ctex.dtx)

源码保存在 `vendor/xeCJK.dtx`、`vendor/ctex.dtx`。许可为 LPPL 1.3c 或更新版本，完整原始版权与许可声明位于各 dtx 文件开头。本包的生成步骤仅提取所需模块并填入发布版本元信息，没有改写其运行代码。可用 `python3 tools/build_vendor.py` 重新生成。

其他宏包由用户的 TeX 发行版提供，不在本包内重复分发。构建与源码使用均不要求联机访问上游网站。
