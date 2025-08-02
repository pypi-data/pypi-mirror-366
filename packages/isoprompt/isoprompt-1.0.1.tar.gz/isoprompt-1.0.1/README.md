# IsoPrompt

IsoPrompt [`isoprompt`] offers prompt optimization via a simple, user-friendly CLI and programmable API SDK.

[![PyPI version](https://img.shields.io/pypi/v/isoprompt.svg)](https://pypi.org/project/isoprompt/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 🎯 **Optimizes prompts** for better results.
- 🔧 **Domain-specific tuning** for various fields.
- 🛠 **Multiple optimization modes** for different use cases.
- 📚 **Rich documentation** and examples.
- 🧪 **Test-driven development** with high coverage.
- 🔒 **Type-safe** with full type hints.

## Quick Start

```python
from isoprompt import optimize_prompt

prompt = "Write a blog post about AI"
optimized = optimize_prompt(prompt)
print(optimized)
```

Or via CLI:

```bash
isoprompt --prompt "Generate a fitness plan for students."
```

## Installation

```bash
pip install isoprompt
```

## Documentation

- [Getting Started](https://github.com/thehackersplaybook/isoprompt/blob/main/docs/GETTING_STARTED.md).
- [API Reference](https://github.com/thehackersplaybook/isoprompt/blob/main/docs/API_REFERENCE.md).
- [Examples](https://github.com/thehackersplaybook/isoprompt/blob/main/docs/EXAMPLES.md).

## Changelog

### v1.0.1

- Initial public release on PyPI.
- Renamed package to isoprompt.
- Added comprehensive documentation.
- Added type hints and py.typed marker.

## License

MIT License - see [LICENSE](https://github.com/thehackersplaybook/isoprompt/blob/main/LICENSE) for details.
