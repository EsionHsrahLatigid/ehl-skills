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

## Current-tree cleanup preflight

- Run the bundled guard against both the proposed current tree and the exact patch that would become public. A clean resulting file does not make its conventional commit, pull-request, or forge diff safe when removed protected text remains visible in that patch.
- If the patch guard fails, do not print, paste, review, commit, push, or publish the conventional diff. Preserve the candidate only in a private local path-limited stash or equivalent recovery snapshot, identified by metadata rather than content.
- Leave the public branch and worktree unchanged until an exact history-safe remediation path is authorized. Do not convert the cleanup into an ordinary commit merely to make the current-tree guard pass.
- Treat applying or publishing a history-safe replacement as the same explicit-authorization boundary as ref rewriting. Resolve the exact repositories and refs first, then follow the private recovery, isolated rewrite, verification, and authorized publication gates below.

## Private recovery snapshot

1. Fetch all branches and tags in the source repository.
2. Require a clean worktree and prove the local default branch equals its remote-tracking branch.
3. Create a recovery-only bundle with all refs outside every public repository.
4. Store the bundle in a mode `0700` directory with mode `0600`, verify it with `git bundle verify`, and record its SHA-256.
5. Record pre-rewrite heads, tags, release targets, open pull requests, forks, LFS use, submodules, branch protections, and rulesets.
6. Mark the bundle and manifest `DO NOT PUBLISH`. They intentionally retain the old history.
7. Enumerate every ref namespace in the bundle. Recovery bundles may legitimately retain `refs/backup/*`, `refs/remotes/*`, or other private refs, but those refs are never part of the publication surface.

## Isolated rewrite

1. Use a fresh clone for each repository. Do not rewrite a development checkout or bypass the fresh-clone check with `--force`.
2. Keep any replacement specification outside the clone, mode `0600`, untracked, and out of logs and Obsidian. Remove it only after verification and authorized publication are complete.
3. Run `git filter-repo --sensitive-data-removal` with the narrowest applicable operation:
   - Remove a historical path with `--invert-paths --path`.
   - Replace blob text with `--replace-text`.
   - Replace commit or tag messages with `--replace-message` or a message callback.
   - Use callbacks only when path or encoding variants cannot be handled safely by the simpler operations.
4. Capture `.git/filter-repo/commit-map`, `changed-refs`, first-changed commits, and any orphaned-LFS report.
5. Do not add recovery refs or backup branches to the rewritten repository. A mirror clone made from a recovery bundle may import non-public refs even when local branch inspection looked clean.

## Local verification before publication

- Run the bundled public-text guard with `--history` against the isolated rewritten clone.
- Compare the pre- and post-rewrite default-branch tree IDs. They must remain identical when the current public tree was already clean.
- Verify every branch and tag expected by the preflight manifest, and confirm no unexpected refs were created.
- Define the intended push surface as the exact public `refs/heads/*` and `refs/tags/*` set. Before adding a public remote, remove `refs/backup/*`, `refs/remotes/*`, `refs/original/*`, recovery refs, and every other non-public namespace from the isolated publication clone.
- Remember that `git push --mirror` publishes every local ref, not just branches and tags. Enumerate all remaining refs and require exact equality with the intended push surface.
- Keep the rewrite clone's `origin` absent or pointed only at a non-pushable, read-only bundle URL until publication is explicitly authorized. Never use a writable recovery repository as `origin`; an accidental mirror push could damage the recovery source. The absent or non-pushable configuration makes accidental publication fail closed.
- Re-run project-specific tests and metadata checks when the rewrite changes the current tree. A history-only rewrite does not waive release verification.
- Review release tags because GitHub releases are based on Git tags. A moved tag changes the repository snapshot associated with that release.

## Authorized publication

1. Reconfirm the repository write freeze and remote heads immediately before pushing.
2. Add or replace `origin` with the exact authorized public repository only after the local ref-set checks pass. Review `git push --dry-run --mirror origin` and reject any ref creation, deletion, or update outside the approved heads and tags.
3. Force-push the rewritten mirror only after exact-target authorization. Expect forge-managed `refs/pull/*` to reject updates because GitHub marks them read-only.
4. Change branch protection only when a verified non-PR ref is rejected, and restore it immediately afterward.
5. Delete only the release assets and workflow artifacts whose exact IDs failed verification. Preserve safe platform siblings.
6. Never upload the recovery bundle, replacement specification, old-to-new commit map, or private audit material.

## Server and collaborator cleanup

- Count affected pull requests from `changed-refs`. If inaccessible PR refs, cached views, or unreachable objects remain and the data qualifies for GitHub Support removal, provide Support the repository, affected PR count, first-changed commits, and orphaned-LFS report. GitHub documents that Support removal is limited to sensitive data.
- Require collaborators to reclone when possible. Otherwise require rebase rather than merge, deletion of old tags and refs, reflog expiry, and garbage collection before any push.
- Audit forks. Any fork retaining an old commit remains a separate exposure and recontamination source.

## Completion gate

- Clone the remote again into a clean verification directory.
- Run the current-tree and full-history guards there.
- Verify default branch, tags, releases, safe assets, CI, signatures, website/catalog links, and release downloads at the rewritten SHAs.
- Record the old-to-new mapping and verification evidence only in private approved storage and the configured internal knowledge system; never place sensitive plaintext there.
