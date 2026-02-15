# Maintaining

## Adding Support for a New Python Version

When adding support for a new Python version (e.g., Python 3.15):

1. **Upgrade PyO3**: Check if the current PyO3 version supports the new Python version. If not, upgrade PyO3 in `Cargo.toml` to the latest version that supports it. PyO3 typically adds support for new Python versions within a few releases.

2. **Update CI workflow** (`.github/workflows/ci.yml`): Add the new Python version to the `python-version` matrix to ensure tests run against it:
   ```yaml
   python-version: ["3.13", "3.14", "3.15"]
   ```

3. **Update release workflow** (`.github/workflows/release.yml`): Add the new Python version to the `python-version` matrix to build wheels for it:
   ```yaml
   python-version: ["3.13", "3.14", "3.15"]
   ```

4. **Update `pyproject.toml`**: Verify that `requires-python` includes the new version (e.g., `>=3.13` already covers 3.14+).
