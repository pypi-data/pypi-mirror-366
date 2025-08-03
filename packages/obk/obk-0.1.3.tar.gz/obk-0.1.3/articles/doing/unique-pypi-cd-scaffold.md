# unique-pypi-cd-scaffold.md

> **Purpose:**
> A minimal, reliable, self-hosted deployment pipeline for PyPI, designed for the OBK project.
> This guide assumes you are using self-hosted runners and want the simplest, most auditable release path possible. Use this guide to get a working deployment. After that make small changes under the premise "do not break the deployment".


---

## 1. Branching & Protection

* **Deployment branch:**

  * All deploys are merged to a permanent `deploy` branch.
  * `deploy` branch must be protected: PRs only, review required, status checks enabled, no force push.
  * Feature work is done on `feature/*` branches and merged to `main` via PR.
  * Then `main` is merged into `deploy` via PR to trigger deployment.

## 2. Two Self-Hosted Runners: CI vs CD

* **CI Runner:**

  * Used for testing, linting, static analysis, and other non-sensitive jobs.
  * Should **not** have any deployment credentials or PyPI tokens.
  * Can be shared or general-purpose.

* **CD Runner:**

  * Used **only for deployment jobs** (publishing to PyPI or production).
  * Has access to sensitive secrets (`PYPI_API_TOKEN`).
  * Should have minimal system permissions, be dedicated, and not run general CI jobs.
  * Label this runner distinctly (e.g., `deploy-runner`).

* **Workflow isolation:**

  * Only the `pypi-cd.yml` job should use the `deploy-runner`.
  * All other jobs (e.g., in `ci.yml`) use your standard CI runner.

## 3. Automatic Patch Version Bump

> **Why:**
> PyPI will reject uploads if the version hasn’t changed.
> We bump the Z (patch) version in `pyproject.toml` before every deploy to ensure every upload is unique.

* **Add this script to your repo:** `.github/scripts/bump_patch.py`

  ```python
  # .github/scripts/bump_patch.py
  import re
  from pathlib import Path

  pyproject = Path("pyproject.toml")
  content = pyproject.read_text(encoding="utf-8")

  match = re.search(r'version\s*=\s*"(\d+)\.(\d+)\.(\d+)"', content)
  if not match:
      raise SystemExit("Could not find version string in pyproject.toml!")

  major, minor, patch = map(int, match.groups())
  patch += 1

  new_version = f'{major}.{minor}.{patch}'
  new_content = re.sub(
      r'version\s*=\s*"\d+\.\d+\.\d+"',
      f'version = "{new_version}"',
      content
  )

  pyproject.write_text(new_content, encoding="utf-8")
  print(f"Bumped version to {new_version}")
  ```

- If you use `setup.cfg` instead, adapt the script accordingly.

## 4. PyPI Deployment Workflow (`pypi-cd.yml`)

* **Workflow file:** `.github/workflows/pypi-cd.yml`
* **Trigger:** Push to `deploy` branch

- #### **Bare Minimum Example:**

    ```yml
    name: PyPI Deploy
    
    on:
      push:
        branches: [deploy]
    
    jobs:
      build-and-publish:
        runs-on: [self-hosted, deploy-runner]
    
        steps:
          - uses: actions/checkout@v4
    
          - name: Clean workspace
            run: git clean -fdx
    
          - name: Set up Python
            uses: actions/setup-python@v5
            with:
              python-version: '3.11'
    
          - name: Set up virtual environment and install tools
            run: |
              python -m venv .venv
              .venv/bin/pip install --upgrade pip
              .venv/bin/pip install build twine
    
          - name: Bump patch version
            run: .venv/bin/python .github/scripts/bump_patch.py
    
          - name: Build package
            run: .venv/bin/python -m build
    
          - name: Publish to PyPI
            env:
              TWINE_USERNAME: __token__
              TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
            run: .venv/bin/twine upload dist/*
    ```  
  - _**Reminder:** GitHub Actions doesn’t preserve shell state between steps, so you need to re-`source` the `.venv/bin/activate` in each step that uses Python._


## 5. Self-Hosted Runner Security & Reliability

* **Separate runners for CI and CD.**
* **Runner should have label:**

  * CI: e.g., `ci-runner`
  * CD: e.g., `deploy-runner`
* **Secrets:**

  * Add `PYPI_API_TOKEN` to GitHub repo secrets, only accessible to the CD runner.
* **Runner user:**

  * Should be a dedicated, minimal-privilege system user.
* **Cleaning:**

  * Always clean workspace at start to avoid leftover build artifacts.
* **Monitoring:**

  * Set up notifications if runner goes offline or job fails.

## 6. Step-by-Step Setup Workflow

Follow these steps to set up your minimal, self-hosted PyPI deployment pipeline:

#### 6.1. Prepare Your Branch Structure

1. Create a permanent `deploy` branch in your repository.
2. Protect the `deploy` branch (GitHub Settings → Branches):

    > The settings below are one possibility. Adjust them based on your situation: 

   1. Require PRs for merging.
   2. Require at least one approving review.
   3. Enable required status checks (if any).
   4. Disallow force pushes and direct pushes.
   5. **Allowed merge methods: 'Merge'** (It should already be squashed in `main` and it should reflect `main`.)

#### 6.2. Two Configured Self-Hosted Runners (at minimum)

1. (If not already registered) Register one runner for general CI tasks (label: `ci-runner`).
2. Register a second runner for CD tasks (label: `deploy-runner`).
3. Ensure the `deploy-runner` is dedicated and has minimal system permissions.
4. For detailed requirements, see Section 2.

#### 6.3. Add PyPI Secret

1. Generate a PyPI API token ([see reference](https://pypi.org/help/#apitoken)).
2. In your GitHub repository, go to Settings → Secrets and variables → Actions.
3. Add a new repository secret:

   1. Name: `PYPI_API_TOKEN`
4. Restrict this secret so only workflows running on `deploy-runner` can access it (see Section 5).

#### 6.4. Add the Patch Version Bump Script

1. Copy the provided bump script from Section 3.
2. Save it to `.github/scripts/bump_patch.py` in your repository.
3. Commit and push the file.

#### 6.5. Create the PyPI Deployment Workflow

1. In your repo, create the file: `.github/workflows/pypi-cd.yml`
2. Copy the workflow YAML from Section 4 into this file.
3. Adjust the `runs-on` label if your CD runner uses a different label.
4. Commit and push.

#### 6.6. Test Your Setup



1. Push a feature branch with a trivial change.
2. Open a PR to the `main` branch and merge.
3. Open a PR from `main` to `deploy`.
4. Merge the PR.
5. Monitor Actions:

   1. Confirm that:

      1. The workflow runs on the `deploy-runner`.
      2. The patch version bumps in `pyproject.toml`.
      3. The package is published to PyPI (check your project at [pypi.org](https://pypi.org/)).
6. If anything fails, review logs and runner health per Section 5.

#### 6.7. Next Steps After Success

1. Use this deployment pipeline for all releases.
2. Gradually introduce additional checks, PR templates, changelog automation, or versioning rules as needed (see Section 7).

*Refer back to referenced sections for details or code snippets as you work through these steps.*

## 7. Optional Next Steps

* Add version bump script for `setup.cfg` if needed.
* Enforce PR template to indicate release type for future automation.
* Gradually add changelog, release-drafter, and full CI integration as needed.

## 8. References

* [ci.yml](.github/workflows/ci.yml)
* [commitlint.yml](.github/workflows/commitlint.yml)
* [release-drafter.yml](.github/workflows/release-drafter.yml)
* [PyPI token setup](https://pypi.org/help/#apitoken)
* [GitHub self-hosted runners](https://docs.github.com/en/actions/hosting-your-own-runners/about-self-hosted-runners)

---
