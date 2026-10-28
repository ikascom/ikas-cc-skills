---
name: ikas-theme-builder
description: Use when building, scaffolding, modifying, or reviewing sections and sub-components of an ikas storefront theme, or composing and filling its pages in the live editor. Triggers on tasks like "add a new section", "create the X section", "add a prop", "remove a prop", "compose the homepage / PDP / cart page", "add login / register / my account / orders pages", "add a drawer / modal / toast", "review this section against the ruleset", "review a PR for theme consistency", "fix the audit findings".
---

# ikas Theme Builder

| Source | Decides | Where |
|---|---|---|
| `references/commerce.md` | What every surface must DO: behavior contracts, feature surface, prop architecture and editor sidebar schema, merchant control, page composition | This skill's `references/` |
| Design source | Everything visual: layout, color, typography, spacing, motion | Delivered design (Stitch / Figma / screens), a project-root `design.md`, or the user as design authority |
| `CLAUDE.md` + `ikas-code-components` MCP | Framework facts: CLI shapes, auto-generated files, templates, prop types, function signatures, model fields | Project root / MCP server |

On conflict, each source wins in its own territory.

**Standing rules**

- **commerce.md before code.** Read the section(s) the workflow names below; jump with `Read`, don't read end-to-end.
- **MCP for facts, never memory.** Query signatures, prop types, model fields and templates. MCP content is either a framework fact (must) or a reference-theme convention (one valid design). commerce.md §2 draws the line.
- **Never invent visuals.** If the design source hasn't decided, route the decision through commerce.md §6.1:
  - **Merchant lever:** expose it as a prop and ask the user only for its default.
  - **Design territory:** ask the user for the decision itself and fix it in code.
  - The collected answers become the design source and the shippable defaults.
- **Migration from an old-system theme:** start from MCP `get_migration_guide("iterative-workflow")`, not from blind scaffolding.

**Setup check:** `CLAUDE.md` at project root (if missing, it's probably not an ikas project — confirm first). Identify the design source; if there's none, the user is the design authority.

## Workflows

### A. New section

1. **Contract:** read the commerce.md §13 entry (mandatory / optional features, states, interactions, a11y) + §5 universal contract + the §7 contracts it triggers. Not catalogued? Derive from §3 + §5 and propose the entry to the user first.
2. **Design input:** capture the delivered design's structure, tokens and copy. Without a design, resolve open visual decisions with the user as described above.
3. **Starter:** use `get_section_template(type)` and follow what it returns, including any Setup Recipe or "ask the user first" banner. `list_section_types()` also lists *Pattern* templates worth reading before hand-rolling a behavior (add-to-cart, variant-selection…).
4. **Prop surface:** adapt the starter per §1 + §6.1:
   - Expose editable content; drop knobs the design fixed; add what the design implies.
   - Put every prop in its §6.3 group with a Turkish `displayName`, and write a description only where §6.3 calls for one.
   - Defaults are the design's content (shippable on install).
5. **Scaffold:** `add-enum` first for any custom ENUM (§6.5), then `add-component` with all props. Header / Footer take `--isHeader` / `--isFooter`, which is what makes them the theme-wide COMMON section.
6. **Implement:** look up APIs first (`get_model_guide`, `get_function_doc`). Behavior per §7, visuals per the design source.
7. **Done check** (below).

### B. Add / remove a prop

1. §6.1 + §1: if the design source already fixed this decision, the prop is noise — push back.
2. Confirm against the section's §13 entry.
3. `add-prop` with its §6.3 group and Turkish label (ENUM: `add-enum` first, reusing template enums when the meaning matches). Wire it per §5.4.
4. Removal: `remove-prop`, then grep the source for dead references.

### C. Compose and fill a page

1. **Constraints:** commerce.md §8 + §4.3. Order beyond those comes from the design source, not a remembered "standard" rhythm.
2. **Placing and filling:** read `get_editor_workflow()` first and follow it. It owns the tool order, value shapes, COMMON header / footer values, reordering, binding to globals, and which actions need the user's OK.
3. **Content:** fill with the design source's copy and images — defaults must be shippable (§1).
4. **Verify:** §4.1 surfaces are covered and §9 chrome triggers are wired, with one ATC feedback pattern theme-wide.

### D. Chrome surface (drawer / modal / toast / indicator)

1. **Reuse first:** check `get_framework_guide("sub-component-catalog")` and `"slider-overlay-patterns"` before building a shell yourself.
2. **Contract:** read commerce.md §9 for the surface (mount point, triggers, close conditions, feature surface) and §7 for the behavior that triggers it.
3. **Wiring:** mount it from the correct parent and wire **every** trigger source. Add focus trap, `Esc`, backdrop close and `aria-live` (§7.10, §12.3). Pair motion with `prefers-reduced-motion`.

### E. Review a section or PR

1. **Checks:** run the §15 checklist, the §14 anti-pattern scan (any hit is a blocker) and design-source fidelity (flag deviations, don't normalize them).
2. **Must vs preference (§2):** framework-fact violations are blockers; divergence from reference-theme conventions is a noted theme choice.
3. **Report:** a punch list of passing / blockers / theme choices.

This is a compliance review. For a whole-theme shopper-experience audit, use `ikas-theme-audit`.

### F. Auth & account pages (login, register, password, my account, orders, addresses, favorites)

ikas ships these as **ready-made pages** (commerce.md §4.4). MCP enforces the "ask the user first, ready-made as the recommended option" gate: the `get_section_template` banner, `get_editor_workflow`, `list_ready_made_pages`. Follow it; don't re-derive it. What MCP leaves to you:

1. **Header / footer:** ready-made pages are born without the theme's header and footer; they draw their own top bar. Ask the user whether to place them, and if so, follow the MCP guidance for placement.
2. **Entry points (theme code):** the header account icon, favorites, and guest favorite / review gates lead to auth with a return path (§7.2).
3. **Branding:** colors bound to theme tokens, not hex. The `ikas-theme-globals` skill covers this.
4. **Custom route (user chose it):** Workflow A with the §13.B / §13.C entries.

### G. Fix audit findings

The input is an `ikas-theme-audit` report; every finding cites a commerce.md §.

1. **Order:** İhlal first, then Boşluk. Tema tercihi only if the user asks. Kontrat dışı is new scope — confirm first.
2. **Route:** missing section → A, prop → B, page coverage → C, chrome → D, auth/account → F.
3. **Verify:** check each fix against the cited § (not just the symptom), then run the done check. A scoped re-audit (`section <Name>` / `surface <name>`) closes the loop.

## Done check

Before reporting any task done:

- **commerce.md §15 build checklist**, including a §14 scan. Read both from the file, not memory.
- **Design-source fidelity:** no invented substitutions.
- **Framework pitfalls:** `get_framework_guide("common-pitfalls")` when touching unfamiliar APIs.
- **Lint:** `python3 <this skill's base directory>/scripts/lint.py <project-root>` exits 0. It mechanically checks the §14 items it can: root `observer`, `backgroundColor`, catch-less cart mutations, swallowed failures (console-only `catch`, unread mutation results), a theme-side debounce around `searchProductList`, static text, reduced motion, DIY price formatting, multiple `<h1>`, plus project-wide coverage (option sets never loaded, bundle sub-products / favorites never used, a dead edit-line mode). Fix HATA findings. A deliberate exception goes into `--allow <file>` with a `//` justification.
- **Build:** `npx ikas-component check --json` and `npx ikas-component build` both pass clean.
