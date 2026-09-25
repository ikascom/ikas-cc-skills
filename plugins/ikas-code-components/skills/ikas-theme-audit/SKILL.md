---
name: ikas-theme-audit
description: Use when auditing an existing ikas storefront theme's shopper experience — checking for missing page/chrome surfaces, incomplete or wrong flows, weak recovery paths, silent failures, or merchant-control gaps. Triggers on "temayı denetle", "audit this theme", "eksik section var mı", "chrome surface'lar tam mı", "akışlar doğru mu", "experience review", "pre-launch review", "bu tema yayına hazır mı".
context: fork
allowed-tools: Read, Grep, Glob, Bash(python3:*), mcp__ikas-code-components__list_ready_made_pages, mcp__ikas-code-components__list_editor_pages, mcp__ikas-code-components__list_page_sections, mcp__ikas-code-components__get_function_doc, mcp__ikas-code-components__search_docs, mcp__ikas-code-components__get_type_definition, mcp__ikas-code-components__get_framework_guide
model: opus
effort: high
---

# ikas Theme Audit

An **experience audit**, not a code review. The measuring stick is **commerce.md** — the design-agnostic ruleset shared with `ikas-theme-builder`, at `<this skill's base directory>/../ikas-theme-builder/references/commerce.md` for what an ikas theme must DO. You read code only to infer what the shopper and the merchant will experience; you do not police framework style, CSS quality, or implementation taste. For framework-compliance review, route to the `ikas-theme-builder` skill's review workflow instead.

**Core discipline: every finding is anchored.** A finding either cites the commerce.md section it violates (§7.1, §13.B, §14 #15 …) or is explicitly labeled **kontrat dışı** (beyond contract). Unanchored criteria — "modern e-commerce best practice", "most themes do X" — are how audits drift; if you can't cite it, label it or drop it.

## Severity taxonomy

Classify every finding as exactly one of:

| Class | Meaning | Example |
|---|---|---|
| **İhlal (blocker)** | Breaks a commerce.md contract: a §7 behavior contract, a §13 mandatory feature, a §14 anti-pattern, a §4 required function | Cart mutation with no failure feedback (§7.8, §14 #15) |
| **Boşluk (gap)** | A §4 surface or chrome **function** is absent entirely | No toast/feedback queue anywhere (§4.2, §7.9) |
| **Tema tercihi** | Diverges from a convention but commerce.md allows it — often design-canonical | Full-page search instead of a Search Modal (§4.2 allows: the function, not the form) |
| **Kontrat dışı öneri** | Would likely improve conversion but no commerce.md rule requires it | Free-shipping progress bar in the cart drawer |

**Classification rules:**
- **Store-setting-gated contracts** (back-in-stock, option sets, bundles…): if the code has no branch for the feature, it's an **İhlal** whatever the store's current setting. The setting only decides when shoppers hit the gap. Note the unknown setting under Doğrulanamadı.
- **Design source:** it exists when the project has a `design.md`, or the user or project docs point to a delivered design (Figma / Stitch / screens). Without one, the design-canonical anti-patterns (§14 #21, #22) don't apply; list such knobs as Tema tercihi.
- **API facts** (what a function returns, which helper gates what): look them up before classifying, never from memory. Use `get_function_doc` / `search_docs`; if MCP is unavailable, read the JSDoc in `node_modules/@ikas/bp-storefront/**/*.d.ts`.

**Tema tercihi and kontrat dışı findings are never blockers** and never lead the report. Remember §4.2's rule: if the design source omitted a chrome surface's *form*, the *function* must still exist somewhere — audit the function, not the form.

## Audit procedure

Work through all five passes in order — fixed coverage is what makes two audits of the same theme agree. Open commerce.md (path above) with `Read` and jump to sections; don't read it end-to-end.

### Pass 1 — Surface inventory

Read `ikas.config.json` + the `src/components/` and `src/sub-components/` listings. Then, if the editor is reachable, call `list_ready_made_pages()` — account and auth surfaces may be served by ikas's ready-made pages, which leave no trace in `src/` (commerce.md §4.4). `list_editor_pages()` + `list_page_sections(pageId)` also show whether built sections are actually placed. Map what exists onto:
- **§4.1 page surfaces** (homepage, PLP, PDP, cart, account ×5, auth, content, utility). A surface is covered by a section **or** an enabled ready-made page. Neither → **Boşluk**.
- **Editor unreachable** (tools missing or "No editor connected"): list account/auth surfaces with no section under **Doğrulanamadı**, not Boşluk. Tell the user how to confirm: `ikas-component dev` + open editor, or check the ready-made toggle in the editor.
- **§4.2 chrome surfaces** (header/footer, cart drawer, search, mobile drawer, profile/address modals, quick view, toast queue, loading indicator). For each: does the *function* exist somewhere? Optional ones (Quick View, Cart Drawer) missing → not a finding unless nothing covers the function. Profile-edit and address modals come with a ready-made account group.

### Pass 2 — Journey walk

Trace the shopper journey through the code, one stage at a time. For each stage, read the relevant components deeply enough to answer the stage questions — especially error/empty/loading paths (`catch` blocks, empty-state renders, §7.7 state anatomy).

| Stage | What must be true | Ruleset |
|---|---|---|
| **Keşif** (header, nav, search) | Nav reachable on mobile; search reachable, live or paged, with a no-results recovery; cart count visible when > 0 | §7.5, §9.2–9.3, §14 #8 |
| **Gezinme** (PLP) | Filter/sort state survives reload & back (URL); filtered-empty state offers clear-filters; pagination or infinite-scroll-with-fallback | §7.4, §14 #7 |
| **Karar** (PDP) | Variant selection updates price/stock/media and disables unavailable options; out-of-stock exposes back-in-stock (or an equivalent recovery), not a dead end; bundles and product option sets render when the product carries them | §7.3, §7.11–7.13, §13.B |
| **Satın alma** (ATC → cart → checkout) | ONE consistent ATC feedback pattern theme-wide; card ATC follows the OOS/bundle/variant ladder; quantity limits clamp with user-facing copy; optimistic mutations render immediately AND roll back visibly on failure — silent `try/finally` with no user-facing error is an automatic İhlal; checkout handoff works from cart page and drawer | §7.1, §7.8, §7.9, §13.B |
| **Kurtarma** (errors, 404, auth recovery) | Every failure surface (login, search, ATC, form save) exposes a next step; 404 offers routes back; forgot/recover password complete | §3 #7, §7.2, §7.6, §7.7 |
| **Sahiplik** (account, favorites, orders) | Auth gate waits for store hydration before redirecting (both directions); guest-favorite flow explains the redirect; account surfaces handle empty states; order detail covers multi-package + refund states; a guest can track an order (or the omission is deliberate). **Ready-made surfaces:** skip their internals (platform-owned) and audit only the theme's entry points into them (account icon, favorites, guest gates → auth with a return path) and their branding. Their missing theme header / footer is by design (§4.4), not a §14 #13 violation | §4.4, §7.2, §13.C, §13.E Guest Order Tracking |
| **Güven** (footer, i18n, a11y) | Prices via storefront formatting everywhere (no hand-built currency); focus trap + Esc + backdrop-close on every overlay; keyboard path through carousels; status never color-only | §11, §7.10, §12.3, §14 #2/#6/#12 |

### Pass 3 — Section-level contracts

For each section present, open its **§13 catalogue entry** and check the **Mandatory features** list. Missing mandatory feature → **İhlal**. Optional features absent → not a finding (they're design-dependent). Section not in the catalogue → check it against §5 (universal contract) only.

### Pass 4 — Anti-pattern sweep

1. **Mechanical items:** run `python3 <this skill's base directory>/../ikas-theme-builder/scripts/lint.py <project-root>` (for a `section` / `surface` scope, pass `--path` with the component folder and the sub-component folders it imports). Each finding already carries its §; verify it in the code before reporting, since the script is a filter.
2. **Remaining items:** scan the theme against the rest of **§14**. Read the list from the file, don't recall it.
   - Experience-level items (#1–#18, #24) are in scope.
   - The design-canonical items (#21, #22) are in scope when a design source exists.
   - Purely framework items (#19, #20, #23) are out of scope beyond what lint reports; note them in one line for a follow-up code review, don't expand.

### Pass 5 — Merchant reality check

Per **§10**: can the merchant edit every piece of copy, image, and destination (§10.1)? Are there knobs that fight the design (§10.2)? Would a zero-edit install look shippable and coherent (§10.3, §3 #6) — e.g. consistent default language across all sections, defaults that reflect a real store?

## Report contract

The report is in Turkish (unless asked otherwise) and has exactly these parts, in order:

1. **Karar cümlesi** — one sentence: is this theme'in deneyimi yayına hazır mı, ve tek en büyük risk ne.
2. **İhlaller** — table: bulgu, kanıt (component/dosya), dayanak (§). Ordered by revenue/UX impact.
3. **Boşluklar** — same table shape.
4. **Tema tercihleri** — short bullet list; explicitly marked "engel değil".
5. **Kontrat dışı öneriler** — optional, max 5 bullets, clearly separated so they can't be mistaken for requirements.
6. **Doğrulanamadı** — only if something couldn't be checked (typically ready-made page state with the editor offline): each item states what's unknown and how to confirm it. Omit the part when empty.
7. **Öncelikli aksiyon listesi** — numbered, blockers first, each one actionable.

Evidence means a component/file name and what you saw there — enough for someone to verify without re-auditing. The audit **changes nothing**: no fixes, no scaffolding, no prop edits, no ready-made page toggles. If the user wants fixes, that's a follow-up task routed to `ikas-theme-builder` (its "Fixing audit findings" workflow takes this report as input). After fixes, a scoped re-audit (`section <Name>` / `surface <name>`) closes the loop.

## Scope arguments

| Invocation | Scope |
|---|---|
| (none) | Full audit — all five passes |
| `surface <name>` | One page surface (e.g. `surface pdp`): passes 2–5 scoped to it |
| `section <Name>` | One section: its §13 entry, §5 universal contract, relevant journey stage(s), §14, and §10 for its props. Theme-wide gaps (missing chrome, toast) are reported under Boşluk only when this section's contract depends on them, marked "(tema geneli)" |
| `quick` | Passes 1 + 4 only — inventory and anti-patterns; say so in the report |

## Common mistakes

- Grading the theme against a remembered "standard theme" instead of commerce.md — that's the unanchored drift this skill exists to prevent.
- Treating a missing *optional* chrome form (Cart Drawer, Quick View) as a gap when the function exists elsewhere (§4.2).
- Reporting account/auth surfaces as Boşluk because `src/` has no sections for them — ready-made pages serve them without code (§4.4). Check `list_ready_made_pages()`, or file them under Doğrulanamadı.
- Burying a real İhlal (silent failure, dead end) under a pile of kontrat dışı ideas — severity classes exist so blockers surface first.
- Reporting "eksik section" for marketing sections the design source never shipped — sections are design-dependent; only §4.1 surface coverage and §13 mandatory features are contractual.
- Auditing code style (naming, CSS, structure) — out of scope; note once, move on.
