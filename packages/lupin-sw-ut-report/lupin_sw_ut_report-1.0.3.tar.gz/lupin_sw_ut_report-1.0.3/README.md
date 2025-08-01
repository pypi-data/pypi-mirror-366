# lupin_sw_ut_report

This project converts test files (in `.txt` and `.xml` formats) into Markdown reports. The goal is to facilitate the documentation of software test results by providing readable Markdown files that can be used for comprehensive reporting.

## Features

- **TXT and XML File Conversion**: Converts test files into structured Markdown files for better readability.
- **Support for Given-When-Then Formats**: Parses and converts test files defined using the `Given`, `When`, `Then` format.
- **Combined Report Generation**: Creates a single Markdown file summarizing all tests found in the specified folder.
- **Command-Line Interface (CLI) with Typer**: A CLI tool for easy execution of conversions.

## Setting Up a Python Virtual Environment (Recommended for Development)

A **Python virtual environment** is an isolated workspace that allows you to install dependencies for a project without affecting your global Python installation or other projects. This is especially useful for development, as it helps avoid dependency conflicts and keeps your system clean.

> **Note:** This setup is recommended for developers who want to contribute to or test the project locally. End users installing via `pip install lupin-sw-ut-report` do not need to follow these steps.

### Why Use a Virtual Environment?
- Keeps project dependencies isolated from other Python projects and your system Python.
- Prevents version conflicts between packages.
- Makes it easy to manage and reproduce development environments.

### Step-by-Step Setup (Windows)

1. **Create a virtual environment in the project root:**
   ```powershell
   python -m venv .lupin_sw_ut_report
   ```

2. **Activate the virtual environment:**
   ```powershell
   .\.lupin_sw_ut_report\Scripts\activate
   ```
   You should see the environment name (e.g., `(.lupin_sw_ut_report)`) appear in your terminal prompt.

3. **Install the project in editable mode:**
   ```powershell
   pip install -e .
   ```
   This installs the project in "editable mode," meaning any changes you make to the source code will immediately affect your environment without needing to reinstall. This is ideal for development and testing.

4. **Deactivate the virtual environment when done:**
   ```powershell
   deactivate
   ```
   This returns your terminal to the global Python environment.

> **Tip:** The `.lupin_sw_ut_report` folder should be added to your `.gitignore` file to avoid committing it to version control.

## Installation

Run `pip install lupin-sw-ut-report`

## Usage

This project provides a command-line interface to generate reports from a folder containing test files (`.txt` and `.xml`).

To run the script, use the following command:

```bash
sw-ut-report --input-folder <path/to/your/input-folder>
```

## Environment Variables

This project supports several environment variables for configuration, particularly for Jama integration and sandbox environments.

### Jama Configuration Variables

These variables are required for Jama integration features:

```bash
# Required Jama connection settings
export JAMA_URL="your-jama-instance"
export JAMA_CLIENT_ID="your-client-id"
export JAMA_CLIENT_PASSWORD="your-client-password"
export JAMA_DEFAULT_PROJECT_ID="8"
```

### Jama Test Set Configuration

Configure the test set container for unit test organization:

```bash
# Optional: Custom test set ID (defaults to "SmlPrep-SET-359")
export JAMA_TEST_SET_ID="YourCustom-SET-123"
```

### Sandbox Search and Replace

For sandbox environments or when working with different Jama instances, you can configure automatic search and replace rules for cover IDs:

```bash
# Optional: Search and replace rules for cover IDs
export JAMA_SANDBOX_SEARCH_AND_REPLACE="sourceString1,replacement1;sourceString2,replacement2"
```

#### Search and Replace Format

The `JAMA_SANDBOX_SEARCH_AND_REPLACE` variable uses the following format:
- Multiple rules are separated by semicolons (`;`)
- Each rule has a source string and replacement string separated by comma (`,`)
- Whitespace around rules is automatically handled

#### Examples

**Single rule:**
```bash
export JAMA_SANDBOX_SEARCH_AND_REPLACE="SmlPrep,MyProject"
```

**Multiple rules:**
```bash
export JAMA_SANDBOX_SEARCH_AND_REPLACE="SmlPrep,MyProject;SET-359,SET-123;SUBSR,REQ"
```

**With spaces (automatically handled):**
```bash
export JAMA_SANDBOX_SEARCH_AND_REPLACE=" SmlPrep , MyProject ; SET-359 , SET-123 "
```

#### Transformation Examples

**Input cover IDs:**
- `SmlPrep-SUBSR-123`
- `SmlPrep-SWID-456`
- `SmlPrep-SET-359`

**With `JAMA_SANDBOX_SEARCH_AND_REPLACE="SmlPrep,MyProject;SET-359,SET-123"`:**

**Output cover IDs:**
- `MyProject-SUBSR-123`
- `MyProject-SWID-456`
- `MyProject-SET-123`

#### Use Cases

- **Sandbox Testing**: Transform production IDs to sandbox equivalents
- **Multi-Environment Support**: Use different Jama instances with different naming conventions
- **Migration**: Transform old naming patterns to new ones
- **Testing**: Create test-specific transformations without modifying source files

#### Error Handling

- Invalid rule formats are logged and skipped
- Empty search or replacement strings are ignored
- Graceful handling of malformed environment variables
- Safe handling of None/empty inputs

## Manual Publishing to PyPI

> **Note:**
> For a fully automated deployment process, see the next section on using the provided PowerShell script.

To publish this package to PyPI, follow these manual steps:

### 1. Update the Version

You must update the version number in **both** of these files:
- `src/sw_ut_report/__init__.py` (e.g., `__version__ = "0.1.0"`)
- `pyproject.toml` (e.g., `version = "0.1.0"`)

Make sure the version numbers match in both files. This is required for a successful and consistent release.

### 2. Build the Package

Install the build tool if you haven't already:

```bash
pip install build
```

Run the following command from the root of the project:

```bash
python -m build --no-isolation
```

This will generate distribution files in the `dist/` directory.

### 3. Prepare for Upload: PyPI Token and `.pypirc`

- Create an API token on your [PyPI account](https://pypi.org/manage/account/#api-tokens).
- Create a `.pypirc` file in the root of your repository (but **do not commit it to git**!).
- The `.pypirc` file is already listed in `.gitignore` by default, but always double-check before committing.

Example `.pypirc` file:

```
[distutils]
index-servers =
    pypi

[pypi]
username = __token__  # Do not change this value; it must remain exactly as shown
password = <your-pypi-api-token-here>  # Provide your token without any quotes or extra characters
```

**Replace `<your-pypi-api-token-here>` with your actual PyPI API token.**
- Do not add any quotation marks (`"` or `'`) or extra characters around the token.
- The line `username = __token__` must remain exactly as written.

> **Important:**
> - Never share your PyPI token.
> - Never commit `.pypirc` to version control, even if it is already in `.gitignore`.

### 4. Upload to PyPI

Install Twine if you haven't already:

```bash
pip install twine
```

Upload your package using Twine and your `.pypirc` configuration:

```bash
twine upload --config-file ./.pypirc dist/*
```

If successful, your package will be published to PyPI.

### Security Reminder
- Keep your PyPI API token secret.
- Do not share your `.pypirc` file or its contents.
- Always verify you are uploading the correct version and files.

### Automated Publishing with PowerShell

You can automate the version update, build, and upload process using the provided PowerShell script:

#### Prerequisites
- Windows with PowerShell 7 or later
- Python installed and available in your PATH
- `.pypirc` file present in the project root (see above for details)

#### Usage
From the project root, run:

```powershell
pwsh ./publish-to-pypi.ps1 -Version "0.1.2"
```
Replace `0.1.2` with your desired version number.

#### What the Script Does
- Checks for the presence of `.pypirc` and stops if missing
- Installs `build` and `twine` if not already installed
- Updates the version in both `src/sw_ut_report/__init__.py` and `pyproject.toml`
- Cleans the `dist/` directory
- Builds the package
- Uploads the package to PyPI using your `.pypirc` configuration
- Stops and reports at the first error

This script streamlines the release process and helps ensure consistency between your code and published package.
