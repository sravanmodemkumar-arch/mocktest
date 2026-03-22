# Module 16 — Notes & Study Material

## Purpose
Provide a platform-native, in-app notes and study material system for EduForge.
Teachers author structured notes linked to the syllabus hierarchy (Module 15).
Students read notes in-app with personalised bookmarks, highlights, and annotations.
No file uploads and no downloads — all content is created and consumed within the platform.
YouTube links open in-app WebView via a "Watch Video" button; the YouTube app is never launched.

---

## 1. Notes Creation — Rich Text Editor

### 1.1 Core Formatting
- Bold, Italic, Underline, Strikethrough
- Heading levels: H1 / H2 / H3 / H4
- Bullet list (unordered) and numbered list (ordered)
- Nested lists (up to 3 levels)
- Blockquote
- Horizontal rule / section divider
- Inline code and code block
- Superscript / Subscript (for chemical formulas, footnotes)
- Text colour and highlight colour (limited palette — no distraction)
- Text alignment: Left / Centre / Right / Justify

### 1.2 Math Equation Editor
- LaTeX-based inline equations: `$E = mc^2$`
- Block equations: `$$\int_0^\infty f(x)\,dx$$`
- Live preview while typing
- Equation palette: common symbols (Greek letters, operators, set notation, calculus, statistics)
- Same engine as Module 14 (homework assignments) — consistent across platform

### 1.3 Chemical Formula & Structure Input
- Text-based chemical notation: H₂SO₄, CH₃COOH, CaCO₃ — Unicode subscript/superscript
- Structural formula text notation (condensed structural formula)
- IUPAC name field per compound (optional teacher entry)
- No drawing upload — all in-platform text representation

### 1.4 Diagram / Sketch Canvas
- In-platform drawing tool — no image upload from device
- Tools: line, arrow, rectangle, circle, ellipse, polygon, freehand, text label, colour fill
- Labelled diagram support: draw shape → attach text label with leader line
- Use cases: biology diagrams (cell, heart, leaf cross-section), circuit diagrams, geometry figures, map sketches, flowcharts
- Canvas auto-scales for different screen sizes
- Completed diagram embedded inline in note body

### 1.5 Table Builder
- In-platform table: define rows × columns
- Merge cells (horizontal and vertical)
- Column alignment: Left / Centre / Right
- Header row highlight
- Use cases: comparison tables, periodic table excerpts, data tables, truth tables, case law comparison
- Tables render cleanly in print-friendly view

### 1.6 Code Block
- Syntax-highlighted code block for Computer Science notes
- Languages supported: Python, C, C++, Java, JavaScript, HTML, CSS, SQL, Scratch pseudocode
- Line numbering option
- Monospace font rendering
- Copy-to-clipboard button (for teacher preview only — students see view-only)

### 1.7 Embedded Video Button
- Teacher pastes a YouTube URL or platform-hosted video URL into note
- System renders a "Watch Video" button inline — not an embed frame
- Student taps "Watch Video" → opens URL in in-app WebView (stays within EduForge app)
- YouTube app is never launched; no external browser redirect
- Multiple video buttons allowed per note
- Video title (teacher-entered label) shown next to button

### 1.8 Practice & Assignment Links
- "Practice Questions" button per note → navigates to Module 17 question bank filtered by that topic
- "View Assignment" button per note → navigates to Module 14 assignment for that topic
- Buttons rendered as in-app navigation; no external links

---

## 2. Note Types

| Type | Description | Format Guidance |
|---|---|---|
| Lecture Notes | Full class lecture in structured form | Headings + body paragraphs + examples |
| Summary Notes | Condensed chapter summary | Bullets under topic headings |
| Revision Notes | Pre-exam quick recall | Short bullets, bold key terms |
| Formula Sheet | All formulas for a chapter/unit | Two-column: Name \| Formula |
| Mind Map | Radial concept tree | Root node → branches → leaf nodes |
| Concept Map | Free-form node-link diagram | Nodes + directional arrows + relation labels |
| Worked Examples | Solved problems step by step | Problem → Steps → Answer |
| Common Mistakes | Wrong vs correct approaches | Two-column: Wrong \| Correct |
| Exam Tips | Board/competitive exam writing guidance | Numbered tips, point-wise |
| PYQ Analysis | Previous year question frequency per chapter | Table: Year \| Question \| Marks \| Topic |
| NCERT Solutions | Chapter-wise NCERT exercise answers | Question → Answer (worked example format) |
| Guest Lecture Notes | Single-session notes by visiting faculty | Auto-archived after session |
| FLN Activity Card | Classes 1–3 literacy/numeracy activity | Large font, picture-description, activity steps |

---

## 3. Note Metadata & Tagging

### 3.1 Syllabus Linkage
Every note must be linked to:
- Institution / Branch
- Board
- Subject
- Grade / Semester
- Unit
- Chapter
- Topic (optional — note can be chapter-level or topic-level)

Linkage drives: chapter-wise notes index, exam auto-assembly, assignment suggestions.

### 3.2 Bloom's Taxonomy Tag
- Each note tagged: Remember / Understand / Apply / Analyse / Evaluate / Create
- Helps student understand cognitive level of content

### 3.3 Difficulty Tag
- Foundation / Standard / Higher / HOT (same taxonomy as Module 15 topics)

### 3.4 Exam Relevance Tag
- Board Exam / Internal Assessment / Competitive (JEE / NEET / UPSC / CA / Banking / State PSC)
- Multiple tags allowed per note

### 3.5 CO Tag (College / Higher Education)
- For degree/diploma courses: note tagged with Course Outcome (CO) codes defined in Module 15
- Used in NAAC/NBA evidence export

### 3.6 NSQF / NOS Tag (ITI / Vocational)
- For ITI/vocational notes: note tagged with NOS (National Occupational Standards) code
- Links to NCVT competency unit from Module 15

### 3.7 NIPUN Bharat FLN Tag (Classes 1–3)
- FLN competency code tagged per note
- Used in FLN milestone tracking and DEO reporting (Module 15 linkage)

---

## 4. Notes Visibility & Access Control

### 4.1 Visibility States

| State | Who Can See |
|---|---|
| Draft | Author teacher only |
| Published | All students in linked section/batch |
| Restricted | Specific section(s) or batch(es) only |
| Institution Library | All teachers of same subject/board/grade (after HOD approval) |
| Archived | Not visible to students; accessible to teachers for restoration |
| Expired | Auto-archived on teacher-set expiry date |

### 4.2 Section / Batch Scoping
- School notes: scoped to section (e.g., Class 10 — Section A only, or all sections of Class 10)
- Coaching notes: scoped to batch (e.g., JEE 2025 Morning Batch only)
- College notes: scoped to course section / division

### 4.3 Scheduled Release
- Teacher sets future publish date and time
- Note auto-publishes on schedule — no manual action required
- Student receives in-app notification when note is published
- Schedule can be modified before publish time; change logged

### 4.4 Notes Expiry
- Teacher sets optional expiry date (e.g., exam tips note expires after board exam date)
- On expiry: note auto-archived; no longer visible to students
- Teacher can restore from archive at any time

---

## 5. Notes Versioning & Governance

### 5.1 Auto-Versioning
- Every save creates a new version (v1, v2, v3 …)
- Teacher can view full version history: who edited, when, what changed (diff view)
- Any previous version can be restored with one click; restoration itself creates a new version
- Version history retained for current academic year + 2 archive years

### 5.2 Approval Workflow
- Teacher creates note → submits for HOD review
- HOD: Approve (publishes to institution library) / Return with comments
- Returned notes: teacher sees HOD comments inline; edits and re-submits
- Approved notes stamped with approver name + date
- Bypass option: teacher can publish to own section without HOD approval; HOD approval required only for institution-wide library sharing

### 5.3 Institution Notes Library
- Searchable repository of all HOD-approved notes
- Search by: subject / board / grade / chapter / topic / note type / Bloom's level / difficulty
- Teacher clones any library note → customises for own section
- Cloning tracked: original author credited; clone is independent copy

### 5.4 Notes Duplication Detection
- Before publishing, system checks new note content against institution library for similarity
- If > 80% similar to existing note: warning shown to teacher
- Teacher can proceed (with confirmation) or discard and use existing note
- Prevents redundant note proliferation

### 5.5 Stale Notes Alert
- Notes older than one academic year flagged as "Stale"
- HOD prompted to review per subject at start of new academic year
- Teacher marks each stale note: Archive / Update / Carry Forward
- Carry Forward: cloned into new academic year as v1 of new instance

### 5.6 Academic Year Notes Handover
- At year-end, HOD reviews all published notes for their department
- Bulk action: Archive all / Carry forward selected
- Carried-forward notes cloned into new academic year; linked to new year's syllabus hierarchy
- Old year notes remain accessible in archive for reference

---

## 6. Student Experience

### 6.1 Chapter-wise Notes Index
- Student sees all notes for a chapter in organised list
- Sorted by note type: Lecture → Summary → Formula → Worked Examples → Revision → Exam Tips
- Each entry shows: note title, type badge, Bloom's tag, read status (Read / Unread), teacher name

### 6.2 Note Reading — In-App View
- Full-screen reading mode: clean, distraction-free
- Scroll, pinch-to-zoom
- Full-text search within note (highlights all matches, navigate with arrows)
- Table of Contents for long notes (> 5 sections): auto-generated, anchor-linked
- Font size control: 3 levels (Small / Medium / Large); preference saved per student
- Night mode / dark mode: renders per device setting automatically
- No download option — view-only in-app at all times

### 6.3 Offline Cache
- Notes viewed at least once are automatically cached in student app (no manual action)
- Cached notes readable offline with full formatting
- Cache auto-updates when student reconnects and note has a newer version
- Cache size managed: oldest cached notes evicted first when storage limit approached
- No explicit "download" — system handles caching transparently

### 6.4 Student Bookmark
- Student taps bookmark icon on any note → saved to personal Bookmarks list
- Bookmarks list in student dashboard: sorted by subject / date bookmarked
- Remove bookmark with one tap
- Bookmarks are private (not visible to teacher or other students)

### 6.5 Student Text Highlight
- Student long-presses text → selects → chooses highlight colour (yellow / green / pink)
- Highlights saved per student account — not visible to others
- Highlighted notes: bookmark auto-applied if not already
- Highlights persist across sessions; cleared only by student
- Highlight count per note shown as indicator in notes list

### 6.6 Student Personal Annotations
- Student can add typed notes at any paragraph in a note body
- Annotations appear as sticky-note icons in margin; tap to expand/collapse
- Private: not visible to teacher or classmates
- Student can edit or delete their own annotations
- Annotations visible in offline cache

### 6.7 Mark as Read
- "Mark as Read" button at bottom of each note
- Triggers: read completion tracking, feeds HOD/teacher read % dashboard
- System also auto-marks as read if student scrolls to bottom + minimum time spent (configurable)
- Read status shown in chapter-wise notes index

### 6.8 Notes Completion % in Student Dashboard
- Per subject: "X of Y notes read" with progress bar
- Broken down by chapter on drill-down
- Feeds student performance analytics (Module 47)

### 6.9 Notes Read Streak
- Student earns streak badge for reading at least one note per day
- Streak counter shown in student dashboard gamification panel
- Streak resets if no notes read for a day
- Milestone badges: 7-day / 30-day / 100-day streak

### 6.10 Student Notes Feedback
- Thumbs up / thumbs down + optional one-line comment per note
- Student can choose to submit anonymously (DPDPA 2023 compliant)
- Aggregated rating shown to teacher (not individual identity when anonymous)
- Teacher uses feedback to improve note quality

### 6.11 Read-Aloud Mode (CWSN)
- Notes structured with semantic HTML / ARIA labels for screen reader compatibility
- Compatible with Android TalkBack and iOS VoiceOver
- Headings, lists, tables all properly tagged for assistive navigation
- CWSN students identified in Module 07 profile auto-prompted to enable accessibility mode

---

## 7. Teacher Experience

### 7.1 Notes Dashboard (Teacher)
- My Notes: all notes authored by the teacher — by status (Draft / Published / Archived)
- Quick actions: Edit / Publish / Schedule / Archive / Clone / Submit for HOD Review
- Notes performance per note: view count, read %, avg time spent, student rating

### 7.2 Notes Read Tracker
- Per note: list of students who have read vs not read (section/batch view)
- Read % per section (e.g., "Class 10-A: 72% students have read this note")
- Filter: unread students — for follow-up assignment or alert

### 7.3 Unread Notes Nudge (Teacher Action)
- Teacher can send in-app nudge to students who have not read a note
- Nudge message pre-filled: "Please read [Note Title] before next class"
- One-tap send; nudge count logged per note to avoid spam

### 7.4 HOD Notes Gap Report
- Per subject/chapter: list of chapters with zero published notes
- Teacher assignment: HOD can assign note creation task to a specific teacher with due date
- Teacher receives in-app notification of assignment
- Gap report updated in real time as notes are published

### 7.5 Teacher Notes Performance Score
- Per teacher, per subject: avg student read %, avg student rating, total notes published, notes pending review
- Visible to HOD in department analytics
- Used in academic quality review

### 7.6 Collaborative Notes (Co-Teaching)
- Two co-teachers of same subject can co-edit a note
- Last-edit-wins with version conflict detection: if both edit simultaneously, system saves both as conflict versions; teacher resolves by choosing one or merging
- Co-author name shown on published note

### 7.7 Revision Pack Builder
- Teacher selects any combination of published notes (formula sheet + summary + PYQ + exam tips) for a chapter
- Bundles into a named Revision Pack
- Students access the pack as a collection with one-tap navigation between notes
- Pack visible in student dashboard under "Exam Prep"

### 7.8 Exam Revision Pack Auto-Assembly
- 2 weeks before any exam scheduled in Module 19:
  - System identifies all chapters in the exam scope
  - Auto-assembles a revision pack: all formula sheets + summaries + PYQ analysis notes for those chapters
  - Pack published automatically; students notified
- Teacher can edit or supplement the auto-assembled pack

---

## 8. Specialised Note Types — Detailed Specs

### 8.1 Formula Sheet
- Two-column layout: Formula Name | Formula (with LaTeX rendering)
- Unit field: physical unit or dimension (e.g., m/s², N/m²)
- Condition/note field: when formula applies, exceptions
- Auto-sorted alphabetically or by topic sequence
- Print-friendly: single-page A4 layout with all formulas

### 8.2 Mind Map
- Root node (chapter/topic name) at centre
- Main branches: sub-topics
- Leaf nodes: key terms, facts, examples
- Colour coding per branch (auto-assigned; teacher can change)
- Rendered as interactive expandable tree in student view
- Each node supports one-line text label

### 8.3 Concept Map
- Free-form nodes placed on canvas
- Directed arrows connecting nodes
- Relationship label on each arrow (e.g., "leads to", "is a type of", "causes")
- Export as in-app view; no download

### 8.4 Worked Examples
Structured template:
```
Problem Statement:
[Problem text with equation if needed]

Given:
[Known quantities]

Find:
[What to determine]

Solution:
Step 1: [Step description]
  [Equation / calculation]
Step 2: …
Step N: …

Answer:
[Final answer with units]

Note: [Common error or alternate method]
```

### 8.5 PYQ Analysis Note
- Chapter-wise table: columns = Year (last 10 years), rows = Topics
- Cell value: number of questions / marks asked from that topic in that year
- Heatmap colouring: darker = more frequent
- Source: manually entered by teacher or pulled from Module 17 question bank PYQ tags
- Visible to students as exam strategy guide

### 8.6 FLN Activity Card (Classes 1–3, NIPUN Bharat)
- Large font size (minimum 18pt) for young readers
- Picture description: teacher enters image description in text (no image upload); system renders a coloured placeholder card
- Activity steps: numbered, simple language (Flesch-Kincaid Grade 1–3)
- Oral/physical activity instructions: clearly marked "DO THIS:" section
- Available in: Hindi, English, and state regional language (trilingual)
- Linked to NIPUN Bharat competency code

### 8.7 Parent-Facing Weekly Summary Note (Classes 1–5)
- Auto-generated from teacher's lecture note for the week
- Simplified language: key concepts in 3–5 bullet points
- "What your child learned this week" framing
- "How you can help at home" — 2 suggested activities
- Visible in parent app (Module 09) for parents of Classes 1–5 students only
- School-configurable: on/off per grade

---

## 9. Subject-Specific Notes Features

### 9.1 Competitive Exam Notes (Coaching)
- JEE / NEET shortcut technique notes: formula tricks, elimination methods, approximation techniques
- UPSC notes: constitutional articles cited, landmark judgements, government schemes, maps (text-based)
- CA/CS/CMA notes: statutory provisions, case studies, ICAI study material reference
- Banking/SSC notes: formula sheets for Quant, grammar rules for English, GK current affairs notes
- State PSC notes: state-specific history, geography, polity linked to state syllabus

### 9.2 JEE / NEET Chapter Weightage Note (Auto-Generated)
- Per chapter, per exam (JEE Main / JEE Advanced / NEET UG):
  - Last 10-year question frequency per topic (from Module 17 PYQ data)
  - Marks distribution by topic
  - "High priority" / "Medium priority" / "Low priority" topic classification
  - Student-visible strategy: "Focus on topics X, Y, Z first"
- Auto-updated when new PYQ data entered in Module 17

### 9.3 NCERT Solution Notes
- Chapter-wise: all NCERT exercise questions with model answers
- Intext questions + end-of-chapter questions + exemplar problems
- Each answer: worked example format with steps
- Linked to NCERT chapter reference stored in Module 15

### 9.4 Physical Education Notes
- Fitness test protocol notes: 600m run, Standing Broad Jump, Partial Curl-Up, Push-Ups, BMI
- Rules of games: CBSE PE theory syllabus content
- Anatomy and physiology notes for Classes 11–12 PE theory
- Sports training principles: FITT principle, types of training

### 9.5 Art / Music / Dance Notes
- Theory notes for performing arts: notation systems, raga/tala (Carnatic/Hindustani), art history
- Rubric notes: performance assessment criteria per term
- Recital preparation checklist note type

---

## 10. Multi-Institution Type Support

### 10.1 School Notes
- Board-aligned notes linked to NCERT chapters where applicable
- CBSE: CCE unit-wise notes, activity calendar notes, project guidelines
- State board: state textbook chapter alignment (from Module 15)
- NIOS: self-study notes with inline self-check questions

### 10.2 College Notes
- Semester/unit-wise notes per course
- CO tag mandatory for college notes (UGC/AICTE compliance)
- Reference: university prescribed textbook chapter + page reference per note
- Lab manual notes: experiment procedure, observation table template, result analysis (linked to Module 14 lab record)

### 10.3 Coaching Notes
- Batch-scoped: notes visible only to enrolled batch students
- Topic sequence follows coaching syllabus (may differ from school board sequence)
- Revision notes time-locked: released only after teacher marks topic as taught (Module 15 coverage log)
- Multi-batch release: same note released to multiple batches simultaneously

### 10.4 ITI / Vocational Notes
- Trade unit-wise notes; NOS code tagged
- Theory + practical notes pair per competency unit
- Illustrated procedure notes (diagram canvas for tool usage, safety procedures)
- Linked to NCVT MIS unit completion tracking

### 10.5 Open / Distance Learners (NIOS / CBSE Open School)
- Self-study notes with inline self-check MCQs embedded in note body
- Student answers MCQ inline; result shown immediately (not recorded in gradebook — self-assessment only)
- Notes structured for independent study: recap boxes, summary boxes, key term glossary at end

---

## 11. Accessibility & Multilingual Support

### 11.1 Regional Language Notes
- Note body supports full Unicode input in all 22 scheduled languages
- Scripts: Devanagari, Tamil, Telugu, Kannada, Malayalam, Gujarati, Bengali, Odia, Gurmukhi, Assamese, Urdu (Nastaliq RTL)
- Bilingual notes: single note with English section + regional language section side by side (two-column layout for parallel text)

### 11.2 Grade-Appropriate Vocabulary Check
- System checks note text against Flesch-Kincaid grade-level index for the target grade
- Words above grade threshold flagged inline (yellow underline)
- Advisory only — teacher can override; not a hard block
- Especially useful for Classes 1–8 where language complexity matters

### 11.3 CWSN Adapted Notes
- Teacher can create a CWSN variant of any note:
  - Font size: +2 levels from standard
  - Shorter sentences (max 15 words per sentence advisory)
  - Simplified vocabulary
  - Extra spacing between paragraphs
- CWSN students (Module 07 profile) automatically shown CWSN variant if available
- Non-CWSN students see standard note; CWSN variant not visible to them

### 11.4 Print-Friendly View
- Clean, paginated A4 layout: removes navigation, sidebar, buttons
- Retains all formatting: tables, equations, diagrams, headings
- For low-connectivity areas: teacher uses print view to print and distribute offline
- Page break control: teacher inserts manual page breaks in note
- Print-friendly also used for formula sheets (single-page A4 optimised)

---

## 12. Analytics & Reporting

### 12.1 Per-Note Analytics (Teacher View)
- Total views
- Unique student views (distinct students)
- Read % (marked as read / total enrolled)
- Average time spent per reading session
- Section/batch-wise engagement breakdown
- Drop-off point: which section of the note students typically stop reading
- Student rating: aggregated thumbs up % + comment themes

### 12.2 Subject-wise Notes Dashboard (HOD View)
- Total notes published per subject / chapter / teacher
- Pending HOD approval count
- Average read % across all notes for the subject
- Chapters with zero notes (gap report)
- Teacher-wise notes count and avg read %

### 12.3 Notes Analytics Export
- Per subject, per academic year: notes inventory, view counts, read %, ratings
- Exportable as Excel
- Used in academic committee review, NAAC SSR Criterion 2

### 12.4 NAAC / NBA Notes Evidence
- Criterion 2 (Teaching-Learning): number of e-learning resources created, avg student engagement
- NBA Criterion 4: learning material availability per CO
- Auto-populated tables in NAAC SSR and NBA self-assessment document exports

---

## 13. Data Architecture

### 13.1 Tenancy
- All notes data tagged with `tenant_id` (PostgreSQL RLS)
- Institution notes library scoped to tenant; platform has no cross-tenant note access
- DPDPA 2023: student highlight/annotation data is personal data — stored with student consent flag; retained for session duration + 1 academic year

### 13.2 Database Schema

```sql
-- Notes master
notes (
  note_id UUID PK,
  tenant_id UUID FK tenants,
  branch_id UUID FK branches,
  author_id UUID FK users,
  co_author_id UUID FK users,          -- co-teaching
  syllabus_id UUID FK syllabi,
  unit_id UUID FK syllabus_units,
  chapter_id UUID FK syllabus_chapters,
  topic_id UUID FK syllabus_topics,    -- nullable (chapter-level notes)
  note_type VARCHAR(30),               -- LECTURE | SUMMARY | REVISION | FORMULA | MIND_MAP |
                                       -- CONCEPT_MAP | WORKED_EXAMPLE | COMMON_MISTAKES |
                                       -- EXAM_TIPS | PYQ_ANALYSIS | NCERT_SOLUTION |
                                       -- GUEST_LECTURE | FLN_CARD | PARENT_SUMMARY
  title VARCHAR(500),
  bloom_level VARCHAR(20),
  difficulty_tag VARCHAR(20),
  exam_relevance_tags TEXT[],          -- BOARD | INTERNAL | JEE | NEET | UPSC | CA | BANKING
  co_tags TEXT[],                      -- CO1, CO2 … (college)
  nos_code VARCHAR(50),                -- NCVT NOS code (ITI)
  nipun_competency_code VARCHAR(50),   -- FLN (Classes 1–3)
  visibility VARCHAR(20),              -- DRAFT | PUBLISHED | RESTRICTED | LIBRARY | ARCHIVED | EXPIRED
  section_ids UUID[],                  -- for RESTRICTED visibility
  batch_ids UUID[],                    -- for coaching batch scoping
  scheduled_publish_at TIMESTAMPTZ,
  expires_at TIMESTAMPTZ,
  academic_year_id UUID FK academic_years,
  version INTEGER DEFAULT 1,
  cloned_from_note_id UUID,
  has_cwsn_variant BOOLEAN DEFAULT FALSE,
  is_parent_facing BOOLEAN DEFAULT FALSE,
  word_count INTEGER,
  approved_by UUID FK users,
  approved_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
)

-- Note content (versioned)
note_versions (
  version_id UUID PK,
  note_id UUID FK notes,
  version_number INTEGER,
  content_json JSONB,                  -- full rich-text document as JSON (ProseMirror/TipTap format)
  content_text TEXT,                   -- plain text for search indexing
  edited_by UUID FK users,
  edit_reason TEXT,
  created_at TIMESTAMPTZ
)

-- Student interaction
student_note_reads (
  read_id UUID PK,
  tenant_id UUID FK tenants,
  note_id UUID FK notes,
  student_id UUID FK users,
  first_read_at TIMESTAMPTZ,
  last_read_at TIMESTAMPTZ,
  read_count INTEGER DEFAULT 0,
  total_time_seconds INTEGER DEFAULT 0,
  marked_as_read BOOLEAN DEFAULT FALSE,
  marked_at TIMESTAMPTZ,
  drop_off_section VARCHAR(200),
  device_type VARCHAR(20)              -- MOBILE | TABLET | WEB
)

-- Student bookmarks
student_note_bookmarks (
  bookmark_id UUID PK,
  tenant_id UUID FK tenants,
  student_id UUID FK users,
  note_id UUID FK notes,
  created_at TIMESTAMPTZ
)

-- Student highlights
student_note_highlights (
  highlight_id UUID PK,
  tenant_id UUID FK tenants,
  student_id UUID FK users,
  note_id UUID FK notes,
  note_version INTEGER,
  selection_start INTEGER,             -- character offset in plain text
  selection_end INTEGER,
  colour VARCHAR(10),                  -- YELLOW | GREEN | PINK
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
)

-- Student personal annotations
student_note_annotations (
  annotation_id UUID PK,
  tenant_id UUID FK tenants,
  student_id UUID FK users,
  note_id UUID FK notes,
  paragraph_index INTEGER,
  annotation_text TEXT,
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
)

-- Student feedback
note_feedback (
  feedback_id UUID PK,
  tenant_id UUID FK tenants,
  note_id UUID FK notes,
  student_id UUID FK users,
  is_anonymous BOOLEAN DEFAULT FALSE,
  rating SMALLINT,                     -- 1 = thumbs down, 2 = thumbs up
  comment TEXT,
  created_at TIMESTAMPTZ
)

-- Revision packs
revision_packs (
  pack_id UUID PK,
  tenant_id UUID FK tenants,
  created_by UUID FK users,
  name VARCHAR(300),
  chapter_id UUID FK syllabus_chapters,
  academic_year_id UUID FK academic_years,
  is_auto_generated BOOLEAN DEFAULT FALSE,
  published_at TIMESTAMPTZ,
  expires_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ
)

revision_pack_notes (
  pack_note_id UUID PK,
  pack_id UUID FK revision_packs,
  note_id UUID FK notes,
  sequence_no INTEGER
)

-- Notes export / evidence log
notes_export_log (
  export_id UUID PK,
  tenant_id UUID FK tenants,
  export_type VARCHAR(50),             -- NAAC_SSR | NBA | PRINT_FRIENDLY | EXCEL_ANALYTICS
  generated_by UUID FK users,
  generated_at TIMESTAMPTZ,
  status VARCHAR(20)
)
```

### 13.3 Full-Text Search Index
```sql
CREATE INDEX idx_note_versions_fts ON note_versions
  USING GIN (to_tsvector('english', content_text));

CREATE INDEX idx_notes_tenant_chapter ON notes(tenant_id, chapter_id, visibility);
CREATE INDEX idx_student_reads_student ON student_note_reads(student_id, note_id);
CREATE INDEX idx_student_reads_note ON student_note_reads(note_id, marked_as_read);
CREATE INDEX idx_highlights_student ON student_note_highlights(student_id, note_id);
CREATE INDEX idx_annotations_student ON student_note_annotations(student_id, note_id);
```

---

## 14. Roles & Permissions

| Action | Student | Parent | Teacher | HOD | Principal | Admin |
|---|---|---|---|---|---|---|
| Create / Edit notes | — | — | Own notes | Department | View | All |
| Publish to own section | — | — | ✅ | ✅ | — | ✅ |
| Submit for library approval | — | — | ✅ | — | — | — |
| Approve for library | — | — | — | ✅ | ✅ | ✅ |
| View notes | ✅ Read-only | Class 1–5 summary | ✅ | ✅ | ✅ | ✅ |
| Bookmark / Highlight / Annotate | ✅ Own only | — | — | — | — | — |
| View read analytics | — | — | Own notes | Department | All | All |
| Export analytics | — | — | — | ✅ | ✅ | ✅ |
| Archive / Restore | — | — | Own | Department | All | All |
| Send unread nudge | — | — | ✅ | ✅ | — | — |

---

## 15. Notifications (In-App Only)

| Trigger | Recipient |
|---|---|
| New note published for subject/chapter | Student |
| Revision pack published / auto-assembled | Student |
| Unread nudge from teacher | Student |
| Note returned by HOD with comments | Teacher |
| Note approved by HOD | Teacher |
| HOD gap report: chapter has zero notes | HOD |
| Scheduled note published (auto) | Teacher (confirmation) |
| Note expired and archived (auto) | Teacher |
| Stale notes review reminder (start of new academic year) | HOD, Teacher |
| New note available from anchor/prerequisite topic | Student |

---

## 16. Compliance Summary

| Standard | Coverage |
|---|---|
| CBSE Curriculum Framework 2023 | NCERT solution notes, CCE unit notes, activity calendar notes, lesson plan linkage |
| NEP 2020 | FLN activity cards (NIPUN Bharat), 21st-century competency tagging, multilingual notes |
| NIPUN Bharat (NCERT FLN Framework 2022) | Classes 1–3 FLN activity cards, competency code tagging, DEO reporting feed |
| UGC / AICTE | CO-tagged notes, CO-PO evidence for NBA/NAAC, reference textbook linkage |
| NCVT / DGT | NOS code tagging for ITI trade notes, unit-wise competency alignment |
| RTE Act 2009 | CWSN adapted notes (Sections 3 & 12), simplified language, screen reader support |
| RPWD Act 2016 | Accessibility: TalkBack/VoiceOver support, large font, simplified CWSN variant |
| DPDPA 2023 | Student annotation/highlight data consent flag; anonymous feedback option; data retention policy |
| NAAC SSR Criterion 2 | Notes inventory, engagement stats, CO-tagged material count for accreditation |
| NBA Criterion 4 | Learning material mapped to COs; attainment evidence |
