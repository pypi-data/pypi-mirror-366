# Getting Started with IsoPrompt

## Installation

Install IsoPrompt using pip:

```bash
pip install isoprompt
```

## Basic Usage

```python
from isoprompt import optimize_prompt

# Simple prompt optimization
prompt = optimize_prompt("Write a blog post about AI")
print(prompt)
```

## Optimization Modes

IsoPrompt supports various optimization modes:

```python
from isoprompt import optimize_prompt, get_available_modes

# List available modes
modes = get_available_modes()
print(modes)

# Use a specific mode
prompt = optimize_prompt(
    "Write a technical spec",
    mode="analytical"
)
```

## Domain Specialization

```python
from isoprompt import optimize_prompt, get_available_domains

# List available domains
domains = get_available_domains()
print(domains)

# Use a specific domain
prompt = optimize_prompt(
    "Write a technical specification",
    domain="technology"
)
```

## Configuration

IsoPrompt can be configured using a JSON file:

```json
{
  "mode": "analytical",
  "domain": "technology",
  "temperature": 0.7,
  "model": "gpt-4"
}
```
