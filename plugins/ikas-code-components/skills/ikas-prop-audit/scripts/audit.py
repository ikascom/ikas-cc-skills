#!/usr/bin/env python3
"""ikas.config.json prop/grup envanteri — ikas-prop-audit skill'inin denetim aracı.

Kullanım: python3 audit.py [ikas.config.json yolu]
Çıktı: her component'in grupları ve propları; İngilizce görünümlü adlar EN?,
diakritiksiz/karar verilemeyenler ?? ile işaretlenir. Sonda özet sayaçlar.
Bayraklar önceliklendirme içindir — nihai karar tüm listeyi okuyarak verilir.
"""
import json
import re
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "ikas.config.json"
cfg = json.load(open(path))

EN = re.compile(
    r"\b(Label|Text|Title|Button|Show|Hide|Enable|Items?|Links?|Close|Open|"
    r"Drawer|Preview|Placeholder|Count|Empty|Image|Color|Background|Products?|"
    r"List|Search|Add|Remove|Next|Prev(ious)?|Zoom|More|Template|Guide|Notice|"
    r"Notify|Cart|Order|Address|Page|Size|State|Section|Heading|Description|"
    r"Icon|Slide|First|Last|Name|Phone|Email|Password|Submit|Loading|Error|"
    r"Success|View|All|New|Default|Filter|Sort|Price|Range|Stock|Shipping)\b"
)
TR = re.compile(r"[çğıöşüÇĞİÖŞÜ]")
# Diakritik içermeyen yaygın Türkçe kelimeler de Türkçe sayılır
TR_WORDS = re.compile(
    r"\b(ve|veya|Metni|Metinler|Metin|Etiketi|Rengi|Renkler|Renk|Arka|Plan|"
    r"Buton|Butonu|Linki|Sepete|Sepet|Ekle|Ekleniyor|Daha|Fazla|Favori|Alan|"
    r"Alani|Adet|Toplam|Kargo|Teslimat|Durumlar|Duyuru|Kalemler|Yolculuk|"
    r"Sekmeler|Onaylar|Veri|Adres|Kayit|Hesap|Siparis|Kapat|Sonraki|Onceki|"
    r"Navigasyon|Aksiyonlar|Sosyal|Medya)\b",
    re.I,
)
# Her iki dilde de geçerli / çevrilmeyecek terimler tek başına bayrak üretmez
NEUTRAL = re.compile(r"^(URL|SVG|ID|CTA|Min|Maks|Logo|Banner|Panel|Form|Slogan|E-posta|Promo|Upsell)( \d+)?$", re.I)


def flag(s):
    if not s or TR.search(s) or TR_WORDS.search(s) or NEUTRAL.match(s):
        return ""
    return "EN?" if EN.search(s) else "??"


comps = cfg["components"]
en_count = ungrouped = desc_count = total = 0
print(f"TOPLAM {len(comps)} component\n")

for c in comps:
    props = c.get("props", [])
    groups = c.get("propGroups", [])
    total += len(props)
    print(f"== {c['name']} ({c.get('type', 'component')}) — {len(props)} prop, {len(groups)} grup")

    def walk(gs, depth=1):
        for g in gs:
            f = flag(g["name"])
            d = g.get("description")
            print(f"{'  ' * depth}[grup {g['id']}] {g['name']!r} {f}" + (f" desc={d!r}" if d else ""))
            walk(g.get("children", []), depth + 1)

    walk(groups)
    for p in props:
        f = flag(p.get("displayName", ""))
        if f:
            en_count += 1
        gid = p.get("groupId")
        if not gid and groups:
            ungrouped += 1
            gid = "!! GRUPSUZ"
        d = p.get("description")
        if d:
            desc_count += 1
        print(
            f"    - {p['name']:34} {p['type']:20} grp={gid or '-':16} "
            f"{p.get('displayName')!r} {f}" + (f" desc={d!r}" if d else "")
        )
    print()

for e in cfg.get("customTypes") or []:
    print(f"[enum] {json.dumps(e, ensure_ascii=False)[:200]}")

print(f"\nÖZET: {total} prop | {en_count} bayraklı ad | {ungrouped} grupsuz (gruplu component içinde) | {desc_count} açıklamalı")
