---
name: EduForge Module Document Style & Structure
description: Exact format, section structure, depth, and content patterns used in all EduForge module specification documents
type: project
---

All module docs follow a strict pattern. New modules must match this exactly.

**Why:** Consistency across 57 modules; user reviews and merges these into the codebase spec.
**How to apply:** When writing a new module doc, follow this structure exactly — same heading levels, same table format, same section naming convention.

## File Naming
`{nn}-{kebab-case-name}.md` — e.g., `25-fee-collection-receipts.md`
Stored at: `e:\mocktest\docs\modules\`

## Document Structure

```
# Module {N} — {Title}

## 1. Purpose
[2-4 sentence dense paragraph covering: what the module owns, what institution types it covers,
key Indian regulations it enforces, and which modules it links to. No bullet points in purpose.]

---

## 2. {First Major Entity/Concept}

### 2.1 {Sub-concept}
- Bullet point rules
- Always include: entity fields, states/statuses, validations

### 2.2 {Sub-concept}
| Column | Column | Column | Notes |
|---|---|---|---|
| ... | ... | ... | ... |

---

## 3. {Second Major Area}
...continues with ### 3.1, 3.2 etc.
```

## Key Style Rules
1. **Tables everywhere**: Any list of options, types, statuses, rules → use a table
2. **Bullet points for rules**: Business logic, validations, edge cases → bullet list under the relevant heading
3. **--- separators** between every top-level ## section
4. **Sub-sections**: Always `### X.Y` format (never skip levels)
5. **Cross-module references**: Always "Module XX" (e.g., "Module 07", "Module 25 owns collection")
6. **Indian-specific depth**: Every section must cover Indian regulatory edge cases, state variations, government scheme integration
7. **Status flows**: Use `STATUS_A → STATUS_B → STATUS_C` arrow notation for lifecycle states
8. **No fluff**: No introductory paragraphs beyond Purpose. Jump straight to content.
9. **Code blocks**: Use for SQL schemas, Python snippets, JSON structures, Dart code — only when adding clarity
10. **Scale always in mind**: Write for 5 crore students; mention performance implications where relevant

## Section Types That Must Appear in Financial Modules
- Entity definition (fields, types, constraints)
- Status lifecycle
- Workflow / process flow (numbered steps or flowchart in code block)
- GST treatment
- Audit trail requirements
- Regulatory compliance (CBSE/UGC/FRA/RBI as applicable)
- Cross-module dependencies (what this module reads from / writes to)
- Role-based access (who can do what)
- Edge cases (specific Indian scenarios: RTE students, NRI, govt schemes, court orders)

## Depth Benchmark
Module 24 (Fee Structure) = 800+ lines. Target depth for financial modules: 600-900 lines.
Each section should have enough detail that a developer can implement without ambiguity.

## "50+ years of experience" Thinking
When writing, think as a domain expert who has:
- Handled every Indian board (CBSE, ICSE, all 28 state boards)
- Seen every edge case in Indian schools (RTE, aided/unaided, govt schemes, court orders)
- Designed fee systems for schools, colleges, and coaching at scale
- Navigated GST, income tax, DPDPA, POCSO compliance
Include those edge cases proactively — don't wait to be asked.
