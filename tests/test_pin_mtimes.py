"""Changed build inputs remain newer than the cached build, even with leading-dash paths."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "tools/ci/pin_mtimes.sh"


@unittest.skipUnless(sys.platform.startswith("linux"), "pin_mtimes uses GNU touch on Linux CI")
class PinMtimesTests(unittest.TestCase):
    def test_changed_leading_dash_files_and_parents_are_touched(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            env = dict(os.environ, GIT_AUTHOR_NAME="CI fixture", GIT_AUTHOR_EMAIL="fixture@example.invalid",
                       GIT_COMMITTER_NAME="CI fixture", GIT_COMMITTER_EMAIL="fixture@example.invalid")

            def git(*args):
                return subprocess.check_output(["git", "-c", "core.hooksPath=" + os.devnull,
                                                "-c", "commit.gpgsign=false", *args],
                                               cwd=root, env=env, text=True).strip()

            git("init", "--quiet")
            paths = [root / "-input.txt", root / "-inputs/data.txt"]
            (root / "-inputs").mkdir()
            for path in paths:
                path.write_text("old")
            git("add", "--", "-input.txt", "-inputs/data.txt")
            git("commit", "--quiet", "-m", "cached inputs")
            (root / ".ci-built").mkdir()
            (root / ".ci-built/sha").write_text(git("rev-parse", "HEAD") + "\n")
            for path in paths:
                path.write_text("new")
            git("add", "--", "-input.txt", "-inputs/data.txt")
            git("commit", "--quiet", "-m", "changed inputs")

            start = time.time_ns()
            result = subprocess.run(["bash", str(SCRIPT), ".ci-built"], cwd=root,
                                    capture_output=True, text=True, check=True)
            for path in [*paths, root / "-inputs"]:
                with self.subTest(path=path.relative_to(root)):
                    self.assertGreaterEqual(path.stat().st_mtime_ns, start, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
