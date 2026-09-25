#!/usr/bin/env python3
"""ikas.config.json prop/grup envanteri — ikas-prop-normalize skill'inin denetim aracı.

Kullanım: python3 audit.py [ikas.config.json yolu]
Çıktı: her component'in grupları ve propları + commerce.md §6.3 şemasına göre bayraklar.
  Ad bayrakları:   EN? = İngilizce kelime içeriyor (Türkçe ile karışık olsa bile)
                   ??  = dil belirlenemedi (diakritiksiz, bilinen kelime yok)
  Yapı bayrakları: !! ile başlar (grupsuz prop, eşik ihlali, grup sırası…)
Bayraklar önceliklendirme içindir — nihai karar tüm listeyi okuyarak verilir.
"""
import json
import re
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "ikas.config.json"
cfg = json.load(open(path))

EN = re.compile(
    r"\b(Label|Text|Title|Subtitle|Button|Show|Hide|Enable|Items?|Links?|Close|Open|"
    r"Drawer|Preview|Placeholder|Count|Empty|Image|Color|Background|Products?|"
    r"List|Search|Add|Remove|Next|Prev(ious)?|Zoom|More|Template|Guide|Notice|"
    r"Notify|Cart|Order|Address|Page|Size|State|Section|Heading|Description|"
    r"Icon|Slide|First|Last|Name|Phone|Email|Password|Submit|Loading|Error|"
    r"Success|View|All|New|Default|Filter|Sort|Price|Range|Stock|Shipping|"
    r"Breadcrumb|Content|Appearance|Gallery|Layout|Aspect|Ratio|Behavior|Settings|"
    r"Data|Texts|Colors|Quantity|Selector|Brand|Note|Main|Style)\b"
)
TR = re.compile(r"[çğıöşüÇĞİÖŞÜ]")
# Diakritik içermeyen yaygın Türkçe kelimeler de Türkçe sayılır
TR_WORDS = re.compile(
    r"\b(ve|veya|Metni|Metinler|Metin|Etiketi|Rengi|Renkler|Renk|Arka|Plan|"
    r"Buton|Butonu|Linki|Sepete|Sepet|Ekle|Ekleniyor|Daha|Fazla|Favori|Alan|"
    r"Alani|Adet|Toplam|Kargo|Teslimat|Durumlar|Duyuru|Kalemler|Yolculuk|"
    r"Sekmeler|Onaylar|Veri|Adres|Kayit|Hesap|Siparis|Kapat|Sonraki|Onceki|"
    r"Navigasyon|Aksiyonlar|Sosyal|Medya|Ayarlar|Galeri|Ana)\b",
    re.I,
)
# Her iki dilde de geçerli / çevrilmeyecek terimler tek başına bayrak üretmez
NEUTRAL = re.compile(r"^(URL|SVG|ID|CTA|Min|Maks|Logo|Banner|Panel|Form|Slogan|E-posta|Promo|Upsell)( \d+)?$", re.I)

# §6.3 kanonik grup sırası; bunların dışındaki id'ler özellik grubudur (sıra 2)
RANK = {"data": 0, "content": 1, "behavior": 3, "settings": 3, "texts": 4, "colors": 5, "appearance": 5}
FEATURE_RANK = 2


def flag(s):
    if not s or NEUTRAL.match(s):
        return ""
    if EN.search(s):
        return "EN?"  # Türkçe ile karışık etiketler de yakalanır ("Breadcrumb Göster")
    if TR.search(s) or TR_WORDS.search(s):
        return ""
    return "??"


def flatten(groups, depth=0):
    for g in groups:
        yield g, depth
        yield from flatten(g.get("children", []), depth + 1)


comps = cfg["components"]
counts = dict(total=0, name=0, ungrouped=0, desc=0, gdesc=0, struct=0)
print(f"TOPLAM {len(comps)} component\n")

for c in comps:
    props = c.get("props", [])
    groups = c.get("propGroups", [])
    counts["total"] += len(props)
    print(f"== {c['name']} ({c.get('type', 'component')}) id={c.get('id', '?')} — {len(props)} prop, {len(groups)} grup")

    struct = []
    if len(props) <= 4 and groups:
        struct.append("!! ≤4 prop ama grup var (§6.3: düz kalmalı)")
    if len(props) >= 5 and not groups:
        struct.append("!! ≥5 prop ama hiç grup yok")

    by_group = {}
    for p in props:
        by_group.setdefault(p.get("groupId"), []).append(p)

    for g, depth in flatten(groups):
        f = flag(g["name"])
        d = g.get("description")
        if d:
            counts["gdesc"] += 1
        members = by_group.get(g["id"], [])
        non_color = [p for p in members if p["type"] != "COLOR"]
        note = ""
        if depth == 0 and g["id"] not in RANK and len(non_color) < 3 and not g.get("children"):
            note = "  !! özellik grubu <3 prop (§6.3: dağıtılmalı)"
            struct.append(f"!! '{g['id']}' özellik grubu {len(non_color)} prop")
        if members and all(p["type"] == "COLOR" for p in members) and g["id"] not in ("colors", "appearance") and depth == 0:
            note += "  !! yalnız COLOR içeriyor — Renkler'de olmalı"
        colors_elsewhere = [p["name"] for p in members if p["type"] == "COLOR"] if g["id"] not in ("colors", "appearance") and depth == 0 else []
        if colors_elsewhere:
            struct.append(f"!! COLOR Renkler dışında: {', '.join(colors_elsewhere)} ({g['id']})")
        if not members and not g.get("children"):
            note += "  !! boş grup"
            struct.append(f"!! '{g['id']}' boş grup")
        print(f"{'  ' * (depth + 1)}[grup {g['id']}] {g['name']!r} {f}{note}" + (f" desc={d!r}" if d else ""))

    top = [g["id"] for g in groups]
    ranks = [RANK.get(i, FEATURE_RANK) for i in top]
    if ranks != sorted(ranks):
        struct.append("!! grup sırası §6.3'e uymuyor: " + " → ".join(top))

    for p in props:
        f = flag(p.get("displayName", ""))
        if f:
            counts["name"] += 1
        gid = p.get("groupId")
        if not gid and groups:
            counts["ungrouped"] += 1
            gid = "!! GRUPSUZ"
        d = p.get("description")
        if d:
            counts["desc"] += 1
        print(
            f"    - {p['name']:34} {p['type']:20} grp={gid or '-':16} "
            f"{p.get('displayName')!r} {f}" + (f" desc={d!r}" if d else "")
        )
    for s in struct:
        print(f"    {s}")
    counts["struct"] += len(struct)
    print()

for e in cfg.get("customTypes") or []:
    opts = e.get("enumOptions") or {}
    labels = [k for k in opts if flag(k)]
    print(f"[enum] {e.get('name')} id={e.get('id')} options={json.dumps(opts, ensure_ascii=False)}"
          + (f"  EN? etiketler: {', '.join(labels)}" if labels else ""))

print(
    f"\nÖZET: {counts['total']} prop | {counts['name']} bayraklı ad | "
    f"{counts['ungrouped']} grupsuz (gruplu component içinde) | {counts['struct']} yapı bayrağı | "
    f"{counts['desc']} prop açıklaması | {counts['gdesc']} grup açıklaması"
)
