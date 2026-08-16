# DSP, Realtime, and Tests

Use this reference for DSP, parameters, audio callbacks, and behavior changes.

## Primary Research First

Before editing DSP or framework integration, inspect official or primary material for the chosen API, algorithm, codec behavior, format contract, or host expectation. Acceptable evidence includes upstream docs, source, specs, release notes, local vendored headers, or a cited paper. Record exact versions, commits, paths, or URLs.

## Realtime Boundary

Treat `processBlock`, YUP audio callbacks, and every reachable helper as hard realtime:

- allocate and resize during preparation, not per block;
- avoid locks, waits, joins, filesystem/network I/O, logging, exceptions, and unbounded loops;
- bound history scans and feedback paths;
- preserve MIDI sample offsets;
- smooth discontinuous parameter changes;
- define reset, sample-rate, block-size, transport, and bypass behavior;
- reject or sanitize NaN, infinity, denormals, invalid state, and invalid parameters.

Keep editor ownership, preset browsing, file access, and message-thread work outside the audio path.

## Deterministic Tests

Cover changed behavior with deterministic block-level tests:

- silence, impulse, step, sine, and seeded noise inputs;
- mono, stereo, zero-channel, short-block, and maximum-block cases;
- min/default/max parameters plus rapid automation;
- prepare/reset cycles and sample-rate changes;
- MIDI events at sample 0, inside the block, and final sample when MIDI is supported;
- state serialization and parameter ID stability;
- finite output and bounded gain.

Avoid wall-clock assertions unless timing itself is the product contract.

## Audibility and Aggression

EHL effects may be harsh, broken, clipped, noisy, or hostile by design, but they must stay controlled and meaningfully audible.

Add objective checks for:

- RMS or loudness above a practical threshold for non-silent input and enabled processing;
- crest factor, zero-crossing, or spectral spread appropriate to the effect;
- no collapse into all-zero, denormal-only, DC rail, clipped constant, or ultrasonic-only output at extreme settings;
- bounded output suitable for hosts, with documented intentional gain staging;
- reproducible seeded randomness.

When an effect intentionally gates, mutes, freezes, or produces sparse output, test both active-audible and intentional-silence states so a broken always-silent implementation fails.
