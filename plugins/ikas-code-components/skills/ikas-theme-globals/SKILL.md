---
name: ikas-theme-globals
description: Use when creating or migrating ikas theme global COLOR and TYPOGRAPHY design tokens in a Code Components theme project — extracting a token catalog from existing CSS, building tokens for a new theme, or binding CSS/TSX to tokens via cssVar/className. Triggers - tema global renk/tipografi token'ları, create_theme_global, design token migration, global renk ayarları, cssVar/className bağlama, hardcoded renk temizliği.
---

# ikas Tema Global Token Kurulumu (Renk + Tipografi)

Bir ikas Code Components temasında renk ve tipografi global token setini kurar,
CSS/TSX'i token'lara bağlar ve doğrular. Token seti **temanın kendi CSS diline göre
tasarlanır** — hazır bir katalog şablonu dayatılmaz; başka temaların setleri en fazla
ilham kaynağıdır.

**Temel ilke: envanter ve doğrulama script'le (deterministik), token seti kararı
kullanıcı onayıyla.** Token oluşturmak mağaza-kalıcı bir yan etkidir; onaysız yapılmaz.

## Ön koşullar

- `ikas-component dev` çalışıyor VE editör tarayıcıda bağlı olmalı (MCP token
  araçlarının ikisi de gerekir; sadece dev yetmez — "No editor connected" hatası verir).
- **İlk iş `list_theme_globals`** — mevcut katalogu çek, çıktıyı olduğu gibi bir dosyaya
  kaydet (örn. `/tmp/theme-globals.json`; Adım 6'da `--tokens` girdisi). Var olan token
  asla duplike edilmez; isim çakışması varsa bile eşleşme **id ile** yapılır, name ile
  değil (name'ler unique değildir).

## Adım 1 — Durum tespiti

`src/` altında yazılmış component CSS'i var mı?

- **Varsa → migration modu:** envanter mevcut koddan çıkar (Adım 2).
- **Yoksa → kurulum modu:** envanter tasarım spec'inden/palet kararından gelir;
  Adım 2 atlanır, Adım 3'e tasarım girdileriyle girilir. Sonraki adımlar ortak.

## Adım 2 — Envanter (migration modu)

```bash
python3 <skill-dizini>/scripts/inventory.py <proje-kökü> > /tmp/token-inventory.txt
```

Hardcoded renkleri ve font-family/size/weight değerlerini frekans sıralı döker
(`var(--...)` üzerinden gelenler zaten token'lıdır, sayılmaz). Bilinen sınırlamalar:
TSX'teki COLOR prop default'ları ve `#8249` gibi anchor/id string'leri de yakalanır —
listeyi yorumlayarak oku, prop default'ları token'lanmaz (onlar editör değeridir).

## Adım 3 — Token seti tasarımı (skill'in kalbi)

Envanterden/spec'ten **temaya özgü** bir katalog önerisi çıkar:

- **Adlandırma:** `"Grup/İsim"` — `/` editörde otomatik gruplar (örn. `Marka/Orman`,
  `Nötr/Koyu`, `Vurgu/Bal`). Grup şemasını temanın paletinden türet; tipik iskelet:
  Marka (2-4), Nötr (zemin/metin, 3-5), Vurgu (1-3). İsimler Türkçe ve rol anlatır.
- **Tekilleştirme:** yakın renkleri birleştir (envanterde `#6f735f` ile `#6e7b5c` gibi
  komşular tek token olur). Bir rengin saydamlık/ton varyantına ayrı token açma —
  CSS'te `color-mix(in srgb, var(--token) N%, transparent)` ile türet.
- **Tipografi rolleri:** temanın gerçek kullanımından 3-6 rol çıkar (örn.
  Display/Başlık/Gövde/Etiket/UI). Her rol = bir typography token (font_family +
  gerekirse size/weight). Font boyutu ölçeği envanterdeki en sık değerlere oturmalı;
  29 farklı font-size varsa token'lar roldür, her boyut token olmaz.
- **UX tabanı:** metin/zemin çiftlerinde WCAG AA kontrastını (4.5:1) koru; token
  sayısını asgaride tut — az token, tutarlı tema demektir.

**Katalog önerisini tablo halinde sun (isim → değer → nereleri kapsayacağı) ve
KULLANICI ONAYI al. Onaysız `create_theme_global` çağrısı yapılmaz.**

## Adım 4 — Token'ları oluştur

Onaylı katalogu `create_theme_global` ile aç (`kind: "color"` / `kind: "typography"`).

| Tuzak | Kural |
|---|---|
| Color `cssVar` casing'i `id`'den FARKLI (örn. id `IMl0NDdlCA` → cssVar `var(--iMl0NDdlCa)`) | Dönen `cssVar` string'ini **birebir kopyala**; id'den asla elle türetme |
| `font_weight` fontun shiplemediği değerde reddedilir | `supportedFontWeights` listesine bak; emin değilsen `400` (italic: `"400i"`) |
| Color token başka token'ı alias'layamaz | `value` her zaman somut renk (hex); `var(...)` reddedilir |
| Var olan rengi değiştirme ihtiyacı | `update_theme_color` (cssVar sabit kalır) — delete+recreate YASAK |
| Name'ler unique değil | Token takibi ve eşleştirme her zaman `id` ile |

Typography'de `className` = `_<id>` (casing sorunu yok). Her create sonucundaki
id/cssVar/className'i not al — Adım 5'in girdisi.

## Adım 5 — CSS/TSX'i bağla

Temanın yapısına göre yöntem seç:

- **CSS-ağırlıklı tema (semantik alias katmanı):** `global.css` `:root` içinde
  `--<prefix>-orman: var(--<cssVar-adı>);` gibi alias'lar tanımla, component CSS'i
  alias'ları kullansın. Alias eklemeden önce hedefin katalogda **gerçekten var olan**
  bir token'a çözüldüğünü doğrula — dangling alias'a bağlanan her `color-mix`/`var`
  satırını tarayıcı sessizce düşürür.
- **Az kullanım / TSX-ağırlıklı:** doğrudan `style={{ color: cssVar }}` veya
  typography `className`'i.

Bağlama kuralları:

- **Tipografi specificity tuzağı:** token class'ı düşük specificity'dir (`._id` = 0,1,0);
  scoped component CSS'i (`.cc_x .y` = 0,2,0) onu EZER. Token class verilen elemanın
  component CSS'inden `font-family` satırını SİL; form kontrollerine (button/input/
  select/textarea — miras almazlar) `font-family: inherit` ver.
- **`:root` kopyalama tuzağı:** build, `global.css`'teki `:root` bildirimlerini her
  component'in scope köküne kopyalar. Runtime'da JS ile `documentElement`'e yazılan
  bir değişkeni `:root`'ta tanımlama — kopya her scope sınırında mirası keser; onun
  yerine her kullanımda `var(--x, fallback)` ver.
- **Canlı vs snapshot:** görsel her şeyde `cssVar`/`className` kullan (editör
  düzenlemesi anında yansır); `resolved`/`value` render anı snapshot'ıdır.
- Tema partner design asset olarak dağıtılacaksa: kodda hardcoded global-variable
  key taşınmaz — ayrıntı için MCP `get_framework_guide("theme-globals")` Portability bölümü.

## Adım 6 — Doğrulama akışı (bitiş kontrolü)

1. ```bash
   python3 <skill-dizini>/scripts/verify.py <proje-kökü> \
     --tokens /tmp/theme-globals.json --allow /tmp/allow.txt
   ```
   `--tokens` = **güncel** `list_theme_globals` çıktısı (oluşturma sonrası yeniden çek).
   Rapor: (1) fallback'siz dangling `var()` — sıfır olmalı; (2) kalan hardcoded
   renkler — bilinçli kalanlar (prop default'ları, üçüncü parti marka renkleri örn.
   Google/Facebook butonları) allowlist'e `//` yorumuyla gerekçelenerek eklenir,
   gerisi bağlanır; (3) TSX `_<id>` class'larının katalog eşleşmesi.
2. `npx ikas-component build` temiz geçmeli.
3. **Canlı test:** editörde bir renk token'ının değerini geçici değiştir → sayfada
   anında yansımalı (cssVar canlıdır); bir typography token'ında font değiştir →
   token class'lı elemanlar değişmeli. Değişmeyen eleman = specificity tuzağı
   (Adım 5'e dön). Testten sonra değerleri geri al.

## Sık hatalar

- `list_theme_globals` çağırmadan token açmak → duplike katalog.
- cssVar'ı id'den türetmek → sessizce çözülmeyen renk (belgelenmiş gerçek vaka).
- Migration'da alias'ı bağlarken hedef token'ı doğrulamamak → dangling `var()`,
  tarayıcı satırı düşürür, hata da vermez.
- Token class'ı ekleyip component CSS'indeki `font-family`'yi bırakmak → font
  "değişmiyor" şikâyeti.
- Kullanıcı onayı almadan katalog açmak → mağazada temizlenmesi gereken token çöplüğü.
