---
name: ikas-theme-globals-inventory
description: Use when you need a theme's design-token inventory and a proposed global token catalog WITHOUT creating anything — extracting the hardcoded color/typography usage of an existing ikas theme and turning it into a reviewable catalog proposal. Read-only half of ikas-theme-globals. Triggers - token envanteri çıkar, design system dokümanı çıkar, hangi renkler kullanılmış, token katalog önerisi, hardcoded renk taraması.
context: fork
---

# ikas Tema Token Envanteri + Katalog Önerisi (salt-okunur)

Bu skill `ikas-theme-globals`'ın **karar öncesi yarısıdır**. Bir temanın gerçek CSS/TSX
kullanımından token envanterini çıkarır ve onaylanmaya hazır bir katalog önerisi döndürür.

**Hiçbir şey oluşturmaz, değiştirmez, silmez.** `create_theme_global`,
`update_theme_*`, `delete_theme_global` ve CLI'ın `create-color` / `create-text-style` /
`create-color-scheme` komutları bu skill'in kapsamı DIŞINDADIR. Katalog onaylandıktan
sonra uygulama `ikas-theme-globals` Adım 4 ile devam eder.

Tek çıktı: aşağıdaki **Rapor sözleşmesi**ne uyan bir metin. Dosya yazma, prop düzenleme,
CSS bağlama yok.

## Adım 1 — Mevcut katalog

Önce temada zaten NE VAR onu çek — var olan token yeniden önerilmez:

- MCP `list_theme_globals` (gerektirir: `ikas-component dev` çalışıyor + editör bağlı).
- Editör bağlı değilse ("No editor connected") CLI eşdeğeri:
  `npx ikas-component list-theme-globals`.
- İkisi de yoksa bunu raporda **açıkça belirt** ("mevcut katalog okunamadı, öneri
  sıfırdan çıkarıldı") — sessizce varsayma.

Çıktıyı olduğu gibi `/tmp/theme-globals.json`'a kaydet ve rapora id/cssVar kolonuyla
taşı. Eşleştirme her zaman **id** ile yapılır, name ile değil (name'ler unique değildir).

## Adım 2 — Kod envanteri

```bash
python3 <plugin-skills-dizini>/ikas-theme-globals/scripts/inventory.py <proje-kökü> > /tmp/token-inventory.txt
```

(Script aynı plugin içindeki `ikas-theme-globals/scripts/inventory.py` dosyasıdır —
kopyalanmaz, oradan çalıştırılır.)

Hardcoded renkleri ve font-family/size/weight değerlerini frekans sıralı döker;
`var(--...)` üzerinden gelenler zaten token'lıdır, sayılmaz. Bilinen gürültü: TSX'teki
COLOR prop default'ları ve `#8249` gibi anchor/id string'leri de yakalanır — bunlar
token'lanmaz (editör değerleridir), listede **kapsam dışı** olarak işaretle.

`src/` altında hiç component CSS'i yoksa kod envanteri yoktur: bu **kurulum modudur**,
öneri tasarım spec'inden/palet kararından çıkar. Raporda hangi modda olduğunu yaz.

## Adım 3 — Katalog önerisi

Envanteri **temaya özgü** bir katalog önerisine dönüştür. Hazır şablon dayatma; başka
temaların setleri en fazla ilham kaynağıdır.

- **Mimari:** varsayılan öneri **color scheme (slot + palet)** mimarisidir — adlandırılmış
  slot'lar (`Background`, `Metin`, `PrimaryButton/Text`…) + slot→renk paletleri; section
  editörden scheme seçer, component'ler slot cssVar'larını kullanır. Flat renk seti tek
  paletli tema / hızlı migration için hâlâ geçerli. İki fark bilinçli seçilir: scheme slot
  değerleri `var(--<colorId>)` linked reference kabul eder; ve partner design asset
  taşınabilirliğinde slot id'leri store'lar arası taşınır, flat renk id'leri taşınmaz.
  **Mimari kararını gerekçesiyle raporun başına koy.**
- **Adlandırma:** `"Grup/İsim"` — `/` editörde otomatik gruplar (`Marka/Orman`,
  `Nötr/Koyu`, `Vurgu/Bal`). Grup şemasını temanın kendi paletinden türet; tipik iskelet
  Marka (2-4), Nötr (3-5), Vurgu (1-3). İsimler Türkçe ve rol anlatır.
- **Tekilleştirme:** komşu renkleri birleştir (`#6f735f` + `#6e7b5c` → tek token).
  Saydamlık/ton varyantına ayrı token AÇMA — `color-mix(in srgb, var(--token) N%,
  transparent)` ile türetilir; bunu öneride not düş.
- **Tipografi:** gerçek kullanımdan 3-6 **rol** çıkar (Display/Başlık/Gövde/Etiket/UI).
  Her rol bir typography token'ıdır; 29 farklı font-size varsa 29 token değil, rol sayısı
  kadar token olur. Ölçek envanterdeki en sık değerlere oturmalı.
- **UX tabanı:** metin/zemin çiftlerinde WCAG AA (4.5:1) kontrastını kontrol et ve
  ihlalleri raporda ayrı satırda göster. Token sayısını asgaride tut.

## Rapor sözleşmesi

Rapor Türkçedir ve tam olarak şu parçalardan oluşur:

1. **Mod ve kapsam** — migration mı kurulum mu; mevcut katalog okunabildi mi; taranan
   dosya sayısı.
2. **Mimari önerisi** — scheme mi flat mi, tek paragraf gerekçe.
3. **Renk katalogu** — tablo: `Önerilen ad | Değer | Kaynak (envanterdeki hangi hex'ler
   birleşti, kaç kullanım) | Mevcut token id (varsa)`.
4. **Tipografi katalogu** — tablo: `Rol | font-family | size/weight | Nereleri kapsar`.
5. **Kapsam dışı bırakılanlar** — prop default'ları, üçüncü parti marka renkleri
   (Google/Facebook butonları), anchor string'leri; her biri tek satır gerekçeyle.
6. **Kontrast uyarıları** — AA'yı geçmeyen metin/zemin çiftleri (varsa).
7. **Onay sorusu** — "Bu katalog onaylanırsa uygulama `ikas-theme-globals` Adım 4'ten
   devam eder" cümlesiyle bitir.

Rapor, onay verildiğinde `ikas-theme-globals` Adım 4'ün girdisi olacak kadar somut
olmalı: her satır doğrudan bir `create_theme_global` çağrısına çevrilebilmeli.

## Sık hatalar

- `list_theme_globals` çağırmadan öneri çıkarmak → var olan token'ı yeniden önerirsin.
- Envanterdeki her hex'i token yapmak → tekilleştirme bu skill'in asıl işi.
- Her font-size'a token açmak → token roldür, ölçek değil.
- Prop default'larını ve üçüncü parti marka renklerini katalogda saymak.
- Onay beklemeden token oluşturmak → bu skill'in tanımı gereği YASAK; oluşturma
  `ikas-theme-globals`'ın işidir.
