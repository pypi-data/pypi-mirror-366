# IsoPrompt Examples

## Basic Usage

```python
from isoprompt import optimize_prompt

# Simple prompt optimization
prompt = optimize_prompt("Write a blog post about AI")
print(prompt)
```

## Using Different Modes

```python
from isoprompt import optimize_prompt, get_available_modes

# List available modes
modes = get_available_modes()
print(modes)

# Use analytical mode
prompt = optimize_prompt(
    "Write a technical spec",
    mode="analytical",
    temperature=0.5
)
```

For more details about modes, see our [API Reference](https://github.com/thehackersplaybook/isoprompt/blob/main/docs/API_REFERENCE.md#modes).

## Domain Specialization

```python
from isoprompt import optimize_prompt, get_available_domains

# List available domains
domains = get_available_domains()
print(domains)

# Use technology domain
prompt = optimize_prompt(
    "Write a technical specification",
    domain="technology",
    mode="analytical"
)
```

For more details about domains, see our [API Reference](https://github.com/thehackersplaybook/isoprompt/blob/main/docs/API_REFERENCE.md#domains).

## CLI Usage

```bash
# Basic usage
isoprompt --prompt "Generate a fitness plan for students."

# With domain
isoprompt --prompt "Optimize supply chain" --domain logistics

# With mode
isoprompt --prompt "Marketing ideas" --mode creative

# With both
isoprompt --prompt "Technical spec" --mode analytical --domain technology
```

For more CLI options, see our [Getting Started](https://github.com/thehackersplaybook/isoprompt/blob/main/docs/GETTING_STARTED.md#cli-usage) guide.
