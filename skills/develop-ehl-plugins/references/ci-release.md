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
- CI artifacts may use ad-hoc signatures for build-time validation, but never promote an ad-hoc or unsigned macOS ZIP as a public release asset.
- Public macOS releases must sign `.app`, `.vst3`, and `.component` bundles with Developer ID Application, Hardened Runtime, and a secure timestamp.
- Notarize with `notarytool` using an App Store Connect Team API key. Individual API keys are not supported by `notarytool`.
- Submit a temporary ZIP for notarization, staple and validate every distributable bundle, then create and verify a fresh final ZIP. A ZIP itself cannot carry a stapled ticket.
- Sign nested Mach-O code before its containing bundle, verify the expected Apple Team ID and absence of `get-task-allow`, and fail closed on unrecognized nested code containers.
- Verify that the latest release, latest workflow artifact, README download instructions, and repository release notes point to the same build output.
- Record exact ZIP names, checksums, sizes, release URL, workflow URL, and commit SHA.

## Signing secret contract

- Keep certificate and notarization credentials in GitHub Secrets; never commit or print them.
- Reusable workflow callers map these named secrets explicitly: `MACOS_CERTIFICATE_P12_BASE64`, `MACOS_CERTIFICATE_PASSWORD`, `APPLE_TEAM_ID`, `APPLE_API_KEY_ID`, `APPLE_API_ISSUER_ID`, and `APPLE_API_PRIVATE_KEY_P8_BASE64`.
- Restrict the certificate and private key to the macOS signing job. Provenance resolution and public release publication do not need those secrets.
- Put signing and publication behind the caller repository's protected `release` environment, with tag/branch restrictions and required reviewers. Keep credential values in organization/repository secrets and do not shadow them with same-named environment secrets.
- Import the certificate into an ephemeral keychain, use an exact Team ID identity match, and remove all temporary key and keychain material on exit.
- Serialize release runs by repository and tag without cancelling an in-flight notarization.
- Pin shared workflows and the common signing action to immutable full commit SHAs.

## Web/Catalog Final Gate

Update the public website/catalog only after:

1. local tests pass;
2. plugin artifacts are verified;
3. public-text guard passes against the plugin repo and this skill when relevant;
4. release or latest artifact URLs are stable;
5. the web verifier passes in the website repository;
6. the web deployment reports success.

If any gate fails, stop before publishing web copy and report the failing command or URL.
