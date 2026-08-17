# Published History and Artifact Remediation

Use this reference only when the bundled public-text guard fails on published history, a release asset, a workflow artifact, a cached view, or a forge-managed ref.

## Primary sources

- [git-filter-repo manual](https://github.com/newren/git-filter-repo/blob/main/Documentation/git-filter-repo.txt)
- [GitHub: Removing sensitive data from a repository](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [GitHub: About releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)

Use `git-filter-repo` 2.47 or newer for `--sensitive-data-removal`. Do not substitute legacy `filter-branch` for this workflow.

## Authorization boundary

- Treat ref rewriting, force-pushing, release-asset deletion, workflow-artifact deletion, branch-protection changes, repository deletion, and support requests as explicit-authorization operations.
- Resolve exact repository names, refs, tags, release asset IDs, and workflow artifact IDs before requesting authorization.
- Freeze pushes and merges during the rewrite window. Concurrent changes can be lost or reintroduce removed history.

## Private recovery snapshot

1. Fetch all branches and tags in the source repository.
2. Require a clean worktree and prove the local default branch equals its remote-tracking branch.
3. Create a recovery-only bundle with all refs outside every public repository.
4. Store the bundle in a mode `0700` directory with mode `0600`, verify it with `git bundle verify`, and record its SHA-256.
5. Record pre-rewrite heads, tags, release targets, open pull requests, forks, LFS use, submodules, branch protections, and rulesets.
6. Mark the bundle and manifest `DO NOT PUBLISH`. They intentionally retain the old history.

## Isolated rewrite

1. Use a fresh clone for each repository. Do not rewrite a development checkout or bypass the fresh-clone check with `--force`.
2. Keep any replacement specification outside the clone, mode `0600`, untracked, and out of logs and Obsidian. Remove it only after verification and authorized publication are complete.
3. Run `git filter-repo --sensitive-data-removal` with the narrowest applicable operation:
   - Remove a historical path with `--invert-paths --path`.
   - Replace blob text with `--replace-text`.
   - Replace commit or tag messages with `--replace-message` or a message callback.
   - Use callbacks only when path or encoding variants cannot be handled safely by the simpler operations.
4. Capture `.git/filter-repo/commit-map`, `changed-refs`, first-changed commits, and any orphaned-LFS report.
5. Do not add recovery refs or backup branches to the rewritten repository.

## Local verification before publication

- Run the bundled public-text guard with `--history` against the isolated rewritten clone.
- Compare the pre- and post-rewrite default-branch tree IDs. They must remain identical when the current public tree was already clean.
- Verify every branch and tag expected by the preflight manifest, and confirm no unexpected refs were created.
- Re-run project-specific tests and metadata checks when the rewrite changes the current tree. A history-only rewrite does not waive release verification.
- Review release tags because GitHub releases are based on Git tags. A moved tag changes the repository snapshot associated with that release.

## Authorized publication

1. Reconfirm the repository write freeze and remote heads immediately before pushing.
2. Force-push the rewritten mirror only after exact-target authorization. Expect forge-managed `refs/pull/*` to reject updates because GitHub marks them read-only.
3. Change branch protection only when a verified non-PR ref is rejected, and restore it immediately afterward.
4. Delete only the release assets and workflow artifacts whose exact IDs failed verification. Preserve safe platform siblings.
5. Never upload the recovery bundle, replacement specification, old-to-new commit map, or private audit material.

## Server and collaborator cleanup

- Count affected pull requests from `changed-refs`. If inaccessible PR refs, cached views, or unreachable objects remain and the data qualifies for GitHub Support removal, provide Support the repository, affected PR count, first-changed commits, and orphaned-LFS report. GitHub documents that Support removal is limited to sensitive data.
- Require collaborators to reclone when possible. Otherwise require rebase rather than merge, deletion of old tags and refs, reflog expiry, and garbage collection before any push.
- Audit forks. Any fork retaining an old commit remains a separate exposure and recontamination source.

## Completion gate

- Clone the remote again into a clean verification directory.
- Run the current-tree and full-history guards there.
- Verify default branch, tags, releases, safe assets, CI, signatures, website/catalog links, and release downloads at the rewritten SHAs.
- Record the old-to-new mapping and verification evidence only in private approved storage and the configured internal knowledge system; never place sensitive plaintext there.
