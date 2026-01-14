# bugProwler 🐛🔍

A powerful and intelligent bug hunting and vulnerability scanner designed to help developers, security researchers, and DevOps teams identify and track security issues across their applications.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Configuration](#configuration)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

## Overview

bugProwler is a comprehensive vulnerability and bug detection tool that leverages advanced scanning techniques to identify security vulnerabilities, code quality issues, and potential bugs in your codebase. Whether you're a solo developer or part of a large security team, bugProwler provides the insights you need to maintain a secure application.

## Features

✨ **Core Capabilities:**

- 🔐 **Multi-Scanner Support** - Integration with multiple security scanning engines
- 🎯 **Precise Detection** - Advanced algorithms for accurate vulnerability identification
- 📊 **Detailed Reporting** - Comprehensive vulnerability reports with severity levels and remediation guidance
- 🔄 **Continuous Integration** - Seamless integration with CI/CD pipelines
- 🏷️ **Issue Tracking** - Built-in support for tagging and categorizing vulnerabilities
- ⚡ **High Performance** - Optimized scanning for quick results
- 🔌 **Extensible Architecture** - Easy to extend with custom scanners and plugins
- 📈 **Trend Analysis** - Track vulnerability trends over time
- 🛡️ **Multiple Severity Levels** - Prioritize issues by criticality (Critical, High, Medium, Low, Info)
- 💾 **Multiple Export Formats** - Export results in JSON, CSV, XML, and HTML formats

## Requirements

- **Python** 3.8 or higher
- **pip** (Python package manager)
- **Git** (for cloning the repository)
- **System Dependencies** (varies by platform):
  - Linux/macOS: Standard development tools
  - Windows: Python development headers

## Installation

### Method 1: Clone from GitHub (Recommended for Development)

```bash
# Clone the repository
git clone https://github.com/ivangrana/bugProwler.git
cd bugProwler

# Create a virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Method 2: Install from PyPI (Stable Release)

```bash
pip install bugprowler
```

### Method 3: Docker Installation

```bash
# Build Docker image
docker build -t bugprowler .

# Run in Docker container
docker run -v $(pwd):/workspace bugprowler scan /workspace
```

## Quick Start

### Basic Scan

```bash
# Scan current directory
bugprowler scan .

# Scan specific file
bugprowler scan path/to/file.py

# Scan with specific severity level
bugprowler scan . --min-severity high
```

### Generate Report

```bash
# Generate HTML report
bugprowler scan . --output report.html --format html

# Generate JSON report
bugprowler scan . --output results.json --format json
```

## Usage

### Command-Line Interface

```bash
bugprowler [COMMAND] [OPTIONS] [PATH]
```

### Available Commands

#### `scan`
Scan a directory or file for vulnerabilities.

```bash
bugprowler scan <path> [options]

Options:
  --recursive, -r           Scan directories recursively (default: true)
  --output, -o             Output file path for results
  --format, -f             Output format (json, csv, xml, html)
  --min-severity, -s       Minimum severity level (critical, high, medium, low, info)
  --exclude, -e            Exclude patterns (comma-separated)
  --config, -c             Configuration file path
  --verbose, -v            Enable verbose output
  --timeout, -t            Scan timeout in seconds
  --threads, -j            Number of parallel threads
```

#### `init`
Initialize a bugProwler configuration file.

```bash
bugprowler init [path]
```

#### `config`
Manage configuration settings.

```bash
bugprowler config [key] [value]
```

#### `version`
Display version information.

```bash
bugprowler version
```

## Configuration

### Configuration File

Create a `.bugprowler.yml` configuration file in your project root:

```yaml
# bugProwler Configuration

# Scan settings
scan:
  recursive: true
  timeout: 300
  threads: 4

# Severity levels to include
severity:
  critical: true
  high: true
  medium: true
  low: false
  info: false

# Exclude patterns
exclude:
  - node_modules/
  - venv/
  - .git/
  - __pycache__/
  - *.pyc
  - test/

# Scanners to enable
scanners:
  - python
  - dependency
  - secrets
  - code_quality

# Output settings
output:
  format: json
  directory: ./reports/
  include_timestamp: true

# Reporting
report:
  include_remediation: true
  include_references: true
  group_by_severity: true
```

### Environment Variables

```bash
# Set API key for external services (if applicable)
export BUGPROWLER_API_KEY=your_api_key

# Set log level
export BUGPROWLER_LOG_LEVEL=debug

# Set output directory
export BUGPROWLER_OUTPUT_DIR=/path/to/output
```

## Examples

### Example 1: Simple Directory Scan

```bash
# Scan entire project
bugprowler scan .

# Output:
# Scanning project...
# Found 5 vulnerabilities:
#   Critical: 1
#   High: 2
#   Medium: 2
#   Low: 0
```

### Example 2: Scan with Severity Filter

```bash
# Only show critical and high severity issues
bugprowler scan . --min-severity high

# Output filters issues below 'high' severity
```

### Example 3: Generate HTML Report

```bash
# Generate comprehensive HTML report
bugprowler scan . --output security-report.html --format html --verbose

# Report includes:
# - Vulnerability summary
# - Detailed findings
# - Code snippets
# - Remediation guidance
# - Trends and statistics
```

### Example 4: Exclude Specific Directories

```bash
# Scan excluding test and vendor directories
bugprowler scan . --exclude "tests/,vendor/,node_modules/"
```

### Example 5: CI/CD Integration

```bash
# Example GitHub Actions workflow
name: Security Scan
on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run bugProwler
        run: |
          pip install bugprowler
          bugprowler scan . --output results.json --format json
          # Fail if critical issues found
          bugprowler scan . --min-severity critical --fail-on-findings
```

### Example 6: Scan with Custom Configuration

```bash
# Create configuration
bugprowler init .

# Edit .bugprowler.yml as needed

# Run scan with configuration
bugprowler scan . --config .bugprowler.yml
```

### Example 7: Parallel Scanning

```bash
# Use multiple threads for faster scanning
bugprowler scan . --threads 8 --timeout 600

# Useful for large projects
```

### Example 8: Export to Multiple Formats

```bash
# Generate multiple report formats
bugprowler scan . --output results.json --format json
bugprowler scan . --output results.csv --format csv
bugprowler scan . --output results.html --format html

# Create combined report directory
mkdir -p ./security-reports
bugprowler scan . --output ./security-reports/ --format html
```

## Best Practices

1. **Run Regularly** - Include bugProwler in your CI/CD pipeline for continuous security monitoring
2. **Review Results** - Always review and validate findings before taking action
3. **Keep Updated** - Regularly update bugProwler to get the latest vulnerability definitions
4. **Custom Configuration** - Tailor configuration to your project's needs
5. **Version Control** - Commit `.bugprowler.yml` to version control
6. **Track Trends** - Monitor vulnerability trends over time
7. **Remediate Promptly** - Address critical and high-severity issues quickly

## Troubleshooting

### Common Issues

**Issue: "Command not found" after installation**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows
```

**Issue: Scan times out**
```bash
# Increase timeout value
bugprowler scan . --timeout 600

# Or reduce number of threads
bugprowler scan . --threads 2
```

**Issue: Permission denied**
```bash
# Ensure proper permissions
chmod +x bugprowler
```

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please ensure all tests pass and code follows the project's style guidelines.

## Support

- 📖 **Documentation**: [Full Documentation](https://github.com/ivangrana/bugProwler/wiki)
- 🐛 **Issues**: [Report Issues](https://github.com/ivangrana/bugProwler/issues)
- 💬 **Discussions**: [Community Discussions](https://github.com/ivangrana/bugProwler/discussions)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ by [ivangrana](https://github.com/ivangrana)**

**Last Updated**: 2026-01-14
