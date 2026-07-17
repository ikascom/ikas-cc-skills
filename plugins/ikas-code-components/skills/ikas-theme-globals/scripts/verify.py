#!/usr/bin/env python3
"""ikas tema token bağlama doğrulaması.

Kullanım: python3 verify.py <proje-kökü> [--tokens <list_theme_globals-çıktısı>] [--allow <dosya>]

Kontroller:
1. Dangling var(): FALLBACK'SİZ referans verilen ama ne projede tanımlı ne de token
   kataloğunda olan CSS custom property'ler (tarayıcı satırı sessizce düşürür).
   var(--x, fallback) kullanımı güvenlidir, raporlanmaz.
2. Kalan hardcoded renkler (allowlist düşülerek) — migration sonrası kaçak tespiti.
3. TSX'te kullanılan _<id> tipografi class'larının katalogda var olup olmadığı
   (--tokens verilmişse).

--tokens: list_theme_globals çıktısının kaydedildiği dosya (JSON/metin farketmez);
içindeki var(--X) ve "id":"X" desenleri okunur. Renk token'larında cssVar casing'i
id'den FARKLIDIR — eşleşme cssVar'dan çıkarılan adla, birebir casing ile yapılır.
Çıkış kodu: dangling varsa 1, yoksa 0.
"""
import argparse
import os
import re
import sys
from collections import Counter, defaultdict

# grup 2: ')' = fallback'siz, ',' = fallback'li kullanım
VAR_REF = re.compile(r"var\(\s*--([A-Za-z0-9_-]+)\s*([,)])")
VAR_DEF = re.compile(r"--([A-Za-z0-9_-]+)\s*:")
# TSX tanım desenleri: style objesi {"--x": v}, bracket ataması ["--x"], setProperty("--x")
TSX_DEF = re.compile(r"[\"']--([A-Za-z0-9_-]+)[\"']")
SET_PROP = re.compile(r"setProperty\(\s*['\"]--([A-Za-z0-9_-]+)")
TOKEN_ID = re.compile(r"\"id\"\s*:\s*\"([A-Za-z0-9_-]+)\"")
HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")
COLOR_FUNC = re.compile(r"\b(?:rgba?|hsla?|oklch)\((?:[^()]|\([^)]*\))*\)")
TYPO_CLASS = re.compile(r"className=\{?[\"'`]([^\"'`]*)[\"'`]")
BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.S)


def iter_source(root):
    src = os.path.join(root, "src")
    if not os.path.isdir(src):
        sys.exit(f"HATA: {src} bulunamadı — proje kökünden çalıştır.")
    for dirpath, dirnames, filenames in os.walk(src):
        dirnames[:] = [d for d in dirnames if d not in ("node_modules", "dist", "build")]
        for fn in filenames:
            if fn.endswith((".css", ".tsx", ".ts")):
                path = os.path.join(dirpath, fn)
                try:
                    yield os.path.relpath(path, root), open(path, encoding="utf-8").read()
                except OSError:
                    continue


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--tokens", help="list_theme_globals çıktısı dosyası")
    ap.add_argument("--allow", help="izinli hardcoded değerler (satır başına bir değer)")
    args = ap.parse_args()

    known_vars, known_ids = set(), set()
    if args.tokens:
        blob = open(args.tokens, encoding="utf-8").read()
        known_vars = {m.group(1) for m in VAR_REF.finditer(blob)}
        known_ids = set(TOKEN_ID.findall(blob))

    # allowlist: satır başına bir değer; yorum satırı "//" ile başlar (hex'ler # ile başladığından)
    allow = set()
    if args.allow:
        for line in open(args.allow, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("//"):
                allow.add(line.lower())

    defined, referenced = set(), defaultdict(Counter)
    hardcoded = defaultdict(Counter)
    typo_used = defaultdict(set)

    for rel, raw in iter_source(args.root):
        text = BLOCK_COMMENT.sub("", raw)
        for m in VAR_DEF.finditer(text):
            defined.add(m.group(1))
        for m in SET_PROP.finditer(text):
            defined.add(m.group(1))
        if rel.endswith((".tsx", ".ts")):
            for m in TSX_DEF.finditer(text):
                defined.add(m.group(1))
        for m in VAR_REF.finditer(text):
            if m.group(2) == ")":  # fallback'siz kullanım — kırılma riski taşıyan bu
                referenced[m.group(1)][rel] += 1
        for m in HEX.finditer(text):
            v = m.group(0).lower()
            if v not in allow:
                hardcoded[v][rel] += 1
        for m in COLOR_FUNC.finditer(text):
            v = re.sub(r"\s+", " ", m.group(0))
            if "var(" not in v and v.lower() not in allow:
                hardcoded[v][rel] += 1
        if rel.endswith(".tsx"):
            for m in TYPO_CLASS.finditer(text):
                for cls in m.group(1).split():
                    if re.fullmatch(r"_[A-Za-z0-9]{6,}", cls):
                        typo_used[cls[1:]].add(rel)

    dangling = {
        name: files for name, files in referenced.items()
        if name not in defined and name not in known_vars
    }

    print("== 1) Dangling var() ==")
    if dangling:
        for name, files in sorted(dangling.items()):
            locs = ", ".join(f"{f}({c}×)" for f, c in files.most_common())
            print(f"  --{name}: {locs}")
        if not args.tokens:
            print("  NOT: --tokens verilmedi; platform token'ları da bu listede görünür.")
    else:
        print("  temiz ✓")

    print("\n== 2) Kalan hardcoded renkler ==")
    if hardcoded:
        for v, files in sorted(hardcoded.items(), key=lambda kv: -sum(kv[1].values())):
            locs = ", ".join(f"{f}({c}×)" for f, c in files.most_common(4))
            print(f"  {sum(files.values()):4d}×  {v}   [{locs}]")
        print(f"  toplam: {sum(sum(f.values()) for f in hardcoded.values())} kullanım "
              "(bilinçli kalanları allowlist'e ekle)")
    else:
        print("  temiz ✓")

    if args.tokens:
        print("\n== 3) TSX tipografi class'ları (_<id>) ==")
        unknown = {i: f for i, f in typo_used.items() if i not in known_ids}
        if unknown:
            for i, files in sorted(unknown.items()):
                print(f"  _{i} katalogda YOK: {', '.join(sorted(files))}")
        else:
            print(f"  {len(typo_used)} class, hepsi katalogda ✓")

    sys.exit(1 if dangling else 0)


if __name__ == "__main__":
    main()
