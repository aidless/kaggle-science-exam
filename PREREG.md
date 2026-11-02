# PREREG — kaggle-science-exam 预注册规格

> 本文件是 kaggle-science-exam（18 个 stage 分析 CLI 模块 D41–D58）的**预注册规格**：
> 把研究假设、评测方案、成功标准与明确边界写在分析之前。所有数字可从仓库内
> 确定性代码/实测结果复算。

## 1. 研究问题

原始 Kaggle 竞赛工作（stages D1–D40）在 2026-07-20 工作区丢失后**永久不可恢复**。
本仓库回答的问题是：**如何从工作区日志重建一套可复跑的 stage 分析工具**，让「项目
阶段工作流」的节奏、结构、质量可以被度量——而不是假装审计原项目。

**核心假设（H1）**：`.workbuddy/memory/YYYY-MM-DD.md` 日志文件可被 18 个 CLI 模块
解析，并产出文档化的报告结构（streak / cadence / coverage / clusters / backlog /
coupling / maturity / velocity / distribution / calendar 等）。

**辅助假设（H2，fail-closed）**：输入缺失时模块**不编造数字**——`_safe_read` 对
不存在的路径返回空串，`build_summary` 对空目录返回 `n_stages=0, health="D"`
（最差等级），而不是伪造健康度。

**辅助假设（H3，边界）**：本仓库测量的是**重建日志**，不是原始竞赛运行；不声称
任何 leaderboard 分数、提交排名或竞赛结果。

## 2. 评测方案（可复算）

### 2.1 离线单测（71 项）

```bash
python -m pytest -q          # 71 passed
```

71 项来自 `tests/` 下 18 个测试文件（每个 D41–D58 一个），用 fixture 输入
`.workbuddy/memory/2026-07-20.md` 逐模块校验核心逻辑。

### 2.2 冒烟测试（18 stages）

```bash
python tests/smoke_test.py   # ALL 18 SMOKE TESTS PASSED (D41 - D58)
```

实测输出：`[18/18] stage_calendar CLI` → `ALL SMOKE TESTS PASSED (D41 - D58)`。

### 2.3 单 CLI 复算

```bash
python -m src.analysis.stage_timeline \
    --memory_dir .workbuddy/memory \
    --out report/stage_timeline.md --out_json report/stage_timeline.json
```

### 2.4 成功标准

| 判据 | 成功标准 |
|---|---|
| 离线单测 | `pytest -q` = 71 passed |
| 冒烟 | `smoke_test.py` = ALL 18 STAGES PASSED |
| fail-closed | 空目录 → `build_summary` 返回 `n_stages=0, health="D"`（不编造） |
| 可复算 | 71 是 `pytest --collect-only` 实际总数，非目标值 |

## 3. 明确边界（不证明什么）

1. **不证明这些模块描述原始 Kaggle 竞赛工作**——stages D1–D40 永久丢失
   （工作区 2026-07-20 被清空），"stage analysis"测量的是**重建日志**，不是原始
   竞赛运行。
2. **不声称任何 leaderboard 分数、提交排名或竞赛结果**——分析是重建产物，不是
   原项目审计。
3. **不证明日志语义与真实工作流一致**——D41–D58 从会话历史重建，D1–D40 不在
   本仓库内。
4. **`report/` 输出是 CLI 产物**，不承诺任何特定业务含义之外的解读。

## 4. 成功标准（判据）

本预注册声明**成功**当且仅当：
1. `pytest -q` = 71 passed（离线）；
2. `smoke_test.py` = ALL 18 STAGES PASSED；
3. 空输入 → `build_summary` 返回 `n_stages=0, health="D"`（fail-closed 有测试覆盖）；
4. 每一条"不证明"边界都在 README「What this does and does not prove」或本文件
   有对应记录。
