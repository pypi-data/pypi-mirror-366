# Changelog

## [1.0.3] - 2nd August 2025 1:20am IST.

- Update prompts.
- Bump default max tokens.

## [1.0.2] - 1st August 2025 11pm IST.

- Fix functional bugs and incorrect logic.

## [1.0.1] - 1st August 2025 9pm IST.

- Update broken links in README.

## [1.0.0] - 1st August 2025 4pm IST.

### Added.

- Core prompt optimization API with OpenAI integration.
- Multiple optimization modes for different use cases:
  - Simple mode for basic Q&A and instructions.
  - Reasoning mode for step-by-step logical thinking.
  - Chain-of-thought mode for complex analysis.
  - Creative mode for innovative content generation.
  - Conversational mode for natural dialogue.
  - Persuasive mode for sales and marketing.
  - Summarization mode for content condensation.
  - Critical review mode for analysis.
  - And many more! See `modes.py`.
- Domain specialization with 40+ specialized knowledge domains including:
  - Pure Sciences (Mathematics, Physics, Chemistry, etc.).
  - Engineering & Technology.
  - Medicine & Life Sciences.
  - Social Sciences & Humanities.
  - Business & Management.
  - Arts & Culture.
  - Environment & Sustainability.
  - Emerging Technologies.
  - And many more! See `domains.py`.
- Command-line interface with features:
  - Direct prompt input or file-based input/output.
  - Mode selection for optimization strategy.
  - Domain selection for specialized knowledge.
  - Temperature control for output variation.
  - Model selection flexibility.
- Python API for programmatic access:
  - `optimize_prompt()` for core functionality.
  - Domain and mode discovery functions.
  - Configuration validation.
- Type hints support (PEP 561 compliant).
- Comprehensive documentation:
  - API Reference.
  - Getting Started Guide.
  - Usage Examples.
- Modern Python packaging with pyproject.toml.

### Dependencies.

- Python >=3.8.
- OpenAI SDK >=1.0.0.
- Pydantic >=2.0.0.
- python-dotenv >=1.0.0.
