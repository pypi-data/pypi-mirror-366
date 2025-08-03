# Stanlee

Stanlee is a simple collection of AI agents that are in use on a daily basis. These consist of financial assistants, news reporters, paper readers - and more! The library is meant to cover comprehensive use cases - from Claude Code SDK to multiple LLM providers. Stanlee also comes with a front end - also built from scratch. 

The backend consists of Python, for the wider support of libraries.

## Installation

```bash
pip install stanlee
```

or with uv:

```bash
uv add stanlee
```

## Usage

```python
from stanlee import Agent, Tool

# Create and use your agent
agent = Agent(name="MyAgent")
```