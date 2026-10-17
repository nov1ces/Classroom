# DS/CO 错题台账的恢复说明

主文件为上一级的 `ds_co_errors.json` 与 `ds_co_errors.csv`，读取范围和限制见 `../ds_co_read_report.md`。JSON 顶层 `records` 存逐题登记。

`native_records.json` 是从实际原 PDF 再提取的227条快照；`question_raw_text` 保留页眉页脚，`question_text` 删除阅读无关的页眉页脚，原排式丢失不静默改写。`source_correction` 保存原题差异和原书恢复依据。`answer_explanation_ocr_unverified` 是旧OCR定位得到的解释文字，未逐字校订。

`answer_labels/` 保存原扫描书答案题号/字母及解析开头，全部227条字母已目验；`question_anomalies/` 保存实际查看的50道题面和4处原书题面对照。`sheets/` 是查看用拼页，旁边JSON列出题目ID。完整答案带图另以`_full.png`保存。`read_events.jsonl`和`visual_checks.json`说明实际阅读对象和范围。

`recalculation_results.json` 保留72项运行结果及关键过程，涉及71题。只把有实际计算记录的题标记`independent_calculation_checked=true`。这与原书答案字母目验、原卷身份核验、题面视觉检查分别计数。

需要恢复台账时运行：

```bash
python /workspace/408_lecture_notes/editorial/errors/ds_co_checks/rebuild.py
```

脚本先比较六个原始材料的SHA-256，只有源文件未改变才恢复已人工观察的登记。提取、题面裁图、人工分类映射、覆盖表关联、复算、汇总分别在六个脚本中。脚本的“已目验”来自本轮已完成的人工审读记录，并不意味着重新运行代码就重新目验了页面。资料改变时脚本停止，需要再读真实页后更新观察与基线。

覆盖表关联依赖`../../scope/DS_coverage.json`和`../../scope/CO_coverage.json`。226条已有`knowledge_ids`，CO 3.2 第26题单体多字存储器尚待覆盖表明确去向。代码不会自动把它猜配为多模块交叉存储器。

继续章节选题时，先处理`source_issues.md`中的条件，再核真题原卷；保留所有个人原错选，缺少推理者继续使用“错因不可确定”。候选正文、复习、合并和待条件核是初拟去向，不能当作四科例题已定稿。
