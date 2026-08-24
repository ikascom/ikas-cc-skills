# COMMERCE.md — UX & Conversion Ruleset for ikas Themes

> **What this is.** The UX/behavior ruleset for an ikas storefront theme. It defines what the storefront must DO — purchase flow, recovery paths, optimistic UI, accessibility, merchant control — **without dictating how it looks**. Visual decisions come from a *design source*: a delivered design (a Google Stitch project, a design partner's screens, a supplied Figma file) or, when building from scratch, the brief and direction given by the user / design team during the build.
>
> **What this is not.** Not a visual style guide — visual identity comes from the design source. Not a framework manual — see `CLAUDE.md` + the `ikas-code-components` MCP server.
>
> **How to use it.** Before scoping a section, find its entry in §13 and lock its mandatory features, interactions, and accessibility intent. Before composing a page, consult §8. Before adding interactivity, consult §7. For the **actual code** — starter templates, prop names, helper functions, type definitions — query MCP (§2).
>
> **Conflict order.** Visual concerns → the supplied design source. Framework / CLI concerns → `CLAUDE.md` + MCP. Commerce behavior, feature surface, recovery paths, merchant control surface area → this doc.

---

## 1. Working from a design source

The design source is **canonical for everything visual**: layout, spacing, color, typography, image treatment, alignment, aspect ratios, motion. It takes one of two forms:

- **Delivered design** — a Stitch export, a Figma file, a set of supplied screens. The job is not to design — it is to **match, wire, and ship**.
- **Design authority** — no complete design exists yet; the user / design team makes visual calls during the build (optionally captured in a project-root `design.md`). When a visual decision is needed and not yet made, **ask the design authority — don't invent from a "modern e-commerce" reflex**.

Either way, this doc never decides visuals. It decides behavior, feature surface, and merchant control.

### The five-step workflow

1. **Identify every screen and component in the design source.** Map each one to an ikas *page surface* (homepage / PLP / PDP / cart / account / etc.) and a *section type* (or, when nothing matches, a new composition).
2. **Pick the closest MCP starter for each section.** Run `get_section_template(...)` and use its CLI command as the scaffolding starting point. Adapt its prop surface to fit the design — don't shape the design to fit the template.
3. **Translate the design's structure to JSX faithfully.** Match the DOM the design implies. Don't simplify a 3-column layout into a 2-column to fit a starter default; don't replace an asymmetric hero with a centered one because a template assumed centered.
4. **Wire commerce behavior per §7–9 of this doc.** Behavior is invariant across designs — every theme has the same cart mutation contract, the same login redirect rules, the same optimistic UI requirements.
5. **Expose merchant controls for content the design treats as editable surface** — copy, images, destination links, product / category sources, *inherently* optional content blocks (§5). **Do not** expose merchant controls for design decisions (colors, alignment, layout variants, aspect ratios).

### Prop philosophy with a canonical design

Prop surface area depends on whether the design is canonical. When it is, many conventionally-recommended props become noise — they either contradict the design or expose a knob the merchant shouldn't turn.

| Concern | No canonical design (design decisions still open) | Design is canonical |
|---|---|---|
| COLOR props per section | 3–6 typical (`textColor`, `accentColor`, …) | `backgroundColor` only (framework requirement); additional colors only if the design treats a value as a merchant-tunable brand lever |
| Layout / alignment / aspect-ratio ENUMs | Common — give merchants choice | Avoided — the design picked one |
| Background alternation between sections | Mandatory | Decided by the design |
| Section-header alignment ENUM | Standard pattern | Removed; alignment is designed |
| Show / Hide block toggles | Liberal | Only for inherently optional blocks (countdown, brand line on PDP, ratings on a card when the design ships them as optional). Not for design-decided variants |
| Layout variant ENUMs (`centered` / `asymmetric` etc.) | Standard pattern | Avoided unless the design explicitly ships multiple variants the merchant should pick between |

What does **not** change: behavior contracts, recovery paths, optimistic UI, accessibility, i18n, performance, anti-patterns.

### Default values reflect the design

A merchant installing this theme with zero edits should see **the design source**. That means default copy = the design's copy, default images = the design's images (or close licensable placeholders), default product / category sources = sensible seeds (e.g. first published collection), default `backgroundColor` = the section's designed background. Defaults are non-negotiable: shippable on install.

---

## 2. MCP boundary — what to query, not duplicate

The `ikas-code-components` MCP server is the source of truth for **all framework / API / type / template knowledge**. Before writing code, query MCP — never reconstruct what MCP returns from this doc.

**Calibration rule (also for editing this doc):** this doc states what a surface must DO and points at MCP for shapes. When tempted to quote a signature, field list, or child count here, write a pointer instead — in practice, every fact this doc has ever gotten wrong was a quoted shape; the behavior contracts don't rot.

| MCP tool | Returns | Use when |
|---|---|---|
| `list_section_types()` | The section types available as templates | Discovering what's pre-built |
| `get_section_template(sectionType)` | Production starter: config snippet + working source files + the CLI setup steps (container sections get a multi-step **Setup Recipe** — children first, capture opaque ids, then wire the parent) + child lists; an `include` param bundles subtrees inline | **Always**, before scaffolding any section |
| `get_section_child(section, name, kind)` | The full files of one child / component / sub-component under a section template | When extending a section with its child |
| `list_topics()` / `get_framework_guide(topic)` | Framework guides — `ai-workflow`, `common-pitfalls`, `prop-types`, `prop-groups`, `css-scoping`, `form-handling`, `async-data-patterns`, `component-renderer-patterns`, `private-var-map`, `sub-component-catalog`, `custom-enums`, `theme-globals`, `image-handling`, `page-composition`, `global-css`, plus pattern guides: `product-detail-patterns`, `product-list-patterns`, `cart-patterns`, `account-patterns`, `header-footer-patterns`, `review-patterns`, `slider-overlay-patterns`, `blog-patterns`, `navigation-patterns` — the list grows; `list_topics()` is the source of truth | Before writing CSS, prop wiring, forms, async data, slot rendering, navigation |
| `get_prop_types()` | All ikas.config.json prop types with TS types and examples | When deciding the type of a new prop |
| `get_model_guide(model)` | A model's full TS type definition + every utility function with summary + every related type + the import statement | Before reading from any storefront model |
| `get_type_definition(name)` / `search_types(query)` / `list_types(domain?, kind?)` | Full TS type / enum definitions, ranked matches, filtered listings | Type / enum discovery |
| `list_functions(category?)` / `get_function_doc(name)` / `get_functions_for_type(typeName)` | Function inventory and per-function docs | Before calling any storefront function |
| `search_docs(query)` | Hybrid search across functions + framework topics + types | When you don't know which tool to call |
| `get_editor_workflow()` + the live-editor tool family (`add_sections_to_page`, `update_page_sections`, `get_component_props`, `get_section_values`, entity lookups, `upload_images`, `publish_theme` — guarded) | Placing sections on editor pages and filling their prop **values** (define-props vs fill-values are different jobs); the workflow doc enumerates the family, tool sequence, and per-type value shapes. Requires `ikas-component dev` + connected editor | Composing a page / filling content — read `get_editor_workflow()` first |
| Theme-global tools (`list_theme_globals`, `create_theme_global`, `update_theme_color`, `update_theme_color_scheme`, `update_text_style`, `update_theme_breakpoint`, `update_theme_keyframe`, …) | Store-persistent design tokens: colors, typography, color schemes, breakpoints, keyframes | Token work — route to the `ikas-theme-globals` skill |
| Migration tools (`analyze_old_theme`, `plan_migration`, `get_migration_guide`, `get_migration_example`, `get_section_migration_plan`) | Old-system theme → Code Components migration workflow | Migrating an existing theme |
| `get_code_example(task)` / `list_examples()` | API usage examples extracted from a production theme (the registry can be empty on some servers — fall back to function docs) | When a function doc alone isn't enough |

**Pointers are starting points, not boundaries.** When the listed tools don't answer your question, fall back to discovery (`list_topics()`, `list_section_types()`, `search_docs(query)`). MCP wins over this doc.

### Two kinds of MCP content — distinguish them

- **Framework facts (must):** API signatures, prop types, model fields, function return shapes, enum values, the auto-validate-after-submit rule, "root sections are auto-reactive (don't wrap in `observer()`)", `IkasCartOperationResult.validationError` enum values, `Router` method names. **Non-negotiable.**
- **Reference-theme conventions (preference):** What the production ikas reference theme chose — tab-based account dashboard, ToastContainer mounted from Header, CartPage without a separate Cart Drawer, two-slot Product Detail composition. **One valid design.** The incoming design source may pick differently — follow the design.

Never violate framework facts (e.g. omitting `backgroundColor`, hand-formatting prices instead of `formattedPrice`, wrapping a section root in `observer()`). Freely deviate from reference-theme conventions when the design source asks for it.

---

## 3. Commerce-First Principles

1. **The storefront is a transaction.** Every section either (a) supports the path to purchase, (b) recovers an interrupted purchase, or (c) services an existing customer.
2. **The design is canonical; the merchant is the content author.** Visual identity comes from the design source. The merchant edits copy, images, destinations, optional toggles — not visual structure.
3. **Optimistic UI by default** for cart and favorites — render new state immediately, reconcile with the server, roll back visibly on failure.
4. **Mobile is the design target.** Buying converts on mobile.
5. **Accessibility, SEO, i18n are commerce features**, not polish.
6. **Defaults must be sellable.** Default prop values reflect the design's shipped content — installable with zero edits.
7. **Recovery paths are first-class.** Every failure (login, payment, search, ATC, address save) exposes a recovery affordance. No dead ends.

---

## 4. The Surface Map

The theme covers **page surfaces** and **chrome surfaces**. Every section belongs to one.

### 4.1 Page surfaces

| Surface | Purpose | Primary sections |
|---|---|---|
| Homepage | Brand orientation + funnel entry | Hero, Featured Collection, Brand Story, Lookbook, Newsletter, Promo Banner, Product Slider, Blog Slider, Trust Badges |
| Product Listing (PLP) | Browse + filter the catalogue | Product List, Collection Hero, Filter Panel |
| Product Detail (PDP) | The decision surface | Product Detail, Product Reviews, Recently Viewed, Trust Badges, editorial blocks |
| Cart | Pre-checkout review | Cart Page |
| Account: Dashboard | Self-service landing | Account Dashboard |
| Account: Orders | Order history + detail | Account Orders, Account Order Detail |
| Account: Addresses | Shipping/billing book | Account Addresses |
| Account: Favorites | Saved products | Favorite Products |
| Account: Auth | Sign in / up / recover | Login, Register, Forgot Password, Recover Password |
| Content | Editorial pages | Blog List, Blog Detail, Blog Slider, Rich Text, Image+Text, FAQ |
| Utility | Out-of-flow states | Search Results, 404 / Not Found, Guest Order Tracking |

### 4.2 Chrome surfaces (global, mounted outside page flow)

| Surface | Mount point | When it appears |
|---|---|---|
| Header (with Announcement Bar) | `Header` section | Always |
| Footer | `Footer` section | Always |
| Cart Drawer *(optional, design-dependent)* | From Header | On ATC OR cart-icon click |
| Search Modal | From Header | On search-icon click |
| Mobile Drawer | From Header | On hamburger tap (mobile) |
| Profile Edit Modal | From Account Dashboard | On "Edit profile" |
| Address Form Modal/Drawer | From Account Addresses | On add/edit address |
| Quick View Modal *(optional)* | From PLP / Featured Collection | On card "Quick view" |
| Toast / Snackbar Queue | Global | On optimistic UI success/failure |
| Top Loading Indicator | Global | On long-running navigation or mutation |

Sections may **trigger** chrome surfaces; they never **embed** them. If the design source omits a chrome surface (e.g. no Cart Drawer; a full-page Search instead of a modal), follow the design — the **function** must exist somewhere, not this specific form.

### 4.3 Page composition is decoupled from sections

A "page" is a merchant-arranged sequence of sections. **Only Header and Footer are immovable.** Page rhythm is the design source's decision, subject to the few UX constraints in §8.

---

## 5. Universal Section Contract

Every section must satisfy these.

### 5.1 Background prop (framework requirement)

Every section declares a `backgroundColor` COLOR prop with default = **the section's designed background color** (typically `#ffffff`). Do not add additional COLOR props unless the design treats a value as a merchant-tunable brand lever.

### 5.2 Mobile-first responsive

Every section renders usable at 360px without horizontal scroll. The design source specifies breakpoints; honor them.

### 5.3 Null-safety culture

Every storefront model access is null-guarded. Empty render is a defined empty state (§7.7), never a crash, never an empty `<div>` with no signal. Storefront stores (`customerStore.customer`, `cartStore.cart`) are `null` before initialization completes; props from the editor are `undefined` before the merchant sets them.

> **(MCP)** Concrete patterns: `get_framework_guide("common-pitfalls")` items #5, #8, #11.

### 5.4 No static user-visible text

Every visible string is a TEXT (or RICH_TEXT) prop with a realistic default — including headings, button labels (with `submitButtonText` + `submittingButtonText` pair), empty-state messages, error messages the theme controls, `aria-label` on icon-only controls, image `alt` text. **Default values match the copy in the design source.** Structural ARIA (`role="dialog"`, `aria-modal="true"`) may be literal.

> **(MCP)** `get_framework_guide("common-pitfalls")` #16.

### 5.5 Prop groups

Use the vocabulary in §6.3. Sections with 5+ props always have groups.

### 5.6 Self-contained mount/unmount

Sections set up their own subscriptions, timers, listeners on mount and tear them down on unmount. No global side effects (cookie writes, analytics, navigation) on mount unless the section's job *is* that side effect.

### 5.7 Reduced motion and focus states

Every transition/animation pairs with `@media (prefers-reduced-motion: reduce)`. Every interactive element has a visible `:focus-visible` state. The **visual style** of the focus ring comes from the design source; the **fact** of its presence is non-negotiable.

### 5.8 Slot props for compositional sections

Slots are used when the section is a **layout shell** that the design composes from multiple child components (e.g. PDP info column has product name + price + variants + ATC as separate child components). Editorial guidance:

- Slot prop names are descriptive (`slides`, `cards`, `tabs`, `bottomComponents`), never `children`.
- A section can have multiple COMPONENT_LIST slots when the layout has multiple regions.
- When a slot passes per-item data to its children (a Product Slider passing each `product` to its card), the data binding is declared via `privateVarMap`.
- Use `filteredComponentIds` to restrict which child components can be placed in a slot.

> **(MCP)** `get_framework_guide("component-renderer-patterns")` + `get_framework_guide("private-var-map")`. Reusable internal components: `get_framework_guide("sub-component-catalog")`.

---

## 6. Prop Architecture

### 6.1 What to expose as props

**Always expose:**

- All visible copy as TEXT / RICH_TEXT.
- All images as IMAGE props paired with an `imageAlt` TEXT.
- Destination links as LINK (or LIST_OF_LINK for menus).
- Product / Category / Brand / Blog sources (PRODUCT, PRODUCT_LIST, CATEGORY, BRAND, BLOG, etc.).

**Expose conditionally:**

- BOOLEAN toggles for *inherently optional* content blocks — countdown timer, announcement bar dismissibility, "show ratings on card" when the design ships ratings as optional, brand line on PDP. Do **not** expose toggles for design-decided variants.
- COLOR props **beyond `backgroundColor`** only when the design treats a value as a brand-tunable lever (typical: site-wide accent in Footer; a promo strip background. atypical: per-section text color).
- NUMBER props for editorial counts (autoplay delay, max items in a slider, items per row when the design supports multiple counts).

**Do NOT expose:**

- Layout variants, alignment ENUMs, aspect-ratio ENUMs, image-position ENUMs — design decides.
- Per-element colors (card background, badge text color) — design decides.
- Typography / spacing / radius — design decides.
- HTML semantics, validation rules, focus management.

### 6.2 The IMAGE triplet

Every image-bearing prop ships as:

| Prop | Purpose |
|---|---|
| `image` (IMAGE) | The source |
| `imageAlt` (TEXT) | Mandatory alt text |
| `imageLink` (LINK, optional) | When the image is clickable |

The image's aspect ratio, fit, position, overlay opacity — these are design decisions, not props. (Exception: if the design explicitly supports merchant-tunable overlay opacity for a hero, `imageOverlayOpacity` NUMBER is fine.)

The prop-type catalog goes beyond single images: `IMAGE_LIST`, `VIDEO`, `SVG` / `SVG_LIST` (editor-sanitized; render via `normalizeSvg`), `DATE`, `NUMBER_RANGE`, and `*_LIST` entity sources (`CATEGORY_LIST`, `BRAND_LIST`, `BLOG_LIST`, `BLOG_CATEGORY_LIST`, `PRODUCT_ATTRIBUTE_LIST`) all exist — check `get_prop_types()` before inventing a workaround with TEXT props.

> **(MCP)** Image rendering helpers (`getDefaultSrc`, `getThumbnailSrc`, `getSrc`, `createMediaSrcset`): `get_functions_for_type("IkasImage")`.

### 6.3 Prop group vocabulary

Recommended starting points for top-level group ids. MCP section templates use this vocabulary plus context-specific variants; match the template when starting from one.

| Group id | Display name | Contains |
|---|---|---|
| `content` | Content | TEXT, RICH_TEXT, IMAGE props that fill the section |
| `texts` | Texts | When the section has 5+ TEXT props that share no other group |
| `behavior` | Behavior | BOOLEAN toggles, NUMBER limits |
| `links` | Links | Standalone LINK props (when 2+; otherwise inline with content) |
| `data` | Data | PRODUCT_LIST / CATEGORY / BLOG sources |
| `advanced` | Advanced | Rarely-edited (e.g. `backgroundColor` when the design has already chosen it) |

Sub-groups allowed one level deep. **The `appearance` and `layout` groups are typically empty** when visual decisions come from a canonical design — most colors and all layout variants live in the design, not in the editor.

> **(MCP)** Group mechanics + CLI: `get_framework_guide("prop-groups")`.

### 6.4 The LINK pattern

The `LINK` prop type produces an `IkasNavigationLink | null` (field list via `get_type_definition("IkasNavigationLink")`). Theme code respects `openInNewTab` and adds `rel="noopener noreferrer"` automatically when true. For navigation menus that need a flat or nested list, use `LIST_OF_LINK`. LINK `defaultValue`s are typed objects, not `{href, label}` literals — get the accepted shape from `get_prop_types()` before writing shippable defaults (§1).

> **(MCP)** `get_type_definition("IkasNavigationLink")`. Prop type definitions: `get_prop_types()`.

### 6.5 Custom ENUMs

When a prop genuinely needs 2–6 named options the merchant should pick between (e.g. countdown text alignment when the design supports both options), use ENUM. When the design is canonical, ENUMs are rare — most "options" are design decisions, not merchant levers.

> **(MCP)** Custom ENUM CLI lifecycle: `get_framework_guide("custom-enums")` + `CLAUDE.md`.

### 6.6 The loading-state prop quartet

Every data-listing section (cart, favorites, orders, blog, search, PLP) declares:

```
loadingText           — "Loading…"
emptyTitle            — section-appropriate
emptySubtitle         — section-appropriate
emptyCtaLabel         — "Continue shopping" / "Browse the catalog"
emptyCtaLink          — home or category root
```

All four are mandatory.

---

## 7. Behavior & State Contracts

The interaction grammar of the theme. Behavior is invariant across visual designs.

### 7.1 Cart mutations

#### Add to cart

- **Single gate.** The ATC action is gated by the storefront's add-to-cart eligibility check — it already accounts for required option values, stock, and overselling. Don't hand-roll a stock-only check: a variant with overselling enabled (`sellIfOutOfStock`) stays purchasable at zero stock, and a product with unfilled required options must not submit (§7.13).
- **Optimistic.** Cart count badge increments immediately.
- **Existing line merge.** Adding a variant already in the cart must not create a duplicate row — find the existing line and increase its quantity instead.
- **Edit mode.** When the PDP is opened from a cart line's "edit" affordance (edit-line query param), the ATC CTA becomes an "Update this line" action instead of adding a new line — with its own TEXT prop pair for the label.
- **Quantity limits.** When the product declares per-sales-channel min/max quantities, the stepper clamps to them and the initial quantity starts at the minimum. Limit violations render merchant-editable copy, not a silently unresponsive stepper.
- **Feedback choice (design-dependent).** Pick one and apply consistently: (a) auto-open Cart Drawer if the design ships one and the user isn't on the Cart page, (b) success toast, (c) inline confirmation on the ATC button.
- **Pending state.** ATC button reads `form.isSubmitting`-style state and renders `submittingButtonText`. Drawer / list rows reflecting the same line render `is-pending`.
- **Failure.** Optimistic state rolls back; cart count decrements; error toast with Retry; CTA returns to idle. Surface the specific `validationError` (e.g. `INSUFFICIENT_STOCK`, `INVALID_PRODUCT_OPTION_VALUES`) as user-facing copy — read the current value set from `get_function_doc("addItemToCart")`; the two examples here are not exhaustive.

> **(MCP)** Result shape: `addItemToCart` returns `IkasCartOperationResult { success, validationError }` — the type is not in the type index, so read the shape from `get_function_doc("addItemToCart")` (not `get_type_definition`). Eligibility gate: `get_function_doc("isAddToCartEnabled")`. Line merge: `findExistingCartItem` / `changeItemQuantity`. Edit mode + quantity clamp reference implementation: `get_section_template("add-to-cart")`. Channel limit shape: `get_type_definition("IkasProductSalesChannel")`. Loading-flag pattern: `get_framework_guide("async-data-patterns")` §2.

#### Add to cart from product cards (PLP, sliders, favorites, search)

A card's ATC affordance follows this ladder — first matching rule wins:

1. **Out of stock** → the card shows its OOS state and offers a recovery affordance: notify-me per §7.11, or navigation to the PDP. Never a silently dead button.
2. **Bundle product** → navigate to the PDP; cards never quick-add bundles (§7.12).
3. **Single variant, no option set** → direct ATC per the contract above.
4. **Multiple variants or an option set** → open the Quick View surface (§9.6) or navigate to the PDP (design decision). Never silently add a default variant the shopper didn't choose.

#### Update quantity, remove

- Optimistic — the mutation functions mutate the model in place; the observer re-renders automatically.
- `changeItemQuantity(item, quantity)` and `removeItem(item)` **also return `Promise<IkasCartOperationResult>`** — check `success` to drive rollback + the error toast. `quantity = 0` removes the line.
- Pending state on the affected row; rollback + error toast on failure.

> **(MCP)** In-place mutation semantics: `get_framework_guide("common-pitfalls")` #3 — most storefront mutations return `void`, but the cart row mutations above are result-returning exceptions. Functions: `get_function_doc("changeItemQuantity")`, `get_function_doc("removeItem")`, full inventory `list_functions("Cart")` / `list_functions("OrderLineItem")`.

#### Empty cart

- Cart page (and Cart Drawer if the design ships one) render the empty state quartet from §6.6.
- No fake "recommended products" pretending the cart has items. A separate `RecentlyViewed` block is fine.

> **(MCP)** `get_framework_guide("cart-patterns")`.

### 7.2 Authentication

#### Login success destination

1. `redirect` query param if present and same-origin
2. The page the user was on before being prompted (if captured)
3. `/account` fallback

The cart and favorites state merges if the customer had a guest session — no silent data loss.

When the theme ships social sign-in, the Login surface also processes the OAuth **return**
callback on mount (the provider redirects back to it) and applies the same success destination
rules. Provider buttons alone are not enough — without the callback handler the round-trip
dead-ends.

#### Login failure

- Inline error (`aria-live="polite"`) above the submit button.
- Focus does NOT auto-move to email — respect screen reader state.
- "Forgot password?" link visible at all times, not gated behind a failure.

#### Register success

- Auto sign-in; redirect per Login success.
- If email confirmation is required, replace the form with a "Check your email" surface.

#### Forgot Password / Recover Password

- After submission, replace the form with a neutral confirmation ("If an account exists, we sent instructions"). **Do not confirm or deny the account's existence** — same message either way (enumeration prevention).
- Recover Password page reads `token` query param. Invalid/expired → recovery-failed surface with "Request a new link" CTA. Never blank-screen.

#### Sign out

- Available from the account shell at all times.
- Redirect to `/`. Cart preserved as guest cart if storefront supports it; otherwise cleared.

> **(MCP)** Form mechanics + submit lifecycle (`submit*Form` returns `boolean`, sets `form.isSuccess` / `isFailure` / `responseMessage`): `get_framework_guide("form-handling")`. Functions: `list_functions("Authentication")`, `list_functions("Login")`, `list_functions("Registration")`, `list_functions("ForgotPassword")`, `list_functions("RecoverPassword")`.

### 7.3 Variant selection (PDP)

- Selecting a variant pushes `variant` to the URL so the URL is shareable.
- Gallery scrolls to the first image associated with the new variant (when variant images exist); does **not** reset to image 1.
- Price, SKU, stock status, ATC button state update synchronously.
- Out-of-stock variants are visually marked but still selectable; on selection, ATC reads `outOfStockButtonText` and exposes the back-in-stock affordance per §7.11. (The design source may instead hide OOS values entirely — acceptable, as long as it can never leave the shopper on an unselectable dead combination.)

> **(MCP)** `get_framework_guide("product-detail-patterns")`. Variant helpers: `get_model_guide("IkasProductVariant")`, `get_function_doc("selectVariantValue")`, `get_function_doc("getSelectedProductVariant")`. Notify-me on OOS: §7.11.

### 7.4 Pagination & filtering (PLP)

- Filter changes push to URL as query params. Browser back button restores the previous filter state.
- Scroll position preserved when filters change.
- "Load more" appends without re-fetching previous pages. Numbered pagination replaces and scrolls to top of the grid.
- Infinite scroll is allowed but **must expose a "Load more" button as a fallback** (one click = one page, for keyboard / screen reader users).
- Result count is always visible.

> **(MCP)** `IkasProductList` helpers: `get_type_definition("IkasProductList")` + `get_framework_guide("product-list-patterns")`. Infinite-scroll primitive: `IkasThemeInfiniteScroller` via `get_framework_guide("slider-overlay-patterns")`.

### 7.5 Search

- Search Modal (or whatever search surface the design ships) opens via header icon.
- Typing debounces by 200ms before firing a query. Results render as the user types; no Enter required.
- Recent searches (if persisted) + popular queries (if the storefront provides) shown when the input is empty.
- Enter / "See all results" navigates to the full Search Results page.
- Empty query → recent + popular; empty results → empty surface + "Browse all" CTA.

### 7.6 Form validation

- **Don't render errors before the user attempts to submit.** The framework gates this via `form.isSubmitted` — until that flag flips, `field.hasError` won't surface meaningful errors. Once it's true, the storefront re-validates on every setter call automatically; the theme simply renders the current `field.hasError` + `field.message`.
- **On submit failure**, move focus to the first invalid field.
- **On submit success**, replace the form with a confirmation surface (terminal flows: contact, recover password) OR show an inline success above the cleared form (repeatable flows: address book, profile edit). Pick one per form.
- **Required-field indicator** is a theme decision (asterisk, badge, none). Be consistent across all forms.

> **(MCP)** Form model shape (`field.value` / `hasError` / `message`, `form.isSubmitting` / `isSubmitted` / `isSuccess` / `isFailure` / `responseMessage`), `init*Form` / `set*Form` / `submit*Form` lifecycle, the auto-validate-after-submit rule: `get_framework_guide("form-handling")`. Field access pattern: `get_framework_guide("common-pitfalls")` #10. Validation functions: `list_functions("Validation")`.

### 7.7 State anatomy

Every section that fetches data implements four states with the same shape:

| State | Anatomy |
|---|---|
| Loading | Skeleton blocks matching the loaded layout (the design source specifies skeleton appearance). Skip entirely when data is already cached. |
| Empty | Centered illustration/icon + `emptyTitle` + `emptySubtitle` + `emptyCtaLabel`. Always offer a way out. |
| Error | Same anatomy as empty but error tone. Action-oriented title ("Something went wrong, try again"). Primary CTA "Retry"; secondary "Contact support". |
| Loaded | Real content. |

Loading skeletons match the loaded shape exactly — no layout shift.

> **(MCP)** Async loading patterns: `get_framework_guide("async-data-patterns")`.

### 7.8 Optimistic mutation contract

For every mutation (cart, favorites, address, profile):

1. Render new state immediately. **Most storefront mutation functions handle step 1 for you** — they mutate the model in place; observer-driven re-renders deliver the new state without explicit setState. (Many return `void`; cart row mutations additionally return an `IkasCartOperationResult` whose `success` flag drives step 5.)
2. Apply `is-pending` class to the affected UI (row, button, card) for visual feedback during the async window.
3. Dispatch the mutation. For ATC and similar await-able mutations, use the `try/finally` loading-flag pattern.
4. On success: remove `is-pending`. Optional toast.
5. On failure: roll back, remove `is-pending`, error toast with Retry.

Track in-flight mutations by stable id (line item id, product id) so parallel mutations don't collide.

> **(MCP)** In-place mutation semantics (don't capture return values from `selectVariantValue`, `initLoginForm`, `clearFilter`, etc.): `get_framework_guide("common-pitfalls")` #3. Loading-flag pattern with `try/finally`: `get_framework_guide("async-data-patterns")` §2. Store reactivity: `get_framework_guide("async-data-patterns")` §5.

### 7.9 Toast / feedback queue

- One global queue, max 3 stacked.
- Persistence: success 3s, info 4s, error 6s, manual close on each.
- Never block interaction.
- Retry actions stay focusable until dismissal.
- ARIA: `role="status"` for info/success, `role="alert"` for error.
- Position is dictated by the design source.

> **(MCP)** `Toast` + `useToast` hook: `get_framework_guide("sub-component-catalog")`. The Header-mounted `ToastContainer` convention: `get_framework_guide("header-footer-patterns")`.

### 7.10 Keyboard expectations

- `Esc` closes any open modal, drawer, dropdown (in reverse-open order if stacked).
- `Tab` order follows DOM order; never override with `tabindex > 0`.
- Focus traps inside modals/drawers: focus stays within the open surface; returns to trigger on close.
- `Enter` on a card link navigates; `Space` on a button triggers it.

### 7.11 Out-of-stock recovery — back-in-stock ("notify me")

Out of stock is a recovery surface (§3 #7), never a dead end. When the storefront enables back-in-stock notifications, the OOS ATC state becomes a notify-me affordance.

- **Feature-gated.** Render the affordance only when the storefront reports back-in-stock enabled for the variant; otherwise the OOS state stands alone.
- **Two branches, keyed to the login-required flag:**
  - Login required + guest → route to Login with a return path (§7.2), don't show an email form.
  - Login required + logged-in → save the reminder with the customer's email in one tap.
  - Login not required → inline email form using the storefront's back-in-stock form lifecycle; validation per §7.6.
- **Success is persistent state, not a toast alone.** The variant carries a saved-reminder flag — render a "we'll notify you" state and don't re-offer the form while it's set.
- **Per-variant.** Re-evaluate on every variant change (§7.3): a different variant may be in stock, unsaved, or already saved.
- **Cards may delegate.** A product card facing an OOS product may route to the PDP instead of hosting the form inline (§7.1 card ladder).
- All copy (notify CTA, form labels, success state) = TEXT props (§5.4).

> **(MCP)** Two function families exist — a form-based flow and a direct-save flow: `list_functions("BackInStock")` + `list_functions("Stock")`. Pick one, don't mix. The enabled / login-required / saved-reminder flags live on the variant: `get_model_guide("IkasProductVariant")`.

### 7.12 Bundle products

A variant can carry bundle settings (a composed set of sub-products sold as one line). Check for them via the storefront helper before rendering the standard single-product ATC.

- **PDP renders the bundle's sub-products** — selection and per-item quantity editing per what the bundle settings allow.
- **ATC eligibility widens:** it includes every sub-product's stock (respecting each one's own overselling flag) and the bundle's min/max quantity constraints. A violation blocks ATC **with a stated reason** (which sub-product, which limit) — not a silently disabled button.
- **Cart lines for bundles render their sub-products**; editing a bundle line routes back to the PDP rather than editing inline.
- **Cards never quick-add bundles** — navigate to the PDP (§7.1 card ladder).

> **(MCP)** Reference implementation: `get_section_template("bundle-products")`. Canonical PDP entry point: `get_function_doc("initBundleProducts")`. Settings shape: `get_type_definition("IkasBundleSettings")`.

### 7.13 Product options (personalization)

When a product carries an option set (engraving text, uploaded artwork, date selection, add-on choices…), the PDP — and any Quick View surface — must render it; skipping it silently produces carts the merchant can't fulfill.

- **Render every displayed option** in its declared type and display style; child options appear only when their parent's selection requires them. Don't cherry-pick the types the design happened to show — a merchant can attach any type to any product.
- **Validation mirrors §7.6:** no errors before the first ATC attempt; after it, invalid options show their message and ATC stays blocked by the same single gate as §7.1.
- **File options** upload through the storefront's upload function; constraint violations (extension, min/max file count) render merchant-editable error copy.
- **Priced options** show their price on the label, and totals reflect them via storefront price helpers — no hand math (§11.1).
- **After a successful ATC, option values reset** to their initial state.

> **(MCP)** Function families: `list_functions("Customization")`, `list_functions("ProductOption")`, `list_functions("ProductOptionSet")`. Fetch/attach: `get_function_doc("getProductOptionSet")`. Reference validation flow: `get_section_template("add-to-cart")` (its option-set util).

---

## 8. Page Composition

The design source dictates which sections appear on each page and in what order. This doc adds the few UX rules that hold regardless of design:

### 8.1 First product surface within 1 scroll (homepage)

On the homepage, the first product surface (Featured Collection / Product Slider) must appear within the first 3 sections after the hero. Buyers should see product within 1 viewport scroll.

### 8.2 No marketing decoration on utilitarian pages

Cart, Auth, Account, 404 pages render only:

```
Header → primary section(s) → Footer
```

No newsletter, no testimonials, no lookbook between. Account pages may include "You may also like" beneath order detail, only when contextual.

### 8.3 PDP rhythm constraint

Reviews and "you may also like" never appear above the Product Detail section. (Other rhythm decisions belong to the design source.)

### 8.4 Only Header and Footer are immovable

Everything else is a design decision.

---

## 9. Chrome Surfaces

These live outside the page flow. Visual styling comes from the design source; **this doc defines what each surface DOES**: triggers, close conditions, cross-page behavior, feature surface, accessibility expectations.

If the design source ships a chrome surface differently (e.g. a full-page Search instead of a modal, no Cart Drawer), build what the design ships — the **function** must exist somewhere, not this specific form.

**The framework already provides plumbing for most chrome surfaces** — reuse before building (§14 #20). Don't memorize the inventory; read it fresh:

- `get_framework_guide("sub-component-catalog")` — modal shells (`Modal`, `ConfirmModal`), notifications (`Toast` + `useToast`), `ImagePreviewModal`, `PageLoader`, plus the form/UI building blocks and icons every chrome surface composes from.
- `get_framework_guide("slider-overlay-patterns")` — the runtime APIs from `@ikas/bp-storefront`: `IkasThemeSlider` (carousels), `IkasThemeOverlay` (an overlay *state type*, not a JSX component — build the surface UI yourself), `IkasThemeInfiniteScroller`.
- `get_framework_guide("header-footer-patterns")` — the Header-mounted `ToastContainer` convention and the mega-menu MenuItem pattern.

### 9.1 Cart Drawer (when the design ships one)

**Mount:** From the Header. Visible across all pages.

**Triggers to open:**
- Cart icon click in Header.
- Add to Cart from any surface (PDP, PLP quick view, recently viewed) **unless** the user is on the Cart page.

**Triggers to close:** Close button; backdrop click; `Esc`; checkout CTA (after navigation kicks off).

**Feature surface:**
- Header row: title + close.
- Scrollable item list.
- Footer row: subtotal + summary breakdown (shipping note, discount, tax) + Checkout CTA + secondary "View cart" link.
- Empty state replaces the item list when cart is empty.

**Behavior:** Per §7.1.

### 9.2 Search Modal

**Mount:** From the Header.

**Triggers to open:** Search icon click.

**Triggers to close:** Close button; backdrop; `Esc`; clicking a result; pressing Enter on "See all".

**Feature surface:**
- Search input (auto-focused) + submit.
- Tabbed content — recent + popular pills by default; result rows (thumbnail + name + variant note + price) once typing.
- Loading indicator while query is in flight.
- Empty results → empty surface with "Browse all" → PLP.

**Behavior:** Per §7.5. Show top 6 + "See all results" link.

### 9.3 Mobile Drawer

**Mount:** From the Header (mobile only; breakpoint per design).

**Triggers to open:** Hamburger tap.

**Triggers to close:** Close icon; backdrop; `Esc`; tapping a navigation link.

**Feature surface:**
- Close icon.
- Top actions: Search, Favorites, Account (or Sign in), Cart with count.
- Main list: navigation items with multi-level accordion expansion.
- Footer: contact info, language / currency selectors.

### 9.4 Profile Edit Modal

**Mount:** From Account Dashboard. **Trigger:** "Edit profile" CTA.

**Feature surface:** Form limited to the fields `getAccountInfoForm` exposes — first/last name, phone, marketing consent. Email is read-only display, not an editable field. **No password-change field:** the storefront account-info form has none; password changes go through Forgot / Recover Password (§7.2). Field-level validation per §7.6. Success: modal closes, dashboard re-renders, toast.

> **(MCP)** Form lifecycle + functions (`getAccountInfoForm`, `initAccountInfoForm`, `setAccountInfoForm*`, `submitAccountInfoForm`): `get_framework_guide("account-patterns")`.

### 9.5 Address Form Modal / Drawer

**Mount:** From Account Addresses. **Trigger:** "Add address" CTA or "Edit" on a card.

**Feature surface:** Form with country, name, line 1, line 2, city, state/region, postal code, phone, "Set as default" toggle. Country selector drives state/region visibility. Postal code validation respects country format where the storefront provides hints.

> **(MCP)** `getIkasCustomerAddressForm`, `getEmptyAddressForm` (new address), `initAddressForm`, `submitAddressForm`, `deleteCustomerAddress`. `list_functions("Address")`.

### 9.6 Quick View Modal (optional)

**Mount:** Optional, surfaced from PLP cards when the design ships a "Quick view" affordance.

**Feature surface:** Compact PDP — smaller gallery + title + price + variant selector + option set per §7.13 (when the product carries one) + ATC + "View full details" link. Does NOT include reviews, accordion, breadcrumbs, related products. ATC behavior per §7.1. Never opens for bundle products — those navigate to the PDP (§7.12).

### 9.7 Top Loading Indicator

**Mount:** Globally.

**Behavior:** Bar at the top of the viewport (visual specification per design). Appears on:
- Route navigations longer than 200ms (debounced).
- Long-running async actions where a per-component spinner is insufficient (full PLP re-fetch on filter change).

Disappears on completion or failure. Under reduced-motion: static visible bar.

> **(MCP)** Distinct from MCP's `PageLoader` sub-component (full-page route-transition spinner) — both can coexist: top bar for short navigations, `PageLoader` for first-paint of a heavy route. See `get_framework_guide("sub-component-catalog")`.

---

## 10. Merchant Editorial Philosophy

### 10.1 Merchants control

- All visible copy.
- Images + alt text.
- Destination links.
- Product / category / brand / blog sources.
- Optional content block visibility (countdown, announcement bar, brand line on PDP, etc.).
- Section visibility (optional sections only).
- Section order, within the constraints in §8.
- Per-section color-scheme selection, when the theme ships designed palettes (scheme-slot architecture — see the `ikas-theme-globals` skill). Picking among designed schemes is design-sanctioned; per-element color knobs still are not.

### 10.2 Merchants do NOT control

- Visual identity (colors, typography, spacing, layout, alignment, aspect ratios) — encoded in the design source.
- HTML semantics.
- Interaction patterns (cart drawer auto-open on ATC, login redirect, etc.).
- A11y wiring (focus management, ARIA roles, keyboard handlers).
- Performance behaviors (lazy-loading, image priorities, prefetching, route splitting).
- Validation rules (merchant edits error strings, not the rule).
- State machine transitions.
- Schema / SEO metadata structure.

### 10.3 The "explain via defaults" rule

When in doubt about whether to expose a setting, set a sensible default and **don't** expose it. Adding a control is reversible; removing one after merchants depend on it is not. **Bias even harder toward not exposing when the design is canonical** — the design source has already decided, so a "give the merchant a knob" instinct usually conflicts with it.

---

## 11. Internationalization, Currency, Locale

### 11.1 Currency

- Use the storefront's pre-formatted price strings (`formattedPrice`, `formattedFinalPrice`, `formattedSellPrice`).
- Never construct currency manually.
- Compare-at and discounted prices: render storefront-formatted values for each — no math in the theme.
- Cart totals: use the order model's formatted fields.

> **(MCP)** Pricing helpers: `list_functions("Pricing")` + `list_functions("VariantPrice")`. `getProductVariantFormattedFinalPrice`, `getProductVariantFormattedSellPrice`, `hasProductVariantDiscount`, etc.

### 11.2 Language and currency switchers

When the storefront supports multiple locales / currencies, expose switchers wherever the design places them (typically Footer + Mobile Drawer; sometimes a compact switcher in Header).

---

## 12. Performance, SEO, Accessibility

### 12.1 Image performance

- Hero / first viewport image: `fetchpriority="high"`, no `loading="lazy"`.
- Use storefront image helpers — `getDefaultSrc` (1080), `getThumbnailSrc` (180), `getSrc(image, size)`, `createMediaSrcset`. Never serve the original.
- For images >400px wide on desktop, render with `srcset` via `createMediaSrcset`.
- Product media items can be videos — **always branch on `item.isVideo`** before rendering. For videos the `size` argument is ignored (`getSrc(item, 240)` is misleading); use `getDefaultSrc` for the video src, and apply `createMediaSrcset` only to `<img>` elements.

> **(MCP)** Full helper docs: `get_functions_for_type("IkasImage")`.

### 12.2 Heading hierarchy

One `<h1>` per page. PDP = product title; PLP = collection name; Blog detail = article title; Cart = page heading; Account = surface name.

### 12.3 Accessibility specifics for commerce

- **Cart count badge** announces changes via `aria-live="polite"`.
- **Variant selectors (PDP)** use `<fieldset>` + `<legend>`; options are `<input type="radio">` with custom-styled labels.
- **Form errors** use `aria-invalid="true"` and `aria-describedby` pointing at the error.
- **Quantity steppers** expose `aria-label` for + / −; value cell `aria-live`.
- **Disabled CTAs** never use `aria-disabled="true"` alone — pair with a tooltip or inline note ("Select a size to continue").
- **Skip-to-content link** as the first focusable element.
- **Color is not the sole signal** for any status — pair with icon or text.

---

## 13. Section Catalogue

Per-section ecommerce contract — **functional features only.** Visual structure (layout, alignment, position, aspect ratio) is dictated by the design source. Format for each entry:

- **Role**, **Page surface**
- **Mandatory features** (functional must-haves)
- **Optional features** (only when the design ships them)
- **Interactions** (cross-section behaviors not covered by §7)
- **A11y notes** (commerce-specific)
- **MCP starter**

> **No prop names are listed in this catalogue.** The actual prop list comes from `get_section_template("<sectionType>")` and is auto-generated by the CLI. This doc owns the **intent layer**; the framework owns the **shape layer**.
>
> **Template coverage moves faster than this catalogue.** `list_section_types()` also ships sections not catalogued here (currently `features-section`, `category-images-section`, `email-verification-section`) plus non-section *Pattern* templates — API reference implementations, not placeable sections (`add-to-cart`, `bundle-products`, `component-renderer`, `image-handling`, `navigation`, `product-pricing`, `variant-selection`, `favorites`). When a surface isn't catalogued below, check `list_section_types()` first, then derive its contract from §3 + §5.

---

### 13.A Marketing Sections

#### Hero Slider

- **Role:** Brand orientation, top of homepage.
- **Page surface:** Homepage, top slot.
- **Mandatory features:** ≥1 Hero Slide via COMPONENT_LIST (filtered to the template's `HeroSliderItem` child); navigation when slide count > 1 (dots and/or arrows, per design); `backgroundColor`.
- **Optional features (when the design ships them):** Autoplay (BOOLEAN) + autoplay delay (NUMBER ms); show-arrows toggle (BOOLEAN); loop.
- **Interactions:** Slide CTA click → navigate; swipe → next slide on touch; keyboard arrows when focused; autoplay pauses on user interaction; respects reduced-motion.
- **A11y:** `aria-roledescription="carousel"` on container; `aria-roledescription="slide"` on slides; dot buttons get `aria-label="Go to slide N"`.
- **MCP starter:** `get_section_template("hero-slider-section")`.

#### Hero Slide / Single Hero

- **Role:** Single full-bleed brand statement; child of Hero Slider OR standalone full-bleed banner.
- **Mandatory features:** Background image / video; foreground content (title + subtitle + primary CTA).
- **Optional features:** Secondary CTA; eyebrow; image vs video mode; video controls (mute/unmute).
- **Interactions:** CTA click → navigate; video autoplay muted; users can unmute (controls exposed).
- **MCP starter:** As children of `hero-slider-section`; drill via `get_section_child("hero-slider-section", "HeroSliderItem", "children")`.

#### Featured Collection / Product Slider

- **Role:** Funnel entry; surface curated picks within 1 scroll of homepage entry.
- **Page surface:** Homepage; optionally PDP / Cart ("you may also like").
- **Mandatory features:** Section title; product source via PRODUCT_LIST prop; carousel of product cards; per-card ATC label + submittingButtonText + OOS label + "View Product" label; card content via COMPONENT_LIST + `privateVarMap.product` passing each `product` to the children.
- **Optional features (when the design ships them):** Multi-tab structure ("New in" / "Bestsellers" / "Sale") with auto-tab switch and per-tab "View all" CTA.
- **Interactions:** Card click → PDP; card ATC → §7.1 card ladder (OOS / bundle / variants decide between direct ATC, Quick View, and PDP); favorite toggle.
- **A11y:** If tabs: `role="tablist"` / `role="tab"` / `role="tabpanel"` with arrow-key navigation.
- **MCP starter:** `get_section_template("product-slider-section")` (single-source slider with `privateVarMap.product` wired through to card children).

#### Image + Text

- **Role:** Brand storytelling, lifestyle context, ingredient/material education.
- **Page surface:** Homepage, PDP, content pages.
- **Mandatory features:** Image + content (title + body + CTA).
- **Optional features:** Eyebrow; secondary CTA.
- **Interactions:** CTA click → navigate.
- **MCP starter:** No dedicated template; compose from primitives.

#### Media Link Grid (Lookbook)

- **Role:** Visual category navigation; shop-the-look tiles.
- **Page surface:** Homepage, content pages.
- **Mandatory features:** 2–6 cells (COMPONENT_LIST); each cell has image + caption + link.
- **Optional features:** Section Header block above grid.
- **Interactions:** Card click → navigate.

#### Newsletter

- **Role:** Capture email for marketing.
- **Page surface:** Homepage, blog pages, Cart (post-empty).
- **Mandatory features:** Title + subtitle; email input + submit; success state replaces the form; inline error state; GDPR consent checkbox.
- **Interactions:** Submit → optimistic disable input + label swap; success → form replaces with success surface; error → inline message.
- **A11y:** Required-field indicator on email; `aria-describedby` for the consent checkbox.
- **MCP starter:** No dedicated template; subscribe via storefront functions — `list_functions("Newsletter")`, don't hand-roll the call.

#### Promo Banner (Countdown)

- **Role:** Urgency-driven sale callout.
- **Page surface:** Global strip OR homepage strip.
- **Mandatory features:** Headline + sub-line + countdown to ISO datetime; CTA + link; auto-hide on expiry.
- **Optional features:** Dismissible (sessionStorage persistence).
- **Interactions:** Countdown updates display every second; CTA → navigate; dismiss → hide for the session.
- **A11y:** Countdown values update via `aria-live="polite"` at minute boundaries (not every second).

#### Trust Badges Bar

- **Role:** Reassurance — free shipping, secure checkout, easy returns.
- **Page surface:** Homepage, PDP, Cart.
- **Mandatory features:** 3–6 badges; each with icon (IMAGE) + title + subtitle.
- **Interactions:** None; static reassurance.

#### Blog Slider

- **Role:** Surface latest editorial on homepage / blog detail.
- **Page surface:** Homepage; blog detail (as "Related articles").
- **Mandatory features:** Section Header block; 3 cards (NUMBER limit); each card: cover image, title, excerpt, publish date, reading time, link.
- **Interactions:** Card click → blog detail.
- **MCP starter:** Blog patterns via `get_framework_guide("blog-patterns")`.

---

### 13.B Transactional Sections

#### Product Detail (PDP)

- **Role:** The decision surface; convert browsing into ATC.
- **Page surface:** Product detail page, mandatory.
- **Mandatory features:** Breadcrumbs (Home → Collection → Product); gallery (per the design's gallery mode); product title (`<h1>`); prices (current + compare-at when discounted); variant selectors per attribute; quantity stepper (clamped per §7.1 when the product declares limits); Add to Cart CTA; back-in-stock affordance on OOS per §7.11; bundle rendering per §7.12 when the variant carries bundle settings; option set rendering per §7.13 when the product carries one; favorite toggle; accordion (description, ingredients, shipping, returns — content via RICH_TEXT props).
- **Optional features (when the design ships them):** Brand line; rating (read-only); badges (discount, OOS, "new"); SKU / barcode meta; tags; size guide modal link; pre-order CTA label override; share buttons; stock urgency (visible stock count and/or "last N left" note with a NUMBER threshold); Buy Now CTA (successful ATC → navigate straight to checkout via the cart store's checkout URL); WhatsApp order CTA (prefilled message + product URL).
- **Interactions:** Per §7.3 (variant select), §7.1 (ATC), §7.11 (OOS notify-me), §7.12 (bundles), §7.13 (options); favorite toggle optimistic.
- **A11y:** `<h1>` is product title; variant groups use `<fieldset>` / `<legend>`; gallery uses `aria-roledescription`; ATC reads stock status via `aria-live` when it changes.
- **MCP starter:** `get_section_template("product-detail-section")` — a slot-based shell (breadcrumb + gallery + COMPONENT_LIST info/bottom regions). The reference theme decomposes the info column into many small child components — match the design source's breakdown instead of copying the reference decomposition. See `get_framework_guide("product-detail-patterns")`.

#### Product Reviews

- **Role:** Social proof + customer voice on the product page.
- **Page surface:** PDP, as a separate section below Product Detail.
- **Mandatory features:** Section title; review summary (average star rating + total review count + per-star distribution) when reviews exist; review cards (rating + title + comment + author + formatted date); pagination; "Write a review" CTA → review form (typically a modal); empty state when no reviews yet; merchant reply display when present.
- **Optional features:** Image attachments in reviews (with preview modal); login gate when `isCustomerReviewLoginRequired(product)` returns true.
- **Interactions:**
  - "Write a review" → if `isCustomerReviewLoginRequired(product)` is true and `hasCustomer(customerStore)` is false → `Router.navigateToPage("LOGIN")`. Otherwise open the review form surface.
  - Submit review → on success, re-fetch reviews + close form + show empty/loaded state per §7.7.
  - Pagination → smooth-scroll the list back to the top after page change.
- **A11y:** Star-rating input keyboard accessible (radio-group semantics); review images focusable + Enter opens the preview modal; modal traps focus until close.
- **MCP starter:** `get_section_template("product-reviews-section")`. Full pattern: `get_framework_guide("review-patterns")`. Form lifecycle: `getIkasProductCustomerReviewForm`, `setCustomerReviewForm*`, `submitCustomerReviewForm`.

#### Product List (PLP)

- **Role:** Browse + filter + sort the catalogue.
- **Page surface:** Collection, search results, brand, tag pages.
- **Mandatory features:** Result count; filter panel (form factor per design — sidebar / drawer / etc.); sort selector; product card grid; pagination per §7.4; empty state on no results.
- **Optional features (when the design ships them):** Collection hero block; "Clear all filters"; saved searches/sorting (when storefront supports); card hover image swap (when product has multiple images).
- **Interactions:** Filter change → URL update + grid refresh (no full reload); per §7.4; card → PDP.
- **MCP starter:** `get_section_template("category-list-section")` + `get_framework_guide("product-list-patterns")`. Infinite scroll via `IkasThemeInfiniteScroller`.

#### Cart Page

- **Role:** Pre-checkout review + edit.
- **Page surface:** Cart page, mandatory.
- **Mandatory features:** Title (`<h1>`); item list (row: image + name + variant + price + stepper + remove); order summary panel (subtotal, discounts, taxes, shipping, total); Checkout CTA; continue shopping link; empty state per §7.7.
- **Optional features:** Discount code input; gift wrap; order notes textarea; shipping calculator.
- **Interactions:** Per §7.1; Checkout CTA → checkout flow.
- **MCP starter:** `get_section_template("cart-section")` + `get_framework_guide("cart-patterns")`. Optional features have storefront functions — discount codes `list_functions("CouponCode")`, gift wrap `list_functions("GiftPackage")`.

#### Login

- **Role:** Authenticate returning customer.
- **Mandatory features:** Heading (`<h1>`); email + password fields; "Forgot password?" link (always visible); submit CTA (with submitting state); "Register" prompt link; inline error region (`aria-live="polite"`).
- **Optional features:** Social sign-in providers (`SocialLoginButton` in the sub-component catalog); phone/SMS login when the storefront supports it (`list_functions("SMSLogin")`); "Remember me".
- **Interactions:** Per §7.2.
- **MCP starter:** `get_section_template("login-section")`.

#### Register

- **Role:** Account creation.
- **Mandatory features:** Same fields as Login + first/last name + password confirmation + consent checkbox (terms & marketing).
- **Optional features:** Phone number; date of birth (when storefront supports loyalty/birthday).
- **Interactions:** Per §7.2.
- **MCP starter:** `get_section_template("register-section")`.

#### Forgot Password / Recover Password

- **Role:** Recovery flow.
- **Mandatory features:** Forgot — email field + submit + post-submit neutral confirmation. Recover — new password + confirm + submit + post-success login link.
- **Behavior:** Per §7.2 (enumeration prevention on Forgot; token validation on Recover).
- **MCP starter:** `get_section_template("forgot-password-section")` + `get_section_template("recover-password-section")`.

#### Email Verification

- **Role:** Post-registration verification landing.
- **Mandatory features:** Verification status surface driven by the URL token (pending / success / failure); success links onward (account or intended destination); failure offers a re-send affordance. Never blank-screen.
- **MCP starter:** `get_section_template("email-verification-section")`.

#### Search Results

- **Role:** Full-page search beyond the modal.
- **Mandatory features:** Query echo ("Results for 'foo'"); result count; filter chips; product grid; empty state.
- **Optional features:** Sort; blog post results inline (when storefront supports cross-content search).
- **MCP starter:** Reuse PLP starter (`category-list-section`); detect search mode via the `isProductListSearch(list)` helper (don't compare `list.type` by hand — the enum isn't in the type index); echo `list.searchKeyword` in the heading.

---

### 13.C Account Sections

All inherit:
- Account Shell layout per the design source (sidebar / tabs / hub — whatever the design ships).
- Auth gate (redirect to Login when unauthenticated). **The gate waits for customer-store
  hydration before deciding** — checking the customer before the store initializes bounces
  logged-in users to Login. The inverse gate holds on auth pages: an already-logged-in user
  landing on Login / Register / Forgot is redirected to the account surface.
- Sign-out reachable from every account surface.
- See `get_framework_guide("account-patterns")`. ⚠️ Known-stale spots in that guide (tracked
  in ikas-editor-monorepo#740): it shows public `customerStore.orders` / `customerStore.favoriteProducts`
  store fields and a `deleteAddress(customerStore, addressId)` signature that don't exist —
  trust `get_function_doc(...)` signatures over the guide's snippets.

#### Account Dashboard

- **Role:** Self-service landing.
- **Mandatory features:** Customer name greeting; quick stats (orders count, default address summary); quick links (View orders, Edit profile, Manage addresses, Favorites).
- **Optional features:** Loyalty status; store credit balance; recent order preview.
- **Interactions:** "Edit profile" → Profile Edit Modal (§9.4).
- **MCP starter:** `get_section_template("account-info-section")` ships tab-based child components — the design may decompose differently.

#### Account Orders (list)

- **Role:** Order history overview.
- **Mandatory features:** Sortable list of orders (number, date, status, total, item count); status pill per order; "View order" → detail; pagination per §7.4; empty state ("No orders yet" + shop CTA).
- **Optional features:** Date range filter; status filter.

#### Account Order Detail

- **Mandatory features:** Order number + date + status banner; itemized lines (image, name, variant, qty, line total); **multi-package rendering** — when the order ships in more than one package, lines group per package with a per-package status pill and per-package tracking info (single-package orders show tracking in the delivery block); shipping + billing address blocks; totals breakdown (subtotal → discount/campaign adjustment rows → shipping → total, via the order's formatted helpers); tracking link (when shipped+); reorder CTA (optional).
- **Optional features:** **Refund request flow** (when the storefront allows it) — offer it only when the order has refundable items; the shopper picks per-line refund quantities, submits, and on success the order re-fetches and the panel closes; items already in a refund state leave the main list and render in their own section with per-item status badges. Cancel order CTA (when status allows); download invoice.
- **Status semantics:** derive "active / delivered / returned / cancelled" groupings and any progress indicator from the real order status enum — do not carry over v1 status names. The enum values aren't in the MCP type index yet (read them from the package's `.d.ts`; tracked in ikas-editor-monorepo#740); statuses outside the progress mapping hide the progress indicator instead of guessing a step.
- **MCP:** order resolution from the URL: `get_function_doc("getOrderDetailsOfPage")`. Refund family: `search_docs("refund")` (`isIkasOrderRefundable`, refundable/refunded item getters, per-line quantity setter, `refundOrder`) — note the per-line quantity write may not trigger a re-render on its own, and a successful refund requires re-fetching the order. Packages: `get_function_doc("getIkasOrderDisplayedPackages")`. Tracking data via `list_functions("OrderTracking")`; detail/totals via `list_functions("OrderDetail")`.

#### Account Addresses

- **Mandatory features:** Card list of saved addresses; default indicator; "Add address" → modal (§9.5); Edit / Delete per card; empty state.
- **Optional features:** "Make default" action per card. There is no dedicated storefront API for it — the pattern is saving the customer with the address list re-mapped so only the target has `isDefault` (tracked for documentation in ikas-editor-monorepo#740).
- **Interactions:** Add / Edit → modal; Delete → confirm step (inline confirm or `ConfirmModal`) → optimistic remove.

#### Favorite Products

- **Role:** Saved products.
- **Mandatory features:** Grid of favorited cards; empty state with browse CTA; remove from favorites action on each card.
- **Optional features:** Sort by date added / name / price.
- **MCP starter:** `get_section_template("favorites")` + `list_functions("Customer")` for favorite helpers.

---

### 13.D Content Sections

#### Blog List

- **Role:** Listing of editorial posts.
- **Mandatory features:** Card grid (cover image via `blog.image`, title, summary/excerpt, formatted date via `getIkasBlogFormattedDate`, link via `getIkasBlogHref`); pagination via `hasBlogListNextPage` / `getBlogListNextPage`; empty state.
- **Optional features (when the design ships them):** Blog hero above the grid; category filter chips; reading-time estimate; per-card category label.
- **MCP starter:** `get_section_template("blog-home-section")` + `get_framework_guide("blog-patterns")`. Full function list: `list_functions("BlogList")`.

#### Blog Detail

- **Role:** Single editorial post.
- **Mandatory features:** Cover image (via `blogPost.image` + `getDefaultSrc`); title (`<h1>` via `blogPost.title`); publish date (via `getIkasBlogFormattedDate`); **article body — rendered from `blogPost.blogContent.content` via `dangerouslySetInnerHTML`, NOT from a RICH_TEXT prop** (the body lives on the BLOG model, not the section).
- **Optional features (when the design ships them):** Reading-time estimate; author byline; tag list; "Back to all posts" link; sticky TOC for long articles; share buttons.
- **MCP starter:** `get_section_template("blog-post-section")`.

#### Rich Text

- **Role:** Editorial paragraph block.
- **Mandatory features:** RICH_TEXT body.
- **MCP starter:** `get_section_template("rich-text-section")`.

#### FAQ Accordion

- **Mandatory features:** Section Header block; list of question/answer pairs; expand mode (one-at-a-time vs multi-open — per design).
- **MCP starter:** No dedicated template; compose with primitives.

---

### 13.E Utility / Chrome Sections

#### Header

- **Role:** Brand identity + primary nav + key actions, persistent.
- **Mandatory features:** Logo (text or image, link to home); primary nav (multi-level); search trigger → §9.2; account icon → Login or Dashboard; cart icon with count badge → Cart page or §9.1; hamburger (mobile) → §9.3; Announcement Bar (when the design includes one); sticky positioning per design.
- **Optional features:** Favorites icon; language / currency selector; secondary nav row; mega-menu — when a nav item needs more than `LIST_OF_LINK` can carry (image, badge, columns), use the MenuItem-child + COMPONENT_LIST pattern from `get_framework_guide("header-footer-patterns")` / `get_framework_guide("navigation-patterns")`.
- **MCP starter:** `get_section_template("header-section")` + `get_framework_guide("header-footer-patterns")`.

#### Footer

- **Role:** Site map, brand affirmation, legal links, contact.
- **Mandatory features:** Brand column (logo + tagline + socials); 1–4 sitemap columns; bottom bar (copyright, legal links, payment method icons).
- **Optional features:** Contact column; inline newsletter signup; language / currency switchers.
- **MCP starter:** `get_section_template("footer-section")`.

#### Announcement Bar (sub of Header)

- **Mandatory features:** 1–N rotating messages (TEXT[] or COMPONENT_LIST); auto-rotate interval (default 5s); manual prev/next on desktop; dismissible (sessionStorage).
- **MCP starter:** Implemented as a child of `header-section` or composed via `IkasThemeSlider` with autoplay.

#### Not Found (404)

- **Mandatory features:** Large heading (`<h1>`); subtitle; primary CTA → home; secondary CTA → search or contact.
- **Optional features:** Featured products row.
- **MCP starter:** `get_section_template("not-found-section")`.

#### Guest Order Tracking (optional, recommended)

- **Role:** Let a guest see their order without an account — a recovery path (§3 #7) for the largest post-purchase support driver ("where is my order?").
- **Page surface:** Utility page; linked from Footer and/or order emails. No auth gate — open to guests and logged-in users alike.
- **Mandatory features:** Email + order number form (storefront's order-tracking form lifecycle, validation per §7.6); on success, a **read-only** order view reusing the Account Order Detail anatomy (status, progress, line items with multi-package grouping, totals, delivery + payment blocks); not-found and generic-error states with merchant-editable copy; a "search another order" action that resets to the form.
- **Excluded:** the refund flow — guests don't refund from this surface.
- **MCP:** `list_functions("OrderTracking")` — note the submit returns the found order (or null), not a boolean like other form submits. No section template exists yet (ikas-editor-monorepo#740); derive from the Account Order Detail contract.

---

## 14. Anti-Patterns

These are violations. Theme PRs that introduce them should be rejected.

1. Hardcoded user-visible text in JSX.
2. DIY price formatting (building currency strings by hand instead of using storefront `formattedPrice`).
3. Blocking modals on page load.
4. Auto-opening modals/drawers (Cart Drawer after ATC is the only allowed exception).
5. Forced sign-up walls in front of browse / search / PDP.
6. Carousels without keyboard navigation or pause-on-hover.
7. Infinite scroll without a Load More fallback.
8. Hidden cart count badge when count > 0.
9. Layout-shifting images (no declared dimensions / aspect-ratio).
10. Animations without `prefers-reduced-motion` fallback.
11. Multiple `<h1>` elements per page.
12. Color as the only signal for status (out-of-stock, error, success).
13. Removing Header or Footer from any page (including 404 and auth pages).
14. Sections mutating global state on mount.
15. Optimistic UI without rollback handling.
16. Re-fetching the whole cart on a single-row mutation.
17. Disabling form submit on keystroke validation (disable only during async submission).
18. Removing semantic HTML in favor of `<div>` everywhere.
19. Wrapping a root section export with `observer()`.
20. Reconstructing framework behavior when MCP primitives exist (`IkasThemeSlider`, `IkasThemeOverlay`, `IkasThemeInfiniteScroller`, `createMediaSrcset`).
21. **Design-canonical:** Adding layout / alignment / aspect-ratio / per-element color ENUMs to a section when the design source has already decided. Merchant control over visual structure conflicts with the canonical design.
22. **Design-canonical:** Rewriting visual choices the design source made — replacing the palette, changing aspect ratios, swapping a designed layout for a "more standard" one — even when the change feels like a better default. The design source is canonical.
23. **Design-canonical:** Inventing props from this doc instead of querying `get_section_template(...)`. The MCP template's prop list is the starting point; adapt it to the design, don't reconstruct it from prose.
24. A dead out-of-stock button when the storefront has back-in-stock enabled — OOS must expose the §7.11 affordance (or route to the PDP, on cards).

---

## 15. Build Checklist

Before merging a section:

1. **Design parity.** The rendered section visually matches the design source.
2. **MCP starter consulted.** Before scaffolding, `get_section_template(...)` was queried and its CLI command run; props were not invented.
3. **Universal contract** (§5) satisfied.
4. **Section feature surface** (§13) complete — all Mandatory features present.
5. **Behavior contracts** (§7) implemented for every interaction the section triggers.
6. **State anatomy** (§7.7) — loading, empty, error, loaded all render.
7. **Defaults are shippable.** A merchant could install with zero edits and see the design source.
8. **Optimistic mutations** (where applicable) handle success AND failure rollback.
9. **Chrome triggers** wired per §9.
10. **No prop bloat** — no merchant controls for design-decided dimensions (color, alignment, layout, aspect ratio).
11. **No anti-patterns** (§14).
12. **`npx ikas-component check --json`** passes.
13. **`npx ikas-component build`** completes clean.

---

*Last updated: 2026-07-22 — verified against the live ikas-code-components MCP server and a production ikas theme's purchase-flow inventory.*
