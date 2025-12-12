<p align="center">
  <a href="https://github.com/lianstemp/Oops">
    <img src="https://img.shields.io/badge/Oops-Red_Team_Orchestrator-DC143C?style=for-the-badge&logo=kalilinux&logoColor=white" alt="Oops Logo">
  </a>
</p>

<p align="center">
  The Open Source Offensive Security Agent.
</p>

<p align="center">
  <a href="https://github.com/lianstemp/Oops/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/badge/License-MIT-blue?style=flat" /></a>
  <a href="https://python-poetry.org/"><img alt="Poetry" src="https://img.shields.io/badge/managed_by-Poetry-blueviolet?style=flat" /></a>
  <a href="https://www.python.org/"><img alt="Python" src="https://img.shields.io/badge/Python-3.10+-yellow?style=flat" /></a>
  <a href="https://strandsagents.com"><img alt="Strands Agents" src="https://img.shields.io/badge/Powered_by-Strands_Agents-orange?style=flat" /></a>
</p>

---

### Installation

```bash
# Clone the repository
git clone https://github.com/lianstemp/Oops.git
cd Oops

# Install dependencies with Poetry
poetry install
```

### Configuration

Copy the example environment file and configure your LLM provider.

```bash
cp .env.example .env
```

Edit `.env` to set your `LLM_API_KEY`, `LLM_BASE_URL`, and `LLM_MODEL`.

### Usage

Start the interactive orchestrator:

```bash
poetry run python src/main.py
```

### Workflow

Oops follows a strict 3-phase workflow to ensure safe and authorized assessments:

1. **Scope** - Defines the Rules of Engagement (ROE) and verifies target ownership via DNS/IP validation.
2. **Intel** - Performs passive and active reconnaissance (headers, tech stack) on authorized assets.
3. **Plan** - Analyze gathered data to map potential attack vectors and required tools.

### Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

### License

[MIT](https://choosealicense.com/licenses/mit/)
