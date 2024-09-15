# Contributing to Rank Torrent Name (RTN)

We're thrilled you're considering contributing to RTN! This comprehensive guide will walk you through the process of setting up your development environment, making changes, and submitting your contributions. By participating, you agree to adhere to our community norms and code of conduct.

## Getting Started

### Setting Up Your Development Environment

1. **Fork and Clone the Repository**:
   Start by forking the RTN repository on GitHub. Then, clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/rank-torrent-name.git
   cd rank-torrent-name
   ```

2. **Install Poetry**:
   RTN uses Poetry for dependency management. If you haven't already, install Poetry by following the [official installation guide](https://python-poetry.org/docs/#installation). Poetry provides a consistent and isolated environment for development.

3. **Install Project Dependencies**:
   With Poetry installed, set up your development environment:
   ```bash
   poetry install --with dev
   ```
   This command creates a virtual environment and installs all necessary dependencies, including development tools.

4. **Activate the Virtual Environment**:
   To work within the project's virtual environment, run:
   ```bash
   poetry shell
   ```

### Making Changes

1. **Create a New Branch**:
   Always create a new branch for your changes:
   ```bash
   git switch -c feature/your-feature-name
   ```
   Use a descriptive branch name that reflects the nature of your changes.

2. **Implement Your Changes**:
   Make your desired changes to the codebase. Be sure to:
   - Follow the project's coding style and conventions.
   - Write clear, commented code where necessary.
   - Update or add tests to cover your changes.
   - Update documentation if you're introducing new features or changing existing functionality.

### Testing and Quality Assurance

Before submitting your changes, ensure they meet our quality standards:

1. **Run Tests**:
   ```bash
   make test
   ```
   This command runs the project's test suite. All tests should pass before you submit your changes.

2. **Check Code Style**:
   ```bash
   make lint
   ```
   This runs our linting tools to ensure your code adheres to our style guidelines.

3. **Check Test Coverage**:
   ```bash
   make coverage
   ```
   Aim to maintain or improve the project's test coverage with your changes.

4. **Performance Benchmarking**:
   If your changes might impact performance, run our benchmarks:
   ```bash
   make benchmark
   ```
   Include these results in your pull request description if relevant.

### Committing Your Changes

1. **Follow Conventional Commits**:
   We use [Conventional Commits](https://www.conventionalcommits.org/) for clear and standardized commit messages. For example:

```
feat: add new ranking algorithm for improved accuracy
fix: resolve issue with parsing certain file formats
docs: update installation instructions in README
```

2. **Push Your Changes**:
   Push your branch to your fork on GitHub:
   ```bash
   git push origin feature/your-feature-name
   ```

### Submitting a Pull Request

1. Go to the [RTN GitHub repository](https://github.com/dreulavelle/rank-torrent-name).
2. Click "Pull requests" and then "New pull request".
3. Choose your fork and the branch containing your changes.
4. Click "Create pull request".
5. Provide a clear title and detailed description of your changes, including:
   - The problem you're solving
   - Your approach to the solution
   - Any potential impacts or considerations
   - Benchmark results, if applicable

## Getting Help

If you need assistance or have questions:

- Open an issue for bugs or feature discussions
- Join our [Discord community](https://discord.gg/rivenmedia) for real-time chat
- Check out the [FAQ](Users/FAQ.md) for common questions

---

Thank you for contributing to RTN! Your efforts help make this project better for everyone. We look forward to your contributions and are here to support you throughout the process.
