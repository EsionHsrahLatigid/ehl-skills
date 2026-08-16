# ehl-skills

Reusable Codex skills for EsionHsrahLatigid plugin development.

## Skills

- `develop-ehl-plugins`: build, test, review, package, and release EHL audio plugins across JUCE and YUP repositories.

## Validation

```sh
python3 .ci/quick_validate.py skills/develop-ehl-plugins
python3 -m unittest discover -s tests
python3 skills/develop-ehl-plugins/scripts/check_public_text.py --history .
```

The public-text guard prevents internal brand rationale from entering tracked files, tests, commit messages, or repository history.
