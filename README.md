# ehl-skills

Reusable Codex skills for EsionHsrahLatigid plugin development.

## Skills

- `develop-ehl-plugins`: build, test, review, package, and release EHL audio plugins across JUCE and YUP repositories.

## Validation

```sh
python3 .ci/quick_validate.py skills/develop-ehl-plugins
python3 -m unittest discover -s tests
python3 skills/develop-ehl-plugins/scripts/check_public_text.py .
```

The public-text guard keeps the private descriptor, known internal planning identifiers, and internal brand rationale out of the current public tree. Existing Git history and cleanup diffs are explicitly non-gating; `--history --report-json` remains available for redacted diagnostics.
