# JUCE Projects

Use this reference for EHL plugins built with JUCE and CMake.

## Discovery

- Read `AGENTS.md`, `README.md`, root and nested `CMakeLists.txt`, `CMakePresets.json`, processor/editor sources, tests, `.github/workflows`, and any vendored EHL design module pointer.
- Identify JUCE source mode: in-tree `add_subdirectory`, pinned `FetchContent`, or `find_package(JUCE CONFIG REQUIRED)`.
- Extract product name, company, manufacturer code, plugin code, bundle ID, formats, MIDI flags, copy/install behavior, and artifact paths.
- Confirm the expected JUCE version or commit from CMake, lockfiles, workflow inputs, or FetchContent declarations before relying on API behavior.

## Identity

Use:

- `COMPANY_NAME "EsionHsrahLatigid"`;
- `PLUGIN_MANUFACTURER_CODE EHL_`;
- bundle prefix `jp.ehl.`;
- GitHub owner `EsionHsrahLatigid`;
- requested product name exactly;
- a stable, unique four-character `PLUGIN_CODE`.

Treat post-release changes to bundle ID, manufacturer code, plugin code, product name, parameter IDs, or preset schema as migrations.

## Build

Prefer a fast DSP/test build before plugin formats when the project supports it:

```sh
cmake -S . -B build/dsp -DPROJECT_BUILD_PLUGIN=OFF -DPROJECT_BUILD_TESTS=ON
cmake --build build/dsp --parallel 2
ctest --test-dir build/dsp --output-on-failure
```

Then build requested formats through the repository's real options and target names:

```sh
cmake -S . -B build/plugin -DPROJECT_BUILD_PLUGIN=ON -DPROJECT_BUILD_TESTS=ON
cmake --build build/plugin --parallel 2
ctest --test-dir build/plugin --output-on-failure
```

Use a fresh build directory when changing generator, compiler, architecture, JUCE revision, SDK, CMake cache shape, or plugin formats.

## Local Install

EHL JUCE projects should expose `EHL_COPY_PLUGIN_AFTER_BUILD`. On local macOS outside CI, default it on for VST3 and AU developer convenience; in CI and non-macOS default it off. Standalone applications remain in the build or artifact tree.

Verify installed bundles by comparing executable SHA-256 with the built/staged copy and, on macOS, by running `codesign --verify --deep --strict`.
