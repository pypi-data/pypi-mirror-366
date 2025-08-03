# Project Plan

## Overview
This document outlines tasks and their implementation strategies for the stanlee AI agent framework.

## Tasks

### Task 1: Write Comprehensive Test Suite
**Description:** Create unit tests for core modules and integration tests to ensure code quality before publishing

**Implementation Steps:**
1. Create unit tests for `stanlee/history.py`:
   - Test History class initialization
   - Test add_message with different message types
   - Test get_messages and filtering
   - Test clear_history functionality
   - Test edge cases (empty history, invalid types)

2. Create unit tests for `stanlee/agent.py`:
   - Test Agent initialization with mock LLM
   - Test tool registration and validation
   - Test message handling and response generation
   - Test error handling and retries
   - Test streaming vs non-streaming modes
   - Mock litellm calls to avoid API usage

3. Create unit tests for `stanlee/tools/`:
   - Test Tool base class functionality
   - Test SendMessage tool execution
   - Test tool validation and error handling
   - Test tool result formatting

4. Create integration test for simple agent example:
   - Test end-to-end agent creation and execution
   - Test tool calling flow
   - Test conversation history management
   - Use mock LLM responses for deterministic testing

5. Set up test configuration:
   - Add pytest fixtures for common test objects
   - Configure pytest-cov for coverage reporting
   - Add pytest-mock for mocking external dependencies
   - Set minimum coverage threshold (80%)

**Dependencies:**
- pytest, pytest-cov, pytest-mock in dev dependencies
- Proper test structure in tests/ directory

**Success Criteria:**
- All core functionality has unit tests
- Code coverage is above 80%
- Integration test proves the framework works end-to-end
- Tests run quickly without external API calls

---

### Task 2: Convert stanlee to PyPI Package (v0.0.1)
**Description:** Package stanlee as a PyPI package and publish it to allow users to install via `pip install stanlee` or `uv add stanlee`

**Implementation Steps:**
1. Update pyproject.toml with proper metadata:
   - Change version from "0.1.0" to "0.0.1"
   - Add proper description
   - Add author information
   - Add project URLs (homepage, repository, issues)
   - Add classifiers (Development Status, Intended Audience, License, Python versions)
   - Add keywords
   - Ensure all dependencies have latest versions

2. Configure build system:
   - Add [build-system] section with appropriate build backend (uv uses hatchling by default)
   - Ensure package structure follows Python standards

3. Prepare package files:
   - Update README.md with installation instructions
   - Add LICENSE file if not present
   - Add CHANGELOG.md for version history
   - Add __version__ to __init__.py

4. Build and test locally:
   - Run `uv build` to create distribution files
   - Test installation in a fresh virtual environment
   - Verify all imports work correctly
   - Run example scripts to ensure functionality

5. Set up PyPI publishing:
   - Configure .pypirc or use PyPI tokens
   - Consider using GitHub Actions for automated releases
   - Set up test PyPI first for validation

6. Publish to PyPI:
   - Use `uv publish` or `twine upload`
   - Verify package appears on PyPI
   - Test installation from PyPI

**Dependencies:**
- PyPI account and API token (needed from user)
- All code should be working and tested
- Proper versioning strategy (using v0.0.1 as requested)

**Success Criteria:**
- Users can run `pip install stanlee` or `uv add stanlee`
- Package imports correctly: `from stanlee import Agent, Tool`
- All dependencies are properly specified
- Package metadata is complete and professional

---

### Task 3: Set up GitHub CI/CD Pipeline
**Description:** Create GitHub Actions workflows for automated testing, linting, and formatting checks on pull requests

**Implementation Steps:**
1. Create `.github/workflows/ci.yml` for PR checks:
   - Run on all pull requests and pushes to main
   - Set up Python 3.11 and 3.12
   - Install dependencies with uv
   - Run `ruff format --check` to verify formatting
   - Run `ruff check` for linting
   - Run `pytest` with coverage reporting
   - Fail if any check doesn't pass

2. Create `.github/workflows/publish.yml` for automated PyPI releases:
   - Trigger on GitHub releases (when you create a release with tag v*)
   - Verify tag matches version in pyproject.toml
   - Run all tests before publishing
   - Build package with `uv build`
   - Publish to PyPI using `UV_PUBLISH_TOKEN` secret
   - Post release verification

3. Configure branch protection rules:
   - Require PR reviews before merging
   - Require status checks to pass: format, lint, tests
   - Dismiss stale reviews on new commits
   - No direct pushes to main branch

4. Set up pre-commit hooks (`.pre-commit-config.yaml`):
   - Run ruff format
   - Run ruff check
   - Check for merge conflicts
   - Verify no large files

**Dependencies:**
- GitHub repository with admin access
- PyPI API token stored as GitHub secret `UV_PUBLISH_TOKEN`
- pytest and pytest-cov in dev dependencies

**Success Criteria:**
- All PRs must pass format, lint, and test checks
- Creating a GitHub release automatically publishes to PyPI
- Local pre-commit hooks catch issues before pushing

---

## Information Provided:
1. **PyPI API Token**: ✅ PROVIDED (stored securely)

2. **Author Information**: ✅ PROVIDED
   - Name: Aman Arora
   - Email: aman.arora0210@gmail.com
   - GitHub: https://github.com/amaarora/stanley

3. **License Choice**: MIT (assuming MIT for open source compatibility)

## Execution Order (Updated):
- [ ] Task 1: Convert to PyPI Package - 30 minutes (PRIORITY - Do this first!)
- [ ] Task 2: Write Comprehensive Test Suite - 45 minutes
- [ ] Task 3: Set up GitHub CI/CD Pipeline - 20 minutes

## Notes
- We'll use uv's built-in commands for building and publishing
- Version will be v0.0.1 as requested, continuing pre-release until v1.0.0
- Package name "stanlee" needs to be available on PyPI (we should check this first)
- Automated PyPI releases prevent manual errors and ensure consistent release process
- GitHub Actions will handle all CI/CD needs without external services