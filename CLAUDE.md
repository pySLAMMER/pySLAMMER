# Claude Code Guidelines for pySLAMMER

## Testing Conventions

### Avoid Test Redundancy
- **Parent class tests** should cover all base functionality thoroughly
- **Child class tests** should focus only on:
  - Child-specific implementations (`__str__`, `__repr__`, new methods)
  - Integration points where child extends/overrides parent behavior
  - Critical inherited behavior that must work correctly
- **Don't test** basic parent functionality that's already covered in parent tests

### Test Organization
- Use pytest fixtures for reusable test data
- Follow naming pattern: `test_<functionality>`
- Include docstrings explaining what each test validates

## Code Style

### Type Hints
- Always add type hints to function signatures, especially for public APIs
- Use `Optional[Type]` for optional parameters
- Import types: `from typing import Optional, Union`

### Documentation
- Keep docstrings concise but informative
- Focus on what the function/class does, not how
- Include parameter types in docstrings

## Project Structure

### Import Organization
- Standard library imports first
- Third-party imports second  
- Local imports last
- Use relative imports for local modules: `from .module import Class`
