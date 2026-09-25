#!/usr/bin/env python3
"""ikas tema lint'i — commerce.md §14 anti-pattern'lerinin mekanik olarak yakalanabilenleri.

Kullanım: python3 lint.py <proje-kökü> [--allow <dosya>] [--only kural1,kural2] [--path yol1,yol2]
  --path: yalnızca bu yollarla başlayan dosyaların bulguları (ör. section denetimi için
          src/components/X,src/sub-components/Y); config bulguları component adıyla eşleşir.

Kurallar (her bulgu dosya:satır ve dayanak § ile basılır):
  observer-root    HATA   Kök section/component export'u observer() ile sarılmış (§14 #19)
  bg-color         HATA   Section'da backgroundColor COLOR prop'u yok (§5.1)
  mutation-catch   HATA   Sepet mutasyonu catch'siz — hata kullanıcıya ulaşmaz (§7.8, §14 #15)
  static-text      HATA   JSX'te sabit görünür metin veya sabit aria-label/alt/placeholder (§5.4, §14 #1)
  reduced-motion   UYARI  Animasyon/transition var, prefers-reduced-motion yok (§5.7, §14 #10)
  diy-price        UYARI  Elle para biçimlendirme şüphesi (§11.1, §14 #2)
  multi-h1         UYARI  Aynı component klasöründe birden fazla <h1> (§12.2, §14 #11)

Allowlist (--allow): satır başına "kural:dosya" ya da "kural:dosya:satır"; "//" ile başlayan
satır yorumdur — her istisnayı gerekçelendir. Çıkış kodu: HATA varsa 1, yoksa 0.
Bu bir eleme filtresidir: yargı gerektiren maddeler (§14 #21-23, OOS kurtarma…) kapsam dışı.
"""
import argparse
import json
import os
import re
import sys
from collections import defaultdict

SEVERITY = {
    "observer-root": "HATA", "bg-color": "HATA", "mutation-catch": "HATA", "static-text": "HATA",
    "reduced-motion": "UYARI", "diy-price": "UYARI", "multi-h1": "UYARI",
}
BASIS = {
    "observer-root": "§14 #19", "bg-color": "§5.1", "mutation-catch": "§7.8, §14 #15",
    "static-text": "§5.4, §14 #1", "reduced-motion": "§5.7, §14 #10", "diy-price": "§11.1, §14 #2",
    "multi-h1": "§12.2, §14 #11",
}

BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.S)
LINE_COMMENT = re.compile(r"(?<![:\"'])//[^\n]*")
# Sepet mutasyonları (MCP list_functions("Cart"), 2.9.2) + alias'ları
MUTATIONS = re.compile(
    r"\b(addItemToCart|addVariantToCart|addSelectedtedVariantToCart|addToCart|changeItemQuantity|"
    r"changeCartItemQuantity|changeQuantityOnCart|removeItem|removeItemFromCart|saveCouponCode|"
    r"removeCouponCode|removeGiftCardLine|windowAddToCart)\s*\("
)
JSX_TEXT = re.compile(r"<([a-zA-Z][\w.]*)(?:\s[^<>]*?)?>([^<>{}]*?[A-Za-zÇĞİÖŞÜçğıöşü]{2,}[^<>{}]*?)</")
LITERAL_ATTR = re.compile(r"\b(aria-label|alt|placeholder|title)\s*=\s*\"([^\"]*[^\s\"][^\"]*)\"")
MOTION = re.compile(r"\b(transition|animation)\s*:\s*(?!none\b)|scroll-behavior\s*:\s*smooth")
SMOOTH_JS = re.compile(r"behavior\s*:\s*[\"']smooth[\"']")
PRICE = re.compile(r"toFixed\s*\(|[\"'`][^\"'`\n]*(₺|\bTL\b|\$(?!\{)|€)[^\"'`\n]*[\"'`]|Intl\.NumberFormat")


def strip_comments(text, css=False):
    text = BLOCK_COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    return text if css else LINE_COMMENT.sub("", text)


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def matching_brace(text, open_pos):
    depth = 0
    for i in range(open_pos, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return i
    return len(text)


def catch_protected(text, pos):
    """Çağrı catch'li bir try bloğunda ya da .catch( zincirinde mi?"""
    for m in re.finditer(r"\btry\s*\{", text[:pos]):
        start = m.end() - 1
        end = matching_brace(text, start)
        if start < pos < end and re.match(r"\s*catch\b", text[end + 1:]):
            return True
    stmt_end = text.find(";", pos)
    stmt = text[pos:stmt_end if stmt_end != -1 else len(text)]
    return ".catch(" in stmt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--allow")
    ap.add_argument("--only")
    ap.add_argument("--path")
    args = ap.parse_args()
    root = args.root
    src = os.path.join(root, "src")
    if not os.path.isdir(src):
        sys.exit(f"HATA: {src} bulunamadı — proje kökünden çalıştır.")
    only = set(args.only.split(",")) if args.only else None
    paths = [p.strip().rstrip("/") for p in args.path.split(",")] if args.path else None

    allow = set()
    if args.allow:
        for line in open(args.allow, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("//"):
                allow.add(line)

    findings = []  # (kural, dosya, satır, mesaj)

    def add(rule, rel, line, msg):
        if only and rule not in only:
            return
        if paths:
            if rel == "ikas.config.json":
                if not any(msg.startswith(os.path.basename(p) + ":") for p in paths):
                    return
            elif not any(rel == p or rel.startswith(p + os.sep) for p in paths):
                return
        if f"{rule}:{rel}" in allow or f"{rule}:{rel}:{line}" in allow:
            return
        findings.append((rule, rel, line, msg))

    # --- config tabanlı: bg-color
    cfg_path = os.path.join(root, "ikas.config.json")
    comp_dirs = {}
    if os.path.isfile(cfg_path):
        cfg = json.load(open(cfg_path, encoding="utf-8"))
        for c in cfg.get("components", []):
            if c.get("type") == "section":
                bg = [p for p in c.get("props", []) if p.get("name") == "backgroundColor" and p.get("type") == "COLOR"]
                if not bg:
                    add("bg-color", "ikas.config.json", 0, f"{c['name']}: backgroundColor COLOR prop'u yok")
                elif not bg[0].get("defaultValue"):
                    add("bg-color", "ikas.config.json", 0, f"{c['name']}: backgroundColor defaultValue boş")

    # --- klasör bazında dosyaları topla
    global_css = ""
    gpath = os.path.join(src, "global.css")
    if os.path.isfile(gpath):
        global_css = open(gpath, encoding="utf-8").read()
    folders = defaultdict(list)  # klasör -> [(rel, text, ext)]
    for dirpath, dirnames, filenames in os.walk(src):
        dirnames[:] = [d for d in dirnames if d not in ("node_modules", "dist", "build")]
        for fn in filenames:
            if fn.endswith((".tsx", ".css")):
                path = os.path.join(dirpath, fn)
                rel = os.path.relpath(path, root)
                css = fn.endswith(".css")
                text = strip_comments(open(path, encoding="utf-8").read(), css=css)
                folders[os.path.relpath(dirpath, root)].append((rel, text, "css" if css else "tsx"))

    for folder, files in folders.items():
        is_root_component = folder.startswith(os.path.join("src", "components") + os.sep)
        motion_hits, reduced, h1s = [], "prefers-reduced-motion" in global_css, []
        for rel, text, kind in files:
            if kind == "css":
                if "prefers-reduced-motion" in text:
                    reduced = True
                for m in MOTION.finditer(text):
                    motion_hits.append((rel, line_of(text, m.start())))
                continue
            # tsx
            for m in SMOOTH_JS.finditer(text):
                motion_hits.append((rel, line_of(text, m.start())))
            if "prefers-reduced-motion" in text:
                reduced = True
            if is_root_component and rel.endswith("index.tsx"):
                obs = re.search(r"export\s+default\s+observer\s*\(", text)
                if not obs:
                    d = re.search(r"export\s+default\s+(\w+)\s*;", text)
                    if d:
                        obs = re.search(rf"(?:const|let)\s+{d.group(1)}\s*=\s*observer\s*\(", text)
                if obs:
                    add("observer-root", rel, line_of(text, obs.start()), "kök export observer() ile sarılmış — runtime zaten reaktif yapar")
            for m in MUTATIONS.finditer(text):
                # import satırlarını ve fonksiyon tanımlarını atla
                prev = text[max(0, m.start() - 40):m.start()]
                if re.search(r"(import\s*\{[^}]*|function\s+)$", prev):
                    continue
                if not catch_protected(text, m.start()):
                    add("mutation-catch", rel, line_of(text, m.start()), f"{m.group(1)}() catch'siz — başarısızlıkta kullanıcı geri bildirimi yok")
            for m in JSX_TEXT.finditer(text):
                t = " ".join(m.group(2).split())
                add("static-text", rel, line_of(text, m.start(2)), f"sabit metin: {t[:50]!r}")
            for m in LITERAL_ATTR.finditer(text):
                add("static-text", rel, line_of(text, m.start()), f"sabit {m.group(1)}: {m.group(2)[:40]!r}")
            for m in PRICE.finditer(text):
                add("diy-price", rel, line_of(text, m.start()), f"para biçimlendirme şüphesi: {m.group(0)[:40]!r} — get*FormattedPrice helper'ları / formatCurrency (MCP common-pitfalls #20)")
            for m in re.finditer(r"<h1\b", text):
                h1s.append((rel, line_of(text, m.start())))
        if motion_hits and not reduced:
            rel, line = motion_hits[0]
            add("reduced-motion", rel, line, f"{len(motion_hits)} animasyon/transition, klasörde prefers-reduced-motion yok")
        if len(h1s) > 1:
            add("multi-h1", h1s[1][0], h1s[1][1], f"klasörde {len(h1s)} <h1> — sayfada tek <h1> olmalı")

    # --- rapor
    errors = sum(1 for f in findings if SEVERITY[f[0]] == "HATA")
    by_rule = defaultdict(list)
    for f in findings:
        by_rule[f[0]].append(f)
    for rule in SEVERITY:
        items = by_rule.get(rule)
        if not items:
            continue
        print(f"== {rule} [{SEVERITY[rule]}] ({BASIS[rule]}) — {len(items)}")
        for _, rel, line, msg in sorted(items, key=lambda x: (x[1], x[2])):
            loc = f"{rel}:{line}" if line else rel
            print(f"  {loc}  {msg}")
        print()
    warnings = len(findings) - errors
    print(f"ÖZET: {errors} hata, {warnings} uyarı" + ("" if findings else " — temiz ✓"))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
