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

For more examples, see our [Examples](https://github.com/thehackersplaybook/isoprompt/blob/main/docs/EXAMPLES.md) documentation.

## Domain Specialization

```python
from isoprompt import optimize_prompt, get_available_domains

# List available domains
domains = get_available_domains()
print(domains)

# Use a specific domain
prompt = optimize_prompt(
    "Write a technical specification",
    domain="technology",
    mode="analytical"
)
```

## API Reference

For detailed API documentation, see our [API Reference](https://github.com/thehackersplaybook/isoprompt/blob/main/docs/API_REFERENCE.md).
