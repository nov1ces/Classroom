# DS06 续作核验记录

- 王道课件映射：`course_coverage.json` 记录 14 个文件的页码、主题和正文锚点。映射是知识组级清单；源图逐幅对照的人工证据未在本文件中完整留存，不能据此声称全部源图已审定。
- 正文 `content.md` SHA-256：`6839c4ab16e43f99309575f462105b15fdc26d8c8aacb56e3fd3d8596459a1d7`。
- 重新编译运行 `code/verify_textbook.cpp`：g++ -std=c++17，-Wall -Wextra -Wpedantic -Werror，AddressSanitizer 与 UndefinedBehaviorSanitizer；实际结果：DFS/BFS order, cycles, disconnected and directed traversal passed。教材式引用参数用C++编译；测试源码的原样同步另见已有 `sources/reviews/independent/displayed_code_sync.json`，其适用内容指纹需独立核对。
- PDF视觉审阅与指纹见 `visual_review.json` 和 `qa.json`；源课件逐页图像与所有教学图逐幅审定不由本记录证明。
- 检查时间 UTC：2026-10-27T05:20:36.369810+00:00。
