# Contributing to Rank Torrent Name (RTN)

Thank you for considering a contribution to RTN! This document provides guidelines and instructions for contributing to this project. By contributing, you agree to abide by our community norms and conduct.

## Getting Started

### Setup Environment

1. **Fork and Clone the Repository**: Start by forking the project repository, then clone your fork and enter the project directory:

```bash
git clone https://github.com/dreulavelle/rank-torrent-name.git
cd rank-torrent-name
```

2. **Install Poetry**: RTN uses Poetry for dependency management. Ensure you have Poetry installed by following the [official instructions](https://python-poetry.org/docs/#installation).

3. **Install Dependencies**: Install the project dependencies with Poetry:

```bash
poetry install --with dev
```

### Making Changes

- Create a new branch for your changes:

```bash
git switch -c <branch-name>
```

- Make your changes, ensuring you adhere to the project's coding standards and practices.

### Testing and Linting

Before submitting your changes, run the tests and ensure your code passes all lint checks:

- **Run Tests**:

```bash
make test
```

- **Check Code Style**:

```bash
make lint
```

- **Check Coverage**
```bash
make coverage
```

### Performance Benchmarking

RTN uses `pyperf` for performance benchmarking. If your changes could impact performance, please run the benchmarks:

```bash
make benchmark
```

Include the benchmark results in your pull request if relevant.

### Committing Your Changes

- We try to follow [Conventional Commits](https://www.conventionalcommits.org/) specs.
- Commit your changes with a clear and descriptive commit message.
- Push your changes to your fork:

```bash
git push origin <branch-name>
```

### Submitting a Pull Request

- Go to the GitHub page of the original RTN repository.
- Click on the "Pull requests" tab and then the "New pull request" button.
- Choose your fork and branch with the changes, then click "Create pull request".
- Provide a clear and detailed description of the changes and the reasons behind them.

## Community and Conduct

We strive to maintain a welcoming and inclusive community. All contributors are expected to adhere to our Code of Conduct (link to your code of conduct here).

## Questions and Support

If you have any questions or need help with your setup, feel free to open an issue for discussion or assistance.

---

Thank you for contributing to RTN! Your efforts help make this project better for everyone.
