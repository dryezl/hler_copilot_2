# Human-in-the-Loop Economic Research (HLER) Lab
# 人机协作-经济学研究实验室

*An ongoing experiment in preserving human judgment in the age of vibe research.*  
*在Vibe Research的自动化科研时代，强调人类判断权的一次持续实验。*

[![GitHub Copilot](https://img.shields.io/badge/GitHub%20Copilot-Enabled-blue?logo=github)](https://github.com/features/copilot)

---

## About the Lab | 实验室简介

The **Human-in-the-Loop Economic Research (HLER) Lab** explores how scientific research should evolve when computational execution becomes automated.

Rather than pursuing fully autonomous research pipelines, the Lab designs structured human-AI/Agent collaboration systems in which execution may be automated, but judgment remains human.

因此，**HLER 不是一个"全自动写论文机器"。** 它是一项关于科研结构的长期方法论实验。

在该框架下：

- AI/Agent 负责结构化执行（数据处理、计量估计、图表生成、初稿撰写）
- 人类研究者保留关键判断权（问题选择、识别策略确认、模型审核、发表决定）

> Execution may be automated. Judgment must remain human.  
> 执行可以自动化，判断必须属于人。

---

## GitHub Copilot Integration | GitHub Copilot 集成

This repository is configured for **GitHub Copilot** assistance. Copilot is instructed to follow the HLER framework conventions:

- Respect the human-in-the-loop gates (do not auto-approve or skip review stages)
- Generate structured agent code aligned with the `RunState` pattern
- Assist with econometric scripts, data pipelines, and manuscript drafts
- Always include human approval checkpoints in generated workflows

See [`.github/copilot-instructions.md`](.github/copilot-instructions.md) for the full Copilot instructions.

---

## Pipeline Overview | HLER 研究流程结构

```
Human PI
   │  (1) selects question          │  (2) approves publication
   │                                │
   ▼                                ▼
┌────────────────────────────────────────────────────────────┐
│                      ORCHESTRATOR                          │
│      owns RunState · dispatches tasks · manages gates      │
└──┬────────┬──────────┬──────────┬──────────┬──────────┬────┘
   │        │          │          │          │          │
   ▼        ▼          ▼          ▼          ▼          ▼
Data     Question    Data     Econometrics  Paper    Reviewer
Audit     Agent      Agent      Agent       Agent     Agent
Agent
```

### Core Stages | 核心阶段

| Stage | Agent | Description |
|-------|-------|-------------|
| **DATA_AUDIT** | `DataAuditAgent` | Audits available datasets before question formulation |
| **QUESTIONING** | `QuestionAgent` | Generates candidate research directions; human selects |
| **DATA_COLLECTION** | `DataAgent` | Activates relevant dataset; prevents cross-domain mixing |
| **ANALYSIS** | `EconometricsAgent` | Produces regressions, summary statistics, visualizations |
| **WRITING** | `PaperAgent` | Generates structured manuscript draft |
| **REVIEW** | `ReviewerAgent` | Evaluates novelty, identification, clarity, policy relevance |
| **FINAL_APPROVAL** | Human PI | Publication requires explicit human confirmation |

整个流程强调：
- 数据隔离（Dataset isolation）
- 决策节点可追溯（Auditable human gates）
- 责任明确（Clear authorship accountability）

---

## Repository Structure | 仓库结构

```
hler_copilot_2/
├── .github/
│   ├── copilot-instructions.md   # GitHub Copilot custom instructions
│   └── workflows/
│       └── hler-pipeline.yml     # CI/CD pipeline for HLER stages
├── agents/
│   ├── orchestrator.py           # RunState manager and task dispatcher
│   ├── data_audit_agent.py       # Dataset auditing
│   ├── question_agent.py         # Research question generation
│   ├── data_agent.py             # Data collection and isolation
│   ├── econometrics_agent.py     # Statistical analysis
│   ├── paper_agent.py            # Manuscript drafting
│   └── reviewer_agent.py         # Peer review simulation
├── config/
│   ├── pipeline_config.yaml      # Pipeline stage configuration
│   └── run_state_schema.json     # RunState JSON schema
├── papers/
│   └── templates/
│       └── working_paper.md      # Working paper template
├── data/
│   ├── raw/                      # Raw datasets (gitignored)
│   └── processed/                # Processed datasets (gitignored)
├── outputs/
│   ├── figures/                  # Generated charts and visualizations
│   ├── tables/                   # Regression tables
│   └── manuscripts/              # Draft manuscripts
└── README.md
```

---

## Working Paper Series | 工作论文系列

This repository hosts the **Human-in-the-Loop Economic Research Working Papers**.

Each paper is labeled:

**Human-in-the-Loop Economic Research Working Papers No. XXX** (*hler_wp_XXX.pdf*)

编号按照时间顺序递增，代表系统的迭代轨迹。

These papers are methodological prototypes.  
They are iterative, revisable, and open to critique.

本系列更强调科研结构的探索。

---

## Research Scope | 研究方向

The Lab engages with research in:

- **Labor Economics** | 劳动经济学
- **Health and Human Capital** | 健康与人力资本
- **Agricultural and Development Economics** | 农业与发展经济学
- **Behavioral Economics** | 行为经济学
- **Genoeconomics and Biological Heterogeneity** | 遗传经济学与生物异质性

研究主题涵盖劳动、健康、农业、行为经济学及遗传经济学等领域。

---

## Quick Start | 快速开始

本节演示如何从零开始完成一次完整的 HLER 研究流程。  
This section walks you through a complete research run from scratch.

### Step 0 — Install dependencies | 安装依赖

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/dryezl/hler_copilot_2.git
cd hler_copilot_2

# Install Python dependencies
pip install -r requirements.txt
```

### Step 1 — Place your data | 准备数据

Put your raw dataset file(s) in `data/raw/`. The pipeline will detect them automatically during the DATA_AUDIT stage.

```
data/
└── raw/
    └── labor_dataset.parquet   # example
```

> **Data isolation rule**: each run uses exactly one dataset. Raw files are never modified; all processing writes to `data/processed/`.

### Step 2 — Initialize a new run | 初始化新的研究运行

```bash
python agents/orchestrator.py --init
```

This creates `run_state.json` (gitignored) and advances the pipeline to the `DATA_AUDIT` stage.

### Step 3 — Run the DATA_AUDIT stage | 执行数据审计

```bash
python agents/orchestrator.py --run
```

The `DataAuditAgent` scans `data/raw/` and `data/processed/`, writes an inventory to `outputs/data_audit_report.md`, and advances to the `QUESTIONING` stage.

### Step 4 — ⏸ GATE: select a research question | 人工选择研究问题

Running `--run` now will print candidate questions and **pause** for your input:

```bash
python agents/orchestrator.py --run
```

Example prompt:

```
⏸  HUMAN GATE REQUIRED: GATE_QUESTION_SELECTION
Please select a research question from the candidates above.
  [1] What is the effect of education on wages using the available labor dataset?
  [2] How does health status affect labor market participation?
  ...

Your input: 1
Your name/identifier: Prof. Zhang
Optional notes: Focus on urban workers aged 25–55
```

Alternatively, pre-approve in batch/CI mode:

```bash
python agents/orchestrator.py --approve --gate GATE_QUESTION_SELECTION
# Then advance:
python agents/orchestrator.py --run
```

### Step 5 — Run DATA_COLLECTION and ANALYSIS | 数据收集与计量分析

```bash
# DATA_COLLECTION (automatic — no gate)
python agents/orchestrator.py --run

# ANALYSIS — will pause at GATE_IDENTIFICATION_APPROVAL
python agents/orchestrator.py --run
# Review the proposed identification strategy, then type 'approve'
```

Results are written to `outputs/tables/` (`.csv` + `.tex`) and `outputs/figures/`.

### Step 6 — ⏸ GATE: review the model, then draft the paper | 审核模型并撰写初稿

```bash
# WRITING — will pause at GATE_MODEL_REVIEW
python agents/orchestrator.py --run
# Enter 'proceed' to generate the manuscript draft
```

The draft is saved to `outputs/manuscripts/hler_wp_000_draft.md`.

### Step 7 — Run REVIEW and approve publication | 评审与发表批准

```bash
# REVIEW (automatic — no gate)
python agents/orchestrator.py --run

# FINAL_APPROVAL — will pause for Human PI sign-off
python agents/orchestrator.py --run
# Enter 'approve' to finalize publication
```

### Step 8 — Check status at any time | 随时查看流程状态

```bash
python agents/orchestrator.py --status
```

```
==================================================
  HLER Pipeline Status
==================================================
  Run ID   : a1b2c3d4-...
  Stage    : WRITING
  Dataset  : labor_dataset
  Question : What is the effect of education on wages...
  Gates    : ['GATE_QUESTION_SELECTION', 'GATE_IDENTIFICATION_APPROVAL']
  Artifacts: ['data_audit_report', 'summary_statistics_csv', ...]
==================================================
```

---

## Human Gates | 人工审查节点

The pipeline pauses at the following gates awaiting explicit human approval:

1. **GATE_QUESTION_SELECTION** — Human PI selects the research question from candidates
2. **GATE_IDENTIFICATION_APPROVAL** — Human PI confirms the causal identification strategy
3. **GATE_MODEL_REVIEW** — Human PI reviews the econometric model specification
4. **GATE_PUBLICATION_APPROVAL** — Human PI provides final sign-off for publication

> ⚠️ These gates cannot be bypassed. They are the defining feature of the HLER framework.

---

## Changing Research Domain | 更换研究领域指南

HLER 支持多个研究领域。本节说明如何将流程切换到新的研究方向。  
HLER supports multiple research domains. This guide explains how to adapt the pipeline to a new field.

---

### Option A — Start a fresh run in a different domain | 方案A：在新领域开始全新运行

The simplest approach: place new data in `data/raw/`, then restart the pipeline. Each run is fully isolated via its own `run_state.json`.

```bash
# 1. Add your new-domain dataset
cp /path/to/health_survey.parquet data/raw/health_dataset.parquet

# 2. Delete (or rename) the previous run state
rm run_state.json        # or: mv run_state.json run_state_labor_001.json

# 3. Initialize a fresh run
python agents/orchestrator.py --init

# 4. Continue as normal — the QuestionAgent will now propose
#    questions appropriate to the new data
python agents/orchestrator.py --run
```

---

### Option B — Add a new domain to the pipeline config | 方案B：在配置文件中注册新领域

Edit `config/pipeline_config.yaml` to add your domain to the `research_scope` list:

```yaml
# config/pipeline_config.yaml
research_scope:
  - Labor Economics
  - Health and Human Capital
  - Agricultural and Development Economics
  - Behavioral Economics
  - Genoeconomics and Biological Heterogeneity
  - Public Finance and Taxation        # ← add new domain here
  - Urban and Regional Economics       # ← another example
```

This list is read by `QuestionAgent` to scope the candidate questions it generates.

---

### Option C — Customize domain-specific questions | 方案C：自定义研究问题候选列表

To hard-code domain-specific candidate questions for your field, edit the `_generate_candidates` method in `agents/question_agent.py`:

```python
# agents/question_agent.py  (inside QuestionAgent)
def _generate_candidates(self, state: RunState) -> list[str]:
    """
    Return domain-specific candidate research questions.
    Customize this list for your research field.
    """
    return [
        # === Public Finance examples ===
        "What is the effect of marginal tax rates on labor supply at the extensive margin?",
        "How does the Earned Income Tax Credit affect maternal employment?",
        "Do property tax increases reduce residential investment?",
        # === add your own questions below ===
    ]
```

After editing, the next `QUESTIONING` stage will display your custom questions at the `GATE_QUESTION_SELECTION` pause.

---

### Option D — Add a new dataset mapping | 方案D：添加新的数据集映射

`DataAgent` infers the dataset from the research question by keyword matching. To support a new domain dataset, add a branch in `agents/data_agent.py`:

```python
# agents/data_agent.py  (inside DataAgent._select_dataset)
def _select_dataset(self, state: RunState) -> str:
    question = (state.research_question or "").lower()

    # Existing mappings
    if "wage" in question or "labor" in question:
        return "labor_dataset"
    if "health" in question or "medical" in question:
        return "health_dataset"

    # ← Add your new domain here
    if "tax" in question or "fiscal" in question or "revenue" in question:
        return "public_finance_dataset"

    return "general_dataset"
```

Place the corresponding file at `data/raw/public_finance_dataset.parquet` (or `.csv`).

---

### Copilot tip | Copilot 提示

When using GitHub Copilot to extend the pipeline for a new domain, open `agents/question_agent.py` and type a comment describing your domain. Copilot will follow the HLER conventions in `.github/copilot-instructions.md` and suggest domain-appropriate questions and dataset mappings automatically.

```python
# Generate candidate research questions for Urban Economics research
# covering housing markets, commuting patterns, and agglomeration effects
def _generate_candidates(self, state: RunState) -> list[str]:
    ...  # Copilot will complete this
```

---

## Contributing | 贡献指南

Contributions to the HLER Lab framework are welcome. Please ensure:

1. All new agents implement the `BaseAgent` interface
2. Human gates are preserved and not automated away
3. RunState transitions are logged and auditable
4. Code follows the HLER coding conventions in `.github/copilot-instructions.md`

---

## License | 许可证

This project is open-source. See [LICENSE](LICENSE) for details.

---

*HLER Lab — Execution may be automated. Judgment must remain human.*  
*执行可以自动化，判断必须属于人。*