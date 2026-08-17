#!/usr/bin/env python3
"""Guard public repositories against internal EHL brand rationale."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SKIP_DIRS = {
    ".git",
    ".omx",
    ".pytest_cache",
    "__pycache__",
    "build",
    "cmake-build-debug",
    "cmake-build-release",
    "node_modules",
}
DEFAULT_WINDOW_SIZE = 3
DEFAULT_COMPACT_WINDOW_SIZE = 17
DEFAULT_FORBIDDEN_DIGESTS = frozenset(
    {
        "977c2908e358e8dcae6fbb4db30ba9c8270086a256010014f553a960855cf56b",
    }
)
DEFAULT_FORBIDDEN_COMPACT_DIGESTS = frozenset(
    {
        "df72b45f82869a738a4b6548b7860129cd368209ac73577210765c4b929b17ee",
    }
)
DEFAULT_INTERNAL_TOKEN_DIGESTS = frozenset(
    {
        "338fd9894b114dba6235ea4f939c51c7bb7038dd4f79f4c9985c26ae5217e64d",
        "4888ae60e130799ef640565aa8aa6eb87eb4f96031e37db5af52a11ab495380b",
        "a2374cbb852d23661bc798d061e033606a66cda16a16cd31defc38fa5670f864",
        "68b5100223908763dfb6b9e39ed35d8456a840b337df0244782a9565fb4cdeff",
    }
)
TOKEN_RE = re.compile(r"[a-z0-9]+")
ALNUM_RE = re.compile(r"[a-z0-9]")
REGEX_QUANTIFIER_RE = r"(?:[+*?]|\{\d+(?:,\d*)?\})?"
WHITESPACE_ESCAPE_RE = (
    r"\\{1,2}(?:[sbdwnrt]|x(?:09|0a|0d|20|a0)|u(?:0009|000a|000d|0020|00a0)"
    r"|U(?:00000009|0000000a|0000000d|00000020|000000a0))"
)
PERCENT_WHITESPACE_RE = r"%(?:09|0a|0d|20|a0)"
HTML_WHITESPACE_RE = r"&(?:nbsp|\#(?:0*9|0*10|0*13|0*32|0*160|x0*(?:9|a|d|20|a0)));"
REGEX_SEPARATOR_RE = re.compile(
    "|".join(
        (
            rf"(?:{WHITESPACE_ESCAPE_RE}{REGEX_QUANTIFIER_RE})",
            rf"(?:{PERCENT_WHITESPACE_RE}{REGEX_QUANTIFIER_RE})",
            rf"(?:{HTML_WHITESPACE_RE}{REGEX_QUANTIFIER_RE})",
            rf"(?:\[(?:{WHITESPACE_ESCAPE_RE}|[^\]])+\]{REGEX_QUANTIFIER_RE})",
            r"(?:\(\?[:=!<][^)]*\))",
            r"(?:[\\|+*?^$()[\]{}.,;:_/\-]+)",
        )
    ),
    re.IGNORECASE | re.VERBOSE,
)


def fail(message: str = "public text guard failed") -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def tracked_files(repo: Path) -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "ls-files", "-z"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []
    names = [name for name in result.stdout.decode("utf-8", "replace").split("\0") if name]
    return [repo / name for name in names]


def walked_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for current, dirs, names in os.walk(root):
        dirs[:] = [name for name in dirs if name not in SKIP_DIRS]
        base = Path(current)
        files.extend(base / name for name in names)
    return files


def decode_text(data: bytes) -> str | None:
    if b"\0" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def token_window_digests(text: str, window_size: int) -> set[str]:
    tokens = TOKEN_RE.findall(text.casefold())
    if len(tokens) < window_size:
        return set()
    digests: set[str] = set()
    for index in range(0, len(tokens) - window_size + 1):
        window = " ".join(tokens[index : index + window_size])
        digests.add(hashlib.sha256(window.encode("utf-8")).hexdigest())
    return digests


def contains_forbidden_window(text: str, forbidden_digests: set[str], window_size: int) -> bool:
    return bool(token_window_digests(text, window_size) & forbidden_digests)


def contains_internal_identifier(text: str) -> bool:
    return any(
        hashlib.sha256(token.encode("utf-8")).hexdigest() in DEFAULT_INTERNAL_TOKEN_DIGESTS
        for token in TOKEN_RE.findall(text.casefold())
    )


def compact_window_digests(text: str, window_size: int) -> set[str]:
    compact = "".join(ALNUM_RE.findall(text.casefold()))
    if len(compact) < window_size:
        return set()
    digests: set[str] = set()
    for index in range(0, len(compact) - window_size + 1):
        window = compact[index : index + window_size]
        digests.add(hashlib.sha256(window.encode("utf-8")).hexdigest())
    return digests


def reconstructable_text_variants(text: str) -> tuple[str, str]:
    return (text, REGEX_SEPARATOR_RE.sub(" ", text))


def contains_forbidden_compact(text: str, forbidden_digests: set[str], window_size: int) -> bool:
    return any(
        compact_window_digests(variant, window_size) & forbidden_digests
        for variant in reconstructable_text_variants(text)
    )


def contains_forbidden(
    text: str,
    forbidden_digests: set[str],
    window_size: int,
    forbidden_compact_digests: set[str],
    compact_window_size: int,
) -> bool:
    return (
        contains_forbidden_window(text, forbidden_digests, window_size)
        or contains_forbidden_compact(text, forbidden_compact_digests, compact_window_size)
        or contains_internal_identifier(text)
    )


def scan_files(
    root: Path,
    forbidden_digests: set[str],
    window_size: int,
    forbidden_compact_digests: set[str],
    compact_window_size: int,
) -> list[Path]:
    candidates = sorted(
        {path.resolve() for path in [*tracked_files(root), *walked_files(root)]},
        key=lambda path: str(path),
    )
    offenders: list[Path] = []
    for path in candidates:
        if not path.is_file():
            continue
        try:
            relative_path = str(path.relative_to(root))
        except ValueError:
            relative_path = str(path)
        if contains_forbidden(relative_path, forbidden_digests, window_size, forbidden_compact_digests, compact_window_size):
            offenders.append(path)
            continue
        try:
            data = path.read_bytes()
        except OSError:
            continue
        text = decode_text(data)
        if text is None:
            continue
        if contains_forbidden(text, forbidden_digests, window_size, forbidden_compact_digests, compact_window_size):
            offenders.append(path)
    return offenders


def git_output(repo: Path, args: list[str]) -> bytes:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return b""
    return result.stdout


def scan_history(
    repo: Path,
    forbidden_digests: set[str],
    window_size: int,
    forbidden_compact_digests: set[str],
    compact_window_size: int,
) -> bool:
    if not (repo / ".git").exists():
        return False
    log_text = decode_text(git_output(repo, ["log", "--all", "--format=%B"]))
    if log_text and contains_forbidden(log_text, forbidden_digests, window_size, forbidden_compact_digests, compact_window_size):
        return True
    commits = [line.decode("ascii") for line in git_output(repo, ["rev-list", "--all"]).splitlines() if line]
    for commit in commits:
        entries = [entry for entry in git_output(repo, ["ls-tree", "-rz", commit]).split(b"\0") if entry]
        for entry in entries:
            metadata, _, path_bytes = entry.partition(b"\t")
            parts = metadata.split()
            if len(parts) < 3 or parts[1] != b"blob":
                continue
            path_text = decode_text(path_bytes)
            if path_text and contains_forbidden(path_text, forbidden_digests, window_size, forbidden_compact_digests, compact_window_size):
                return True
            text = decode_text(git_output(repo, ["cat-file", "-p", parts[2].decode("ascii")]))
            if text and contains_forbidden(text, forbidden_digests, window_size, forbidden_compact_digests, compact_window_size):
                return True
    return False


def safe_path_finding(
    kind: str,
    path_text: str,
    forbidden_digests: set[str],
    window_size: int,
    forbidden_compact_digests: set[str],
    compact_window_size: int,
    **metadata: str,
) -> dict[str, str]:
    finding = {
        "kind": kind,
        "path_sha256": hashlib.sha256(path_text.encode("utf-8")).hexdigest(),
        **metadata,
    }
    if not contains_forbidden(
        path_text,
        forbidden_digests,
        window_size,
        forbidden_compact_digests,
        compact_window_size,
    ):
        finding["path"] = path_text
    return finding


def report_current_findings(
    root: Path,
    offenders: list[Path],
    forbidden_digests: set[str],
    window_size: int,
    forbidden_compact_digests: set[str],
    compact_window_size: int,
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for path in offenders:
        try:
            path_text = str(path.relative_to(root))
        except ValueError:
            path_text = str(path)
        path_is_forbidden = contains_forbidden(
            path_text,
            forbidden_digests,
            window_size,
            forbidden_compact_digests,
            compact_window_size,
        )
        findings.append(
            safe_path_finding(
                "current_path" if path_is_forbidden else "current_content",
                path_text,
                forbidden_digests,
                window_size,
                forbidden_compact_digests,
                compact_window_size,
            )
        )
    return findings


def report_history_findings(
    repo: Path,
    forbidden_digests: set[str],
    window_size: int,
    forbidden_compact_digests: set[str],
    compact_window_size: int,
) -> list[dict[str, str]]:
    if not (repo / ".git").exists():
        return []
    findings: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    blob_matches: dict[str, bool] = {}
    commits = [line.decode("ascii") for line in git_output(repo, ["rev-list", "--all"]).splitlines() if line]
    for commit in commits:
        message = decode_text(git_output(repo, ["show", "-s", "--format=%B", commit]))
        if message and contains_forbidden(
            message,
            forbidden_digests,
            window_size,
            forbidden_compact_digests,
            compact_window_size,
        ):
            findings.append({"kind": "history_message", "commit": commit})
        entries = [entry for entry in git_output(repo, ["ls-tree", "-rz", commit]).split(b"\0") if entry]
        for entry in entries:
            metadata, _, path_bytes = entry.partition(b"\t")
            parts = metadata.split()
            if len(parts) < 3 or parts[1] != b"blob":
                continue
            blob = parts[2].decode("ascii")
            path_text = decode_text(path_bytes)
            if path_text and contains_forbidden(
                path_text,
                forbidden_digests,
                window_size,
                forbidden_compact_digests,
                compact_window_size,
            ):
                key = ("history_path", hashlib.sha256(path_text.encode("utf-8")).hexdigest())
                if key not in seen:
                    seen.add(key)
                    findings.append(
                        safe_path_finding(
                            "history_path",
                            path_text,
                            forbidden_digests,
                            window_size,
                            forbidden_compact_digests,
                            compact_window_size,
                            commit=commit,
                            blob=blob,
                        )
                    )
            if blob not in blob_matches:
                text = decode_text(git_output(repo, ["cat-file", "-p", blob]))
                blob_matches[blob] = bool(
                    text
                    and contains_forbidden(
                        text,
                        forbidden_digests,
                        window_size,
                        forbidden_compact_digests,
                        compact_window_size,
                    )
                )
            if blob_matches[blob]:
                key = ("history_blob", blob)
                if key not in seen:
                    seen.add(key)
                    findings.append(
                        safe_path_finding(
                            "history_blob",
                            path_text or "",
                            forbidden_digests,
                            window_size,
                            forbidden_compact_digests,
                            compact_window_size,
                            commit=commit,
                            blob=blob,
                        )
                    )
    return sorted(
        findings,
        key=lambda finding: (
            finding["kind"],
            finding.get("commit", ""),
            finding.get("path_sha256", ""),
            finding.get("blob", ""),
        ),
    )


def digest_arg(value: str) -> str:
    if not re.fullmatch(r"[0-9a-f]{64}", value):
        raise argparse.ArgumentTypeError("digest must be 64 lowercase hex characters")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description="Guard public EHL text")
    parser.add_argument("root", nargs="?", default=".", help="repository root to scan")
    parser.add_argument("--history", action="store_true", help="also scan git commit messages and tracked text blobs")
    parser.add_argument("--digest", action="append", type=digest_arg, default=[], help=argparse.SUPPRESS)
    parser.add_argument("--window-size", type=int, default=DEFAULT_WINDOW_SIZE, help=argparse.SUPPRESS)
    parser.add_argument("--compact-digest", action="append", type=digest_arg, default=[], help=argparse.SUPPRESS)
    parser.add_argument("--compact-window-size", type=int, default=DEFAULT_COMPACT_WINDOW_SIZE, help=argparse.SUPPRESS)
    parser.add_argument(
        "--report-json",
        action="store_true",
        help="emit redacted offender metadata without printing matched text",
    )
    args = parser.parse_args()

    if args.window_size < 1 or args.compact_window_size < 1:
        fail("invalid guard configuration")
    root = Path(args.root).resolve()
    forbidden_digests = set(DEFAULT_FORBIDDEN_DIGESTS) | set(args.digest)
    forbidden_compact_digests = set(DEFAULT_FORBIDDEN_COMPACT_DIGESTS) | set(args.compact_digest)
    offenders = scan_files(root, forbidden_digests, args.window_size, forbidden_compact_digests, args.compact_window_size)
    history_findings: list[dict[str, str]] = []
    if args.history and args.report_json:
        history_findings = report_history_findings(
            root,
            forbidden_digests,
            args.window_size,
            forbidden_compact_digests,
            args.compact_window_size,
        )
    history_failed = bool(history_findings) if args.report_json else args.history and scan_history(
        root,
        forbidden_digests,
        args.window_size,
        forbidden_compact_digests,
        args.compact_window_size,
    )
    if args.report_json:
        report = {
            "schema": "ehl-public-text-report-v1",
            "result": "fail" if offenders or history_failed else "pass",
            "current": report_current_findings(
                root,
                offenders,
                forbidden_digests,
                args.window_size,
                forbidden_compact_digests,
                args.compact_window_size,
            ),
            "history": history_findings,
        }
        print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    if offenders:
        fail("internal brand rationale found in public text")
    if history_failed:
        fail("internal brand rationale found in repository history")
    if not args.report_json:
        print("PASS: public text guard")


if __name__ == "__main__":
    main()
