---
name: ikas-theme-globals-inventory
description: Use when you need an ikas theme's design-token inventory and a proposed global token catalog WITHOUT creating anything — before a token migration, for a design-system write-up, or to see which hardcoded colors and fonts a theme uses. Read-only half of ikas-theme-globals. Triggers - token envanteri çıkar, design system dokümanı çıkar, hangi renkler kullanılmış, token katalog önerisi, hardcoded renk taraması.
context: fork
---

# ikas Tema Token Envanteri (salt-okunur)

`ikas-theme-globals`'ın **Adım 1-3'ünü** izole olarak koşturur ve onaya hazır bir katalog
raporu döndürür. **Hiçbir şey oluşturmaz, değiştirmez, silmez**: `create_*`, `update_*`,
`delete_*` MCP araçları ve CLI komutları bu skill'in kapsamı dışındadır. Dosya yazılmaz,
CSS bağlanmaz.

Kurallar bu skill'de tekrarlanmaz; tek kaynak kardeş skill'dir:
`<bu-skill'in-base-directory'si>/../ikas-theme-globals/SKILL.md`. İşe başlamadan önce
dosyanın **Ön koşullar**, **Adım 1**, **Adım 2** ve **Adım 3** bölümlerini `Read` ile oku.

## Akış

1. **Mevcut katalog:** `list_theme_globals`. Editör bağlı değilse CLI
   `npx ikas-component list-theme-globals` kullanılır. İkisi de olmazsa raporda "mevcut
   katalog okunamadı" diye açıkça belirt. Çıktı scratchpad'e `theme-globals.json` olarak
   kaydedilir.
2. **Mod:** Adım 1'e göre migration mı kurulum mu olduğunu belirle.
3. **Envanter:** migration modunda script'i kardeş skill'in dizininden çalıştır, kopyalama:
   ```bash
   python3 <bu-skill'in-base-directory'si>/../ikas-theme-globals/scripts/inventory.py <proje-kökü> > <scratchpad>/token-inventory.txt
   ```
4. **Katalog önerisi:** globals Adım 3'ün kurallarını uygula (mimari, adlandırma,
   tekilleştirme, tipografi rolleri, kapsam dışı, kontrast). Adım 3'ün sonundaki onay
   isteme işi burada rapora dönüşür, çünkü onayı ana konuşma alır.

## Rapor sözleşmesi

Rapor Türkçedir ve şu parçalardan oluşur, bu sırayla:

1. **Mod ve kapsam:** kurulum, migration ya da kısmi migration; mevcut katalog okunabildi
   mi; taranan dosya sayısı (`inventory.py` ilk satırda basar); hardcoded ve fallback
   kullanım sayıları.
2. **Mimari önerisi:** scheme ya da flat, tek paragraf gerekçe.
3. **Renk katalogu:** `Önerilen ad | Tür (slot / flat renk) | Değer | Kaynak (birleşen hex'ler,
   kullanım sayısı) | Mevcut token id (varsa; katalog okunamadıysa "okunamadı")`.
4. **Tipografi katalogu:** `Rol | font-family | size/weight | Nereleri kapsar | Varsayılan mı`.
5. **Kapsam dışı bırakılanlar:** her biri tek satır gerekçeyle.
6. **Kontrast uyarıları:** WCAG AA'yı geçmeyen metin/zemin çiftleri (varsa).
7. **Onay sorusu:** "Bu katalog onaylanırsa uygulama `ikas-theme-globals` Adım 4'ten devam
   eder" cümlesiyle biter.

Her satır doğrudan bir `create_theme_global` çağrısına çevrilebilecek kadar somut olmalı.
