# Contributing

Thank you for considering contributing to the Stream Deck library.

## Development Setup

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```
   The `requirements-dev.txt` file contains tools such as `flake8`, `bandit` and
   `mypy` used in continuous integration.

2. Run the code style and security checks:
   ```bash
   flake8 src
   bandit --ini .bandit -r src
   mypy --ignore-missing-imports src
   ```

3. Execute the unit tests using a dummy transport:
   ```bash
   pytest
   ```

Please ensure new code is covered by tests and the documentation is kept up to
date.
