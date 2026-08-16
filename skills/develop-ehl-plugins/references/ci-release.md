# CI, Release, and Website Gates

Use this reference for workflows, release artifacts, GitHub publication, and public catalog updates.

## Repository

- Publish EHL plugins under `EsionHsrahLatigid/<repo>`.
- Keep product name, repository name, bundle ID, artifact names, README commands, screenshots, and release text aligned.
- Make small English commits with detailed bodies. Never include internal brand rationale in commit messages.

## CI

- Prefer reusable EHL workflows when the repository already uses them.
- Pin reusable workflow versions intentionally: stable tag for compatible updates or exact commit for immutable supply-chain policy.
- For JUCE, include plugin build targets and tests for requested formats.
- For YUP, build `engine-debug` and `plugin-release` presets when available.
- Confirm cache behavior after CI changes: default-branch success saves caches; rerun the same commit to prove exact restore when cache behavior is part of the change.

## Artifacts

- Release ZIPs must contain stable, documented surfaces, not generator-dependent build folders.
- Include Standalone, VST3, AU, checksums, and `ARTIFACTS.txt` where the project supports them.
- On macOS, verify signatures for `.app`, `.vst3`, and `.component` bundles.
- Verify that the latest release, latest workflow artifact, README download instructions, and repository release notes point to the same build output.
- Record exact ZIP names, checksums, sizes, release URL, workflow URL, and commit SHA.

## Web/Catalog Final Gate

Update the public website/catalog only after:

1. local tests pass;
2. plugin artifacts are verified;
3. public-text guard passes against the plugin repo and this skill when relevant;
4. release or latest artifact URLs are stable;
5. the web verifier passes in the website repository;
6. the web deployment reports success.

If any gate fails, stop before publishing web copy and report the failing command or URL.
