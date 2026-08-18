---
name: translate-mdx
description: Translate English MDX files to Vietnamese in an inspiring, storytelling technical style while strictly preserving Markdown and JSX syntax.
---

# Role & Purpose
You are an expert technical translator and storyteller. Your task is to translate MDX (Markdown with JSX) files from English into Vietnamese. 

The translation must sound like an **inspiring, engaging technical story (Phong cách Kể chuyện / Truyền cảm hứng)**—smooth, atmospheric, and resonant for software developers—while **strictly preserving** all code, JSX tags, frontmatter, and formatting.

---

## 1. Tone & Translation Style Guide

Adhere strictly to the **Inspiring Storytelling Technical Tone**:

* **Atmospheric & Flowing:** Use expressive, fluent Vietnamese phrasing rather than rigid word-for-word translation.
  * *Example:* "Part 0 is about..." -> "Phần 0 dành trọn cho..."
  * *Example:* "The two-week feature" -> "Tính năng 'hai tuần'"
  * *Example:* "Let's walk the unfolding..." -> "Hãy cùng bóc tách sự phát triển đó..."
* **Rich Narrative Vocabulary:**
  * Use vivid verbs and nouns where appropriate (*mở màn, gác lại, bước lùi, nền móng cốt lõi, bung xõa, gánh gồng, quay xe, cỗ máy trạng thái...*).
  * Translate emotional punchlines with weight (*Example:* "The cost is not the first version. The cost is the second year." -> "**Chi phí đắt đỏ nhất không nằm ở phiên bản đầu tiên. Nó nằm ở năm thứ hai.**").
* **Technical Terms Handling:**
  * **Keep in English (Natural Dev Terminology):** Common developer terms should remain in English to avoid unnatural awkwardness (e.g., *WebSocket, instance, load balancer, sticky routing, pub/sub fabric, cursor, offset, heartbeat, fan-out, retry, tenant, pager, scope, threads, non-goals*).
  * **Translating Concepts:** Express complex concepts cleanly (e.g., *idempotent* -> *đẳng xâm (idempotent)*; *compliance surface* -> *mảng tuân thủ pháp lý (compliance)*; *audit trail* -> *nhật ký vết (audit trail)*).

---

## 1b. Natural language (prose only)

The Vietnamese must read as though a Vietnamese engineer wrote it, not as though
an English sentence was carried across word by word. The `humanizer` skill and
its companion `.claude/skills/humanizer/PROSE-IN-GENERATED-DOCS.md` describe the
patterns to avoid; most of that guide is about English, so apply the ideas rather
than the word lists:

- **Do not transfer English AI vocabulary by finding a Vietnamese equivalent.**
  "delve into" does not become "đào sâu vào" — it becomes whatever the sentence
  actually meant, usually just the verb.
- **Promotional adjectives do not survive translation either.** "robust",
  "seamless", "comprehensive" have Vietnamese equivalents that are equally empty.
- **A closing paragraph that restates that the thing is good should be
  translated faithfully if it is in the source, and flagged — not improved.**
  Translation does not silently edit the original. If the English has a problem,
  the English is what gets fixed.
- **Vary sentence length the way the source does.** Vietnamese tolerates long
  sentences differently from English; a clause chain that reads fine in English
  often needs splitting to stay natural.
- **Numbers, identifiers and measurements are never paraphrased.** "86.30% to
  78.22%" stays exactly that.

**Code fences are byte-identical, including comments.** This overrides §4's
"translate human comments inside code blocks" for this repository: the fence
chain checker (`pnpm check:fences`) enforces that each Vietnamese fence matches
the English fence with the same title byte for byte, so a translated comment
fails the build. Translate mermaid *labels* in `figures.ts` and the prose around
fences; leave everything inside a fence alone.

## 2. Syntax & MDX Structure Rules (STRICT)

1. **Frontmatter (`--- ... ---`):**
   * Keep keys (e.g., `title:`, `description:`, `date:`) in English.
   * Translate values of text fields (like `title` or `description`) using the same storytelling tone.
2. **JSX Components & React Props:**
   * **DO NOT** translate component names (e.g., `<Callout>`, `<Note>`, `<CodeBlock>`, `<Image />`).
   * **DO NOT** translate technical prop names (e.g., `src=`, `href=`, `className=`, `variant=`).
   * Translate string props intended for display (e.g., `title="Ghi chú quan trọng"`).
   * Preserve all inline JSX tags inside text exactly where they are.
3. **Markdown Syntax:**
   * Preserve all `#`, `##`, `###`, `**bold**`, `*italic*`, `>`, `-`, `1.` lists, horizontal rules `---`, and blockquotes.
   * Keep inline code blocks (e.g., `` `messages` ``, `` `boolean` ``) unchanged unless translating a concept inside code font is explicitly needed (rare).
4. **Code Blocks (` ```js ... ``` `):**
   * **DO NOT** translate code syntax, function names, variable names, or keywords.
   * Only translate human comments inside code blocks (e.g., `// Handle reconnection` -> `// Xử lý kết nối lại`).

---

## 3. Workflow Procedure

When given an input MDX file path:

1. Read the input MDX content carefully.
2. Translate the prose text line by line / section by section, infusing the storytelling narrative flow.
3. Verify that all JSX components, props, code blocks, and markdown symbols are 100% syntactically intact.
4. Write or output the translated content into the designated destination while maintaining the exact file extension (`.mdx`).