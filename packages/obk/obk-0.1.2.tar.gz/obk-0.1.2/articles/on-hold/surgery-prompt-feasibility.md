
# Feasibility Considerations of a Surgery Prompt

## Overview

A “surgery prompt” is a specialized, machine-readable document intended to propose, justify, and manage the removal of code, features, or architectural components from a software system. Unlike traditional feature requests or bug reports, a surgery prompt formalizes the _deletion_ process, enforcing structure, traceability, and often automated safety checks.

This article explores the feasibility of implementing surgery prompts in modern software projects—highlighting design goals, key considerations, and potential integration strategies.

* * *

## 1. Motivation

Code and feature removal is an inevitable aspect of healthy software evolution. However, “removal” can be risky if handled informally:

* **Unintentional breakages** may occur if dependencies are overlooked.
    
* **Accountability and justification** may be lost, making reversals or audits difficult.
    
* **Stakeholder communication** can suffer, especially on distributed teams.
    

A surgery prompt introduces rigor and automation into the removal process, similar to how a pull request structures code addition.

* * *

## 2. Core Elements of a Surgery Prompt

A feasible surgery prompt implementation typically includes:

* **Metadata:**
    
    * Unique ID (e.g., timestamp-based, traceable)
        
    * Type field (e.g., `"surgery"`)
        
    * Optional TTL/expiry attribute
        
* **Justification:**
    
    * Explicit rationale for the proposed removal (tech debt, deprecation, redundancy, security, etc.)
        
* **Inputs:**
    
    * Preconditions or dependencies to review before deletion (e.g., usage references, stakeholder notices)
        
* **Outputs:**
    
    * Expected state of the codebase post-surgery (e.g., “no avatar code remains”)
        
* **Stakeholders:**
    
    * Approvers, reviewers, or impacted teams
        
* **Workflows:**
    
    * Step-by-step procedure for executing and verifying the surgery
        
* **Test Cases (TDD):**
    
    * Checks to validate the removal’s safety (e.g., “no usages remain,” “all CI passes”)
        
* **TTL/Sunset Clause:**
    
    * Limits the prompt’s validity, forcing periodic review or archival
        

* * *

## 3. Feasibility Analysis

### a. **Schema and Extensibility**

* **XSD or JSON Schema Support:**  
    Defining a formal schema (e.g., XSD for XML) ensures prompts are structured, validatable, and automation-friendly.
    
* **Extensibility:**  
    Future surgery types (e.g., “refactor,” “archive,” “migrate”) can reuse and extend the schema.
    

### b. **Automation Integration**

* **Codex/OBK Compatibility:**  
    Prompts can be consumed by automation agents, which interpret the structured workflow and run the necessary actions/tests.
    
* **CI/CD Integration:**  
    Valid surgery prompts can trigger test runs, dependency analysis, and status reporting.
    
* **TTL Enforcement:**  
    Agents can automatically archive or expire stale prompts, and remind maintainers of pending surgeries.
    

### c. **Organizational Impact**

* **Auditability:**  
    Each code removal is fully documented and attributable, aiding compliance and knowledge transfer.
    
* **Reduced Risk:**  
    Requiring justification, review, and pre/post tests reduces the risk of accidental breakage or loss.
    
* **Stakeholder Communication:**  
    Explicit fields for stakeholder acknowledgment encourage broad visibility and sign-off.
    

* * *

## 4. Potential Challenges

* **Adoption Friction:**  
    Teams must adapt to writing structured removal prompts; initial learning curve.
    
* **Overhead vs. Simplicity:**  
    For very small projects, this may seem like overkill, but scales well with codebase/team size.
    
* **Automation Limits:**  
    Not all removals can be safely automated; some manual review will always be required.
    

* * *

## 5. Example Surgery Prompt Structure

```xml
<gsl-prompt id="20250802T123456+0000" type="surgery" expires="2025-09-01">
  <gsl-header>Remove deprecated 'foo' module</gsl-header>
  <gsl-block>
    <gsl-purpose>Deprecate and remove the unused 'foo' module.</gsl-purpose>
    <gsl-justification>
      No usages remain. Module is obsolete and unmaintained.
    </gsl-justification>
    <gsl-inputs>
      - Check for references in all entrypoints
    </gsl-inputs>
    <gsl-outputs>
      - No foo code in repository
      - No import errors in downstream projects
    </gsl-outputs>
    <gsl-workflows>
      - Remove module files
      - Update docs and CI configs
      - Notify downstream users
    </gsl-workflows>
    <gsl-tdd>
      <gsl-test id="T1">No import of 'foo' in any .py file</gsl-test>
      <gsl-test id="T2">CI passes after removal</gsl-test>
    </gsl-tdd>
    <gsl-document-spec>
      <gsl-ttl>30 days</gsl-ttl>
      <gsl-stakeholders>
        <stakeholder>QA Lead</stakeholder>
        <stakeholder>Backend Maintainer</stakeholder>
      </gsl-stakeholders>
    </gsl-document-spec>
  </gsl-block>
</gsl-prompt>
```

* * *

## 6. Conclusion

A **surgery prompt** system brings needed discipline and automation to the risky process of codebase removal. Its feasibility is high for teams and projects that value auditability, safety, and traceable decision-making. When designed with extensibility and automation in mind, it serves as both a tool for maintainers and a communication bridge for teams—raising the bar for quality and safety in software evolution.

* * *

**For questions on schema design, automation integration, or practical adoption, feel free to reach out or propose enhancements.**