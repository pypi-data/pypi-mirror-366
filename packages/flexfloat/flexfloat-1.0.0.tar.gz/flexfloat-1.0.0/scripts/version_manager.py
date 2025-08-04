#!/usr/bin/env python3
"""
Local development script for version management.
This script helps manage versions locally before pushing to GitHub.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path


def get_current_version():
    """Get the current version from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("[NO] pyproject.toml not found!")
        sys.exit(1)

    content = pyproject_path.read_text()
    match = re.search(r'version = "([^"]+)"', content)
    if match:
        return match.group(1)
    else:
        print("[NO] Could not find version in pyproject.toml")
        sys.exit(1)


def check_version_consistency():
    """Check if versions are consistent across all files."""
    pyproject_path = Path("pyproject.toml")
    init_path = Path("flexfloat/__init__.py")

    if not all(p.exists() for p in [pyproject_path, init_path]):
        print("[NO] Required files not found!")
        return False

    # Get versions
    pyproject_content = pyproject_path.read_text()
    init_content = init_path.read_text()

    pyproject_match = re.search(r'version = "([^"]+)"', pyproject_content)
    init_match = re.search(r'__version__ = "([^"]+)"', init_content)

    if not pyproject_match or not init_match:
        print("[NO] Could not find version strings in files!")
        return False

    pyproject_version = pyproject_match.group(1)
    init_version = init_match.group(1)

    print(f"pyproject.toml version: {pyproject_version}")
    print(f"flexfloat/__init__.py version: {init_version}")

    if pyproject_version == init_version:
        print("[OK] All versions are synchronized!")
        return True
    else:
        print("[NO] Version mismatch detected!")
        return False


def bump_version(bump_type: str) -> str:
    """Bump version using bump2version."""
    if bump_type not in ["patch", "minor", "major"]:
        print("[NO] Invalid bump type! Use: patch, minor, or major")
        sys.exit(1)

    current = get_current_version()
    print(f"Current version: {current}")

    try:
        # Run bump2version
        result = subprocess.run(
            ["bump2version", bump_type], capture_output=True, text=True
        )
        if result.returncode == 0:
            new_version = get_current_version()
            print(f"[OK] Version bumped from {current} to {new_version}")
            return new_version
        else:
            print(f"[NO] Error running bump2version: {result.stderr}")
            sys.exit(1)
    except FileNotFoundError:
        print("[NO] bump2version not found! Install it with: pip install bump2version")
        sys.exit(1)


def run_tests():
    """Run the test suite."""
    print("Running tests...")
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/"], capture_output=True, text=True
        )
        if result.returncode == 0:
            print("[OK] All tests passed!")
            return True
        else:
            print(f"[NO] Tests failed:\n{result.stdout}\n{result.stderr}")
            return False
    except FileNotFoundError:
        print("[NO] pytest not found! Install it with: pip install pytest")
        return False


def build_package():
    """Build the package."""
    print("Building package...")
    try:
        result = subprocess.run(
            ["python", "-m", "build"], capture_output=True, text=True
        )
        if result.returncode == 0:
            print("[OK] Package built successfully!")
            return True
        else:
            print(f"[NO] Build failed:\n{result.stdout}\n{result.stderr}")
            return False
    except FileNotFoundError:
        print("[NO] build not found! Install it with: pip install build")
        return False


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Local development script for version management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Check command
    subparsers.add_parser("check", help="Check version consistency across files")

    # Bump command
    bump_parser = subparsers.add_parser("bump", help="Bump version")
    bump_parser.add_argument(
        "type", choices=["patch", "minor", "major"], help="Type of version bump"
    )

    # Test command
    subparsers.add_parser("test", help="Run the test suite")

    # Build command
    subparsers.add_parser("build", help="Build the package")

    # Release command
    release_parser = subparsers.add_parser("release", help="Full release process")
    release_parser.add_argument(
        "type",
        choices=["patch", "minor", "major"],
        help="Type of version bump for release",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "check":
        check_version_consistency()

    elif args.command == "bump":
        bump_version(args.type)

    elif args.command == "test":
        run_tests()

    elif args.command == "build":
        build_package()

    elif args.command == "release":
        print("Starting release process...")

        # 1. Check version consistency
        if not check_version_consistency():
            print("[NO] Fix version consistency before releasing!")
            sys.exit(1)

        # 2. Run tests
        if not run_tests():
            print("[NO] Fix tests before releasing!")
            sys.exit(1)

        # 3. Bump version
        new_version = bump_version(args.type)

        # 4. Build package
        if not build_package():
            print("[NO] Fix build issues before releasing!")
            sys.exit(1)

        print(f"[OK] Release {new_version} is ready!")
        print("Next steps:")
        print("1. Review the changes")
        print(
            "2. Commit the version bump: git add . && git commit -m 'Bump version to"
            f" {new_version}'"
        )
        print("3. Create a PR or push to main to trigger automated release")


if __name__ == "__main__":
    main()
