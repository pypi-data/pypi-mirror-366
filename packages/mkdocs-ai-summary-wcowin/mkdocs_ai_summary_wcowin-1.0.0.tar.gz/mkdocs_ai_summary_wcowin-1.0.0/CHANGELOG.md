# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of MkDocs AI Summary Plugin
- Support for multiple AI services (DeepSeek, OpenAI, Google Gemini, GLM)
- Intelligent caching system with configurable expiration
- Multi-language summary generation (Chinese and English)
- Flexible file and folder inclusion/exclusion patterns
- CI/CD integration with GitHub Actions support
- Environment variable configuration for API keys
- Fallback service mechanism for high availability
- Responsive summary card design
- Debug logging and error handling

### Changed
- N/A (Initial release)

### Deprecated
- N/A (Initial release)

### Removed
- N/A (Initial release)

### Fixed
- N/A (Initial release)

### Security
- Secure API key handling through environment variables
- No API keys stored in configuration files
- Safe content processing with length limits

## [1.0.0] - 2024-01-XX

### Added
- Initial stable release
- Core plugin functionality
- Documentation and examples
- PyPI package distribution
- Comprehensive test suite
- CI/CD pipeline setup

---

## Release Notes

### Version 1.0.0

This is the initial stable release of the MkDocs AI Summary Plugin. The plugin provides:

**Core Features:**
- Automatic AI-powered summary generation for MkDocs pages
- Support for multiple AI services with automatic fallback
- Intelligent caching to reduce API costs and improve performance
- Flexible configuration options for different use cases
- Seamless CI/CD integration

**Supported AI Services:**
- DeepSeek (deepseek-chat)
- OpenAI (gpt-3.5-turbo, gpt-4)
- Google Gemini (gemini-pro)
- GLM (glm-4)

**Key Benefits:**
- **Cost Effective**: Smart caching reduces API calls by up to 90%
- **Reliable**: Fallback mechanism ensures high availability
- **Flexible**: Fine-grained control over which pages get summaries
- **Developer Friendly**: Easy setup and configuration
- **Production Ready**: Optimized for CI/CD environments

**Getting Started:**
1. Install: `pip install mkdocs-ai-summary`
2. Configure in `mkdocs.yml`
3. Set API keys in `.env` file
4. Build your documentation: `mkdocs build`

For detailed installation and configuration instructions, see the [README](README.md).

**Migration from ai_summary.py:**
If you're migrating from the standalone `ai_summary.py` script, see our [Migration Guide](docs/migration.md) for step-by-step instructions.

**Community:**
- Report issues: [GitHub Issues](https://github.com/mkdocs-ai-summary/mkdocs-ai-summary/issues)
- Join discussions: [GitHub Discussions](https://github.com/mkdocs-ai-summary/mkdocs-ai-summary/discussions)
- Contribute: [Contributing Guide](CONTRIBUTING.md)

**What's Next:**
- Additional AI service integrations
- Enhanced summary customization options
- Performance optimizations
- Advanced caching strategies
- Plugin ecosystem integrations

Thank you for using MkDocs AI Summary Plugin!