# YUP Projects

Use this reference for EHL plugins built with YUP and CMake presets.

## Discovery

- Confirm `CMakeLists.txt` and `CMakePresets.json` exist.
- Read presets before running commands. Preserve project-specific options, target names, plugin formats, helper modules, and install paths.
- Identify the plugin declaration through the evidenced helper `yup_audio_plugin`. If a target uses another helper form, confirm it from local YUP CMake source before documenting or editing it.
- Inspect `cmake/EhlYupArtifactLayout.cmake`, `cmake/StageYupProducts.cmake`, icon helpers, `TARGET_*`, `PLUGIN_*`, and any vendored `yup-ehl-design-module` pointer.
- Confirm the YUP revision or source commit before relying on API behavior.

## Build

Run the fast engine profile first when available:

```sh
cmake --preset engine-debug
cmake --build --preset engine-debug --parallel
ctest --preset engine-debug --output-on-failure
```

Then build distributable products:

```sh
cmake --preset plugin-release
cmake --build --preset plugin-release --parallel
ctest --preset plugin-release --output-on-failure
```

## Artifact Contract

The stable output surface is:

```text
artifacts/
└── plugin-release/
    └── <platform-arch>/
        ├── standalone/
        ├── vst3/
        ├── au/
        └── ARTIFACTS.txt
```

Local macOS builds may also copy VST3 and AU bundles to the current user's plugin folders through `ehl_stage_products`. Do not direct users to generator-dependent build subdirectories as the release surface.

Verify staged and installed products with `ARTIFACTS.txt`, executable checksums, and `codesign --verify --deep --strict` on macOS.

## Failure Handling

- Retry dependency-fetch configure failures at most three times with short backoff.
- If staging reports multiple matching bundles, identify exact stale build directories before deleting anything.
- If installed copies differ from staged bundles, rebuild staging. Do not repair by copying internal build products manually.
