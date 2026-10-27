# NewsEE — 基于大语言模型的新闻事件信息抽取

研究生论文实验代码。数据集：MAVEN-Arg（12 种新闻事件类型子集，文档级抽取）。

## 一次性准备

```bash
cd ~/PycharmProjects/NewsEE
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # 然后在 .env 里填入 API key
python scripts/prepare_data.py          # 生成 data/dev.jsonl, test.jsonl, pool.jsonl
python scripts/evaluate.py --oracle --gold data/dev.jsonl   # 判分自检：所有指标应为 100
```

## 运行基线

```bash
# 试点：5 篇开发集文档，先确认 API 通了
python scripts/run_baseline.py --model glm-flash --split dev --limit 5
# 开发集全量（30 篇）
python scripts/run_baseline.py --model glm-flash --split dev
```

结果保存在 `runs/<运行名>/`：`metrics.json`（分数）、`raw.jsonl`（模型原始输出）、`run.json`（配置和 token 用量）。
所有模型回复都缓存在 `.cache/`，重复运行不再花钱、结果完全一致。

## 模型简称（在 newsee/config.py 修改）

| 简称 | 实际模型 | 说明 |
|---|---|---|
| glm-flash | 智谱 glm-4-flash | 开发调试主力 |
| ds-flash | deepseek-flash | DeepSeek 便宜档 |
| ds-pro | deepseek-v4-pro | 只跑最终主实验 |
| qwen3b | Ollama qwen2.5:3b | 本地小模型 |

DeepSeek 大批量运行请放在北京时间工作日 9–12、14–18 点以外（半价时段）。

## 目录

```
newsee/   schema.py 事件类型与角色定义 | scorer.py 判分 | llm.py API 调用与缓存 | prompts.py 提示词
scripts/  prepare_data.py 数据准备 | evaluate.py 判分 | run_baseline.py 零样本基线
data/     生成的评测数据（不要手改）
runs/     每次实验的结果
```

## 评测口径（已冻结）

- 实体：Entity-I（文本对）/ Entity-C（文本和类型都对）
- 触发词：Trig-I / Trig-C（多重集合匹配）
- 论元：Arg-I / Arg-C，事件级对齐，同一事件的多个触发词提及合并；EM（严格）和 BoW 词袋 F1（宽松），与 MAVEN-Arg 官方一致
- 文本统一做反分词和 SQuAD 式归一化（小写、去标点、去冠词）

## 第 2 周：分阶段框架与消融实验

```bash
# 先用 3 篇快速检查（几乎不花 token）
python scripts/run_framework.py --model glm-air --split dev --limit 3
# 开发集消融（6 种配置 + 金标准触发词设置，约 30 分钟）
python scripts/run_ablation.py --model glm-air --split dev
# 示例数量曲线
python scripts/run_ablation.py --model glm-air --split dev --shots 0,1,3,5
```

框架四个阶段：实体识别 → 触发词检测 → 按事件类型抽取论元（每个触发词附带所在句子）→ 原文校验（规则，不调用模型）。
可开关的模块：`--no-decompose`、`--no-guidelines`、`--demos retrieval|random|none`、`--k N`、`--no-verify`、`--setting gold_trigger`。
消融结果表保存在 `results/`，可直接放进论文第 5 章。

用金标准答案模拟模型输出时，框架的理论上限约为：实体 99.5、触发词 100、论元 98（论元的少量损失来自同一句中同词多事件的合并）。
