# Markdown to PDF — Formatting Rules for Perfect Conversion

Follow these rules to get clean, well-formatted PDFs from your Markdown. The app supports GFM (GitHub Flavored Markdown).

---

## 1. Supported Markdown Syntax

Use **only** these syntaxes for reliable conversion:

| Element | Syntax | Notes |
|---------|--------|-------|
| **Headings** | `# H1` through `###### H6` | Use one space after `#`. Avoid headings inside tables. |
| **Bold** | `**text**` | Prefer `**` over `__`. |
| **Italic** | `*text*` | Prefer `*` over `_`. |
| **Strikethrough** | `~~text~~` | GFM only. |
| **Inline code** | `` `code` `` | Use backticks, not double backticks for inline. |
| **Code block** | ` ``` ` with optional language | Fenced with triple backticks on their own line. |
| **Bullet list** | `-` or `*` + space | Use consistent bullet style. |
| **Numbered list** | `1.` + space | Numbers can be `1.` for all (auto-numbering). |
| **Task list** | `- [ ]` and `- [x]` | Space inside brackets for unchecked; `x` for checked. |
| **Nested list** | Indent 2–4 spaces | Align with parent item. |
| **Blockquote** | `> ` at line start | Add space after `>`. |
| **Table** | `| col | col |` and `|---|` | See table rules below. |
| **Link** | `[text](url)` | URL in parentheses. |
| **Horizontal rule** | `---` (3+ hyphens) | On its own line, blank line before/after. |

---

## 2. Table Rules for Clean PDFs

### Structure
- Put a blank line **before** and **after** the table.
- Alignment row uses `:---` (left), `:---:` (center), `---:` (right).
- Keep column widths similar to avoid layout issues.

### Example

```markdown
| Left   | Center | Right  |
|:-------|:------:|-------:|
| A      | B      | C      |
| 1      | 2      | 3      |
```

### Avoid
- Very long cells without spaces (can break layout).
- Tables inside blockquotes or lists.
- More than ~8 columns.

---

## 3. Code Blocks

### Use fenced code blocks

````markdown
```language
// code
```
````

### Supported language tags
`c`, `cpp`, `python`, `javascript`, `bash`, `json`, etc. Language tag improves syntax highlighting in preview; PDF shows plain monospace.

### Long lines — break onto next line
Long lines in code blocks can be cut off or overflow in PDF. Keep lines under ~72–80 characters where practical.

**How to handle:**
- Break long statements onto the next line with proper indentation.
- Use parentheses or backslash for line continuation.
- Extract sub-expressions into named variables to shorten lines.
- Split list comprehensions, function args, and multi-part conditions across multiple lines.

**Example — before (long line, may be cut):**

```python
results.append((pid, arrival, burst, completion, completion - arrival, completion - arrival - burst, current_time - arrival))
```

**Example — after (split for readability and PDF-safe width):**

```python
tat = completion - arrival
wt = tat - burst
rt = current_time - arrival
results.append((pid, arrival, burst, completion, tat, wt, rt))
```

**Example — long list comprehension split:**

```python
ready = [
    (pid, procs[pid])
    for pid in procs
    if procs[pid][0] <= current_time and procs[pid][2] > 0
]
```

### Avoid
- Indented code blocks (4 spaces) for multi-line code — prefer fenced blocks.
- Tabs inside code — use spaces.
- Lines longer than ~80 characters — break them for PDF safety.

---

## 4. Page Breaks (Practical File mode)

- Each `## Heading` starts a new page when using **Practical File** mode.
- Use `## Practical 1: Title` style headings for per-practical page breaks.
- Put a blank line after `---` before the next `##` for cleaner breaks.

---

## 5. Spacing and Layout

- **Blank lines**: Use one blank line between blocks (paragraphs, lists, tables, headings).
- **No trailing spaces**: Remove spaces at end of lines.
- **Consistent newlines**: Use single line breaks; avoid multiple blank lines in a row.
- **Lists**: One blank line before and after lists.

---

## 6. Characters to Avoid

| Avoid | Use Instead | Reason |
|-------|-------------|--------|
| Tab characters | Spaces (2–4) | Tabs can render inconsistently. |
| Smart/curly quotes | `"` and `'` | Straight quotes ensure proper display. |
| Zero-width chars | — | Invisible characters can cause odd gaps. |
| Emoji in headings | Text or skip | May not render well in all viewers. |

---

## 7. File Length and Size

- **Recommendation**: Up to ~50 pages for smooth export.
- **Images**: Only base64 inline images work in some export paths; prefer links or attachments.
- **Very long code blocks**: Consider splitting or shortening for readability. For long *lines* within code, see Section 3 (Code Blocks) — break them onto the next line.

---

## 8. PDF vs Print to PDF

| Output | When to Use |
|--------|-------------|
| **Download PDF** | Quick one-click file. Text is **not selectable** (image-based). |
| **Print to PDF** | Choose “Save as PDF” in the print dialog for **selectable, copyable text**. |
| **Download Word** | Editable .docx; best for further editing in Word. |

---

## 9. File Review at End of Creation

- **Before finishing**, check the created file for any gibberish, placeholder text, or non-readable content.
- Scan for: filler phrases, partial sentences, broken formatting, repeated/meaningless text, or leftover template text.
- Ensure the file is readable end-to-end and ends with meaningful content (no "*End of document*", "*[Placeholder]*", or generic sign-offs).
- This review step ensures proper user readability before the file is considered complete.

---

## 10. Checklist Before Export

- [ ] Headings use `#` with a space after.
- [ ] Tables have alignment row and blank lines around them.
- [ ] Code blocks use triple backticks, not indentation.
- [ ] Long code lines are split with proper indentation for PDF-safe display.
- [ ] No trailing spaces or odd characters.
- [ ] File reviewed for gibberish/non-readable content (see Section 9).
- [ ] Lists are indented with spaces, not tabs.
- [ ] In Practical mode, `##` is used for each practical title.
- [ ] For copyable text, use **Print to PDF**, not Download PDF.
- [ ] If the doc is a **block-by-block code guide**, also use **Section 12**
  checklist.

---

## 11. Example: Well-Formatted Document

````markdown
# Document Title

Short intro paragraph.

## Section One

- Bullet one
- Bullet two

## Section Two

| A   | B   |
|-----|-----|
| 1   | 2   |

## Section Three

```python
print("Hello")
```

> Important note here.
````

---

## 12. Template: Block-by-Block Code Explanation (Any File → Markdown → PDF)

Use this when you turn **any source file** (e.g. `.py`, `.js`, `.cpp`) into a
Markdown document that explains the code **block by block**, then export to
PDF. Follow **Sections 1–3, 5, and 9** for syntax, tables, code width, spacing,
and final review.

### 12.1 Visual layout of one block (canonical)

Each block uses this **fixed order** (top to bottom):

1. **Block heading** — `### Block N: ShortName (Lines start–end)`  
   - `ShortName` is a **short title** (e.g. *Initialization*, *Training loop*,
     *Imports*), like a slide heading—not a full sentence.
2. **Fenced code** — The snippet with a `language` tag; preserve source comments.
   Keep lines **≤ ~80 characters** where practical (Section 3).
3. **Mathematical notes** (optional) — Formulas, shapes, or one arrow flow
   (`step1 → step2 → step3`). Omit for trivial glue code.
4. **New functions and ideas (first use)** — Required subsection (see 12.3).
5. **`---`** — Horizontal rule, blank lines before/after, then the next block.

### 12.2 Document outline (rest of the Markdown file)

Use `#` for the document title, `##` for major parts (optional page breaks in
Practical File mode — Section 4).

| Section | Heading example | Content |
|:--------|:----------------|:--------|
| Intro | `# Title` + paragraph | What the file does; path or link to source. |
| Theory (optional) | `## Theory` | Math or domain background **before** blocks if needed. |
| Blocks | `## Block-by-Block Explanation of filename.ext` | Repeat 12.1 for each chunk. |
| Index (optional) | `## Block Index` | Table: block #, lines, one-line topic. |
| Extra (optional) | `## Worked example`, `## FAQs` | As needed. |

Separate major `##` sections with `---` (blank line before and after).

### 12.3 “New functions and ideas (first use)” — required pattern

Immediately after the code block (and after **Mathematical notes** if you added
them), use this **exact** bold title, then bullets:

```markdown
**New functions and ideas (first use)**

- `thing_in_backticks` — Plain-language explanation; use more `` `inline` `` for
  names, shapes, or values inside the sentence.
```

**Bullet rules**

- Subsection title is **exactly**: `**New functions and ideas (first use)**`.
- List uses `-` + space.
- Each line: **backticks** around the **expression or name** being explained
  (e.g. `` `X.shape` ``, `` `np.zeros((n_features, 1))` ``).
- Then an **em dash** `—` (U+2014), one space, then the explanation.
- The explanation should say **what it does** and **why it is here** (baseline
  init, shape match with `y`, etc.).

**Examples**

```markdown
- `X.shape` — Tuple `(rows, cols)`; here unpacks `n_samples`, `n_features`.
- `np.zeros((n_features, 1))` — Column vector of zeros for initial `weights`;
  column shape keeps matrix multiplies consistent with `y`.
- `self.bias = 0` — Starts the intercept at zero; gradient descent updates it
  unless you initialize differently on purpose.
```

**First-use rule:** Each API or notable syntax is explained in full **once**,
the first time it appears in the document. Later blocks may note *second use* or
skip this subsection if there is nothing new.

### 12.4 Splitting the source into blocks

- One **logical unit** per block (imports, constructor, one method, plotting
  section, …).
- Line ranges in the heading must **match the real file**.
- Long methods: either **one block** for the whole method or **split** (e.g.
  initialization vs loop) if clearer.

### 12.5 Full mini-example (initialization style)

````markdown
### Block 1: Initialization (Lines 65–69)

```python
def fit(self, X, y):
    # Initialize weights and bias
    n_samples, n_features = X.shape
    self.weights = np.zeros((n_features, 1))
    # (n_features, 1) for consistent dimensions with y
    self.bias = 0
```

**New functions and ideas (first use)**

- `X.shape` — Unpacks number of rows (samples) and columns (features).
- `np.zeros((n_features, 1))` — Starts all weights at zero as a simple baseline;
  gradient descent will adjust them; column shape keeps `X @ w` aligned with `y`.
- `self.bias = 0` — Same idea for the bias: start at zero unless you choose
  otherwise.

---
````

### 12.6 Empty skeleton (copy-paste)

````markdown
## Block-by-Block Explanation of `SOURCE_FILE.ext`

---

### Block 1: ShortName (Lines START–END)

```LANG
```

**Mathematical notes** (optional)

- ...

**New functions and ideas (first use)**

- `...` — ...

---

### Block 2: ShortName (Lines START–END)

```LANG
```

**New functions and ideas (first use)**

- `...` — ...

---
````

### 12.7 Conventions and checklist

- Use **inline code** for identifiers in running text (Section 1).
- **Block index** table: blank lines around it; alignment row (Section 2).
- **Update line numbers** when the source changes.

**Checklist — block-by-block Markdown**

- [ ] Each block: `### Block N: ShortName (Lines …)` → **code** → optional
  **Mathematical notes** → **New functions and ideas (first use)**.
- [ ] Every bullet under “New functions” follows `` `code` — explanation ``.
- [ ] Fenced code, language tag, PDF-safe line length (Section 3).
- [ ] First-use rule across the whole document.
- [ ] Sections 9 and 10 satisfied.

---
