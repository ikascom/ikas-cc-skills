---
name: ikas-theme-audit
description: Use when auditing an existing ikas storefront theme's shopper experience — checking for missing page/chrome surfaces, incomplete or wrong flows, weak recovery paths, silent failures, or merchant-control gaps. Triggers on "temayı denetle", "audit this theme", "eksik section var mı", "chrome surface'lar tam mı", "akışlar doğru mu", "experience review", "pre-launch review", "bu tema yayına hazır mı".
---

# ikas Theme Audit

An **experience audit**, not a code review. The measuring stick is `references/commerce.md` (bundled with this skill) — the design-agnostic ruleset for what an ikas theme must DO. You read code only to infer what the shopper and the merchant will experience; you do not police framework style, CSS quality, or implementation taste. For framework-compliance review, route to the `ikas-theme-builder` skill's review workflow instead.

**Core discipline: every finding is anchored.** A finding either cites the commerce.md section it violates (§7.1, §13.B, §14 #15 …) or is explicitly labeled **kontrat dışı** (beyond contract). Unanchored criteria — "modern e-commerce best practice", "most themes do X" — are how audits drift; if you can't cite it, label it or drop it.

## Severity taxonomy

Classify every finding as exactly one of:

| Class | Meaning | Example |
|---|---|---|
| **İhlal (blocker)** | Breaks a commerce.md contract: a §7 behavior contract, a §13 mandatory feature, a §14 anti-pattern, a §4 required function | Cart mutation with no failure feedback (§7.8, §14 #15) |
| **Boşluk (gap)** | A §4 surface or chrome **function** is absent entirely | No toast/feedback queue anywhere (§4.2, §7.9) |
| **Tema tercihi** | Diverges from a convention but commerce.md allows it — often design-canonical | Full-page search instead of a Search Modal (§4.2 allows: the function, not the form) |
| **Kontrat dışı öneri** | Would likely improve conversion but no commerce.md rule requires it | Free-shipping progress bar in the cart drawer |

**Tema tercihi and kontrat dışı findings are never blockers** and never lead the report. Remember §4.2's rule: if the design source omitted a chrome surface's *form*, the *function* must still exist somewhere — audit the function, not the form.

## Audit procedure

Work through all five passes in order — fixed coverage is what makes two audits of the same theme agree. Open `references/commerce.md` with `Read` and jump to sections; don't read it end-to-end.

### Pass 1 — Surface inventory

Read `ikas.config.json` + the `src/components/` and `src/sub-components/` listings. Map what exists onto:
- **§4.1 page surfaces** (homepage, PLP, PDP, cart, account ×5, auth, content, utility). A surface with no sections covering it → **Boşluk**.
- **§4.2 chrome surfaces** (header/footer, cart drawer, search, mobile drawer, profile/address modals, quick view, toast queue, loading indicator). For each: does the *function* exist somewhere? Optional ones (Quick View, Cart Drawer) missing → not a finding unless nothing covers the function.

### Pass 2 — Journey walk

Trace the shopper journey through the code, one stage at a time. For each stage, read the relevant components deeply enough to answer the stage questions — especially error/empty/loading paths (`catch` blocks, empty-state renders, §7.7 state anatomy).

| Stage | What must be true | Ruleset |
|---|---|---|
| **Keşif** (header, nav, search) | Nav reachable on mobile; search reachable, live or paged, with a no-results recovery; cart count visible when > 0 | §7.5, §9.2–9.3, §14 #8 |
| **Gezinme** (PLP) | Filter/sort state survives reload & back (URL); filtered-empty state offers clear-filters; pagination or infinite-scroll-with-fallback | §7.4, §14 #7 |
| **Karar** (PDP) | Variant selection updates price/stock/media and disables unavailable options; out-of-stock has an affordance, not a dead end | §7.3, §13.B |
| **Satın alma** (ATC → cart → checkout) | ONE consistent ATC feedback pattern theme-wide; optimistic mutations render immediately AND roll back visibly on failure — silent `try/finally` with no user-facing error is an automatic İhlal; checkout handoff works from cart page and drawer | §7.1, §7.8, §7.9, §13.B |
| **Kurtarma** (errors, 404, auth recovery) | Every failure surface (login, search, ATC, form save) exposes a next step; 404 offers routes back; forgot/recover password complete | §3 #7, §7.2, §7.6, §7.7 |
| **Sahiplik** (account, favorites, orders) | Auth redirects return the user to where they were; guest-favorite flow explains the redirect; account surfaces handle empty states | §7.2, §13.C |
| **Güven** (footer, i18n, a11y) | Prices via storefront formatting everywhere (no hand-built currency); focus trap + Esc + backdrop-close on every overlay; keyboard path through carousels; status never color-only | §11, §7.10, §12.3, §14 #2/#6/#12 |

### Pass 3 — Section-level contracts

For each section present, open its **§13 catalogue entry** and check the **Mandatory features** list. Missing mandatory feature → **İhlal**. Optional features absent → not a finding (they're design-dependent). Section not in the catalogue → check it against §5 (universal contract) only.

### Pass 4 — Anti-pattern sweep

Scan the theme against **§14** — read the list from the file, don't recall it. Experience-level items (#1–#17) are in scope; purely framework items (#19, #20, #23) are out of scope here — note them in one line for a follow-up code review, don't expand.

### Pass 5 — Merchant reality check

Per **§10**: can the merchant edit every piece of copy, image, and destination (§10.1)? Are there knobs that fight the design (§10.2)? Would a zero-edit install look shippable and coherent (§10.3, §3 #6) — e.g. consistent default language across all sections, defaults that reflect a real store?

## Report contract

The report is in Turkish (unless asked otherwise) and has exactly these parts, in order:

1. **Karar cümlesi** — one sentence: is this theme'in deneyimi yayına hazır mı, ve tek en büyük risk ne.
2. **İhlaller** — table: bulgu, kanıt (component/dosya), dayanak (§). Ordered by revenue/UX impact.
3. **Boşluklar** — same table shape.
4. **Tema tercihleri** — short bullet list; explicitly marked "engel değil".
5. **Kontrat dışı öneriler** — optional, max 5 bullets, clearly separated so they can't be mistaken for requirements.
6. **Öncelikli aksiyon listesi** — numbered, blockers first, each one actionable.

Evidence means a component/file name and what you saw there — enough for someone to verify without re-auditing. The audit **changes nothing**: no fixes, no scaffolding, no prop edits. If the user wants fixes, that's a follow-up task routed to `ikas-theme-builder`.

## Scope arguments

| Invocation | Scope |
|---|---|
| (none) | Full audit — all five passes |
| `surface <name>` | One page surface (e.g. `surface pdp`): passes 2–5 scoped to it |
| `section <Name>` | One section: its §13 entry + relevant journey stage + §14 |
| `quick` | Passes 1 + 4 only — inventory and anti-patterns; say so in the report |

## Common mistakes

- Grading the theme against a remembered "standard theme" instead of commerce.md — that's the unanchored drift this skill exists to prevent.
- Treating a missing *optional* chrome form (Cart Drawer, Quick View) as a gap when the function exists elsewhere (§4.2).
- Burying a real İhlal (silent failure, dead end) under a pile of kontrat dışı ideas — severity classes exist so blockers surface first.
- Reporting "eksik section" for marketing sections the design source never shipped — sections are design-dependent; only §4.1 surface coverage and §13 mandatory features are contractual.
- Auditing code style (naming, CSS, structure) — out of scope; note once, move on.
