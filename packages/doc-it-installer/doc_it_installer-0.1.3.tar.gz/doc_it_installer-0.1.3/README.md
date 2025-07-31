# Doc-It 

**Doc-It** is a powerful, modular command-line tool that leverages local Large Language Models (LLMs) via [Ollama](https://ollama.com/) to **automatically generate professional documentation** for your code changes.  
Track your work, explain complex changes in natural language, and export your documentation to multiple formats — all from your terminal.

---

## Features

- **AI-Powered Explanations**  
  Automatically generates clear, human-readable explanations for code modifications.

- **Fully Local**  
  Uses your local Ollama instance — ensuring your code stays private and secure.

- **Snapshot-Based Tracking**  
  Intelligently detects changes by comparing snapshots of your codebase.  
  _No Git dependency required._

- **Multiple Export Formats**  
  Generate documentation in:
  - Markdown (`.md`)
  - Microsoft Word (`.docx`)
  - LaTeX (`.tex`)

- **Modular & Configurable**  
  Easily configure the tool using a simple `.json` file to:
  - Specify the Ollama model
  - Select files to watch
  - Customize behavior

- **Simple CLI Interface**  
  Clean and intuitive commands for a seamless documentation experience.

---

## Prerequisites

Ensure you have the following installed on your system:

- Python **3.10 or higher**
- [Ollama](https://ollama.com/)
- At least one Ollama model pulled (e.g. Llama 3):

```bash
ollama pull llama3
```

---

## Installation

Install Doc-It from [PyPI](https://pypi.org/project/doc-it-installer/):

```bash
pip install doc-it-installer
```

---

## Usage

Navigate to your project’s root directory and follow this three-step workflow:

### 1️⃣ Initialize Your Project

Sets up the `.docit` directory, initializes a snapshot database, scans your codebase, and creates a high-level summary using AI.

```bash
doc-it init
```

_Run this only once per project._

---

### 2️⃣ Analyze and "Commit" Changes

After modifying your code, use the `commit` command.  
Doc-It compares snapshots and sends the differences to AI for explanation.

```bash
doc-it commit -m "Refactored the user authentication module"
```

💡 The `-m` flag is required to describe your update.

---

### 3️⃣ Generate the Documentation

Create a final documentation file using the `generate` command.

#### Default (Markdown):

```bash
doc-it generate
```

#### Generate a Word document:

```bash
doc-it generate --format docx
```

#### Generate a LaTeX document:

```bash
doc-it generate --format tex
```

---

## Authors

- **Kartik Sharma**
- **Harshvardhan Singh**

---

## License

This project is licensed under the [MIT License](LICENSE).

---

> _Empower your code with intelligent documentation. Let Doc-It do the writing._