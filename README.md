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

## Getting Started | 快速开始

### Prerequisites | 前置条件

```bash
pip install -r requirements.txt
```

### Running the Pipeline | 运行流程

```bash
# Initialize a new research run
python agents/orchestrator.py --init --config config/pipeline_config.yaml

# Start the pipeline (will pause at human gates)
python agents/orchestrator.py --run

# Approve a human gate and continue
python agents/orchestrator.py --approve --gate QUESTIONING

# Check current RunState
python agents/orchestrator.py --status
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