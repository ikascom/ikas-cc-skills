---
name: ikas-prop-normalize
description: Use when normalizing the prop/propGroup structure of an ikas Code Components project — REWRITES ikas.config.json via CLI to apply canonical grouping, Turkish displayNames and minimal editor descriptions. Pass the `audit` argument for a read-only inventory + change list instead. Triggers - prop gruplama, displayName Türkçeleştirme, ikas.config.json prop düzeni, editör sidebar temizliği.
context: fork
---

# ikas Prop/Grup Normalizasyonu

Bir ikas Code Components projesindeki TÜM component'lerin prop/grup yapısını tek geçişte
tutarlı hale getirir: kanonik gruplama + Türkçe adlar + yalnızca gerekli yerde açıklama.
Sonuç: mağaza sahibinin editör sidebar'da gördüğü her etiket Türkçe, öngörülebilir sırada
ve kendini açıklar durumda.

**Temel ilke: envanter gözle değil script'le çıkarılır; her değişiklik CLI ile yapılır.**

## Çağrı modları

| Çağrı | Kapsam |
|---|---|
| (argümansız) | Tam geçiş: Adım 1 → 6. `ikas.config.json` (ve türetilen `types.ts` / `global-types.ts`) değişir. |
| `audit` | Adım 1-4 yalnızca **planlama** olarak: envanteri çıkar, hangi component'te ne değişeceğini listele, DUR. Adım 5 (uygulama) ve Adım 6 atlanır — tek bir `ikas-component config` komutu çalıştırılmaz. |

`audit` modunun çıktısı bir tablodur: `component | prop veya grup | mevcut → önerilen |
gerekçe (hangi kural)`. Sonunda toplam değişiklik sayısını ve "uygulamak için argümansız
çağır" cümlesini yaz.

`audit` modunda `audit.py`'yi çalıştırmak serbest ve zaten gereklidir — okur, değiştirmez.
Yasak olan tek şey `config update-prop` / `update-prop-group` / `add-prop-group` /
`move-prop-group` / `update-enum` çağırmaktır.

## Adım 1 — Deterministik Envanter

```bash
python3 <skill-dizini>/scripts/audit.py ikas.config.json > /tmp/audit-before.txt
```

Script her component'in gruplarını/proplarını döker; İngilizce görünümlü adları `EN?`/`??`
ile, gruplu component içindeki grupsuz propları `!! GRUPSUZ` ile işaretler ve özet sayaç basar.
Component sayısını nota al — iş bitene kadar kapsam bu sayıdır. Bayraklar önceliklendirme
içindir; nihai kararı tüm dökümü okuyarak ver (bayraksız İngilizce ad da kaçabilir).

## Değişmezler (asla dokunma)

- `ikas.config.json`, `types.ts`, `global-types.ts` elle düzenlenmez — yalnızca
  `npx ikas-component config update-prop / update-prop-group / add-prop-group /
  move-prop-group` kullanılır. (`update-prop` şunları destekler: `--displayName`,
  `--description`, `--group`.) Component kimliği için `--component-id` tercih edilir
  (id'ler `config list-components` çıktısında; `--component` isimle exact-match ister).
- Prop `name` ve grup `id` değişmez (kaynak kodu ve mevcut editör değerlerini kırar).
  Yalnızca görünen ad (`displayName`, grup `name`) ve `description` değişir.
- `defaultValue` çevrilmez — o vitrin içeriğidir, editör etiketi değil. Bu görev yalnızca
  editör sidebar'ını kapsar.
- Enum option `value`'ları değişmez; option görünen adları `update-enum` ile çevrilebilir.
  `--options` formatı label→value objesidir ve seti KOMPLE değiştirir: tüm option'ları
  Türkçe label + mevcut value ile yeniden yaz (örn. `'{"Küçük":"s","Büyük":"l"}'`).
- Kaynak dosyalara (`index.tsx`, `styles.css`) dokunulmaz.

## Adım 2 — Kanonik Gruplama Şeması

- **≤4 prop'lu component**: grup açılmaz, düz kalır. Grup açmak overkill.
- **≥5 prop'lu component**: her prop bir grupta olur (grupsuz prop kalmaz).
- Standart gruplar ve sidebar sırası (yalnız ihtiyaç olanlar açılır):

| Sıra | id | Ad | İçerik |
|---|---|---|---|
| 1 | `data` | Veri | PRODUCT, CATEGORY, PRODUCT_LIST, PRODUCT_ATTRIBUTE ve diğer entity bağları (BRAND/BLOG/`*_LIST` türevleri dahil) |
| 2 | `content` | İçerik | görsel, link, slot (COMPONENT/COMPONENT_LIST), başlık |
| 3 | — | (işlevsel) | component'e özgü: Form, Sekmeler, Yolculuk, Durumlar, Banner 1… |
| 4 | `texts` | Metinler | etiket/buton/boş-durum TEXT propları |
| 5 | `colors` | Renkler | YALNIZCA COLOR propları; ad her yerde "Renkler" (Görünüm/Appearance değil) |

- Mevcut grup id'leri ne olursa olsun korunur (`appearance` id'li grup kalır, sadece adı
  "Renkler" yapılır). Yeni grup id'leri İngilizce camelCase, adları Türkçe.
- İç içe grup en fazla 1 seviye ve yalnızca büyük alt-özellikler için (ör. sepet çekmecesi).
- Sidebar'daki grup SIRASI tablodakine uymuyorsa `config move-prop-group` ile taşınır
  (drag-and-drop eşdeğeri) — sıra düzeltmesi için config elle düzenlenmez.

## Adım 3 — Çeviri Kuralları

Çevrilen: prop `displayName`, grup `name`, mevcut İngilizce `description`'lar, enum option adları.

| İngilizce kalıp | Türkçe karşılık |
|---|---|
| … Label | … Etiketi |
| … Text | … Metni |
| … Placeholder | … Alanı Metni |
| … Title | … Başlığı (tek başına: Başlık) |
| … Template | … Şablonu |
| Show … / Enable … | … Göster / … Aktif |
| Empty State | Boş Durum |
| … Button Text | … Butonu Metni |

Çevrilmeyen: URL, SVG, ID, Min/Maks, marka/ürün adları. Aynı grup içinde ortak önek
tekrarlanmaz (grup "Sepet Çekmecesi" ise prop "Başlık", "Sepet Çekmecesi Başlığı" değil).

## Adım 4 — Açıklama (description) Politikası

Açıklama YALNIZCA şu 4 durumda yazılır; tek cümle, ~80 karakteri geçmez:

1. **Şablon token'ı** içeren proplar (`{name}`, `{count}`…) → token'ın neyle değiştiğini söyle:
   `"{date} tahmini teslim tarihiyle değiştirilir."`
2. **Veri bağı** (PRODUCT_ATTRIBUTE vb.) → hangi verinin nereye bağlandığı:
   `"Beden rehberi içeriğini sağlayan ürün özelliği."`
3. **Format/boyut beklentisi** → `"Önerilen en-boy oranı 4:5 (ör. 790x988px)"`,
   `"Virgülle ayırarak yazın."` — format bilgisi displayName'e sıkıştırılmaz, description'a yazılır.
4. **Adından anlaşılmayan davranış** → önce kaynak koddan doğrula, sonra tek cümle:
   `"Boş bırakılırsa logo metni gösterilir."`

Bunların dışındaki hiçbir prop'a açıklama yazılmaz: "Başlık", "Kapat Etiketi", renk
propları, RICH_TEXT içerikler kendini açıklar. Grup açıklaması varsayılan olarak yazılmaz
(grup adı yeterli); yalnızca grubun kapsamı adından çıkarılamıyorsa yazılır.

## Adım 5 — Uygulama

Tüm CLI komutlarını scratchpad'de tek shell script'te topla (`set -e` ile), component
component sıralı yaz, sonra çalıştır. ~100+ komut normaldir; komutlar idempotent olduğu
için script kaldığı yerden tekrar çalıştırılabilir. Örnek satırlar:

```bash
npx ikas-component config update-prop-group --component "Header" --id cartDrawer --name "Sepet Çekmecesi"
npx ikas-component config update-prop --component "Header" --prop cartDrawerTitle --displayName "Başlık"
npx ikas-component config update-prop --component "ProductDetail" --prop sizeGuideAttribute --group data --description "Beden rehberi içeriğini sağlayan ürün özelliği."
npx ikas-component config move-prop-group --component "Header" --id colors --index 4   # grubu sidebar'da sona taşı
```

## Adım 6 — Doğrulama (hepsi zorunlu)

1. `python3 <skill-dizini>/scripts/audit.py ikas.config.json > /tmp/audit-after.txt` —
   component sayısı Adım 1 ile aynı; `EN?` bayrağı ve `!! GRUPSUZ` sıfır (bilinçli
   istisnaları raporda gerekçelendir); dökümü baştan sona tekrar oku.
2. `git diff --stat` — yalnızca `ikas.config.json` + otomatik üretilen `types.ts`/
   `global-types.ts` değişmiş olmalı; hiçbir `index.tsx`/`styles.css` değişmemiş olmalı.
3. `npx ikas-component check --json` → hatasız, sonra `npx ikas-component build` → temiz.

## Sık Hatalar

| Hata | Doğrusu |
|---|---|
| Component'leri gözle sayıp bazılarını atlamak | audit.py'nin TOPLAM satırı = kapsam |
| ikas.config.json'u elle/toplu düzenlemek ("CLI çok yavaş") | Her değişiklik CLI ile; script'e dizip çalıştır |
| defaultValue'ları Türkçeye çevirmek | Vitrin içeriği kapsam dışı |
| Grup id'sini "düzeltmek" (appearance→colors) | id kalır, yalnız görünen ad değişir |
| Her prop'a açıklama yazmak | Yalnız 4 durum; gerisi bilinçli boş |
| displayName'e format bilgisi gömmek | Format → description |
| Doğrulamayı `check`/`build` ile sınırlamak | audit.py'yi tekrar çalıştırıp dökümü okumak şart |
