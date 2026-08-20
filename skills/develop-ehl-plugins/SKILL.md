---
name: develop-ehl-plugins
description: Build, test, review, package, and release EsionHsrahLatigid audio plugins across JUCE and YUP. Use when Codex works on EHL plugin repositories, DSP behavior, JUCE CMake projects, YUP CMake presets, plugin identity, realtime audio safety, deterministic DSP tests, EHL visual integration, CI artifacts, release ZIPs, GitHub organization publication, or final website/catalog update gates.
---

# Develop EHL Plugins

Develop EsionHsrahLatigid plugins with evidence-first research, framework-specific build paths, hard realtime safety, deterministic tests, audibility checks, EHL design conformance, and verified release artifacts.

## Start

1. Read repository guidance, README, build presets, workflows, and existing tests before editing.
2. Identify framework:
   - JUCE: `juce_add_plugin`, JUCE modules, Projucer or CMake plugin targets.
   - YUP: evidenced `yup_audio_plugin`, `CMakePresets.json`, `engine-debug`, `plugin-release`, or `ehl_stage_products`.
3. Before DSP or release decisions, inspect official or primary sources for the framework/API/library behavior being changed. Use local vendored docs when present; otherwise use upstream documentation or source. Record the source path, URL, version, or commit in the task evidence.
4. For EHL design, discover project-local design rules first, then the workspace-level EHL evidence tree that is a sibling of the active workspace root, the installed `ehl-design` references, and the target design module or submodule state. Do not resolve the evidence tree relative to a target plugin repository; in this workspace, the sibling evidence tree is `/Users/2bit/prog/ehl`.
5. When the workspace-level EHL evidence tree exists, inspect ordinary durable evidence files whose paths or names match session, log, timeline, handover, memo, or decision before changing public-facing guidance. Match those terms as whole path tokens or by the file's documented purpose; a substring such as `logo` is not log evidence. Exclude `.git`, dependency, build, cache, generated, and design-asset trees from this ordinary-evidence pass. If no ordinary durable evidence files exist, inspect nested git repositories under that tree: recent logs, relevant history, public-copy verifier scripts, and commits that changed public identity copy. Record the tree path, matching files found or absent, nested repositories consulted, relevant commits, and verifier paths in task evidence.
6. Treat the public identity as `EsionHsrahLatigid`; keep the private descriptor, known internal planning identifiers, and internal brand rationale out of the current public tree, metadata, UI, release notes, repository metadata, public source, website/catalog text, artifacts, and new commit messages. This also forbids regex, escaped, split, compact, camel-case, embedded, or filename spelling that a human could easily reconstruct as the private descriptor, including encoded whitespace separators. Existing public Git history and cleanup diffs may retain the text and are non-gating. Use the bundled hash-based public-text guard instead of adding plaintext fixtures or prose.
7. For durable work, capture evidence in Obsidian through the configured Obsidian workflow when available: source facts, test commands, artifact paths, CI run links, decisions, and unresolved risks. Do not store secrets, private descriptors, or internal rationale.

## Route By Framework

- JUCE project work: read [references/juce.md](references/juce.md).
- YUP project work: read [references/yup.md](references/yup.md).
- DSP, realtime callback, or test behavior: read [references/dsp-realtime-tests.md](references/dsp-realtime-tests.md).
- Identity, shared logo modules, UI, or public-facing copy: read [references/ehl-identity-design.md](references/ehl-identity-design.md).
- CI, release ZIPs, latest artifacts, or website/catalog updates: read [references/ci-release.md](references/ci-release.md).
- Actual credential exposure, legal removal requests, or explicitly requested history remediation: read [references/history-remediation.md](references/history-remediation.md).

Read only the references needed for the active task, but always combine identity/design with release work because public surfaces are involved.

## Non-Negotiable Gates

- Keep plugin identity stable after release: manufacturer `EsionHsrahLatigid`, manufacturer code `EHL_`, bundle IDs under `jp.ehl.`, GitHub owner `EsionHsrahLatigid`, and unique four-character plugin codes where the framework requires them.
- Keep the audio callback allocation-free and bounded; no locks, file/network I/O, logging, exceptions, unbounded loops, or UI ownership on the realtime path.
- Add deterministic tests for changed DSP behavior before broad packaging claims.
- For aggressive distortion, corruption, noise, or glitch effects, prove the output remains intentionally audible at useful settings and extremes. Prevent failures that collapse into perceived silence, DC rails, clipped constants, NaN/Inf, denormal stalls, ultrasonic-only energy, or host-dangerous output.
- Preserve EHL design module boundaries: production JUCE code uses `juce-ehl-design-module`; production YUP code uses `yup-ehl-design-module`. Do not copy local logo paths into consumer plugins.
- Resolve the bundled guard relative to the loaded `SKILL.md` directory and run `python3 <skill-dir>/scripts/check_public_text.py <consumer-repo>` before public commits, releases, website updates, or other public-surface changes.
- If the current-tree guard fails, clean the current public files before publication. A conventional cleanup commit is allowed even when its diff and Git history retain removed text. Do not rewrite refs or history solely for this public-copy policy.
- Make small commits with English subjects and detailed bodies. Do not include private rationale in commit messages.
- After plugin publication, update the public web/catalog only after artifact verification, public copy verification, and the website verifier pass.

## Verification

Report the concrete evidence that matches the change:

- primary sources consulted;
- files changed;
- test commands and pass/fail output;
- build/typecheck/plugin validation commands;
- artifact paths, checksums, code signatures, and installed copy paths where applicable;
- public-text guard result;
- CI run URLs, release URLs, and latest ZIP names when publishing;
- Obsidian note path or reason it was unavailable.
