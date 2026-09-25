---
name: ikas-prop-normalize
description: Use when an ikas Code Components project's editor sidebar is inconsistent across components — ungrouped or oddly grouped props, English or mixed displayNames, noisy or missing prop descriptions — and needs a project-wide cleanup (modifies ikas.config.json; the `audit` argument only plans). Triggers - prop gruplama, displayName Türkçeleştirme, ikas.config.json prop düzeni, editör sidebar temizliği.
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
| (argümansız) | Tam geçiş: Adım 1 → 4. `ikas.config.json` (ve türetilen `types.ts` / `global-types.ts`) değişir. |
| `audit` | Adım 1-2 yalnızca **planlama** olarak: envanteri çıkar, hangi component'te ne değişeceğini listele, DUR. Adım 3-4 atlanır — tek bir `ikas-component config` komutu çalıştırılmaz. |

`audit` modunun çıktısı bir tablodur: `component | prop veya grup | mevcut → önerilen |
gerekçe (§6.3'ün hangi kuralı)`. Tablonun sonunda şunlar yer alır:
- Toplam: uygulamada çalışacak **CLI komutu sayısı**.
- Kapsam dışı notlar: §6.1 ihlalleri (tasarımın sabitlediği bir layout/aspect-ratio ENUM'u
  gibi) ve eksik `defaultValue`'lar. Her biri tek satır; normalize bunları değiştirmez,
  builder'a bırakır.
- Kapanış cümlesi: "uygulamak için argümansız çağır".

`audit` modunda `audit.py` çalıştırılır (yalnızca okur); Adım 1'deki `shasum` parmak izi
atlanır. `ikas-component config` komutlarının hiçbiri çalıştırılmaz.

## Adım 1 — Deterministik Envanter

```bash
python3 <bu-skill'in-base-directory'si>/scripts/audit.py ikas.config.json > <scratchpad>/audit-before.txt
# kaynak dosyaların parmak izi — Adım 4'te "hiçbir index.tsx/styles.css değişmedi" kanıtı
# (git repo'larında da çalışır; git'e bağımlı değildir)
find src \( -name '*.tsx' -o -name '*.css' \) -exec shasum {} + | sort -k2 > <scratchpad>/src-before.sha
```

Script her component'in id'sini, gruplarını ve prop'larını döker, özet sayaç basar. İki tür
bayrak üretir:
- **Etiket bayrakları:** `EN?` İngilizce kelime içeren (Türkçe ile karışık olsa bile),
  `??` dili belirlenemeyen etiket.
- **§6.3 yapı bayrakları (`!!`):** grupsuz prop, ≤4 prop'a açılmış grup, grupsuz ≥5 prop,
  3'ten az prop'lu özellik grubu, Renkler dışında kalan COLOR, boş grup, yanlış grup sırası.

Enum option etiketleri de kontrol edilir.
Component sayısını nota al — iş bitene kadar kapsam bu sayıdır. Bayraklar önceliklendirme
içindir; nihai kararı tüm dökümü okuyarak ver (bayraksız İngilizce ad da kaçabilir).

## Değişmezler (asla dokunma)

- `ikas.config.json`, `types.ts`, `global-types.ts` elle düzenlenmez. Kullanılacak komutların
  tam listesi (başka komut gerekmez):

  | Komut | Ne için |
  |---|---|
  | `update-prop --displayName / --description / --group` | Etiket, açıklama, grup. `--group none` prop'u gruptan çıkarır; `--description ""` açıklamayı siler |
  | `add-prop-group` / `update-prop-group` | Grup açma (id kebab-case) / grup adını ya da açıklamasını değiştirme |
  | `remove-prop-group` | Yalnızca taşımalardan sonra **boş** kalan grup ya da düzleştirilen (≤4 prop) component'in grupları |
  | `move-prop-group --index` | Grup sırası (0-tabanlı; `--index` verilmezse sona eklenir) |
  | `update-enum --options` | ENUM option etiketleri |

  Component'i her zaman `--component-id` ile hedefle. Id'ler `audit.py` çıktısında ve
  `config list-components`'te bulunur.
- Prop `name` ve grup `id` değişmez (kaynak kodu ve mevcut editör değerlerini kırar).
  Yalnızca görünen ad (`displayName`, grup `name`) ve `description` değişir.
- `defaultValue` çevrilmez — o vitrin içeriğidir, editör etiketi değil. Bu görev yalnızca
  editör sidebar'ını kapsar.
- Enum option `value`'ları değişmez; option görünen adları `update-enum` ile çevrilebilir.
  `--options` formatı label→value objesidir ve seti KOMPLE değiştirir: tüm option'ları
  Türkçe label + mevcut value ile yeniden yaz (örn. `'{"Küçük":"s","Büyük":"l"}'`).
- Kaynak dosyalara (`index.tsx`, `styles.css`) dokunulmaz.

## Adım 2 — Hedef şema: commerce.md §6.3

Hedef şema bu skill'de değil, **commerce.md §6.3 "Editor sidebar schema"** bölümündedir:
grup sırası, İçerik ve Metinler ayrımı, özellik grubu eşiği, Renkler kuralı, etiket
kalıpları ve açıklama politikası orada. Aynı şemayı `ikas-theme-builder` prop açarken
uygular. Dosya: `<bu-skill'in-base-directory'si>/../ikas-theme-builder/references/commerce.md`.
Yalnızca §6.3'ü oku (`Read` + offset); dosyanın tamamı gerekmez.

Her component için §6.3'ü uygulayarak üç şeye karar ver:
1. **Grup:** hangi prop hangi gruba girecek, hangi gruplar hangi sırada duracak.
2. **Etiket:** her prop'un ve grubun Türkçe `displayName`'i. Mevcut İngilizce description'lar
   ve ENUM option adları da çevrilir.
3. **Açıklama:** §6.3'teki dört durumdan birine uyuyorsa yaz. Uymuyorsa var olan açıklamayı
   bırakma, boşalt (`--description ""`). "Adından anlaşılmayan davranış" açıklamasını
   yazmadan önce davranışı kaynak koddan doğrula.

`audit` modunda Adım 2 planlama olarak biter ve sonuç tablo halinde raporlanır.

## Adım 3 — Uygulama

Tüm CLI komutlarını scratchpad'de tek shell script'te topla (`set -e` ile), component
component sıralı yaz, sonra çalıştır. ~100+ komut normaldir; komutlar idempotent olduğu
için script kaldığı yerden tekrar çalıştırılabilir. Örnek satırlar:

```bash
# component kimliği her zaman --component-id (config list-components); --component
# config'deki adla birebir eşleşir ("Example Component" gibi boşluklu adlar tuzaktır)
H=<header-id>; P=<productdetail-id>
npx ikas-component config update-prop-group --component-id $H --id cartDrawer --name "Sepet Çekmecesi"
npx ikas-component config update-prop --component-id $H --prop cartDrawerTitle --displayName "Başlık"
npx ikas-component config update-prop --component-id $P --prop sizeGuideAttribute --group data --description "Beden rehberi içeriğini sağlayan ürün özelliği."
npx ikas-component config update-prop --component-id $P --prop title --description ""   # gereksiz açıklamayı siler
npx ikas-component config move-prop-group --component-id $H --id colors   # --index verilmezse sona eklenir
npx ikas-component config move-prop-group --component-id $H --id data --index 0   # 0-tabanlı: en başa
```

## Adım 4 — Doğrulama (hepsi zorunlu)

1. `python3 <bu-skill'in-base-directory'si>/scripts/audit.py ikas.config.json > <scratchpad>/audit-after.txt` —
   component sayısı Adım 1 ile aynı; `EN?` ve `!!` bayrakları sıfır (bilinçli
   istisnaları raporda gerekçelendir); dökümü baştan sona tekrar oku.
2. Kaynak dokunulmazlığı —
   `find src \( -name '*.tsx' -o -name '*.css' \) -exec shasum {} + | sort -k2 | diff <scratchpad>/src-before.sha -`
   **boş** olmalı (CLI'ın ürettiği `.ts` dosyaları taramaya dahil değil). Çıktıdaki her
   `index.tsx` / `styles.css` satırı ihlaldir — geri al. Git repo'sunda ek olarak
   `git diff --stat` ile aynı sonucu teyit et.
3. `npx ikas-component check --json` → hatasız, sonra `npx ikas-component build` → temiz.

## Sık Hatalar

| Hata | Doğrusu |
|---|---|
| Component'leri gözle sayıp bazılarını atlamak | audit.py'nin TOPLAM satırı = kapsam |
| ikas.config.json'u elle/toplu düzenlemek ("CLI çok yavaş") | Her değişiklik CLI ile; script'e dizip çalıştır |
| defaultValue'ları Türkçeye çevirmek | Vitrin içeriği kapsam dışı |
| Grup id'sini "düzeltmek" (appearance→colors) | id kalır, yalnız görünen ad değişir |
| Şemayı hafızadan uygulamak | Her seferinde commerce.md §6.3'ü oku — builder da aynı kaynağı kullanır |
| Doğrulamayı `check`/`build` ile sınırlamak | audit.py'yi tekrar çalıştırıp dökümü okumak şart |
| Kaynak dokunulmazlığını `git diff`'e bırakmak | Her projede git yok; Adım 1'deki `shasum` parmak izi esastır |
