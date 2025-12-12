# Oops - Open Source Offensive Security Agent

Oops is a high-end, autonomous Red Team Orchestrator built on the **Strands Agents** framework using the **"Agents as Tools"** pattern.

## Architecture

The system mimics a human security team structure:

1.  **Orchestrator Agent**: The Lead. Coordinates the assessment.
2.  **Scope Agent** (Tool): The Legal/Compliance Officer. Defines Rules of Engagement.
3.  **Intel Agent** (Tool): The Recon Specialist. Gathers asset information.
4.  **Plan Agent** (Tool): The Strategist. Develops the attack vectors.

## Project Structure

```
oops/
├── src/
│   ├── agents/
│   │   ├── orchestrator.py  # Main Agent
│   │   ├── scope_agent.py   # Scope Tool
│   │   ├── intel_agent.py   # Intel Tool
│   │   └── plan_agent.py    # Plan Tool
│   ├── tools/
│   │   └── file_ops.py      # File I/O for agents
│   └── main.py              # Entry point
├── output/                  # Generated Reports (scope.md, intel.md, plan.md)
└── requirements.txt
```

## Setup & Usage

1.  **Install Dependencies**:
    Ensure you have [Poetry](https://python-poetry.org/) installed.
    ```bash
    poetry install
    ```

2.  **Configure Environment**:
    - Copy `.env.example` to `.env` in the `oops` directory.
    - Add your API Key (e.g., `LLM_API_KEY`) and other config.

3.  **Run Oops**:
    ```bash
    poetry run python oops/src/main.py
    ```

4.  **Interact**:
    - Describe your target and request.
    - Example: _"Run a red team assessment on example.com"_

## Output
The agents will generate the following artifacts in the `output/` directory:
- `scope.md`: Defined ROE.
- `intel.md`: Reconnaissance data.
- `plan.md`: Attack strategy.
