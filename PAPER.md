# kaggle-science-exam：工作区日志的 stage 分析工具集（D41–D58 重建）

> 本文档是 kaggle-science-exam 的**论文摘要草稿**，内容全部来自仓库真实实现与实测
> 结果，无虚构数字。

## 摘要（Abstract）

原始 Kaggle 竞赛工作（stages D1–D40）在 2026-07-20 工作区丢失后**永久不可恢复**。
本文重建一套可复跑的 **stage 分析工具集**（18 个 CLI 模块 D41–D58），用于从
`.workbuddy/memory/YYYY-MM-DD.md` 日志度量项目阶段工作流的节奏、结构与质量——
而不是假装审计原项目。

**工具集（可复算）**：18 个模块——`stage_streak`（连续活跃天数）、
`stage_leaderboard`（被提及最多的 stage + 一次性/重复分类）、`stage_grep`（在
src/tests/report 中 grep Dxx）、`stage_coverage`（跨项目源的分 stage 覆盖）、
`stage_timeline`（首见日期 + 缺口分析）、`stage_cadence`（逐日节奏 + A-F 等级）、
`stage_suggestion`（可行动建议）、`stage_summary`（项目健康摘要 A-D）、
`stage_trend`（周环比 + 预测）、`stage_fanout`（共现对 + 密度）、`stage_clusters`
（贪心社区检测）、`stage_backlog`（被提及但未实现）、`stage_coupling`（跨簇耦合 +
模块度）、`stage_maturity`（3 通道 0-3 分：memory+code+readme）、`stage_velocity`
（epoch + 活跃比）、`stage_density_curve`（前置/后置标记）、`stage_distribution`
（提及直方图 + Gini）、`stage_calendar`（逐月/逐星期几/逐日计数）。

**验证（可复算）**：71 项 pytest 单测全绿（`pytest -q` = 71 passed，来自 18 个测试
文件，fixture 输入 `.workbuddy/memory/2026-07-20.md`）；18 个 CLI 冒烟测试全部通过
（`ALL SMOKE TESTS PASSED (D41 - D58)`）。

**fail-closed（关键行为）**：输入缺失时模块**不编造数字**——`_safe_read` 对不存在
的路径返回空串；`build_summary` 对空目录返回 `n_stages=0, health="D"`（最差等级），
而非伪造健康度。这是诚实度量：缺失的输入产生最差等级，而不是虚假的"通过"。

**明确边界**：本工具集**不证明**这些模块描述原始 Kaggle 竞赛工作（stages D1–D40
永久丢失，分析测量的是**重建日志**）；**不声称**任何 leaderboard 分数、提交排名
或竞赛结果（分析是重建产物，不是原项目审计）。

## 关键词

Kaggle；stage 分析；工作流节奏；日志解析；CLI 工具集；fail-closed；
重建产物；社区检测；耦合分析

## 与真实代码的对应

| 摘要声明 | 对应真实实现 |
|---|---|
| 18 个 CLI 模块 | `src/analysis/stage_{streak,leaderboard,grep,coverage,timeline,cadence,suggestion,summary,trend,fanout,clusters,backlog,coupling,maturity,velocity,density_curve,distribution,calendar}.py` |
| 71 项单测 | `pytest -q` 实测 71 passed（18 个测试文件） |
| 18 个冒烟 | `tests/smoke_test.py` 实测 ALL 18 STAGES PASSED |
| fail-closed | `_safe_read` 返回空串（`stage_summary.py:29`）+ `test_build_summary_empty` |
| 输入 fixture | `.workbuddy/memory/2026-07-20.md` |
| 重建说明 | README「Note (2026-07-20)」 |
