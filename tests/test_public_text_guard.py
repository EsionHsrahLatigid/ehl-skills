from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
import hashlib
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1] / "skills" / "develop-ehl-plugins"
SCRIPT = SKILL_DIR / "scripts" / "check_public_text.py"
SKILL_MD = SKILL_DIR / "SKILL.md"
IDENTITY_REFERENCE = SKILL_DIR / "references" / "ehl-identity-design.md"
SYNTHETIC_PHRASE = "crimson lunar anvil"
SYNTHETIC_DIGEST = hashlib.sha256(SYNTHETIC_PHRASE.encode("utf-8")).hexdigest()
SYNTHETIC_COMPACT = "".join(SYNTHETIC_PHRASE.split())
SYNTHETIC_COMPACT_DIGEST = hashlib.sha256(SYNTHETIC_COMPACT.encode("utf-8")).hexdigest()
SYNTHETIC_COMPACT_ARGS = (
    "--compact-digest",
    SYNTHETIC_COMPACT_DIGEST,
    "--compact-window-size",
    str(len(SYNTHETIC_COMPACT)),
)


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

    def test_rejects_synthetic_camel_case_compact_variant(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("CrimsonLunarAnvil\n", encoding="utf-8")

            result = run_guard(root, *SYNTHETIC_COMPACT_ARGS)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("public text", result.stderr)
        self.assertNotIn("CrimsonLunarAnvil", result.stderr)

    def test_rejects_synthetic_lowercase_concatenation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text(SYNTHETIC_COMPACT, encoding="utf-8")

            result = run_guard(root, *SYNTHETIC_COMPACT_ARGS)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("public text", result.stderr)
        self.assertNotIn(SYNTHETIC_COMPACT, result.stderr)

    def test_rejects_synthetic_embedded_identifier(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "Processor.cpp").write_text(
                f"auto prefix{SYNTHETIC_COMPACT}Suffix = 0;\n",
                encoding="utf-8",
            )

            result = run_guard(root, *SYNTHETIC_COMPACT_ARGS)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("public text", result.stderr)
        self.assertNotIn(SYNTHETIC_COMPACT, result.stderr)

    def test_rejects_synthetic_filename_variant(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / f"{SYNTHETIC_COMPACT}.txt").write_text("clean content\n", encoding="utf-8")

            result = run_guard(root, *SYNTHETIC_COMPACT_ARGS)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("public text", result.stderr)
        self.assertNotIn(SYNTHETIC_COMPACT, result.stderr)

    def test_rejects_synthetic_regex_whitespace_split_variant(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text(r"crimson\\s+lunar\\s+anvil", encoding="utf-8")

            result = run_guard(root, *SYNTHETIC_COMPACT_ARGS)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("public text", result.stderr)
        self.assertNotIn(SYNTHETIC_COMPACT, result.stderr)

    def test_rejects_synthetic_escaped_newline_tab_body_variant(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text(r"crimson\\n+lunar\\t+anvil", encoding="utf-8")

            result = run_guard(root, *SYNTHETIC_COMPACT_ARGS)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("public text", result.stderr)
        self.assertNotIn(SYNTHETIC_COMPACT, result.stderr)

    def test_rejects_synthetic_encoded_whitespace_filename_variant(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / r"crimson%20lunar&#x20;anvil.txt").write_text("clean content\n", encoding="utf-8")

            result = run_guard(root, *SYNTHETIC_COMPACT_ARGS)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("public text", result.stderr)
        self.assertNotIn(SYNTHETIC_COMPACT, result.stderr)

    def test_rejects_synthetic_encoded_whitespace_history_variant(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init"], cwd=root, check=True, stdout=subprocess.DEVNULL)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=root, check=True)
            (root / "README.md").write_text(r"crimson\\x20lunar&nbsp;anvil", encoding="utf-8")
            subprocess.run(["git", "add", "README.md"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "Synthetic encoded whitespace"], cwd=root, check=True, stdout=subprocess.DEVNULL)
            (root / "README.md").write_text("EsionHsrahLatigid public copy\n", encoding="utf-8")
            subprocess.run(["git", "add", "README.md"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "Clean current copy"], cwd=root, check=True, stdout=subprocess.DEVNULL)

            result = run_guard(root, "--history", *SYNTHETIC_COMPACT_ARGS)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("repository history", result.stderr)
        self.assertNotIn(SYNTHETIC_COMPACT, result.stderr)

    def test_skill_requires_workspace_level_ehl_evidence_tree(self) -> None:
        text = SKILL_MD.read_text(encoding="utf-8")

        self.assertIn("workspace-level EHL evidence tree", text)
        self.assertIn("/Users/2bit/prog/ehl", text)
        self.assertIn("Do not resolve the evidence tree relative to a target plugin repository", text)
        self.assertIn("session, log, timeline, handover, memo, or decision", text)
        self.assertIn("whole path tokens", text)
        self.assertIn("a substring such as `logo` is not log evidence", text)
        self.assertIn("design-asset trees", text)
        self.assertIn("nested git repositories", text)
        self.assertIn("public-copy verifier scripts", text)
        self.assertIn("regex, escaped, split, compact, camel-case, embedded, or filename spelling", text)
        self.assertIn("encoded whitespace", text)

    def test_identity_reference_has_no_ambiguous_target_relative_ehl_path(self) -> None:
        text = IDENTITY_REFERENCE.read_text(encoding="utf-8")
        ambiguous_path = "../" + "ehl"

        self.assertNotIn(f"`{ambiguous_path}`", text)
        self.assertIn("workspace-level EHL evidence tree", text)
        self.assertIn("Locate that tree from the workspace root rather than from a target plugin repository", text)
        self.assertIn("Do not treat incidental substrings such as `logo` as log evidence", text)
        self.assertIn("release notes, repository metadata, public source, website/catalog text", text)


if __name__ == "__main__":
    unittest.main()
