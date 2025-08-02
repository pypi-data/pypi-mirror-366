# PyCode-Explorer 🔍

**Understand Python scripts and packages in seconds, not hours.**

Perfect for busy team leads, managers, and developers who need to quickly assess unfamiliar Python code. Stop wasting time deciphering "vibe coding" - get instant insights into what any Python script actually does.

## 🚀 Quick Start

```bash
# Install
pip install pycode-explorer

# Analyze a script
pycode-explorer script.py

# Quick assessment (perfect for busy managers)
pycode-explorer script.py --brief

# Check entire project
pycode-explorer --directory ./project_folder
```

## 🎯 Perfect For

- **Team Leads**: Quickly assess intern/contractor code submissions
- **Code Reviewers**: Get instant script understanding before diving deep  
- **DevOps Teams**: Audit dependencies and security implications
- **Busy Managers**: Executive summaries of codebase health
- **Developers**: Understand unfamiliar codebases rapidly

## ✨ Features

### 📄 Script Analysis
- **Instant Understanding**: What does this script actually do?
- **Dependency Tracking**: Which packages are being used and how?
- **Security Warnings**: Flags for potentially risky imports
- **Optimization Tips**: Detect unused imports and issues

### 📦 Package Exploration  
- **Function Discovery**: Explore any installed package's capabilities
- **Smart Search**: Find specific functions within packages
- **Documentation Extraction**: Automatic descriptions from docstrings

### 🏢 Corporate Features
- **Executive Summaries**: High-level codebase assessments
- **Security Auditing**: Identify system access and network usage
- **Batch Analysis**: Process entire directories at once
- **JSON Output**: Integration with corporate tools

## 📋 Real-World Examples

### Scenario 1: Intern Code Review
```bash
# The intern submitted a script - what does it do?
$ pycode-explorer intern_script.py --brief
📄 intern_script.py: Uses pandas, numpy for data analysis ✅

# Need more details?
$ pycode-explorer intern_script.py
# Full analysis with function usage and warnings
```

### Scenario 2: Security Audit
```bash
# Check entire project for security implications
$ pycode-explorer --directory ./new_project

📊 EXECUTIVE SUMMARY
📁 Total Files Analyzed: 15
⚠️  Total Issues Found: 3  
📦 Unique Packages Used: 8

🚨 SECURITY CONSIDERATIONS:
   • requests (Network access)
   • subprocess (System command execution)
   • os (File system access)
```

### Scenario 3: Package Research
```bash
# What can pandas do?
$ pycode-explorer --explore pandas

# Find all file reading functions
$ pycode-explorer --explore pandas --search read
```

## 🖥️ Command Line Reference

### Script Analysis
```bash
pycode-explorer script.py              # Full analysis
pycode-explorer script.py --brief      # One-line summary  
pycode-explorer script.py --warnings-only  # Issues only
pycode-explorer script.py --output json    # JSON format
```

### Directory Analysis
```bash
pycode-explorer --directory ./project     # Analyze all .py files
pycode-explorer -d ./src --brief          # Brief summary of all files
```

### Package Exploration
```bash
pycode-explorer --explore numpy           # Explore numpy package
pycode-explorer --explore pandas --search read  # Search within package
```

## 🐍 Python API

```python
from pyexplorer import ScriptAnalyzer, PackageExplorer

# Analyze a script
analyzer = ScriptAnalyzer()
result = analyzer.analyze_file("script.py")
analyzer.print_analysis(result)

# Explore a package
explorer = PackageExplorer()
pkg_info = explorer.explore_package("pandas")
explorer.print_exploration(pkg_info)
```

## 📊 Sample Output

### Script Analysis
```
============================================================
SCRIPT ANALYSIS: data_processor.py
============================================================

Import: 1. pandas (as pd) - Data manipulation and analysis library
Functions used under this import:
  1.a. read_csv() - Read a comma-separated values (csv) file into DataFrame
  1.b. DataFrame() - Two-dimensional, size-mutable, potentially heterogeneous tabular data

============================================================
WARNINGS & SUGGESTIONS:
============================================================
⚠️  Potential issue: Function call plt.show() found, but matplotlib was not imported.

============================================================
OVERALL UNDERSTANDING:
============================================================
Technical Summary: The script 'data_processor.py' imports and utilizes 1 external package: pandas.

Clear Explanation: This script is designed for data manipulation and analysis.
============================================================
```

### Directory Summary
```
📊 EXECUTIVE SUMMARY
📁 Total Files Analyzed: 12
⚠️  Total Issues Found: 5
📦 Unique Packages Used: 6

🔝 Most Used Packages:
   1. pandas (used in 8 files)
   2. numpy (used in 5 files)  
   3. requests (used in 3 files)

✅ OVERALL STATUS: Codebase looks healthy.
```

## 🛡️ Security Features

PyCode-Explorer automatically flags security-sensitive packages:

- **Network Access**: `requests`, `urllib`, `socket`
- **System Access**: `subprocess`, `os`, `sys`  
- **Serialization Risks**: `pickle`, `eval`
- **File System**: `pathlib`, `shutil`

Perfect for corporate environments where security matters.

## ⚡ Performance

- **Zero Dependencies**: Uses only Python built-ins
- **Lightning Fast**: Analyze scripts in milliseconds
- **Memory Efficient**: Handles large codebases smoothly
- **Caching**: Package exploration results are cached

## 📈 Use Cases

### For Team Leads
- Quickly assess code quality before reviews
- Identify problematic dependencies
- Get executive summaries for stakeholder reports

### For Developers  
- Understand legacy code rapidly
- Discover package capabilities
- Debug import issues

### For DevOps
- Audit security implications
- Track dependency usage across projects
- Automate code quality checks

## 🔧 Installation

```bash
# From PyPI (when published)
pip install pycode-explorer

# Development installation
git clone https://github.com/yourusername/pycode-explorer
cd pycode-explorer
pip install -e .
```

## 🤝 Contributing

We welcome contributions! PyCode-Explorer is perfect for:
- Adding support for more programming languages
- Enhanced security analysis
- Integration with CI/CD pipelines
- Better visualization features

## 📄 License

MIT License - Use freely in corporate and personal projects.

## 🙋‍♂️ Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/pycode-explorer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/pycode-explorer/discussions)
- **Email**: your.email@example.com

---

**Stop guessing what code does. Start knowing in seconds.** 🚀