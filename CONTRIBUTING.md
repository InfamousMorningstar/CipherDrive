# Contributing to CipherDrive

Thank you for considering contributing to CipherDrive! We welcome contributions from the community.

## ⚠️ Alpha Development Notice

**Important**: CipherDrive is currently in alpha development. This means:

- Features may change rapidly without notice
- Breaking changes are common
- Code structure may be refactored frequently
- Documentation may be outdated

Please keep this in mind when contributing.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/InfamousMorningstar/CipherDrive/issues)
2. If not, create a new issue with:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - Environment details (OS, Docker version, etc.)

### Suggesting Features

1. Check [Discussions](https://github.com/InfamousMorningstar/CipherDrive/discussions) for similar ideas
2. Open a new discussion with:
   - Clear description of the feature
   - Use case and benefits
   - Possible implementation approach

### Contributing Code

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Test your changes thoroughly
5. Commit with clear messages
6. Push to your fork
7. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/CipherDrive.git
cd CipherDrive

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install

# Run development servers
# Backend: uvicorn main:app --reload
# Frontend: npm run dev
```

### Coding Standards

- **Python**: Follow PEP 8
- **JavaScript/React**: Use ESLint configuration
- **Commits**: Use conventional commit messages
- **Tests**: Include tests for new features
- **Documentation**: Update documentation for new features

### Pull Request Guidelines

- Provide clear description of changes
- Include screenshots for UI changes
- Ensure all tests pass
- Update documentation if needed
- Reference related issues

## Getting Help

- Join our [Discussions](https://github.com/InfamousMorningstar/CipherDrive/discussions)
- Check the [Wiki](https://github.com/InfamousMorningstar/CipherDrive/wiki)
- Review existing [Issues](https://github.com/InfamousMorningstar/CipherDrive/issues)

Thank you for contributing to CipherDrive!