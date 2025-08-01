# Publishing Guide

## Setup for Automated PyPI Publishing

### 1. GitHub Actions (Recommended)

#### Setup Steps:

1. **Get PyPI API Token:**
   ```bash
   # Go to https://pypi.org/account/register/
   # Create account, then go to Account Settings > API tokens
   # Create token with scope "Entire account" or specific project
   ```

2. **Add GitHub Secrets:**
   ```bash
   # In your GitHub repo: Settings > Secrets and variables > Actions
   # Add new repository secret:
   # Name: PYPI_API_TOKEN
   # Value: pypi-AgEIcHlwaS5vcmcC... (your token)
   ```

3. **Publish Methods:**

   **Option A: Create GitHub Release**
   ```bash
   # Tag and create release on GitHub
   git tag v0.1.0
   git push origin v0.1.0
   # Then create release from tag on GitHub UI
   # This triggers automatic PyPI publish
   ```

   **Option B: Manual Trigger**
   ```bash
   # Go to Actions tab > Publish to PyPI > Run workflow
   # This publishes current main branch
   ```

### 2. Alternative Services

#### **Stainless SDK (API-focused)**
```bash
# Best for API wrappers, generates SDKs from OpenAPI specs
# Visit: https://www.stainlessapi.com/
# Upload OpenAPI spec, get auto-generated SDK + publishing
```

#### **GitHub Codespaces + Actions**
```bash
# Built-in with GitHub, no setup needed
# Uses the workflows already created above
```

#### **GitLab CI/CD**
```yaml
# .gitlab-ci.yml
publish:
  stage: deploy
  script:
    - pip install build twine
    - python -m build
    - twine upload dist/*
  variables:
    TWINE_USERNAME: __token__
    TWINE_PASSWORD: $CI_PYPI_TOKEN
  only:
    - tags
```

#### **CircleCI**
```yaml
# .circleci/config.yml
workflows:
  publish:
    jobs:
      - build-and-publish:
          filters:
            tags:
              only: /^v.*/
```

## Current Setup Benefits

✅ **GitHub Actions** (already configured):
- Free for public repos
- Runs tests before publishing
- Supports multiple Python versions
- Auto-publishes on release creation
- Manual trigger option

## Quick Start

1. **Push to GitHub:**
   ```bash
   cd google_workspace_sdk
   git init
   git add .
   git commit -m "Initial SDK"
   git remote add origin https://github.com/yourusername/google-workspace-sdk
   git push -u origin main
   ```

2. **Add PyPI token to GitHub secrets**

3. **Create first release:**
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   # Create release on GitHub UI
   ```

4. **SDK automatically publishes to PyPI!**

Users can then install with:
```bash
pip install google-workspace-sdk
```