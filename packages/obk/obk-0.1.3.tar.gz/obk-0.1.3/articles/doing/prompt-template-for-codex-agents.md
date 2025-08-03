# Prompt Template for Codex Agents

This article provides a ready-to-use template for creating consistent, maintainable prompt files for Codex agent workflows.
Each section is commented for clarity. Simply fill in the placeholders to match your specific task.

This template uses GSL elements for reportability.

---

```xml

<?xml version="1.0" encoding="UTF-8"?>
<gsl-prompt id="<!-- PROMPT_ID_HERE -->">
<gsl-description>
<!--
This is a self-contained prompt and spec for OBK/Codex agent work.
- Inputs, outputs, workflows, and tests are listed below.
- All document rules and agent policies are defined in the "Document Specification" section.
- Agents may only update workflows and add new tests (see rules).
- Everything else is for maintainers to edit as needed.
- This file should be easy to read and quick to update—no hidden steps or dependencies.
-->
</gsl-description>

<gsl-header>
    
# <!-- Title for this prompt/task, e.g., "Add Feature X" -->
</gsl-header>

<!--
Note: This GSL document uses XML-like section tags as containers, but the content inside each section may include markdown, tables, or other non-XML elements. Strict XML parsing is neither required nor expected; all parsing and automation should be tolerant of mixed content.
-->

<gsl-block>

<gsl-purpose>
    
## 1. Purpose

<!-- Describe the high-level objective for this prompt, e.g., "Implement feature Y in project Z." -->
</gsl-purpose>

<gsl-inputs>
    
## 2. Inputs

<!-- List key tools, articles, or other input artifacts that guide the prompt. -->
| Input | Notes |
| --- | --- |
| <!-- Tool/Article/Config --> | <!-- Short description --> |
| <!-- Example: ChatGPT / Codex --> | Tool |
| <!-- Example: "How to Write One-Line Manual Tests" --> | Article |

</gsl-inputs>

<gsl-outputs>
    
## 3. Outputs

<!-- List main components or deliverables produced by this prompt. -->
- <!-- Example: Updated CLI command -->
- <!-- Example: Test suite covering new functionality -->

</gsl-outputs>

<gsl-workflows>
    
## 4. Workflows

<!-- List main steps or processes required for the task. -->
- <!-- Example: Install dependencies -->
- <!-- Example: Refactor module_x.py to use classes -->
- <!-- Example: Update README.md -->

</gsl-workflows>

<gsl-tdd>

<gsl-description>
    
## 5. Tests

<!--
Add single-line manual tests here.
Each `<gsl-test>` element should fully validate a required feature or edge case.
You may add a code block (with triple backticks) under each test if needed.
-->

</gsl-description>    

<gsl-test id="T1">
    
- T1: <!-- Short test description -->
<!--
```python
# Optional code example for T1
\--> 
</gsl-test>

<gsl-test id="T2">

<!-- Add more `<gsl-test>` elements as needed. -->
</gsl-test>

</gsl-tdd>

<gsl-document-spec>
    
## 6. Document Specification

#### Overview

This section defines the rules and conventions for maintaining and updating this prompt document.
This specification applies only to this prompt document.

#### S-1. Identifier and Numbering

Major sections and tests in this document must use a clear, hierarchical ID. Use an uppercase prefix and numbers, like `T1`, `T2.1`, or `S1.2.3`:

* Use `T` for tests in `<gsl-tdd>` (e.g., `T1`, `T2.1`).
* Use `S` for specification items if needed (e.g., `S1`, `S2.1`).
* Number all items in order, with no gaps or repeats.
* Do not remove or change IDs except to fix errors.

These IDs are required for referencing, tracking, and audits.

#### S-2. Update Policy

These rules apply to automated changes by agents. Manual edits by maintainers can update any section.

* Agents **may only** update these sections:

  * `<gsl-workflows>` (agents may add, change, or remove any part)
  * `<gsl-tdd>` (agents may add new `<gsl-test>` elements, but may not change or remove any existing `<gsl-test>`)
* Agents **must not** change or remove any other content in this document.

These rules protect the integrity of the document and its tests, while allowing agents to add workflows and new tests.

#### S-3. Tests Section

* `<gsl-tdd>` holds one or more `<gsl-test>` elements.
* Each `<gsl-test>` must start with a single-line description and have a unique `id` (e.g., `T1`, `T2`, etc).
* You may add a code block (with triple backticks) below the test description if needed.
* Agents may only add new `<gsl-test>` elements. They must not change or remove any existing test.
* Only maintainers can change or remove tests.
* Use these tests for auditing and validation.

</gsl-document-spec>
</gsl-block>
</gsl-prompt>


```

---

## How to use:

1. Duplicate this template for each new prompt or when standardizing older ones.
2. Replace all placeholders (`<!-- ... -->`) with your actual content.
3. Keep comments as guidance for maintainers—they can be deleted from finalized prompts if desired.

---