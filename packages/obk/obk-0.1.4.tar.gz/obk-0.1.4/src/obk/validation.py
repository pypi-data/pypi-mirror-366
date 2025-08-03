from importlib.resources import files
from pathlib import Path
from typing import List, Tuple

import xmlschema

from .preprocess import preprocess_text

PROMPT_SCHEMA_MAP = {
    "gsl": "prompt.xsd",
    "surgery": "prompt.xsd",
}


def get_schema_path(schema_name: str) -> Path:
    return files("obk.xsd").joinpath(schema_name)


def detect_prompt_type(file_path: Path) -> str:
    name = file_path.stem.lower()
    if "surgery" in name:
        return "surgery"
    return "gsl"


def validate_all(prompts_dir: Path) -> Tuple[List[str], int, int]:
    """Validate all prompts under ``prompts_dir`` using mapped schemas."""

    errors: List[str] = []
    count_passed = 0
    count_failed = 0

    prompts_dir = prompts_dir.resolve()

    for file_path in prompts_dir.rglob("*.md"):
        text = file_path.read_text(encoding="utf-8")
        processed, _ = preprocess_text(text)
        prompt_type = detect_prompt_type(file_path)
        schema_name = PROMPT_SCHEMA_MAP.get(prompt_type, "prompt.xsd")
        schema_path = get_schema_path(schema_name)
        schema = xmlschema.XMLSchema(str(schema_path))
        try:
            file_errors = [
                err.reason or str(err) for err in schema.iter_errors(processed)
            ]
        except xmlschema.XMLSchemaException as exc:
            file_errors = [str(exc)]
        if file_errors:
            for msg in file_errors:
                errors.append(f"{file_path}: {msg}")
            count_failed += 1
        else:
            count_passed += 1

    return errors, count_passed, count_failed
