---
name: ikas-theme-builder
description: Use when building, scaffolding, modifying, or reviewing sections and sub-components of an ikas storefront theme. Triggers on tasks like "add a new section", "create the X section", "scaffold a Y section", "add a prop", "remove a prop", "compose the homepage / PDP / cart page", "add a drawer / modal / toast / chrome surface", "review this section against the ruleset", "audit a PR for theme consistency".
---

# ikas Theme Builder

Four sources of truth, each with its own decision territory:

| Source | Owns | Where |
|---|---|---|
| `references/commerce.md` | UX & conversion ruleset — what every surface must DO: behavior contracts, prop architecture, section catalogue, merchant control, anti-patterns. Deliberately design-agnostic. | **Bundled with this skill** — read it from this skill's `references/` directory |
| **Design source** | Everything visual — layout, color, typography, spacing, motion (commerce.md §1). Either a delivered design (Stitch / Figma / supplied screens), a project-root `design.md`, or the user acting as design authority. | Per project |
| `CLAUDE.md` | Framework rules, auto-generated file list, CLI command shapes, MCP tool inventory. | Project root (auto-loaded by Claude Code) |
| `ikas-code-components` MCP | Live framework catalog — templates, prop types, function docs, model types, framework guides. | MCP server |

Always read the relevant commerce.md section(s) **before** writing code. Never improvise theme rules from training data, and **always query MCP for framework facts** (function signatures, prop types, model fields, section templates) rather than reconstructing them from memory.

**Never invent visuals.** When a visual decision is needed and the design source hasn't made it, ask the design authority (the user) — don't default to a "modern e-commerce" reflex (commerce.md §1).

When no canonical design exists, route each open visual decision through commerce.md §6.1: if it's a legitimate merchant lever there (e.g. items-per-row, section colors), expose it as a prop and ask the design authority only for the **default value**; if it's design territory (motion, typography, spacing, layout shape), ask the design authority for the decision itself and fix it in code. The answers collected this way **are** the design source for this theme — they double as the shippable defaults §1 requires.

### MCP returns two kinds of content

MCP responses mix **framework facts (must)** and **reference-theme conventions (preference)**. Framework facts (API signatures, prop types, model fields, enum values, "root sections are auto-reactive — don't wrap in `observer()`") are non-negotiable. Reference-theme conventions (what the reference theme happened to ship — tab-based account, drawerless cart, 12-child PDP) are one valid design among several.

> **(commerce.md §2)** Full distinction with examples + the discovery-fallback rule (`list_*`, `search_docs`).

## Setup check (do this first)

1. **`CLAUDE.md` present at project root?** If not, this is probably not an ikas Code Components project — stop and confirm with the user before proceeding.
2. **Identify the design source.** Check for a delivered design (Stitch project, Figma link, screens supplied in the conversation) and a project-root `design.md`. If neither exists, the user is the design authority: visual decisions get asked, not invented.
3. `references/commerce.md` ships with this skill — no project-root copy is required.

## Reading order

`CLAUDE.md` is the **always-on baseline** — it sets the rules of engagement: never hand-edit auto-generated files (`ikas.config.json`, `types.ts`, `global-types.ts`, `src/components/index.ts`), sub-component file structure, observer rules, CLI command shapes, custom ENUM lifecycle. You don't "step into" it; you obey it throughout.

Default order for a task:

1. **`references/commerce.md` first — establish intent.** What must this surface DO? Read its §13 catalogue entry (mandatory / optional features, interactions, a11y), the relevant §7 behavior contracts, §8 page composition, §5/§6 section contract + prop architecture.
2. **MCP — get the technical facts.** `get_section_template("<type>")` for the starter; pattern guides where applicable (`get_framework_guide("product-detail-patterns")`, `"cart-patterns"`, `"header-footer-patterns"`, `"account-patterns"`, `"review-patterns"`, `"blog-patterns"`, `"product-list-patterns"`, `"slider-overlay-patterns"`, `"navigation-patterns"`); function/model docs (`get_function_doc`, `get_model_guide`, `get_functions_for_type`, `get_framework_guide("common-pitfalls")`).
3. **Design source — apply the visual identity.** Delivered design: match it faithfully (commerce.md §1 five-step workflow). `design.md`: use its tokens. Neither: collect the visual decisions this task needs and ask the design authority before styling.
4. **Implement.** commerce.md → feature surface + merchant-controllable area. CLAUDE.md + MCP → function calls, prop names, type imports, CLI commands, file paths. Design source → colors, spacing, motion, component shape.

**Step 1 is fixed** — it anchors the work to the ecommerce contract that survives any visual identity. Steps 2–3 interleave: style-only edits lead with the design source; behavior bug fixes may never touch it.

**MCP pointers in this skill (and in commerce.md) are starting points, not boundaries.** If the named tools don't answer your question, fall back to MCP discovery: `list_topics()`, `list_section_types()`, `list_examples()`, `list_functions("Category")`, `list_types(domain)`, `search_types(query)`, or the hybrid `search_docs(query)`. MCP is the source of truth; the pointers exist to save discovery cost, not to limit what you can query.

Beyond the doc tools, MCP ships two workflow families this skill routes to: the **live-editor tools** (place sections on pages and fill their prop values — see Workflow C; always read `get_editor_workflow()` first) and the **migration tools** (`analyze_old_theme`, `plan_migration`, `get_migration_guide` — 16 topics, `get_section_migration_plan`) for porting an old-system theme; when the task is a migration, start from those instead of scaffolding blind.

## When to use

- Building a new section component (`src/components/<Name>/`).
- Adding or removing a prop on an existing section or sub-component.
- Composing a page (homepage, PLP, PDP, cart, account, blog, search, 404).
- Adding a chrome surface (drawer, modal, toast, indicator) or wiring its trigger sources.
- Reviewing a section, a PR, or the whole theme against the ruleset.
- Diagnosing why a section feels inconsistent with the rest of the theme.

## Decision Matrix

Open `references/commerce.md` with `Read` and jump to the referenced section — don't read the whole file when one section answers the question.

| Task | First read | Design input | Then run |
|------|------------|--------------|----------|
| Building a **new section** | commerce.md §13 catalogue entry (or derive from §3 + §5 if not catalogued) + §5 universal contract + relevant §7 behavior contracts + §8 placement constraints | Design source for layout / tokens / copy tone | MCP `get_section_template` → CLI `add-component` |
| **Adding a prop** | commerce.md §6 (what to expose — mind §1 prop philosophy) + §13 entry | Only if the prop is a merchant-tunable visual lever | CLI `add-prop` (or `add-enum` first if ENUM, §6.5) |
| **Removing a prop** | commerce.md §13 entry to confirm it's safe to drop | — | CLI `remove-prop`, then grep source for dead references |
| **Composing a page** | commerce.md §8 + §4.3 | Design source decides ordering beyond §8's constraints | MCP `get_editor_workflow()` → `list_editor_pages` → `add_sections_to_page` / `update_page_sections` (needs `ikas-component dev` + connected editor) |
| **Adding a chrome surface** (drawer/modal/toast) | commerce.md §9 entry + §7 for the triggering behavior + MCP `get_framework_guide("sub-component-catalog")` | Design source for panel visuals | Mount from the correct parent; wire triggers per §9 |
| **Reviewing a section** | commerce.md §15 build checklist + §14 anti-patterns | Design source fidelity check | `npx ikas-component check --json` + `npx ikas-component build` |
| **Custom ENUM lifecycle** | commerce.md §6.5 | — | CLI `add-enum` **before** any prop referencing it; `remove-enum` after all references are removed |

## Task Workflows

### A. Building a new section

1. **Find the section in commerce.md §13.** Note mandatory / optional features, props, states, interactions, a11y. If it's not catalogued, derive its contract from §3 + §5 and propose the entry to the user before scaffolding.
2. **Read commerce.md §5** (universal section contract) and confirm the section can satisfy it.
3. **Get the design input.** Delivered design: read the screen / region and capture structure, tokens, copy. Otherwise: list the visual decisions this section needs and resolve them with the design authority.
4. **Identify required custom ENUMs** (§6.5). Run `add-enum` first per `CLAUDE.md`; capture the returned id.
5. **Get the MCP starter**: `get_section_template(sectionType)` — starter files, canonical prop list, child file list (`get_section_child`, or the `include` param to bundle subtrees inline). For **container sections** the template returns a multi-step **Setup Recipe** (create children first, capture their opaque `componentId`s, create the parent, wire `filteredComponentIds` via `update-prop`) — follow it in order, don't collapse it into one command. Check `list_section_types()` when unsure: besides sections it ships *Pattern* templates (`add-to-cart`, `bundle-products`, `variant-selection`, `product-pricing`, `navigation`, `image-handling`, `component-renderer`) — API reference implementations worth reading before hand-rolling those behaviors. For surfaces with a pattern guide, read it too.
6. **Adapt the starter's prop surface per commerce.md §1 + §6.1** — expose editable content (TEXT / IMAGE / LINK / sources / inherently-optional toggles), drop knobs the design source has fixed, add props the design implies. Defaults must be shippable (§1).
7. **Run the CLI `add-component` command.** Never hand-edit auto-generated files.
8. **Look up storefront APIs** via MCP (`get_model_guide`, `get_function_doc`, `get_functions_for_type`) before writing data-access code.
9. **Implement `index.tsx` + `styles.css`** — behavior per commerce.md §7, visuals per the design source, CSS scoping per `CLAUDE.md` / MCP `css-scoping` guide.
10. **Pre-flight checks** (below), then `npx ikas-component check --json` and `npx ikas-component build` — both clean.

### B. Adding a prop to an existing section

1. **Read commerce.md §6** — what to expose, prop group vocabulary (§6.3), patterns (IMAGE triplet §6.2, LINK §6.4, loading quartet §6.6).
2. **Check §1 prop philosophy** — if the design source has fixed this decision, the prop may be noise; push back before adding.
3. **Read the §13 entry** for the section to confirm the prop fits its contract.
4. **If ENUM:** `get_framework_guide("custom-enums")`, then CLI `add-enum` first; reuse existing template enums when the meaning matches.
5. **Run `npx ikas-component config add-prop`** with the correct `--group` flag (§6.3 vocabulary).
6. **Wire the prop into `index.tsx`** per the §5.4 no-static-text rule (TEXT → element content, COLOR → inline style, BOOLEAN → conditional rendering).
7. **Run `check` + `build`.**

### C. Composing a page

1. **Read commerce.md §8** for the page's constraints (first product surface within one scroll, no marketing decoration on utilitarian pages, PDP rhythm, header/footer immovable) and §4.3 (composition decoupled from sections).
2. **Ordering beyond those constraints comes from the design source** — not from a remembered "standard" rhythm.
3. **Place and fill via the MCP live-editor tools** (needs `ikas-component dev` + connected editor). Read `get_editor_workflow()` first — it owns the tool sequence, per-prop-type value shapes, and COMPONENT_LIST read-modify-write rules; don't reconstruct them here. Two standing judgments: prefer the batch tools (`add_sections_to_page`, `update_page_sections`) over per-prop calls, and call `publish_theme` only when the user explicitly asks.
4. **Confirm mandatory surfaces are present** per §4.1 and the §13 entries of the sections used.
5. **Confirm chrome triggers are wired** per §9 — one consistent ATC feedback pattern across the theme; search / mobile drawer triggers from header.

### D. Adding a chrome surface (drawer / modal / toast / indicator)

1. **Check the MCP sub-component catalog first** — `get_framework_guide("sub-component-catalog")`: `Modal`, `ConfirmModal`, `Toast` + `useToast`, `ImagePreviewModal`, `PageLoader`, etc. **Reuse a primitive when one fits.**
2. **Find the surface in commerce.md §9** — mount point, trigger sources, close conditions, feature surface, a11y expectations.
3. **Read commerce.md §7.x** for the triggering behavior (§7.1 cart mutations / ATC feedback, §7.9 toast queue).
4. **Visuals from the design source** — backdrop, panel, motion (with `prefers-reduced-motion` pairing per §5.7).
5. **Mount from the correct parent and wire every trigger source** — a surface that auto-opens on a cross-page mutation must be reachable from every surface firing that mutation.
6. **Focus trap, `Esc`, backdrop-click close, `aria-live` for async state** per §7.10 + §12.3.
7. **Run `check` + `build`.**

### E. Reviewing a section against the ruleset

1. **Run the commerce.md §15 build checklist.**
2. **Scan against §14 anti-patterns** — any hit is a blocker.
3. **Check design-source fidelity** — does the implementation match the delivered design / `design.md` tokens? Deviations are flagged, not silently normalized.
4. **Apply the must-vs-preference lens (§2).** Framework-fact violations (root wrapped in `observer()`, missing `backgroundColor`, hand-formatted currency, wrong model field names) → blockers. Divergence from reference-theme conventions → theme choice, noted not blocked.
5. **`npx ikas-component check --json` + `npx ikas-component build`** — both must pass.

Report findings as a punch list (passing / failing-blockers / theme-choice-noted).

## Conflict order

Visual concerns → the design source. Framework / CLI / API concerns → `CLAUDE.md` + MCP. Behavior, feature surface, prop architecture, merchant control, page composition → `references/commerce.md`.

## Universal Pre-flight Checks

Before reporting any task done:

- **commerce.md §15 build checklist** — behavior contracts, state anatomy quartet, optimistic mutations, no static text, `backgroundColor` prop, null safety, a11y, shippable defaults.
- **Design-source fidelity** — visuals match the source; no invented substitutions.
- **`npx ikas-component check --json`** — passes with no errors.
- **`npx ikas-component build`** — completes clean.

## Anti-pattern Quick Scan

Before merging, scan the change against commerce.md §14. Any hit is a blocker. Don't rely on a memorized list — read it from the source so you always get the current version.

## Common Pitfalls

The MCP `common-pitfalls` framework guide is the canonical list (documented framework pitfalls with right/wrong code examples). Always read it via `get_framework_guide("common-pitfalls")` rather than relying on inline summaries — the list evolves with ikas.

For project-specific gotchas not in MCP, see `CLAUDE.md` (auto-generated file rules, custom ENUM CLI lifecycle, sub-component file structure).
