from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
import hashlib
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "skills" / "develop-ehl-plugins" / "scripts" / "check_public_text.py"
SYNTHETIC_PHRASE = "crimson lunar anvil"
SYNTHETIC_DIGEST = hashlib.sha256(SYNTHETIC_PHRASE.encode("utf-8")).hexdigest()


def run_guard(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args, str(root)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


class PublicTextGuardTests(unittest.TestCase):
    def test_allows_public_text_without_internal_rationale(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text(
                "EsionHsrahLatigid makes controlled experimental audio tools.\n",
                encoding="utf-8",
            )

            result = run_guard(root)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS", result.stdout)

    def test_rejects_internal_rationale_without_plaintext_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text(SYNTHETIC_PHRASE, encoding="utf-8")

            result = run_guard(root, "--digest", SYNTHETIC_DIGEST)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FAIL", result.stderr)
        self.assertNotIn(SYNTHETIC_PHRASE, result.stderr)

    def test_rejects_cpp_text_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "Processor.cpp").write_text(f"// {SYNTHETIC_PHRASE}\n", encoding="utf-8")

            result = run_guard(root, "--digest", SYNTHETIC_DIGEST)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("public text", result.stderr)
        self.assertNotIn(SYNTHETIC_PHRASE, result.stderr)

    def test_rejects_svg_text_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "preview.svg").write_text(
                f"<svg><metadata>{SYNTHETIC_PHRASE}</metadata></svg>\n",
                encoding="utf-8",
            )

            result = run_guard(root, "--digest", SYNTHETIC_DIGEST)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("public text", result.stderr)
        self.assertNotIn(SYNTHETIC_PHRASE, result.stderr)

    def test_rejects_history_message_without_plaintext_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init"], cwd=root, check=True, stdout=subprocess.DEVNULL)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=root, check=True)
            (root / "README.md").write_text("EsionHsrahLatigid\n", encoding="utf-8")
            subprocess.run(["git", "add", "README.md"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", SYNTHETIC_PHRASE], cwd=root, check=True, stdout=subprocess.DEVNULL)
            (root / "README.md").write_text("EsionHsrahLatigid public copy\n", encoding="utf-8")

            result = run_guard(root, "--history", "--digest", SYNTHETIC_DIGEST)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("repository history", result.stderr)
        self.assertNotIn(SYNTHETIC_PHRASE, result.stderr)

    def test_rejects_untracked_public_file_in_git_repo(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init"], cwd=root, check=True, stdout=subprocess.DEVNULL)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=root, check=True)
            (root / "README.md").write_text("EsionHsrahLatigid\n", encoding="utf-8")
            subprocess.run(["git", "add", "README.md"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "Initial clean text"], cwd=root, check=True, stdout=subprocess.DEVNULL)
            (root / "NOTES.md").write_text(SYNTHETIC_PHRASE, encoding="utf-8")

            result = run_guard(root, "--digest", SYNTHETIC_DIGEST)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("public text", result.stderr)
        self.assertNotIn(SYNTHETIC_PHRASE, result.stderr)

    def test_skips_binary_nul_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "blob.bin").write_bytes(b"\x00" + SYNTHETIC_PHRASE.encode("utf-8"))

            result = run_guard(root, "--digest", SYNTHETIC_DIGEST)

        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
