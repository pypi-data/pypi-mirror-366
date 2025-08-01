# SpeedBuild

**Stop rebuilding what already works.**

SpeedBuild extracts, adapts, and deploys battle-tested features from existing codebases to new projects—complete with all dependencies, configurations, and framework integrations.

[![Alpha Launch](https://img.shields.io/badge/Status-Alpha%20Launch-orange)](https://speedbuild.dev)
[![Open Source](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Django](https://img.shields.io/badge/Framework-Django-092E20?logo=django)](https://djangoproject.com)

## The Problem

Developers spend 80% of their time rebuilding features that already exist in proven, production-ready form elsewhere. User authentication, payment processing, CRUD operations—how many times have you built these from scratch?

AI tools generate code fast, but it breaks when real users touch it. You end up spending more time debugging than the AI saved you.

## The SpeedBuild Solution

Extract proven features from existing projects and safely adapt them to new ones:

```bash
# Extract a complete user authentication system
speedbuild extract shop/views.py auth

# Deploy it to a new project with adaptations
speedbuild deploy auth 
```

## How It Works

### 1. **Extract Complete Features**
Our AST-powered engine traces every dependency of a feature—from database models to middleware configurations—ensuring nothing is missed.

### 2. **Adapt with AI** 
Describe your requirements in plain English. SpeedBuild intelligently modifies the extracted code to fit your project's architecture.

### 3. **Deploy Production-Ready Code**
Get complete, working features with proper package installations, configurations, and framework integrations.

## Features

- 🔧 **Complete Feature Extraction** - Logic, configs, middleware, dependencies
- 🤖 **AI-Powered Adaptation** - Modify features using natural language
- 🚀 **One-Command Deployment** - Drop in production-ready features instantly
- 🏗️ **Architecture Aware** - Preserves your project structure and patterns
- 🔒 **Security Focused** - Battle-tested code with proven security patterns
- 📦 **Framework Intelligence** - Deep Django understanding (Flask, FastAPI coming soon)

## Quick Start

### Installation

```bash
pip install speedbuild
```

### Basic Usage

```bash
# Move into project that you want to extract or deploy to directory
cd <django_project_path>

# Extract a feature from an existing codebase
speedbuild extract user-management

# Deploy to your current project
speedbuild deploy user-management

# Adapt a feature before deployment
speedbuild deploy user-management --adapt "add email verification and password reset"
```

### Example: Adding Authentication

```bash
# Extract proven auth system
speedbuild extract auth --from https://github.com/example/django-saas

# Deploy with customizations
speedbuild deploy auth --adapt "
- Add Google OAuth integration
- Use custom User model with profile fields
- Include password strength validation
"
```

## Supported Frameworks

- ✅ **Django** - Full support
- 🚧 **Flask** - Coming Q3 2025
- 🚧 **FastAPI** - Coming Q3 2025

## SpeedBuild Cloud (Coming Soon)

- 🌐 **Public Template Repository** - Community-driven feature marketplace
- 🔍 **AI-Powered Search** - Find the perfect feature with semantic search
- 👥 **Team Collaboration** - Private templates for your organization
- 📊 **Usage Analytics** - Track feature adoption and performance

## Why SpeedBuild?

### vs. Copy-Paste Development
- **SpeedBuild**: Complete features with all dependencies
- **Copy-Paste**: Missing configs, broken imports, hours of debugging

### vs. AI Code Generation
- **SpeedBuild**: Battle-tested, production-proven features
- **AI Generation**: Untested code that breaks under load

### vs. Starting from Scratch
- **SpeedBuild**: Deploy in minutes with proven patterns
- **From Scratch**: Days of development, repeated mistakes

## Contributing

We welcome contributions! SpeedBuild is open source and community-driven.

### Development Setup

```bash
git clone https://github.com/speedbuild/speedbuild.git
cd speedbuild
pip install -r requirements.txt

#run as package
python -m speedbuild.sb
```

### Contributing Templates

Have a proven feature that others could benefit from? Contribute it to our public repository:

```bash
speedbuild contribute my-feature --public --description "Production-ready user authentication with social login"
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## Roadmap

- **Q2 2025**: Django support, CLI tool, template extraction
- **Q3 2025**: Flask/FastAPI support, SpeedBuild Cloud betax,MCP server integration
- **Q4 2025**: Multi-language ecosystem, enterprise features

## License

MIT License. See [LICENSE](LICENSE) for details.

## Support
<!-- - 💬 **Discord**: [Join our community](https://discord.gg/speedbuild) -->

- 📖 **Documentation**: [app.speedbuild.dev/doc](https://app.speedbuild.dev/doc)
- 🐛 **Issues**: [GitHub Issues](https://github.com/EmmanuelAttah1/speedbuild/issues)
- 📧 **Email**: hello@speedbuild.dev

## Alpha Launch

SpeedBuild is launching in alpha! [Sign up for early access](https://app.speedbuild.dev/register) and help us build the future of code reuse.

---

**Built by developers, for developers.** Stop rebuilding. Start reusing.

[Get Started](https://speedbuild.dev) • [Documentation](https://app.speedbuild.dev/doc) • [Community](https://discord.gg/speedbuild)