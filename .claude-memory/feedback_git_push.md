---
name: Auto Git Push After Each Group
description: After completing ALL pages for a Group (e.g. Group 2), commit everything and push to remote — not per page
type: feedback
---

After all page spec files for a Group are written and complete, do a single git add + commit + push for the entire group.

**Why:** User wants one clean push per group, not per page. Keeps git history meaningful at group level.

**How to apply:**
- Write all pages for the group sequentially without pushing
- When the final page of the group is done, run: git add <all new files> → git commit -m "docs: Group 2 — all divisions complete" → git push
- One commit per group, not per page or per division
- Update div-pages-list.md status and memory before pushing
