from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1] / "skills" / "develop-ehl-plugins"
SCRIPT = SKILL_DIR / "scripts" / "check_public_text.py"
SKILL_MD = SKILL_DIR / "SKILL.md"
IDENTITY_REFERENCE = SKILL_DIR / "references" / "ehl-identity-design.md"
HISTORY_REMEDIATION_REFERENCE = SKILL_DIR / "references" / "history-remediation.md"
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

    def test_json_report_redacts_current_match_and_keeps_safe_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text(SYNTHETIC_PHRASE, encoding="utf-8")

            result = run_guard(root, "--report-json", "--digest", SYNTHETIC_DIGEST)

        self.assertNotEqual(result.returncode, 0)
        report = json.loads(result.stdout)
        self.assertEqual(report["result"], "fail")
        self.assertEqual(report["current"][0]["kind"], "current_content")
        self.assertEqual(report["current"][0]["path"], "README.md")
        self.assertNotIn(SYNTHETIC_PHRASE, result.stdout)
        self.assertNotIn(SYNTHETIC_PHRASE, result.stderr)

    def test_json_report_redacts_forbidden_current_filename(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            forbidden_path = root / f"{SYNTHETIC_PHRASE}.md"
            forbidden_path.write_text("clean public text\n", encoding="utf-8")

            result = run_guard(root, "--report-json", "--digest", SYNTHETIC_DIGEST)

        self.assertNotEqual(result.returncode, 0)
        report = json.loads(result.stdout)
        self.assertEqual(report["current"][0]["kind"], "current_path")
        self.assertNotIn("path", report["current"][0])
        self.assertRegex(report["current"][0]["path_sha256"], r"^[0-9a-f]{64}$")
        self.assertNotIn(SYNTHETIC_PHRASE, result.stdout)
        self.assertNotIn(SYNTHETIC_PHRASE, result.stderr)

    def test_json_report_pass_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("clean public text\n", encoding="utf-8")

            result = run_guard(root, "--report-json", "--digest", SYNTHETIC_DIGEST)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            json.loads(result.stdout),
            {
                "schema": "ehl-public-text-report-v1",
                "result": "pass",
                "current": [],
                "history": [],
            },
        )

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

    def test_json_report_identifies_history_message_and_blob_without_match_text(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init"], cwd=root, check=True, stdout=subprocess.DEVNULL)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=root, check=True)
            (root / "README.md").write_text(SYNTHETIC_PHRASE, encoding="utf-8")
            subprocess.run(["git", "add", "README.md"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", SYNTHETIC_PHRASE], cwd=root, check=True, stdout=subprocess.DEVNULL)
            (root / "README.md").write_text("clean current text\n", encoding="utf-8")
            subprocess.run(["git", "add", "README.md"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "Clean current text"], cwd=root, check=True, stdout=subprocess.DEVNULL)

            result = run_guard(
                root,
                "--history",
                "--report-json",
                "--digest",
                SYNTHETIC_DIGEST,
            )

        self.assertNotEqual(result.returncode, 0)
        report = json.loads(result.stdout)
        self.assertEqual({finding["kind"] for finding in report["history"]}, {"history_message", "history_blob"})
        blob_finding = next(finding for finding in report["history"] if finding["kind"] == "history_blob")
        self.assertEqual(blob_finding["path"], "README.md")
        self.assertRegex(blob_finding["commit"], r"^[0-9a-f]{40}$")
        self.assertRegex(blob_finding["blob"], r"^[0-9a-f]{40}$")
        self.assertNotIn(SYNTHETIC_PHRASE, result.stdout)
        self.assertNotIn(SYNTHETIC_PHRASE, result.stderr)

    def test_json_report_redacts_forbidden_history_filename(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init"], cwd=root, check=True, stdout=subprocess.DEVNULL)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=root, check=True)
            forbidden_name = f"{SYNTHETIC_PHRASE}.md"
            (root / forbidden_name).write_text("clean public text\n", encoding="utf-8")
            subprocess.run(["git", "add", forbidden_name], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "Add historical file"], cwd=root, check=True, stdout=subprocess.DEVNULL)
            (root / forbidden_name).unlink()
            (root / "README.md").write_text("clean current text\n", encoding="utf-8")
            subprocess.run(["git", "add", "-A"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "Remove historical file"], cwd=root, check=True, stdout=subprocess.DEVNULL)

            result = run_guard(
                root,
                "--history",
                "--report-json",
                "--digest",
                SYNTHETIC_DIGEST,
            )

        self.assertNotEqual(result.returncode, 0)
        report = json.loads(result.stdout)
        path_finding = next(finding for finding in report["history"] if finding["kind"] == "history_path")
        self.assertNotIn("path", path_finding)
        self.assertRegex(path_finding["path_sha256"], r"^[0-9a-f]{64}$")
        self.assertNotIn(SYNTHETIC_PHRASE, result.stdout)
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

    def test_skips_local_omx_runtime_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            runtime = root / ".omx" / "state"
            runtime.mkdir(parents=True)
            (runtime / "ledger.jsonl").write_text(SYNTHETIC_PHRASE, encoding="utf-8")
            (root / "README.md").write_text("Public product copy\n", encoding="utf-8")

            result = run_guard(root, "--digest", SYNTHETIC_DIGEST)

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_internal_program_identifiers_without_plaintext_fixture(self) -> None:
        identifiers = (
            bytes((100, 104, 110)).decode("ascii"),
            bytes((100, 104, 110, 57)).decode("ascii"),
            bytes((103, 48, 48, 49)).decode("ascii"),
            bytes((103, 48, 48, 50)).decode("ascii"),
        )
        for identifier in identifiers:
            with self.subTest(identifier_length=len(identifier)), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "README.md").write_text(f"internal plan {identifier}\n", encoding="utf-8")

                result = run_guard(root)

                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn(identifier, result.stderr)

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
        self.assertIn("known internal planning identifiers", text)

    def test_identity_reference_has_no_ambiguous_target_relative_ehl_path(self) -> None:
        text = IDENTITY_REFERENCE.read_text(encoding="utf-8")
        ambiguous_path = "../" + "ehl"

        self.assertNotIn(f"`{ambiguous_path}`", text)
        self.assertIn("workspace-level EHL evidence tree", text)
        self.assertIn("Locate that tree from the workspace root rather than from a target plugin repository", text)
        self.assertIn("Do not treat incidental substrings such as `logo` as log evidence", text)
        self.assertIn("release notes, repository metadata, public source, website/catalog text", text)

    def test_skill_routes_guard_failures_to_safe_history_remediation(self) -> None:
        skill_text = SKILL_MD.read_text(encoding="utf-8")
        remediation_text = HISTORY_REMEDIATION_REFERENCE.read_text(encoding="utf-8")

        self.assertIn("references/history-remediation.md", skill_text)
        self.assertIn("If the history guard fails, stop publication", skill_text)
        self.assertIn("explicit authorization for the exact targets", skill_text)
        self.assertIn("git-filter-repo` 2.47 or newer", remediation_text)
        self.assertIn("fresh clone", remediation_text)
        self.assertIn("git bundle verify", remediation_text)
        self.assertIn("pre- and post-rewrite default-branch tree IDs", remediation_text)
        self.assertIn("GitHub releases are based on Git tags", remediation_text)
        self.assertIn("`refs/backup/*`", remediation_text)
        self.assertIn("`git push --mirror` publishes every local ref", remediation_text)
        self.assertIn("require exact equality with the intended push surface", remediation_text)
        self.assertIn("Never use a writable recovery repository as `origin`", remediation_text)
        self.assertIn("`git push --dry-run --mirror origin`", remediation_text)
        self.assertIn("fail closed", remediation_text)
        self.assertIn("Require collaborators to reclone", remediation_text)
        self.assertIn("never place sensitive plaintext there", remediation_text)


if __name__ == "__main__":
    unittest.main()
