# EHL Identity and Design

Use this reference for metadata, UI, shared design modules, assets, README copy, repository descriptions, installers, screenshots, social previews, and website/catalog updates.

## Sources

- Discover project-local design rules first: `design_rules/DESIGN_RULES.md`, `.agents`, `.codex`, repository README files, and checked-in design docs near the active plugin.
- When working in a local workspace with a workspace-level EHL evidence tree that is a sibling of the active workspace root, it may contain design rules, the public web verifier, session evidence, and git history. Locate that tree from the workspace root rather than from a target plugin repository; in this workspace it is `/Users/2bit/prog/ehl`. Treat sibling paths as local examples only; do not bake them into public guidance, generated code, CI, or reusable commands.
- When the workspace-level EHL evidence tree exists, explicitly check relevant `**/*session*`, `**/*log*`, `**/*timeline*`, `**/*handover*`, `**/*memo*`, and `**/*decision*` files before changing public identity or release guidance. Record the files consulted or that no matching ordinary durable evidence exists. If there are no ordinary durable evidence files, inspect nested git repositories under the tree, including recent logs, relevant public-copy commits, and verifier history, and record what was consulted.
- When installed, read the `ehl-design` skill and only the relevant bundled references for brand, logo, output profile, Canva, or plugin UI work.
- Read the target repository's design module, submodule, or pinned dependency state.
- If an EHL web repository is available, treat its verifier and the commit that removed internal rationale from public copy as durable evidence that internal brand rationale must be absent from public surfaces.

## Public Identity

- Public brand: `EsionHsrahLatigid`.
- Public copy may describe the work as experimental, digital, harsh, noisy, technical, underground, precise, and audio-tool oriented.
- Do not expose, translate, explain, or quote internal source rationale in public-facing surfaces, release notes, repository metadata, public source, website/catalog text, commit messages, or commit history. Never surface the private descriptor on public-facing surfaces.
- Resolve the bundled guard from the loaded `SKILL.md` directory and run `python3 <skill-dir>/scripts/check_public_text.py --history <consumer-repo>` before publishing or updating public copy.

## Plugin UI

- Use a compact, operational, monochrome 8-bit UI system.
- Express controlled glitch, jagged pixel geometry, direct construction, and underground restraint through layout and state, not decorative clutter.
- Prefer one primary readout or visualizer and one to three control groups.
- Keep the editor as compact as the verified workflow allows; no fixed size is mandatory.
- Avoid neon cyberpunk, RGB split, generic glitch fonts, fake hardware, decorative frames, blur, glow, and waveform logos.
- Keep labels and values clean. Damage belongs in brand forms or sparse non-operational accents, not in essential text.

## Shared Modules

- JUCE production plugins use `juce-ehl-design-module`.
- YUP production plugins use `yup-ehl-design-module`.
- Use the canonical short `ehl` mark for compact headers. Do not substitute typed `EHL`, full brand text, a raster copy, or a consumer-local SVG path.
- Treat logo geometry, viewBox, path data, header bounds, and scale behavior as shared contracts. Update modules and consumers together.

## Verification

Inspect actual plugin windows or exported assets at target size. Verify text fit, state legibility, grayscale meaning, high contrast, target hit areas, logo source, and absence of prohibited public copy.
