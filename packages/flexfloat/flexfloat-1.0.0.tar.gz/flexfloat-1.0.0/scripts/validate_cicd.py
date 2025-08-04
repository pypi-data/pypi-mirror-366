#!/usr/bin/env python3
"""
Validation script for CI/CD setup.
This script checks if all necessary files and configurations are in place.
"""

import re
import sys
from pathlib import Path

import yaml


def check_file_exists(filepath: str, description: str) -> bool:
    """Check if a file exists."""
    path = Path(filepath)
    if path.exists():
        print(f"[OK] {description}: {filepath}")
        return True
    else:
        print(f"[NO] {description} missing: {filepath}")
        return False


def check_workflow_file(filepath: str) -> bool:
    """Check if a workflow file is valid."""
    path = Path(filepath)
    if not path.exists():
        print(f"[NO] Workflow missing: {filepath}")
        return False

    try:
        with open(path, "r", encoding="utf-8") as f:
            yaml.safe_load(f)
        print(f"[OK] Valid workflow: {filepath}")
        return True
    except (yaml.YAMLError, UnicodeDecodeError) as e:
        print(f"[NO] Invalid YAML in {filepath}: {e}")
        return False


def check_version_consistency() -> bool:
    """Check version consistency across files."""
    pyproject_path = Path("pyproject.toml")
    init_path = Path("flexfloat/__init__.py")

    if not pyproject_path.exists() or not init_path.exists():
        print("[NO] Required version files not found!")
        return False

    # Get versions
    pyproject_content = pyproject_path.read_text()
    init_content = init_path.read_text()

    pyproject_match = re.search(r'version = "([^"]+)"', pyproject_content)
    init_match = re.search(r'__version__ = "([^"]+)"', init_content)

    if not pyproject_match or not init_match:
        print("[NO] Could not find version strings!")
        return False

    pyproject_version = pyproject_match.group(1)
    init_version = init_match.group(1)

    if pyproject_version == init_version:
        print(f"[OK] Version consistency: {pyproject_version}")
        return True
    else:
        print(
            f"[NO] Version mismatch: pyproject.toml={pyproject_version}, "
            f"__init__.py={init_version}"
        )
        return False


def check_pyproject_config() -> bool:
    """Check pyproject.toml configuration."""
    path = Path("pyproject.toml")
    if not path.exists():
        print("[NO] pyproject.toml not found!")
        return False

    content = path.read_text()

    # Check required sections
    required_sections = [
        "[build-system]",
        "[project]",
        "name =",
        "version =",
        "description =",
    ]

    missing: list[str] = []
    for section in required_sections:
        if section not in content:
            missing.append(section)

    if missing:
        print(f"[NO] Missing sections in pyproject.toml: {missing}")
        return False

    print("[OK] pyproject.toml configuration looks good")
    return True


def main():
    """Main validation function."""
    print("Validating CI/CD Setup for flexfloat-py")
    print("=" * 50)

    all_good = True

    # Check essential files
    essential_files = [
        ("pyproject.toml", "Project configuration"),
        ("setup.py", "Setup script"),
        ("README.md", "README"),
        ("LICENSE", "License file"),
        ("MANIFEST.in", "Manifest file"),
        (".bumpversion.cfg", "Bump version config"),
        ("flexfloat/__init__.py", "Package init"),
    ]

    print("\n Essential Files:")
    for filepath, desc in essential_files:
        if not check_file_exists(filepath, desc):
            all_good = False

    # Check workflow files
    workflows = [
        ".github/workflows/test.yml",
        ".github/workflows/release.yml",
        ".github/workflows/manual-release.yml",
        ".github/workflows/version-check.yml",
        ".github/workflows/pr-labeler.yml",
        ".github/workflows/build-check.yml",
    ]

    print("\n GitHub Workflows:")
    for workflow in workflows:
        if not check_workflow_file(workflow):
            all_good = False

    # Check helper scripts
    scripts = [
        ("scripts/version_manager.py", "Version manager script"),
    ]

    print("\n Helper Scripts:")
    for filepath, desc in scripts:
        if not check_file_exists(filepath, desc):
            all_good = False

    # Check configurations
    print("\n Configuration Checks:")
    if not check_pyproject_config():
        all_good = False

    if not check_version_consistency():
        all_good = False

    # Final result
    print("\n" + "=" * 50)
    if all_good:
        print("CI/CD setup validation PASSED!")
        print("\nNext steps:")
        print("1. Commit all changes to your repository")
        print("2. Set up PyPI trusted publishing (see README)")
        print("3. Create a test PR to verify the workflows")
        print("4. Merge the PR to trigger your first automated release!")
    else:
        print("[NO] CI/CD setup validation FAILED!")
        print("Please fix the issues above before proceeding.")
        sys.exit(1)


if __name__ == "__main__":
    main()
