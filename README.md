Commits intended to mass-change whitespace should _only_ change whitespace.

```yaml
# .pre-commit-config.yaml

- repo: https://github.com/ellieayla/only-whitespace-hook
  rev: v0.1.6
  hooks:
    - id: default-commit-message
      #args: [--header="Whitespace-only change"]
    - id: honest-commit-message
      #args: [--header="Whitespace-only change"]
```

## arguments

* `--header="Whitespace-only change"` - text to use for declaring and asserting that the change is whitespace-only
