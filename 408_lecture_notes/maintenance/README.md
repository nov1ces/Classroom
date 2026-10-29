# 工作区维护记录

2026-10-28（Asia/Shanghai）归档整理：

- 原始课件、教材、导图和题本保持原路径。
- 465页课程笔记整套迁移至 `../baselines/course-notes-26/`。
- 早期29章项目、基础重点版及导图版整套归档至 `../archive/`。
- 历史素材压缩包集中放在 `../archive/packages/`，不加入 Git。
- `../dist/` 保留原发布入口的兼容链接。
- 工作区的 `/workspace/study_analysis/` 是教材可读副本与既有分析依赖，`/workspace/scratch/` 是源图核对过程文件，两者保持原路径；新强化笔记集中在 `../current/`。

[迁移清单](archive_manifest_2026-10-28.json)记录每组新旧路径及4796个普通文件的长度和SHA-256。迁移前后逐文件比对通过。归档不删除文件，不重新生成PDF。

[归档脚本](organize_workspace.py)为一次性操作，重复执行会拒绝覆盖已有归档；后续路径维护以迁移清单为准。
