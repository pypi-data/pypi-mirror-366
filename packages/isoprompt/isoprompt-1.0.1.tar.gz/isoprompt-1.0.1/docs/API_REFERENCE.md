# IsoPrompt API Reference

## Core Functions

### optimize_prompt

```python
def optimize_prompt(
    user_input: str,
    mode: str = "simple",
    domain: Optional[str] = None,
    model: str = "gpt-4",
    temperature: float = 0.7,
    verbose: bool = False,
) -> str:
```

Optimize a user's basic prompt into a high-quality, production-ready prompt.

**Parameters:**

- `user_input`: The user's basic prompt or request
- `mode`: Optimization mode (simple, reasoning, chain_of_thought, creative, analytical)
- `domain`: Optional domain specialization
- `model`: OpenAI model to use for optimization
- `temperature`: Temperature for generation (lower = more focused)
- `verbose`: Whether to print verbose output

**Returns:**

- Optimized prompt string

For examples, see our [Examples](https://github.com/thehackersplaybook/isoprompt/blob/main/docs/EXAMPLES.md) documentation.

### get_available_modes

```python
def get_available_modes() -> List[IsoPromptMode]:
```

Get a list of available optimization modes.

**Returns:**

- List of IsoPromptMode objects

### get_available_domains

```python
def get_available_domains() -> List[IsoPromptDomain]:
```

Get a list of available domain specializations.

**Returns:**

- List of IsoPromptDomain objects

## Data Models

### IsoPromptMode

```python
class IsoPromptMode(BaseModel):
    name: str
    description: str
    examples: List[str]
    instructions: str
    parameters: Optional[Dict[str, str]] = None
```

A model representing an optimization mode.

### IsoPromptDomain

```python
class IsoPromptDomain(BaseModel):
    name: str
    description: str
    examples: List[str]
    instructions: str
    parameters: Optional[Dict[str, str]] = None
```

A model representing a domain specialization.

## CLI Usage

For CLI usage examples, see our [Getting Started](https://github.com/thehackersplaybook/isoprompt/blob/main/docs/GETTING_STARTED.md#cli-usage) guide.
