# Contributing to Research AI

Thank you for your interest in contributing to the Research Crew AI project! This document provides guidelines and instructions for contributing to this project.

## Ways to Contribute

There are several ways you can contribute to this project:

1. **Bug Reports**: Report bugs or issues through GitHub issues.
2. **Feature Requests**: Suggest new features or improvements.
3. **Code Contributions**: Submit pull requests for bug fixes or new features.
4. **Documentation**: Help improve or expand the documentation.
5. **Testing**: Test the application and provide feedback.

## Getting Started

1. Fork the repository on GitHub.
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/Research-Crew-AI-project.git
   cd Research-Crew-AI-project
   ```
3. Create a new branch for your work:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

1. Set up a virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

2. Install the development dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy the `.env.example` to `.env` and add your API keys:
   ```bash
   cp .env.example .env
   # Edit the .env file with your API keys
   ```

## Submitting Changes

1. Make your changes in your branch.
2. Test your changes thoroughly.
3. Commit your changes with a descriptive commit message:
   ```bash
   git commit -am "Add a concise description of your changes"
   ```
4. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
5. Submit a pull request to the main repository.

## Pull Request Guidelines

- Give your PR a descriptive title.
- Provide a detailed description of the changes made.
- Reference any relevant issues (e.g., "Fixes #123").
- Ensure all automated tests pass.
- Make sure your code follows the project's coding standards.

## Code Style Guidelines

- Follow PEP 8 style guidelines for Python code.
- Use descriptive variable and function names.
- Include comments where necessary to explain complex logic.
- Add docstrings to all functions, classes, and modules.

## License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project (MIT License).

## Contact

If you have any questions or need help, please open an issue on GitHub or contact the maintainers directly.

Thank you for contributing to Research Crew AI!
