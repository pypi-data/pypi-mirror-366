# Main

> ⚠️ **EARLY DEVELOPMENT NOTICE**  
> This repository is in early development (pre-release/alpha).  
> The current release is a “hello world” scaffold. APIs and behavior will change rapidly as features are added over the coming weeks.  
>  
> **Metadata requirement:**  
> All pre-release/alpha versions must include in their `pyproject.toml`/`setup.py` description:  
> _“This is a pre-release/alpha version for initial feedback and CI testing. Not for production use.”_

## **Task Discovery & Execution Policy for Agents**

This document defines conventions and operational policies for automation agents (e.g., Codex, maintenance bots) discovering and running repo tasks.  
It is intended for both global and per-subfolder use.

* * *

### **Task Folder Structure**

* All agent-driven tasks must be housed under a `tasks/` folder (visible; not dot-prefixed).
    
* Recommended subfolder scheme:
    
    * **Dated tasks:** `tasks/YYYY/MM/DD/` for archival, milestone, or special-run tasks.  
        _These are _not_ run automatically unless referenced by name._
        
    * **In-Use tasks:** `tasks/in-use/` — tasks to be picked up and run automatically by agents during regular/automated maintenance.
        
    * **Disabled tasks:** `tasks/disabled/` — tasks archived or paused; never run automatically.
        
* The `tasks/` scheme may exist in the repo root and/or in any subfolder requiring specialized automation.
    

* * *

### **Task Execution Rules**

1. **Auto-execution:**
    
    * Only tasks located in any `tasks/in-use/` directory are auto-discovered and executed by the agent in routine maintenance or CI runs.
        
    * Maintenance tasks are preferred to be housed here.
        
2. **Manual/specific execution:**
    
    * Tasks in `tasks/YYYY/MM/DD/` or `tasks/disabled/` are never executed automatically.
        
    * To run a specific task from a dated or disabled folder, invoke it by explicit path or ID.
        
3. **Scoped Execution:**
    
    * Agents must recursively scan for `tasks/in-use/` within both the repo root and all subfolders.
        
    * Subfolder `tasks/in-use/` tasks are run **in addition to** root tasks, unless task IDs or filenames conflict.
        
4. **Conflict Handling:**
    
    * If multiple in-use tasks (across any `tasks/in-use/` folders) have the same ID, name, or would result in conflicting actions:
        
        * The agent must halt further execution immediately.
            
        * The agent must report the conflict (with explicit paths or task IDs) and skip remaining tasks for that run.
            
        * No changes should be made until the conflict is resolved by a maintainer.
            
5. **Task Identification:**
    
    * Tasks should have unique IDs or filenames within their respective `in-use` folders.
        
    * Consider prefixing tasks with a short namespace (e.g., `cli-lint-cleanup.md`) for subfolder scoping.
        
6. **Task Format:**
    
    * Tasks should follow the established [Maintenance Task Template](#) or [Prompt-Driven Task Template](#) as appropriate for consistency.
        

* * *

### **Summary Table**

| Folder | Auto-Run? | How to Run | Notes |
| --- | --- | --- | --- |
| `tasks/in-use/` | Yes | Automatic | Maintenance & in-use tasks only |
| `tasks/disabled/` | No | Manual/Explicit | Use for paused or archived tasks |
| `tasks/YYYY/MM/DD/` | No | Manual/Explicit | For archived, milestone, or dated |
| Any subfolder `tasks/in-use/` | Yes | Automatic | Scoped to subproject/module context |

* * *

### **Additional Notes**

* Task execution may be subject to repo security rules and branch protection.
    
* Maintainers should routinely review `tasks/in-use/` to avoid buildup of obsolete or redundant tasks.
    
* Agents and maintainers must resolve conflicts before rerunning maintenance.
    

* * *

## **Examples**

* To add a new recurring maintenance task, place it in `tasks/in-use/` or `subfolder/tasks/in-use/`.
    
* To archive or disable a task, move it to `tasks/disabled/` or a dated subfolder.
    
* If agent output reports a conflict, review the indicated task files, resolve the duplicate or conflicting actions, and rerun.
    

* * *

**For further task template conventions, see**:

* Maintenance Task Template
    
* Prompt-Driven Task Template
    

* * *

**End of `task-main.md`**

* * *