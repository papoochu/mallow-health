import sys
import unittest
from pathlib import Path


def main():
    """
    Run Mallow's unittest suite explicitly.

    This avoids relying on shell-specific test discovery behavior.
    """

    project_root = Path(__file__).resolve().parent
    tests_dir = project_root / "tests"

    if not tests_dir.exists():
        raise SystemExit(
            "Could not find the tests folder next to run_tests.py."
        )

    loader = unittest.TestLoader()

    suite = loader.discover(
        start_dir=str(tests_dir),
        pattern="test_*.py",
        top_level_dir=str(project_root),
    )

    test_count = suite.countTestCases()

    print(
        f"Discovered {test_count} Mallow tests."
    )

    if test_count == 0:
        raise SystemExit(
            "No tests were discovered. Make sure "
            "tests/test_core.py exists and is saved."
        )

    runner = unittest.TextTestRunner(
        verbosity=2,
    )

    result = runner.run(
        suite
    )

    if not result.wasSuccessful():
        sys.exit(1)


if __name__ == "__main__":
    main()
