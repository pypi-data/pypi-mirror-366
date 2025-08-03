# **How to Automate Your PyPI Publishing in a `pypi-cd.yml` File**

Publishing Python packages to PyPI doesn’t have to be a manual, error-prone process. By automating your releases with GitHub Actions, you can trigger builds and uploads on every release or main branch update—ensuring your package is always up to date for users.

This guide shows you how to set up a simple, secure, and reliable continuous deployment (CD) pipeline for PyPI using a `pypi-cd.yml` workflow file in your `.github/workflows` directory.

* * *

## **1. Prerequisites**

* **A published PyPI account** ([Register here](https://pypi.org/account/register/))
    
* **An existing Python project with a valid `pyproject.toml`**
    
* **Your project built with a standard tool** (e.g., [Hatchling](https://hatch.pypa.io/), Setuptools, or Poetry)
    
* **A PyPI API token** (get one [here](https://pypi.org/manage/account/#api-tokens))
    

* * *

## **2. Create Your PyPI API Token**

1. Go to your [PyPI account settings](https://pypi.org/manage/account/#api-tokens).
    
2. Click **Add API token**.
    
3. Name the token (e.g., `github-cd`), and give it permission to upload for your project only.
    
4. Copy and save the token—**you will not be able to see it again!**
    

* * *

## **3. Add Your Token to GitHub Secrets**

1. Go to your repository’s Settings → **Secrets and variables** → **Actions**.
    
2. Click **New repository secret**.
    
3. Name the secret `PYPI_API_TOKEN`.
    
4. Paste your PyPI token value and save.
    

* * *

## **4. Example: Minimal `pypi-cd.yml` Workflow**

Create a new file at `.github/workflows/pypi-cd.yml` in your repo with the following content:

```yaml
name: Publish Python 🐍 distributions 📦 to PyPI

on:
  push:
    tags:
      - 'v*'  # Trigger on version tags like v0.1.0

jobs:
  build-and-publish:
    runs-on: ubuntu-latest

    steps:
      - name: Check out code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install build tools
        run: |
          python -m pip install --upgrade pip
          python -m pip install build twine

      - name: Build package
        run: python -m build

      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: python -m twine upload dist/*
```

* * *

## **5. How It Works**

* **Trigger:** The workflow runs on every push of a tag matching `v*` (e.g., `v1.0.0`).
    
* **Build:** Uses `build` to package your project (creates `dist/*.whl` and `.tar.gz`).
    
* **Publish:** Uploads to PyPI via Twine, using the API token stored as a secret.
    

* * *

## **6. Best Practices**

* **Always test your build locally before pushing tags.**
    
    ```bash
    python -m build
    ```
    
* **Never store your API token in code or commit history.**  
    Always use GitHub Secrets.
    
* **For dry runs,** upload to [TestPyPI](https://test.pypi.org/) first.  
    Add another job or switch the `repository-url` in Twine:
    
    ```yaml
    - name: Publish to TestPyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.TEST_PYPI_API_TOKEN }}
      run: python -m twine upload --repository testpypi dist/*
    ```
    
* **Tag your releases semantically** (`v0.2.0`, `v1.0.0`), and ensure the `version` field in `pyproject.toml` matches.
    

* * *

## **7. Resources**

* PyPI — Uploading Packages
    
* [GitHub Actions — Python Example Workflows](https://github.com/actions/starter-workflows/blob/main/ci/python-package.yml)
    
* [TestPyPI](https://test.pypi.org/)
    

* * *

## **Summary**

By automating your PyPI releases with a `pypi-cd.yml` workflow, you ensure consistent, secure, and repeatable publishing. With each tagged release, your users will always have access to the latest version—no manual uploads or last-minute errors.

**Just push a new tag and your package ships itself!** 🚀

* * *

Let me know if you want an advanced version (e.g., with TestPyPI, build matrix, or conditional release triggers), or a template customized for your project's actual structure!