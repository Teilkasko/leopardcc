# LEOpARD-CC

LLM-Enabled Operations for Assured Refactoring to Decrease Cyclomatic Complexity

<img src="img/logo.jpeg" alt="Leopard eating code" width="200"/>

[Download thesis fulltext document](https://mega.nz/file/xEhEmC5R#t3jDlmMYkG3KFoa4yu4NVyNqrF_NDC4EkWvYVC2Ih0k)

[Download replication package](https://mega.nz/file/4J4RFC4S#1eEIuKRidTEbfLpSEN9r4Ais-dQCIKYrbBpgPES1SwE)

## About

LEOpARD-CC is the first open-source tool for LLM-driven JavaScript refactoring, developed as part of a Master's thesis. It automatically reduces the cyclomatic complexity of JavaScript functions by iteratively prompting a large language model, then verifying the result against linting rules and tests before accepting any change.

The tool was evaluated on four widely used open-source JavaScript projects — **Day.js**, **Express**, **JSON5**, and **Ramda**.

## Approach

For each of the most complex functions in a project (ranked by cyclomatic complexity via [Lizard](https://github.com/terryyin/lizard)):

1. The LLM is asked to refactor the function using a configurable prompt strategy.
2. The refactored code is checked with ESLint; any linting errors are fed back to the LLM for correction.
3. The project's test suite is run; failing tests are similarly fed back for correction.
4. If complexity is not reduced, the LLM is asked to try again.
5. If the function passes all checks and is genuinely simpler, the change is applied.

Results are written to a timestamped CSV log for analysis.

## Components

| Component                  | Description                                                                                                 |
| -------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `Script.py`                | Entry point — configures and runs the refactoring loop                                                      |
| `Refactorer.py`            | Orchestrates a single function's refactoring and verification steps                                         |
| `llm_wrappers/`            | LLM client (wraps the OpenAI API)                                                                           |
| `prompt_strategies/`       | Two prompt strategies: `ChoiEtAl` and `Scheibe`                                                             |
| `verification_strategies/` | Verification logic (lint check → test run → complexity check)                                               |
| `projects/`                | Per-project configuration (paths, lint command, test command) for Day.js, Express, JSON5, Ramda, and others |
| `helpers/`                 | Utilities for Lizard (complexity), Git (diff/patch), and project setup                                      |
| `interfaces/`              | Shared data types and abstract base classes                                                                 |
| `util/`                    | CSV output and logging                                                                                      |

**Key dependencies:**

- [openai](https://github.com/openai/openai-python) — LLM calls via the OpenAI API
- [lizard](https://github.com/terryyin/lizard) — static cyclomatic complexity analysis
- [GitPython](https://gitpython.readthedocs.io) — saving diffs and managing target-project copies
- ESLint and Jest are invoked via `npx` on the target JavaScript projects

## Setup

**Prerequisites:** Python 3.11+, Node.js (for ESLint/Jest on the target projects)

1. Clone this repository and install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Place your OpenAI API key in a file called `openai-key.txt` in the project root:

   ```bash
   echo "sk-..." > openai-key.txt
   ```

3. Clone the JavaScript project(s) you want to refactor and update the paths in the corresponding file under `projects/` (e.g. `projects/Dayjs.py`).

## Running

Open `Script.py` and adjust the `main()` call at the bottom to select a project, prompt strategy, verification strategy, and model:

```python
main(
    project=Dayjs(),
    prompt_strategy=ChoiEtAlPrompt(),        # or Scheibe()
    verification_strategy=ChoiEtAlVerification(),
    model="gpt-4o-mini"
)
```

Then run:

```bash
python Script.py
```

Logs and per-iteration CSV results are written to `logs/<timestamp>-<project>/`.
