# Contributing to fz-casmo

Thank you for your interest in contributing to fz-casmo! This document provides guidelines for contributing to this project.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/fz-casmo.git
   cd fz-casmo
   ```
3. **Set up your environment**:
   - Install the fz framework: https://github.com/Funz/fz
   - Set CASMO_PATH to your CASMO5 installation (if available)

## Making Changes

1. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Follow the existing code style
   - Add comments where necessary
   - Update documentation if needed

3. **Test your changes**:
   - Run the example scripts if possible
   - Verify that existing functionality still works
   - Test with different parameter combinations

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request** on GitHub

## Types of Contributions

### Bug Reports
- Use the GitHub issue tracker
- Include steps to reproduce
- Provide sample input files if possible
- Include error messages and logs

### Feature Requests
- Describe the feature and its use case
- Explain why it would be useful
- Provide examples if possible

### Code Contributions
Areas where contributions are especially welcome:
- Additional output parsing options
- Support for different CASMO5 versions
- Example calculations for different reactor types (BWR, VVER, etc.)
- Documentation improvements
- Test cases

### Documentation
- Fix typos and clarify instructions
- Add examples and use cases
- Improve README or add tutorials

## Code Style

- Follow PEP 8 for Python code
- Use clear variable names
- Comment complex logic
- Keep functions focused and modular

## Model Configuration Guidelines

When modifying `.fz/models/CASMO.json`:
- Ensure output parsing commands work across different CASMO5 versions
- Document any assumptions about output format
- Provide examples of the expected output

## Calculator Script Guidelines

When modifying `.fz/calculators/CASMO.sh`:
- Maintain compatibility with different installation paths
- Handle edge cases (missing files, permissions, etc.)
- Provide clear error messages
- Document environment variable requirements

## Testing

While we don't have automated tests due to CASMO5 licensing restrictions:
1. Test with actual CASMO5 installations when possible
2. Verify that parameter substitution works correctly
3. Check output parsing with real CASMO5 output files
4. Test error handling (missing files, invalid parameters, etc.)

## Communication

- Use GitHub Issues for bugs and feature requests
- Be respectful and constructive in discussions
- Ask questions if you're unsure about anything

## License

By contributing, you agree that your contributions will be licensed under the BSD 3-Clause License.

## Questions?

Feel free to open an issue if you have questions about contributing!
