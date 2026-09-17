---
name: document-reviewer
description: Protocols for applying structured PDF annotation context to local codebase assets.
---

# Document Reviewer Skill Execution Protocol

When the user provides a structured JSON or Markdown dataset of document comments, you must adhere to the following execution sequence:

## 1. Context Alignment
* Isolate the `referenced_text` or code block from the dataset.
* Use global workspace search to locate the exact source files containing matching structures.

## 2. Integrity Checks
* Before making edits, check for secondary impacts on interconnected components.
* If a comment implies architectural changes (such as control loop timing variables or anti-windup clamping thresholds), map out the dependencies first.

## 3. Implementation plan
* Outline a clear and concise implementation plan that addresses the reviewer's comments.
* Explain the changes you are going to make.
* Indicate any assumptions or limitations you are making.
* Do not leave placeholder code or incomplete implementations.
* Save the plan to a markdown file called 'implementation_plan_comments.md' in the current working directory.    