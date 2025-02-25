# Contributing to LLM Catcher

Thank you for considering contributing to LLM Catcher! We welcome contributions from the community and are excited to collaborate with you.

## How to Contribute

1. **Fork the Repository**: Start by forking the repository to your own GitHub account.

2. **Clone Your Fork**: Clone your forked repository to your local machine.

   ```bash
   git clone https://github.com/your-username/llm-catcher.git
   cd llm-catcher
   ```

3. **Create a Branch**: Create a new branch for your feature or bug fix.

   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make Changes**: Implement your changes, ensuring you follow the project's coding standards and guidelines.

5. **Test Your Changes**: Run the existing tests and add new tests if necessary to cover your changes.

6. **Commit Your Changes**: Commit your changes with a clear and descriptive commit message.

   ```bash
   git commit -m "Add feature: your feature description"
   ```

7. **Push to Your Fork**: Push your changes to your forked repository.

   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request**: Go to the original repository and create a pull request from your forked branch.

## Code of Conduct

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project, you agree to abide by its terms.

## Reporting Issues

If you encounter any issues or have questions, please feel free to open an issue on GitHub. We appreciate your feedback and will do our best to address any concerns.

## Thank You!

Thank you for your interest in contributing to LLM Catcher. We look forward to your contributions and appreciate your support in making this project better!

## Development Setup

1. **Set up your development environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -e ".[dev]"   # This will install the package and development dependencies
   ```

Note: The `[dev]` extra includes pytest, flake8, and other development tools needed for contributing to the project.

2. **Install development dependencies**:
   ```bash
   pip install pytest flake8
   ```

## Testing

Run the test suite:
```bash
# Using the test script
./scripts/test.sh

# Or directly with pytest
pytest tests/ -v
```

## Code Style

We use flake8 for linting. Check your code style with:
```bash
# Using the lint script
./scripts/lint.sh

# Or directly with flake8
flake8 . --count --max-line-length=128 --statistics
```