# Publishing nuu-core to PyPI

## Prerequisites

1. Create a PyPI account at https://pypi.org/account/register/
2. Generate an API token at https://pypi.org/manage/account/token/
3. Install build tools:
   ```bash
   uv pip install build twine
   ```

## First-time Setup

1. Update package metadata in `pyproject.toml`:
   - Replace "Your Name" with your actual name
   - Replace "your.email@example.com" with your email
   - Update GitHub URLs with your actual repository

2. Create a `.pypirc` file in your home directory (optional but recommended):
   ```ini
   [pypi]
   username = __token__
   password = pypi-YOUR-API-TOKEN-HERE
   ```

## Publishing Steps

1. Clean previous builds:
   ```bash
   rm -rf dist/
   ```

2. Build the package:
   ```bash
   uv build
   ```

3. Check the built files:
   ```bash
   ls -la dist/
   ```

4. Test upload to TestPyPI first (recommended):
   ```bash
   python -m twine upload --repository testpypi dist/*
   ```
   
   Then test install from TestPyPI:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ nuu-core
   ```

5. Upload to PyPI:
   ```bash
   python -m twine upload dist/*
   ```

   Or if you didn't create `.pypirc`:
   ```bash
   python -m twine upload dist/* --username __token__ --password pypi-YOUR-API-TOKEN
   ```

## Version Management

### Release Process:

1. Update version in both files:
   - `pyproject.toml`
   - `src/core/__init__.py`

2. Commit the version changes:
   ```bash
   git add pyproject.toml src/core/__init__.py
   git commit -m "Bump version to X.Y.Z"
   git push origin main
   ```

3. Create and push a version tag to trigger automatic publishing:
   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

The GitHub Action will automatically:
- Verify the tag matches the version in pyproject.toml
- Build and publish to PyPI
- Create a GitHub release

## Post-Publishing

After publishing, users can install with:
```bash
pip install nuu-core
```

And use the CLI:
```bash
core --help
core fetch document.md
```

## Automation with GitHub Actions

The repository includes automated publishing to PyPI when you push to the main branch with a new version.

### Setup Instructions:

1. **Configure PyPI Trusted Publishing** (Recommended - no tokens needed):
   - Go to https://pypi.org/manage/project/nuu-core/settings/publishing/
   - Add a new trusted publisher:
     - Owner: `yourusername` (your GitHub username)
     - Repository: `nuu-core`
     - Workflow name: `publish.yml`
     - Environment: `pypi`

2. **Alternative: Use API Token** (if trusted publishing unavailable):
   - Generate a PyPI API token at https://pypi.org/manage/account/token/
   - Add it as a GitHub secret named `PYPI_API_TOKEN`
   - Modify `.github/workflows/publish.yml` to use the token

### How it Works:

- The workflow triggers when you push a tag starting with 'v' (e.g., v1.0.0)
- It verifies the tag version matches the version in `pyproject.toml`
- If they match, it builds and publishes to PyPI
- Creates a GitHub release automatically
- You can also manually trigger it from the Actions tab

### Example Release:

```bash
# After updating version to 1.0.0 in pyproject.toml and __init__.py
git add pyproject.toml src/core/__init__.py
git commit -m "Bump version to 1.0.0"
git push origin main

# Create and push tag to trigger publishing
git tag v1.0.0
git push origin v1.0.0
```