---
name: ikas-theme-globals
description: Use when creating or migrating ikas theme global design tokens (COLOR, TYPOGRAPHY, COLOR SCHEME, breakpoint, keyframe) in a Code Components theme project — extracting a token catalog from existing CSS, building tokens for a new theme, or binding CSS/TSX to tokens via cssVar/className. Triggers - tema global renk/tipografi token'ları, color scheme / palet kurulumu, create_theme_global, design token migration, global renk ayarları, cssVar/className bağlama, hardcoded renk temizliği.
---

# ikas Tema Global Token Kurulumu (Renk + Tipografi + Scheme)

Bir ikas Code Components temasında global token setini (renk, tipografi, color scheme;
gerekirse breakpoint/keyframe) kurar, CSS/TSX'i token'lara bağlar ve doğrular. Token seti
**temanın kendi CSS diline göre tasarlanır** — hazır bir katalog şablonu dayatılmaz;
başka temaların setleri en fazla ilham kaynağıdır. Güncel kavram seti ve kurallar için
MCP `get_framework_guide("theme-globals")` kaynağın — bu skill iş akışını verir,
framework gerçeklerini oradan doğrula.

**Temel ilke: envanter ve doğrulama script'le (deterministik), token seti kararı
kullanıcı onayıyla.** Token oluşturmak mağaza-kalıcı bir yan etkidir; onaysız yapılmaz.

## Ön koşullar

- `ikas-component dev` çalışıyor VE editör tarayıcıda bağlı olmalı (TÜM MCP
  theme-global araçları için gerekir; sadece dev yetmez — "No editor connected" hatası
  verir). Editörsüz alternatif: CLI eşdeğerleri (`npx ikas-component create-color`,
  `create-text-style`, `create-color-scheme`, `list-theme-globals`,
  `delete-design-token`…).
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

**Önce mimari kararı ver:** MCP guide'ın önerdiği varsayılan, **color scheme (slot +
palet)** mimarisidir — adlandırılmış slot'lar (`Background`, `Metin`,
`PrimaryButton/Text`…) + slot→renk paletleri. Section editörden scheme seçer,
component'ler slot cssVar'larını kullanır → merchant kod değişmeden re-skin yapar.
Flat renk token'ları hâlâ geçerli (tek paletli tema, hızlı migration), ama iki fark
bilinçli seçilmeli: (1) scheme slot değerleri `var(--<colorId>)` linked reference kabul
eder — eski "alias katmanı" ihtiyacının modern karşılığı budur; (2) partner design asset
taşınabilirliğinde **slot id'leri store'lar arası taşınır, flat renk id'leri taşınmaz**.
Mimari kararı katalog önerisiyle birlikte kullanıcıya sun.

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

Onaylı katalogu `create_theme_global` ile aç. Güncel kind'lar:
`globalVariable | color | typography | breakpoint | keyframe | colorScheme`
(`delete_theme_global` ek olarak `colorSchemeSlot` da siler — slot TÜM scheme'lerden
cascade'li kaldırılır).

| Tuzak | Kural |
|---|---|
| Referansları elle kurma hevesi | Dönen `id`/`cssVar`/`className`'i **birebir kopyala** (cssVar = `var(--<id>)`, className = `_<id>`; yine de dönen string esas alınır) |
| `font_weight` fontun shiplemediği değerde reddedilir | `supportedFontWeights` listesine bak; emin değilsen `400` (italic: `"400i"`) |
| Color token başka token'ı alias'layamaz | `value` her zaman somut renk; `var(...)` reddedilir. İSTİSNA: colorScheme slot değerleri literal renk YA DA `var(--<colorId>)` linked reference alabilir |
| Var olan rengi değiştirme ihtiyacı | `update_theme_color` (cssVar sabit kalır) — delete+recreate YASAK. Scheme paleti: `update_theme_color_scheme` (slot bazında MERGE, `is_default` exclusive). Slot adı: `rename_theme_color_scheme_slot` (id sabit, binding kopmaz). `update_theme_global` YALNIZCA `globalVariable` (Theme Settings) içindir |
| Name'ler unique değil | Token VE slot takibi/eşleştirme her zaman `id` ile (name-lookup bilinçli olarak yok) |

`_<id>` kalıbı üç yerde aynı: typography `className`, keyframe `ref` (animation-name),
scheme palet `className`. Keyframe güncellemede `points` REPLACE semantiğidir (merge
değil). Her create sonucundaki id/cssVar/className'i not al — Adım 5'in girdisi.

## Adım 5 — CSS/TSX'i bağla

Temanın yapısına göre yöntem seç:

- **Scheme mimarisi (önerilen):** component CSS'i slot cssVar'larını
  (`var(--<slotId>)`) doğrudan kullanır ve palet `className`'i EKLENMEZ — className'siz
  kullanım, section'ın editörde seçili scheme'ini inherit eder (guide'ın önerdiği
  varsayılan mod). Palet className'i yalnızca bir bölgeyi bilerek başka palete
  sabitlemek içindir.
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
- **Yükleme sırası:** global CSS unscoped'dur ve önce yüklenir (Global → Shared →
  Component); değişkenler doğal cascade ile ulaşır, component CSS'i aynı property'yi
  yazarsa kazanır. Runtime'da JS ile `documentElement`'e yazılan değişkenlere her
  kullanımda `var(--x, fallback)` ver (SSR/ilk boyamada değer henüz yoktur).
- **Media query'de tema breakpoint'i:** `var()` media query içinde çalışmaz — tek yol
  `bp(<breakpointId>)` token'ı: `@media (max-width: bp(<id>))` render'da somut px'e
  çevrilir; CSS'te referans verilen breakpoint asset dependency olarak otomatik taşınır.
- **Canlı vs snapshot:** görsel her şeyde `cssVar`/`className` kullan (editör
  düzenlemesi anında yansır); `resolved`/`width`/`value` render anı snapshot'ıdır,
  canvas yenilenene dek gecikmesi bug değildir. `resolved`'ı inline style'a yayma.
- Tema partner design asset olarak dağıtılacaksa: kodda hardcoded global-variable
  key ve flat renk token id'si taşınmaz — **scheme slot id'leri ise store'lar arası
  aynen taşınır** (`var(--<slotId>)` portable). Ayrıntı: MCP
  `get_framework_guide("theme-globals")` Portability bölümü.

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
- `cssVar`/`className`/slot referansını elle kurmak veya name ile eşleştirmek →
  dönen değeri kopyala, takip her zaman `id` ile.
- Migration'da alias'ı bağlarken hedef token'ı doğrulamamak → dangling `var()`,
  tarayıcı satırı düşürür, hata da vermez.
- Token class'ı ekleyip component CSS'indeki `font-family`'yi bırakmak → font
  "değişmiyor" şikâyeti.
- Scheme mimarisinde her component'e palet `className`'i yapıştırmak → inherit
  modunu kırar; section'ın editörden seçtiği scheme yansımaz olur.
- Runtime'da `getThemeColorSchemes().schemes`'i iterate edip renkleri boş görmek →
  `colorsByScheme` slot-id anahtarlıdır, oradan oku.
- Kullanıcı onayı almadan katalog açmak → mağazada temizlenmesi gereken token çöplüğü.
