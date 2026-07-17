#!/usr/bin/env python3
"""ikas tema projesinde hardcoded renk/font envanteri çıkarır.

Kullanım: python3 inventory.py <proje-kökü>

src/ altındaki .css ve .tsx dosyalarını tarar; hex/rgb/hsl renkleri ve
font-family / font-size / font-weight değerlerini frekans sıralı döker.
var(--...) üzerinden gelen (zaten token'lanmış) kullanımlar sayılmaz.
"""
import os
import re
import sys
from collections import Counter, defaultdict

HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")
COLOR_FUNC = re.compile(r"\b(?:rgba?|hsla?|oklch)\((?:[^()]|\([^)]*\))*\)")
FONT_FAMILY = re.compile(r"font-family\s*:\s*([^;}\n]+)")
FONT_SIZE = re.compile(r"font-size\s*:\s*([^;}\n]+)")
FONT_WEIGHT = re.compile(r"font-weight\s*:\s*([^;}\n]+)")
BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.S)


def norm_hex(value: str) -> str:
    return value.lower()


def scan(root: str):
    colors = Counter()
    color_files = defaultdict(set)
    families = Counter()
    sizes = Counter()
    weights = Counter()

    src = os.path.join(root, "src")
    if not os.path.isdir(src):
        sys.exit(f"HATA: {src} bulunamadı — proje kökünden çalıştır.")

    for dirpath, dirnames, filenames in os.walk(src):
        dirnames[:] = [d for d in dirnames if d not in ("node_modules", "dist", "build")]
        for fn in filenames:
            if not fn.endswith((".css", ".tsx", ".ts")):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, root)
            try:
                text = open(path, encoding="utf-8").read()
            except OSError:
                continue
            text = BLOCK_COMMENT.sub("", text)

            for m in HEX.finditer(text):
                v = norm_hex(m.group(0))
                colors[v] += 1
                color_files[v].add(rel)
            for m in COLOR_FUNC.finditer(text):
                v = re.sub(r"\s+", " ", m.group(0))
                if "var(" in v:
                    continue  # token'lanmış kullanım — envantere girmez
                colors[v] += 1
                color_files[v].add(rel)

            if fn.endswith(".css"):
                for m in FONT_FAMILY.finditer(text):
                    v = re.sub(r"\s+", " ", m.group(1)).strip()
                    families[v] += 1
                for m in FONT_SIZE.finditer(text):
                    sizes[m.group(1).strip()] += 1
                for m in FONT_WEIGHT.finditer(text):
                    weights[m.group(1).strip()] += 1

    return colors, color_files, families, sizes, weights


def dump(title: str, counter: Counter, files=None, limit_files=4):
    print(f"\n== {title} ({len(counter)} benzersiz) ==")
    for value, count in counter.most_common():
        line = f"{count:5d}×  {value}"
        if files is not None:
            fl = sorted(files[value])
            shown = ", ".join(fl[:limit_files])
            more = f" +{len(fl) - limit_files}" if len(fl) > limit_files else ""
            line += f"   [{shown}{more}]"
        print(line)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    root = sys.argv[1]
    colors, color_files, families, sizes, weights = scan(root)
    dump("RENKLER (hardcoded)", colors, color_files)
    dump("FONT-FAMILY", families)
    dump("FONT-SIZE", sizes)
    dump("FONT-WEIGHT", weights)
    print(f"\nToplam hardcoded renk kullanımı: {sum(colors.values())}")


if __name__ == "__main__":
    main()
