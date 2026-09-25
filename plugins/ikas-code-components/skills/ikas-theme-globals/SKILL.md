---
name: ikas-theme-globals
description: Use when creating or migrating ikas theme global design tokens (COLOR, TYPOGRAPHY, COLOR SCHEME, breakpoint, keyframe) in a Code Components theme project — extracting a token catalog from existing CSS, building tokens for a new theme, or binding CSS/TSX to tokens via cssVar/className. Triggers - tema global renk/tipografi token'ları, color scheme / palet kurulumu, create_theme_global, design token migration, global renk ayarları, cssVar/className bağlama, hardcoded renk temizliği.
---

# ikas Tema Global Token Kurulumu (Renk + Tipografi + Scheme)

Bir temanın global token setini (renk, tipografi, color scheme; gerekirse breakpoint /
keyframe) kurar, kodu ve editör değerlerini bu token'lara bağlar, sonra doğrular.

**Görev dağılımı:**
- **MCP:** framework gerçeklerinin sahibi. Araç kuralları, değer şekilleri, id / cssVar /
  className kalıpları ve runtime API burada.
- **Bu skill:** MCP'nin vermediği kısmın sahibi. Temaya özgü katalog kararı, kullanıcı onayı,
  MCP'de yazmayan tuzaklar ve deterministik script'ler.

Kural: token oluşturmak mağazada kalıcı bir yan etkidir, **onaysız yapılmaz**.

> **Adım 1-3 devredilebilir.** `ikas-theme-globals-inventory` bu adımları izole bir
> subagent'ta koşturur ve onaya hazır bir rapor döndürür. Rapor onaylandıysa buraya
> **Adım 4'ten** gir.

## Ön koşullar ve MCP yönlendirmesi

- **Ortam:** `ikas-component dev` çalışıyor ve editör bağlı olmalı; theme-global araçları
  başka türlü "No editor connected" hatası verir.
- **İlk iş `list_theme_globals`:** çıktıyı olduğu gibi scratchpad'e `theme-globals.json`
  olarak kaydet. Bu dosya Adım 6'da `verify.py --tokens` girdisi olur.
- **Ne zaman neyi oku:**

  | Ne zaman | MCP kaynağı |
  |---|---|
  | Mimari kararından önce (Adım 3) | `get_framework_guide("theme-globals")`, "Using a color scheme" ve "Portability" bölümleri |
  | Her token aracını çağırmadan önce (Adım 4) | O aracın açıklaması. Kurallar (id kopyalama, alias yasağı, yerinde güncelleme, font ağırlığı) orada yazıyor |
  | Kodu bağlamadan önce (Adım 5) | `get_framework_guide("theme-globals")`, runtime getter'lar, `bp()`, canlı ile snapshot değer farkı |
  | Editör değerini bağlamadan önce (Adım 5) | `get_editor_workflow()` |
  | Editör bağlı değilse | Guide'daki "CLI equivalents" bölümü; flag'ler için `npx ikas-component <komut> --help` |

## Adım 1 — Durum tespiti

`src/` altında yazılmış component CSS'i var mı?

- **Varsa → migration modu:** envanter mevcut koddan çıkar (Adım 2).
- **Yoksa → kurulum modu:** envanter tasarım spec'inden/palet kararından gelir;
  Adım 2 atlanır, Adım 3'e tasarım girdileriyle girilir. Sonraki adımlar ortak.
- **Kod token'ları zaten tüketiyorsa → kısmi migration:** runtime getter'larından biri
  (`getThemeColors`, `getThemeTypography`…) ya da `var(--x, #hex)` fallback'leri
  kullanılıyorsa katalogda karşılıkları büyük olasılıkla vardır. Tüketimi eşleştir ve
  **ad ile yapılan aramaları** (`.find(t => t.name === …)`) ayrı bir iş kalemi olarak
  listele, çünkü eşleştirme id ile yapılmalı. Fallback'li kullanımlar sessiz kırılmaz;
  envanterde ayrı listelenir.
- **Katalog okunamadıysa** (editör bağlı değil): öneri yine çıkarılabilir, ama "mevcut
  token id" sütunu boş kalır. Adım 4'ten önce katalog mutlaka yeniden çekilip eşleştirilir.
  Okunamayan katalogla token oluşturulmaz.

## Adım 2 — Envanter (migration modu)

```bash
python3 <bu-skill'in-base-directory'si>/scripts/inventory.py <proje-kökü> > <scratchpad>/token-inventory.txt
```

Script hardcoded renkleri ve font-family / size / weight değerlerini frekans sırasıyla
döker. `var(--x, #hex)` fallback'leri ayrı bir listede gelir ve sayılmaz. Bazı şeyleri
ayırt edemez: TSX'teki COLOR prop default'larını, `#8249` gibi anchor string'lerini ve
fonksiyon argümanı olarak verilen fallback'leri. Listeyi yorumlayarak oku.

## Adım 3 — Token seti tasarımı (skill'in kalbi)

**Önce mimari kararı ver:** color scheme (slot + palet) ya da flat renk. Guide'ın
varsayılanı scheme. Flat renk, tek paletli bir tema ya da hızlı bir migration için makul.
Kararı iki ölçüte göre ver: merchant'ın kod değiştirmeden yeniden renklendirebilmesi ve
partner asset taşınabilirliği. Guide'ın ilgili bölümlerini oku, kararı gerekçesiyle
kataloğun başına koy.

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
  29 farklı font-size varsa token'lar roldür, her boyut token olmaz. Gövde rolü temanın
  **varsayılan metin stili** olarak işaretlenir (Adım 4, `is_default`). Font yığınları
  (`system-ui, …`) token olamaz; en yakın gerçek fontu öner ve bunu karar olarak belirt.
  Font ve ağırlık geçerliliği `update_text_style` açıklamasında ve `list_theme_globals`'ın
  `supportedFontWeights` alanında.
- **Kapsam dışı:** öneride gerekçesiyle ayrı listelenir, token'lanmaz:
  - TSX'teki COLOR prop default'ları (editör değeridir)
  - üçüncü parti marka renkleri (Google/Facebook butonları)
  - `#8249` gibi anchor string'leri
  - CLI scaffold demoları (`ExampleComponent` / `ExampleSection` gibi); bunlar temanın
    dili değildir, kaldırılmaları önerilir
- **UX tabanı:** WCAG AA kontrastını koru. Normal metin 4.5:1, büyük metin (≥24px ya da
  kalın ≥18.66px) 3:1. Kenarlık ve ikon gibi metin dışı UI öğeleri 3:1 (1.4.11); pasif
  kontroller muaftır, ama bilgi taşıyorlarsa ("Tükendi") muafiyet uygulanmaz. Token
  sayısını asgaride tut; az token, tutarlı tema demektir.

**Katalog önerisini tablo halinde sun (isim → değer → nereleri kapsayacağı) ve
KULLANICI ONAYI al. Onaysız `create_theme_global` çağrısı yapılmaz.**

## Adım 4 — Token'ları oluştur

1. **Kapsam:** yalnızca onaylı katalogdaki token'lar açılır; katalogda olmayan hiçbir
   token açılmaz.
2. **Kuralların kaynağı:** her aracın kuralları kendi açıklamasında yazar; önce onu oku.
   `create_theme_global` ile açılır, değişiklik her kind'ın yerinde güncelleme aracıyla
   yapılır. **Delete + recreate yapılmaz**, çünkü id değişir ve kurulmuş bağlar kopar.
3. **Varsayılan metin stili:** Gövde rolü `is_default` olur.
4. **Kayıt:** her sonucun `id` / `cssVar` / `className` değerini birebir not al; bunlar
   Adım 5'in girdisi. Bitince `list_theme_globals`'ı yeniden çekip scratchpad'deki
   dosyanın üzerine yaz.

## Adım 5 — CSS/TSX'i ve editör değerlerini bağla

**Önce `get_framework_guide("theme-globals")` oku.** Aşağıdaki konular orada kodlu
örneklerle anlatılır ve burada tekrarlanmaz:
- scheme slot'larını inherit etme ile palet className'iyle zorlama arasındaki fark
- media query'de `bp(<id>)` kullanımı
- canlı (`cssVar` / `className`) ile snapshot (`resolved`) değer farkı
- partner asset taşınabilirliği

Yöntemi temanın yapısına göre seç:

- **Scheme mimarisi (önerilen):** component CSS'i slot cssVar'larını doğrudan kullanır.
  Palet `className`'i eklenmez; section'ın editörde seçili scheme'i böyle inherit edilir.
- **CSS-ağırlıklı tema:** `global.css` `:root` içinde bir semantik alias katmanı kur
  (`--<prefix>-orman: var(--<id>);`). Her alias'ın katalogda **gerçekten var olan** bir
  token'a çözüldüğünü doğrula. Dangling alias'a bağlanan her `var()` / `color-mix`
  satırını tarayıcı sessizce düşürür.
- **TSX-ağırlıklı / az kullanım:** doğrudan `style={{ color: cssVar }}` ya da typography
  `className`'i.

Guide'da olmayan tuzaklar:

- **Tipografi specificity:** token class'ı `._id` (0,1,0), scoped component CSS'i ise
  `.cc_x .y` (0,2,0) özgüllüğünde, yani component CSS'i token'ı ezer. Token class verilen
  elemanın component CSS'inden `font-family` satırını sil. Form kontrollerine (button,
  input, select, textarea) `font-family: inherit` ver, çünkü bunlar fontu miras almaz.
- **Runtime değişkenleri:** JS ile `documentElement`'e yazılan değişkenlerde her
  kullanımda `var(--x, fallback)` ver; SSR'da ve ilk boyamada değer henüz yoktur.
- **Editör değerleri de token'a bağlanır:**
  - Yerleştirilmiş section'ların COLOR prop'ları `patternValueId` ile renk token'ına
    bağlanır.
  - Theme Setting'ler `bind_global` ile bağlanır.
  - Hazır login/hesap sayfalarının renkleri `update_ready_made_page_prop` ile shared scope
    üzerinden bağlanır.

  Bağlanmayan her hex, palet değiştiğinde eski renkte kalır. Değer şekilleri
  `get_editor_workflow()`'da ve ilgili aracın açıklamasında yazar.

## Adım 6 — Doğrulama akışı (bitiş kontrolü)

1. ```bash
   python3 <bu-skill'in-base-directory'si>/scripts/verify.py <proje-kökü> \
     --tokens <scratchpad>/theme-globals.json --allow <scratchpad>/allow.txt
   ```
   `--tokens` = **güncel** `list_theme_globals` çıktısı (oluşturma sonrası yeniden çek).
   Rapor: (1) fallback'siz dangling `var()` — sıfır olmalı; (2) kalan hardcoded
   renkler — bilinçli kalanlar (prop default'ları, üçüncü parti marka renkleri örn.
   Google/Facebook butonları) allowlist'e `//` yorumuyla gerekçelenerek eklenir,
   gerisi bağlanır; (3) TSX `_<id>` class'larının katalog eşleşmesi; (4) `@media`
   koşulları — koşulda `var()`, katalogda olmayan `bp(<id>)`, `bp()` calc'ında px dışı
   birim. (1) ve (4) sessiz kırılmadır; script bunlarda exit 1 döner, sıfırlanmalı.
2. `npx ikas-component build` temiz geçmeli.
3. **Canlı test:** editörde bir renk token'ının değerini geçici değiştir → sayfada
   anında yansımalı (cssVar canlıdır); bir typography token'ında font değiştir →
   token class'lı elemanlar değişmeli. Değişmeyen eleman = specificity tuzağı
   (Adım 5'e dön). Testten sonra değerleri geri al.

## Sık hatalar

- **Kullanıcı onayı almadan katalog açmak:** mağazada temizlenmesi gereken bir token çöplüğü kalır.
- **Envanterdeki her hex'i token yapmak:** tekilleştirme ve rol çıkarma bu skill'in asıl işidir.
- **Alias'ı hedefini doğrulamadan bağlamak:** dangling `var()` oluşur, tarayıcı satırı sessizce düşürür.
- **Token class'ını ekleyip component CSS'indeki `font-family`'yi bırakmak:** font "değişmiyor" şikâyeti gelir.
- **Hazır login/hesap sayfalarını ve editör COLOR değerlerini bağlamamak:** palet değişir, bu yerler eski renkte kalır.
- **Araç kurallarını hafızadan uygulamak:** her 2.x sürümünde değişiyor, her seferinde araç açıklamasını oku.
