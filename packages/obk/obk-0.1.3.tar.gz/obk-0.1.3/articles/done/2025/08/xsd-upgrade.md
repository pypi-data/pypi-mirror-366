# Modernizing Prompt Validation in OBK: Multi-XSD Support with `xmlschema` and Robust Package Resource Loading

## **Overview**

As OBK matures, prompt validation must become more robust and future-proof. This means:

* Supporting _multiple XSD schemas_ (for different prompt types or evolving standards)
    
* Using a best-in-class XML validation library (`xmlschema`)
    
* Ensuring schemas are reliably loaded from OBK’s installed package, not only from source file paths
    

This article describes the rationale and process for upgrading OBK’s validation to meet these goals.

* * *

## **Why Switch to `xmlschema` and Multi-XSD?**

* **`xmlschema`** is more compliant with XML Schema standards (esp. XSD 1.1) and offers clearer errors than `lxml`.
    
* **Multi-XSD** lets you define specific rules for different prompt file types—critical as OBK scales.
    
* **Package resource loading** is essential for pip-installed tools: hard-coded file paths break, but packaged resources are always accessible.
    

* * *

## **1. Package Your XSDs with OBK**

**Place all XSD files in a dedicated folder (e.g., `src/obk/xsd/`).**  
In `pyproject.toml`, ensure they are included as package data:

```toml
[tool.hatch.build.targets.wheel]
packages = ["src/obk"]
include = [
  "src/obk/xsd/*.xsd"
]
```

> If you use setuptools, see `[tool.setuptools.package-data]`.

* * *

## **2. Loading XSDs as Package Resources**

Use Python’s standard `importlib.resources` API (Python 3.9+):

```python
from importlib.resources import files
from pathlib import Path

def get_schema_path(schema_name: str) -> Path:
    # e.g., schema_name = "gsl.xsd"
    return files("obk.xsd").joinpath(schema_name)
```

* **Why:** This works identically whether OBK is installed via pip, editable, or in a zipapp.
    

* * *

## **3. Multi-XSD Registry and File Association**

Define a **mapping from prompt file type (or file pattern) to schema name**.

Example:

```python
PROMPT_SCHEMA_MAP = {
    "gsl": "gsl.xsd",
    "surgery": "surgery.xsd",
    "other": "other.xsd",
}
```

* Decide file type by convention: filename prefix/suffix, or a tag/attribute in the prompt.
    

* * *

## **4. XML Validation with xmlschema**

Install dependency:

```sh
pip install xmlschema
```

Use like this:

```python
import xmlschema

def validate_prompt(xml_path: Path, schema_path: Path) -> list[str]:
    schema = xmlschema.XMLSchema(str(schema_path))
    errors = []
    for error in schema.iter_errors(str(xml_path)):
        errors.append(error.message)
    return errors
```

* `iter_errors` yields all validation errors (non-blocking).
    

* * *

## **5. Putting It All Together: validate-all Implementation**

**Sample (OBK-style):**

```python
from importlib.resources import files
from pathlib import Path
import xmlschema
import typer

PROMPT_SCHEMA_MAP = {
    "gsl": "gsl.xsd",
    "surgery": "surgery.xsd",
    # Add as needed
}

def detect_prompt_type(prompt_path: Path) -> str:
    # EXAMPLE: decide type by folder, filename, or (better!) by inspecting the file itself.
    # Here, just a dummy implementation
    if "surgery" in prompt_path.name:
        return "surgery"
    return "gsl"

def get_schema_path(schema_name: str) -> Path:
    return files("obk.xsd").joinpath(schema_name)

def validate_all_prompts(prompts_dir: Path):
    all_good = True
    for prompt_path in prompts_dir.rglob("*.md"):
        prompt_type = detect_prompt_type(prompt_path)
        schema_name = PROMPT_SCHEMA_MAP.get(prompt_type, "gsl.xsd")
        schema_path = get_schema_path(schema_name)
        schema = xmlschema.XMLSchema(str(schema_path))
        errors = list(schema.iter_errors(str(prompt_path)))
        if errors:
            all_good = False
            typer.echo(f"{prompt_path}:")
            for err in errors:
                typer.echo(f"  - {err.message}")
    if all_good:
        typer.echo("All prompt files are valid!")

# Typer CLI registration, in obk.cli.py:
@app.command()
def validate_all(
    prompts_dir: Path = typer.Argument(..., help="Directory with prompt files")
):
    validate_all_prompts(prompts_dir)
```

* * *

## **6. Advantages and Best Practices**

* **Reliability:** Validation works identically from source or after pip install.
    
* **Extensibility:** Add new schemas by dropping new `.xsd` files in `src/obk/xsd/` and updating the mapping.
    
* **Maintainability:** Keeps CLI and logic clean and testable.
    

* * *

## **7. Testing in CI**

* Add/keep a GitHub Actions step:
    
    ```yaml
    - name: Validate prompts
      run: obk validate-all prompts/
    ```
    
* This ensures every PR is schema-compliant.
    

* * *

## **8. Summary Checklist**

*  All XSDs in `src/obk/xsd/` and included as package data
    
*  Use `importlib.resources` to load schemas by name
    
*  Use `xmlschema` for all validation
    
*  Map prompt types to schema files
    
*  Validate each prompt against the correct schema
    
*  Show detailed errors for each file
    

* * *

## **Conclusion**

By adopting `xmlschema` and robust resource handling, OBK’s prompt validation is now:

* **pip-install safe**
    
* **Multi-XSD ready**
    
* **More robust and maintainable**
    

This keeps OBK on par with best practices and ready to grow with your workflow.

* * *
