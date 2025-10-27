# Contributing to Phelomia 🤝

Thank you for your interest in contributing to Phelomia! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Git
- Basic knowledge of machine learning and document processing

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/your-username/Phelomia.git
cd Phelomia

# Set up development environment
./setup.sh

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests to ensure everything works
pytest tests/
```

## 📋 How to Contribute

### 1. Find an Issue
- Browse [open issues](https://github.com/Saksham932007/Phelomia/issues)
- Look for issues labeled `good first issue` or `help wanted`
- Comment on the issue to let others know you're working on it

### 2. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number
```

### 3. Make Your Changes
- Write clean, documented code
- Follow the existing code style
- Add tests for new functionality
- Update documentation as needed

### 4. Test Your Changes
```bash
# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run linting
flake8 src/
black src/

# Check type hints
mypy src/
```

### 5. Submit a Pull Request
- Push your branch to your fork
- Create a pull request with a clear description
- Link to any related issues
- Wait for review and feedback

## 🔧 Development Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions small and focused

### Documentation
- Update README.md for user-facing changes
- Add docstrings for all new functions
- Include examples in docstrings
- Update configuration documentation

### Testing
- Write tests for all new functionality
- Maintain test coverage above 80%
- Use descriptive test names
- Include both positive and negative test cases

### Commit Messages
Use conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/modifications
- `chore`: Maintenance tasks

Examples:
```
feat(ui): add batch processing interface
fix(detector): resolve table detection edge case
docs(readme): update installation instructions
```

## 🎯 Areas for Contribution

### High Priority
- 🐛 **Bug Fixes**: Address reported issues
- 📚 **Documentation**: Improve guides and examples
- 🧪 **Testing**: Increase test coverage
- ♿ **Accessibility**: Improve UI accessibility

### New Features
- 🔌 **Plugin System**: Create extensible architecture
- 🌐 **API Endpoints**: Add REST API functionality
- 📱 **Mobile Support**: Improve mobile experience
- 🔒 **Security**: Add authentication and authorization

### Performance
- ⚡ **Optimization**: Improve processing speed
- 💾 **Memory Management**: Reduce memory usage
- 📊 **Monitoring**: Add performance metrics
- 🚀 **Caching**: Implement intelligent caching

## 📝 Issue Guidelines

### Bug Reports
When reporting bugs, include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Error messages and logs
- Screenshots if applicable

### Feature Requests
When requesting features, include:
- Clear description of the feature
- Use case and motivation
- Proposed implementation approach
- Examples of similar features elsewhere

## 🏷️ Labels

We use these labels to organize issues and PRs:

**Type Labels**
- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Documentation improvements
- `question`: Further information is requested

**Priority Labels**
- `critical`: Needs immediate attention
- `high`: Important issue
- `medium`: Standard priority
- `low`: Nice to have

**Status Labels**
- `help wanted`: Good for contributors
- `good first issue`: Good for newcomers
- `in progress`: Currently being worked on
- `needs review`: Ready for code review

## 🎉 Recognition

Contributors will be:
- Added to the CONTRIBUTORS.md file
- Mentioned in release notes for significant contributions
- Invited to join the core team for sustained contributions

## 📞 Getting Help

### Discord Community
Join our [Discord server](https://discord.gg/phelomia) for:
- Real-time discussions
- Development help
- Feature brainstorming
- Community support

### GitHub Discussions
Use [GitHub Discussions](https://github.com/Saksham932007/Phelomia/discussions) for:
- General questions
- Feature discussions
- Show and tell
- Ideas and suggestions

### Direct Contact
For sensitive issues:
- Email: contributors@phelomia.com
- Maintainer: [@Saksham932007](https://github.com/Saksham932007)

## 🏆 Contributor Guidelines

### Be Respectful
- Use inclusive language
- Be patient with newcomers
- Provide constructive feedback
- Respect different perspectives

### Be Collaborative
- Communicate clearly and early
- Ask for help when needed
- Share knowledge and insights
- Help review others' contributions

### Be Professional
- Follow the code of conduct
- Meet commitments and deadlines
- Document your work thoroughly
- Test your changes before submitting

## 📄 Code of Conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/) Code of Conduct. By participating, you are expected to uphold this code.

### Our Pledge
We are committed to making participation in this project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Quick Summary
- Be respectful and inclusive
- No harassment or discrimination
- Focus on constructive feedback
- Report inappropriate behavior

## 🙏 Thank You

Your contributions make Phelomia better for everyone. Whether you're fixing a typo, adding a feature, or helping with documentation, every contribution is valuable and appreciated!

---

**Happy Contributing! 🎉**