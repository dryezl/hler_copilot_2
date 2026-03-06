# GitHub Copilot Instructions for HLER Lab
# GitHub Copilot 针对 HLER 实验室的自定义指令

This repository implements the **Human-in-the-Loop Economic Research (HLER) Lab** framework.
GitHub Copilot must follow these conventions when assisting in this repository.

---

## Core Principle | 核心原则

> Execution may be automated. Judgment must remain human.  
> 执行可以自动化，判断必须属于人。

**Never generate code that bypasses, auto-approves, or skips human gates.**

---

## Framework Architecture | 框架架构

### RunState

All agents communicate through a shared `RunState` object. The `RunState` tracks:

- Current pipeline stage
- Dataset in use (enforces isolation)
- Human gate approvals (stored as signed records)
- Audit log of all agent actions

When generating agent code, always include `RunState` as the first parameter and update it after every significant action.

```python
# Correct pattern
def run(self, state: RunState, **kwargs) -> RunState:
    state.log(f"{self.__class__.__name__} started")
    # ... agent logic ...
    state.advance_stage()
    return state
```

### Pipeline Stages | 流程阶段

The pipeline follows these stages in order:

1. `DATA_AUDIT` → `DataAuditAgent`
2. `QUESTIONING` → `QuestionAgent` + **GATE_QUESTION_SELECTION** (human required)
3. `DATA_COLLECTION` → `DataAgent`
4. `ANALYSIS` → `EconometricsAgent` + **GATE_IDENTIFICATION_APPROVAL** (human required)
5. `WRITING` → `PaperAgent` + **GATE_MODEL_REVIEW** (human required)
6. `REVIEW` → `ReviewerAgent`
7. `FINAL_APPROVAL` → **GATE_PUBLICATION_APPROVAL** (human required)

### Human Gates | 人工审查节点

Human gates are non-negotiable checkpoints. When generating orchestration code:

- Use `state.await_human_gate(gate_name)` to pause execution
- Gates must record who approved, when, and with what input
- Never generate code that sets `gate_approved = True` programmatically without explicit human input

```python
# Correct gate pattern
state.await_human_gate(
    gate="GATE_QUESTION_SELECTION",
    prompt="Please select a research question from the candidates above.",
    options=candidates
)
# Execution pauses here until a human provides input
```

---

## Agent Conventions | Agent 编码规范

### BaseAgent Interface

All agents must inherit from `BaseAgent`:

```python
from agents.base_agent import BaseAgent
from config.run_state import RunState

class MyAgent(BaseAgent):
    stage = "MY_STAGE"

    def run(self, state: RunState, **kwargs) -> RunState:
        """Execute this agent's task and return updated RunState."""
        ...
```

### Naming Conventions | 命名规范

| Component | Convention | Example |
|-----------|-----------|---------|
| Agent classes | `PascalCase` + `Agent` suffix | `EconometricsAgent` |
| Stage constants | `UPPER_SNAKE_CASE` | `DATA_AUDIT` |
| Gate names | `GATE_` prefix + `UPPER_SNAKE_CASE` | `GATE_QUESTION_SELECTION` |
| RunState methods | `snake_case` | `state.log()`, `state.advance_stage()` |
| Output files | `hler_wp_NNN.pdf` | `hler_wp_001.pdf` |

### Data Isolation | 数据隔离

- Each research run activates exactly one dataset
- Cross-dataset operations require explicit human approval
- Raw data in `data/raw/` is never modified; always write to `data/processed/`
- Dataset locks are stored in `RunState.active_dataset`

```python
# Correct data access pattern
def load_data(self, state: RunState, dataset_name: str):
    if state.active_dataset and state.active_dataset != dataset_name:
        raise DataIsolationError(
            f"Cannot switch from {state.active_dataset} to {dataset_name} "
            "without human approval."
        )
    state.active_dataset = dataset_name
    return pd.read_parquet(f"data/processed/{dataset_name}.parquet")
```

---

## Econometrics Guidelines | 计量经济学规范

When generating econometric code for `EconometricsAgent`:

- Default to OLS with heteroskedasticity-robust standard errors (`cov_type='HC3'`)
- Always report: coefficient, standard error, t-statistic, p-value, 95% CI
- For causal identification, prefer: IV/2SLS, DiD, RDD, or matching
- Include first-stage F-statistics for IV regressions
- Export tables to `outputs/tables/` in both `.tex` and `.csv` formats
- Save all figures to `outputs/figures/` as `.png` (300 dpi) and `.pdf`

```python
# Example regression pattern
import statsmodels.api as sm

model = sm.OLS(y, sm.add_constant(X))
results = model.fit(cov_type='HC3')
state.log(f"OLS regression: N={len(y)}, R²={results.rsquared:.4f}")
```

---

## Working Paper Conventions | 工作论文规范

Working papers follow this naming and numbering convention:

- **File name**: `hler_wp_NNN.pdf` (zero-padded 3-digit number)
- **Title line**: `Human-in-the-Loop Economic Research Working Papers No. NNN`
- **Sections**: Abstract, Introduction, Data, Methodology, Results, Discussion, Conclusion, References
- **Language**: Bilingual sections are encouraged (English primary, Chinese annotation)

When generating manuscript drafts with `PaperAgent`:

- Use the template at `papers/templates/working_paper.md`
- Populate all placeholders before outputting the draft
- Do not fabricate citations or results

---

## Research Scope | 可辅助的研究领域

Copilot should be especially helpful with code and analysis in:

- Labor Economics (wage equations, employment transitions)
- Health and Human Capital (health production functions, returns to education)
- Agricultural and Development Economics (yield models, treatment effects)
- Behavioral Economics (choice models, nudge experiments)
- Genoeconomics (PRS construction, gene-environment interactions)

---

## Security and Ethics | 安全与伦理

- Never generate code that exposes PII or individual-level data in outputs
- Aggregate all reported statistics to at least cell size N ≥ 5
- Do not generate fabricated data or synthetic results presented as real
- Respect data use agreements; flag if a requested operation may violate DUA terms

---

## File Structure Reference | 文件结构参考

```
agents/
  base_agent.py          # BaseAgent abstract class
  orchestrator.py        # RunState owner, stage dispatcher
  data_audit_agent.py    # Stage: DATA_AUDIT
  question_agent.py      # Stage: QUESTIONING
  data_agent.py          # Stage: DATA_COLLECTION
  econometrics_agent.py  # Stage: ANALYSIS
  paper_agent.py         # Stage: WRITING
  reviewer_agent.py      # Stage: REVIEW
config/
  run_state.py           # RunState class definition
  pipeline_config.yaml   # Stage order and gate configuration
papers/templates/
  working_paper.md       # Manuscript template
outputs/
  figures/               # .png and .pdf charts
  tables/                # .tex and .csv regression tables
  manuscripts/           # Draft working papers
```
