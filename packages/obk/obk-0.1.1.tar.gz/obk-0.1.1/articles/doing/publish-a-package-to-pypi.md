# **How to Publish obk to PyPI**

## **1. Prepare Your Project Structure**

Your `obk` repository uses the modern **src layout**:
```
obk/
├── pyproject.toml
├── README.md
├── LICENSE
├── src/
│   └── obk/
│       ├── __init__.py
│       └── ... (modules)
└── tests/
    └── ...
```

* The repo root is **`obk/`**.
* The package lives under **`src/obk/`** so it can be imported with `import obk`.

* * *

## **2. Create `pyproject.toml`**

`pyproject.toml` holds all build and metadata information. A simplified version for this project looks like:

```toml
[build-system]
requires = ["hatchling>=1.24"]
build-backend = "hatchling.build"

[project]
name = "obk"
version = "0.1.0"
description = "A scalable hello-world CLI starter. This is a pre-release/alpha version for initial feedback and CI testing. Not for production use."
readme = "README.md"
requires-python = ">=3.9"
authors = [{ name = "Your Name", email = "you@example.com" }]
dependencies = [
    "typer>=0.12",
    "dependency-injector>=4.41",
]

[project.scripts]
obk = "obk.cli:main"

[tool.hatch.build.targets.wheel]
packages = ["src/obk"]
```

Adjust metadata such as author information as needed.

* * *

## **3. Build Your Package**

Install Hatch and build from the project root:

```bash
python -m pip install --upgrade hatch
hatch build
```

This creates a `dist/` directory with `.tar.gz` and `.whl` files.

* * *

## **4. Register and Set Up PyPI Account**

* Go to [https://pypi.org/account/register/](https://pypi.org/account/register/)
* Verify your email.
* **(Optional but recommended)**: Enable two-factor authentication.

* * *

## **5. Upload to PyPI with Twine**

Install Twine if you haven't already:

```bash
python -m pip install --upgrade twine
```

Upload the package:

```bash
python -m twine upload dist/*
```

Enter your PyPI credentials when prompted.

* * *

## **6. Verify Your Package**

* Visit `https://pypi.org/project/obk/`.
* Try installing it:

```bash
pip install obk
```

* * *

## **7. Tips and Best Practices**

* **Choose a unique name**—check availability at `https://pypi.org/project/<your-package-name>/`.
* **Use underscores in your import name**; hyphens are fine for the PyPI distribution name.
* **Include a license** and a clear README.
* **Bump the version** (`0.1.0`, `1.0.0`, etc.) for every release.
* **Test locally** before uploading. You can install from the built wheel:

```bash
pip install dist/obk_cli-0.1.0-py3-none-any.whl
```

* * *

## **8. Optional: Test Uploads to TestPyPI**

To experiment without affecting the real index:

```bash
python -m twine upload --repository testpypi dist/*
```

Install from TestPyPI:

```bash
pip install --index-url https://test.pypi.org/simple/obk
```

* * *

## **9. Useful Resources**

* Packaging Python Projects — Official Guide
* [PyPI — Managing Projects](https://pypi.org/help/)
* Hatchling documentation

### How to test these instructions

1. Run `hatch build` to create `dist/`.
2. Upload to TestPyPI with `python -m twine upload --repository testpypi dist/*`.
3. Install using the TestPyPI command above and run `obk --help`.
