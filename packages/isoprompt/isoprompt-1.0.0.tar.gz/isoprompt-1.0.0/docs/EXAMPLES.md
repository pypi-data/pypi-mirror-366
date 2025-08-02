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

## CLI Usage

```bash
# Basic usage
isoprompt --prompt "Write a blog post about AI"

# With mode and domain
isoprompt --prompt "Write a technical spec" --mode analytical --domain technology
```
