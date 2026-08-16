#!/usr/bin/env python3
"""Guard public repositories against internal EHL brand rationale."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

SKIP_DIRS = {
    ".git",
    ".pytest_cache",
    "__pycache__",
    "build",
    "cmake-build-debug",
    "cmake-build-release",
    "node_modules",
}
DEFAULT_WINDOW_SIZE = 3
DEFAULT_FORBIDDEN_DIGESTS = frozenset(
    {
        "977c2908e358e8dcae6fbb4db30ba9c8270086a256010014f553a960855cf56b",
    }
)
TOKEN_RE = re.compile(r"[a-z0-9]+")


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


def scan_files(root: Path, forbidden_digests: set[str], window_size: int) -> list[Path]:
    candidates = sorted(
        {path.resolve() for path in [*tracked_files(root), *walked_files(root)]},
        key=lambda path: str(path),
    )
    offenders: list[Path] = []
    for path in candidates:
        if not path.is_file():
            continue
        try:
            data = path.read_bytes()
        except OSError:
            continue
        text = decode_text(data)
        if text is None:
            continue
        if contains_forbidden_window(text, forbidden_digests, window_size):
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


def scan_history(repo: Path, forbidden_digests: set[str], window_size: int) -> bool:
    if not (repo / ".git").exists():
        return False
    log_text = decode_text(git_output(repo, ["log", "--all", "--format=%B"]))
    if log_text and contains_forbidden_window(log_text, forbidden_digests, window_size):
        return True
    commits = [line.decode("ascii") for line in git_output(repo, ["rev-list", "--all"]).splitlines() if line]
    for commit in commits:
        entries = [entry for entry in git_output(repo, ["ls-tree", "-rz", commit]).split(b"\0") if entry]
        for entry in entries:
            metadata, _, _path = entry.partition(b"\t")
            parts = metadata.split()
            if len(parts) < 3 or parts[1] != b"blob":
                continue
            text = decode_text(git_output(repo, ["cat-file", "-p", parts[2].decode("ascii")]))
            if text and contains_forbidden_window(text, forbidden_digests, window_size):
                return True
    return False


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
    args = parser.parse_args()

    if args.window_size < 1:
        fail("invalid guard configuration")
    root = Path(args.root).resolve()
    forbidden_digests = set(DEFAULT_FORBIDDEN_DIGESTS) | set(args.digest)
    offenders = scan_files(root, forbidden_digests, args.window_size)
    if offenders:
        fail("internal brand rationale found in public text")
    if args.history and scan_history(root, forbidden_digests, args.window_size):
        fail("internal brand rationale found in repository history")
    print("PASS: public text guard")


if __name__ == "__main__":
    main()
