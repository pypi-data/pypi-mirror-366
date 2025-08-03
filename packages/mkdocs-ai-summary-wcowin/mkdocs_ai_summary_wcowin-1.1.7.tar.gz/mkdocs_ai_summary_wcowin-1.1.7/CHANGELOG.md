# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.7] - 2025-08-03

### Added
- 

### Changed
- 

### Fixed
- 

### Removed
- 


## [1.1.6] - 2025-08-02

### Added
- 修改了 content_processor.py 中的 inject_summary 方法
- 智能定位第一个h1标题 ：使用正则表达式精确匹配 # 标题 格式
- 正确插入位置 ：摘要现在会插入到h1标题的下一行，而不是文档开头
- 保持兼容性 ：如果没有h1标题，仍会在文档开头显示摘要

### Changed
- 

### Fixed
- 

### Removed
- 


## [1.1.5] - 2025-08-02

### Added
- README.md （英文版）和 README_ZH.md （中文版）
- 重新组织文档结构，突出核心功能
- 简化配置示例，保留最常用的配置选项
- 优化快速开始部分，让用户能够快速上手

### Changed
- 

### Fixed
- 修改了 get_content_hash 方法，只基于文件路径和语言生成哈希
- 移除了内容参数对哈希生成的影响，确保缓存文件名的稳定性
- 保证同一文件始终对应同一个缓存文件

### Removed
- 


## [1.1.4] - 2025-08-02

### Added
- 

### Changed
- 

### Fixed
- 

### Removed
- 


## [1.1.3] - 2025-08-02

### Added
- 简化了AI服务调用过程中的冗余日志
- 避免了相同信息的多次显示

### Changed
- 

### Fixed
- 

### Removed
- 删除了 format_summary 方法中的重复输出


## [1.1.2] - 2025-08-02

### Added
- 

### Changed
- 

### Fixed
- 

### Removed
- 


## [1.1.1] - 2025-08-02

### Added
- 

### Changed
- 

### Fixed
- 

### Removed
- 


## [1.1.0] - 2025-08-02

### Added
- 

### Changed
- 

### Fixed
- 

### Removed
- 


## [1.0.9] - 2025-08-02

### Added
- Enhanced front matter parsing with support for multiple YAML formats
- Detailed debug logging for front matter parsing and language detection
- Test script for validating front matter parsing functionality

### Changed
- Improved ContentProcessor initialization to accept debug parameter
- Enhanced get_page_language method with comprehensive debug output

### Fixed
- Fixed front matter parsing regex to handle various YAML front matter formats
- Resolved issue where ai_summary_lang configuration in page front matter was not being recognized
- Fixed page-level language override functionality for English summaries

### Removed
- 


## [1.0.8] - 2025-08-02

### Added
- 

### Changed
- 

### Fixed
- 

### Removed
- 


## [1.0.7] - 2025-08-02

### Added
- 

### Changed
- 

### Fixed
- 

### Removed
- 


## [1.0.6] - 2025-01-03

### Added
- Added `debug` configuration option to control debug output display
- Debug output can now be controlled via `debug: true/false` in mkdocs.yml
- Enhanced debugging documentation with practical examples

### Changed
- All debug print statements are now conditional based on debug configuration
- Debug output is disabled by default (debug: false) for cleaner terminal output
- Updated configuration examples in README files to include debug option

### Fixed
- Reduced terminal noise by making debug information optional
- Improved user experience with cleaner build output when debug is disabled

## [1.0.5] - 2025-08-02

### Added
- 

### Changed
- 

### Fixed
- 

### Removed
- 


## [1.0.4] - 2025-08-02

### Added
- 

### Changed
- 

### Fixed
- 

### Removed
- 


## [1.0.3] - 2025-08-02

### Added
- 

### Changed
- 

### Fixed
- 

### Removed
- 


## [1.0.2] - 2025-01-02

### Fixed
- Fixed configuration parameter recognition issues for users upgrading from older versions
- Ensured all configuration parameters (ai_service, summary_language, cache_enabled, cache_expire_days, enabled_folders, exclude_patterns) are properly defined in config_scheme
- Improved plugin compatibility with existing MkDocs configurations

### Changed
- Updated version references across all files to maintain consistency


## [Unreleased]

### Added
- TBD

### Changed
- TBD

### Fixed
- TBD

## [1.0.1] - 2024-01-XX

### Fixed
- Fixed configuration parameter mismatch between `ci_fallback` and `ci_fallback_summary`
- Updated repository URLs to correct GitHub repository
- Improved method call consistency across modules

### Changed
- Updated all version references to 1.0.1
- Standardized configuration parameter naming

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