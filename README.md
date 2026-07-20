# ikas-cc-skills

ikas Code Components projelerinde kullanılmak üzere hazırlanmış Claude Code skill kütüphanesi.
Skill'ler tek bir plugin (`ikas-code-components`) altında toplanır ve Claude Code'un plugin
marketplace özelliğiyle dağıtılır.

## Kurulum

```
/plugin marketplace add ikascom/ikas-cc-skills
/plugin install ikas-code-components@ikas-cc-skills
```

Kurulumdan sonra skill'ler otomatik olarak kullanılabilir olur; Claude ilgili bir görevle
karşılaştığında skill'i kendisi devreye alır, `/ikas-prop-audit` gibi komutla elle de
çağrılabilir.

Güncelleme için:

```
/plugin marketplace update ikas-cc-skills
```

## Skill Kataloğu

| Skill | Ne zaman kullanılır |
|---|---|
| [ikas-prop-audit](#ikas-prop-audit) | Bir projedeki tüm component'lerin prop/grup yapısını denetleyip toparlamak |
| [ikas-theme-globals](#ikas-theme-globals) | Tema global renk/tipografi/color-scheme token setini kurmak, CSS/TSX'i token'lara bağlamak |
| [ikas-theme-builder](#ikas-theme-builder) | Section/sub-component inşa etmek, prop eklemek, sayfa kompoze etmek, chrome surface kurmak |
| [ikas-theme-audit](#ikas-theme-audit) | Mevcut bir temanın alışveriş deneyimini kural setine göre denetlemek (kod değiştirmez) |

---

### ikas-prop-audit

Bir ikas Code Components projesindeki **tüm** component'lerin prop/grup yapısını tek geçişte
tutarlı hale getirir: kanonik gruplama, Türkçe görünen adlar ve yalnızca gerekli yerde
editör açıklaması. Hedef, mağaza sahibinin editör sidebar'da gördüğü her etiketin Türkçe,
öngörülebilir sırada ve kendini açıklar durumda olması.

**Tetikleyiciler:** prop gruplama, displayName Türkçeleştirme, `ikas.config.json` prop
düzeni, editör sidebar temizliği.

**Nasıl çalışır:**

1. **Envanter** — `scripts/audit.py` ile tüm component'lerin prop/grup dökümü çıkarılır;
   İngilizce görünümlü adlar ve grupsuz proplar bayraklanır. Component sayısı işin kapsamını
   belirler.
2. **Kanonik gruplama** — ≤4 prop'lu component düz kalır; ≥5 prop'lu component'te her prop
   bir gruba girer. Standart grup sırası: Veri → İçerik → (işlevsel) → Metinler → Renkler.
3. **Çeviri** — prop `displayName`, grup adı, mevcut açıklamalar ve enum option adları
   sabit kalıp tablosuna göre Türkçeleştirilir. URL/SVG/ID gibi teknik adlar çevrilmez.
4. **Açıklama politikası** — description yalnızca 4 durumda yazılır: şablon token'ı, veri
   bağı, format/boyut beklentisi, adından anlaşılmayan davranış. Gerisi bilinçli boş.
5. **Uygulama** — her değişiklik `npx ikas-component config update-prop /
   update-prop-group / add-prop-group` CLI komutlarıyla yapılır; config dosyaları asla elle
   düzenlenmez. Komutlar idempotent tek bir shell script'te toplanır.
6. **Doğrulama** — audit.py tekrar çalıştırılır (bayraklar sıfırlanmalı), `git diff --stat`
   yalnızca config + üretilen tip dosyalarını göstermeli, `npx ikas-component check` ve
   `build` temiz geçmeli.

**Değişmezler:** prop `name` ve grup `id` asla değişmez; `defaultValue` (vitrin içeriği)
çevrilmez; kaynak dosyalara (`index.tsx`, `styles.css`) dokunulmaz.

**İçerik:**

```
skills/ikas-prop-audit/
├── SKILL.md          # iş akışı, kurallar, çeviri tablosu, sık hatalar
└── scripts/audit.py  # deterministik prop/grup envanter script'i
```

---

### ikas-theme-globals

Bir ikas Code Components temasında **global token setini** (renk, tipografi, color
scheme; gerekirse breakpoint/keyframe) kurar, CSS/TSX'i token'lara bağlar ve doğrular.
İki modu var: mevcut CSS'ten envanter çıkarıp token'a taşıyan **migration modu** ve
sıfırdan tema için tasarım spec'inden ilerleyen **kurulum modu**. Token seti temanın
kendi CSS diline göre tasarlanır; hazır katalog şablonu dayatılmaz.

**Tetikleyiciler:** tema global renk/tipografi token'ları, `create_theme_global`, design
token migration, cssVar/className bağlama, hardcoded renk temizliği.

**Nasıl çalışır:**

1. **Ön koşul** — `ikas-component dev` çalışır ve editör tarayıcıda bağlı olmalı; ilk iş
   `list_theme_globals` ile mevcut katalogu çekmek (duplike token açılmaz, eşleşme her
   zaman `id` ile yapılır).
2. **Envanter** — migration modunda `scripts/inventory.py` hardcoded renk ve
   font-family/size/weight değerlerini frekans sıralı döker.
3. **Token seti tasarımı** — önce mimari kararı (önerilen: color scheme slot+palet
   mimarisi; alternatif: flat renk token'ları), sonra envanterden temaya özgü katalog
   önerisi: `"Grup/İsim"` adlandırması, yakın renklerin tekilleştirilmesi, 3-6
   tipografi rolü, WCAG AA kontrast kontrolü. **Katalog tablo halinde sunulur ve
   kullanıcı onayı alınmadan hiçbir token oluşturulmaz** — token oluşturmak
   mağaza-kalıcı bir yan etkidir.
4. **Oluşturma** — onaylı katalog `create_theme_global` ile açılır (kind:
   globalVariable/color/typography/breakpoint/keyframe/colorScheme). Kritik tuzaklar
   SKILL.md'de tablolu: dönen id/cssVar/className birebir kopyalanır, color token alias
   alamaz (scheme slot'ları `var(--<colorId>)` linked referans alabilir), değişiklik
   `update_theme_color` / `update_theme_color_scheme` ile yapılır (delete+recreate yasak).
5. **Bağlama** — CSS-ağırlıklı temada `global.css`'te semantik alias katmanı,
   TSX-ağırlıklıda doğrudan `cssVar`/`className`. Tipografi specificity tuzağı ve
   `:root` kopyalama tuzağı için özel kurallar içerir.
6. **Doğrulama** — `scripts/verify.py` dangling `var()`, kalan hardcoded renkler
   (allowlist'le gerekçeli istisna) ve TSX class-katalog eşleşmesini raporlar; `build`
   temiz geçmeli; editörde canlı token değişikliği testi yapılır.

**Değişmezler:** onaysız `create_theme_global` çağrısı yapılmaz; token eşleştirme name
ile değil `id` ile; cssVar asla elle türetilmez; var olan token silinip yeniden açılmaz.

**İçerik:**

```
skills/ikas-theme-globals/
├── SKILL.md               # iş akışı, tuzak tabloları, bağlama kuralları
└── scripts/
    ├── inventory.py       # hardcoded renk/tipografi envanteri (frekans sıralı)
    └── verify.py          # dangling var() + hardcoded kalıntı + class eşleşme raporu
```

---

### ikas-theme-builder

Bir ikas storefront temasında **section ve sub-component inşa etme** iş akışı: yeni
section scaffold etme, prop ekleme/çıkarma, sayfa kompoze etme (anasayfa, PLP, PDP,
sepet…), chrome surface kurma (drawer/modal/toast) ve section'ları kural setine göre
gözden geçirme. `ikas-theme-audit` ile kardeş skill'dir — audit tespit eder, builder
inşa eder ve düzeltir.

**Tetikleyiciler:** "add a new section", "create the X section", "add a prop", "compose
the homepage / PDP / cart page", "add a drawer / modal / toast", "review this section
against the ruleset".

**Dört bilgi kaynağı ve sahiplik alanları:**

| Kaynak | Neyin sahibi |
|---|---|
| `references/commerce.md` (skill ile gelir) | UX & dönüşüm kural seti — her yüzeyin ne YAPMASI gerektiği |
| Design source (Figma/Stitch/design.md/kullanıcı) | Görsel her şey — layout, renk, tipografi, motion |
| Proje `CLAUDE.md` | Framework kuralları, CLI komut şekilleri, otomatik üretilen dosyalar |
| `ikas-code-components` MCP | Canlı framework kataloğu — template'ler, prop tipleri, fonksiyon dokümanları |

**Temel disiplinler:** kod yazmadan önce ilgili commerce.md bölümü okunur; framework
gerçekleri hafızadan değil MCP'den sorgulanır; **görsel karar asla uydurulmaz** — design
source'ta yoksa tasarım otoritesine (kullanıcıya) sorulur. MCP yanıtlarındaki framework
gerçekleri (must) ile referans tema alışkanlıkları (preference) ayrıştırılır.

**İş akışları:** yeni section inşası (10 adım: §13 katalog → §5 kontrat → design input →
ENUM → MCP template → prop yüzeyi → CLI scaffold → API lookup → implement → pre-flight),
prop ekleme, sayfa kompozisyonu (MCP canlı editör araçlarıyla yerleştirme + içerik
doldurma — `get_editor_workflow` → `add_sections_to_page` / `update_page_sections`),
chrome surface kurulumu, section review. Her görev tipinin "önce ne okunur → hangi
design girdisi → hangi komut" karar matrisi SKILL.md'de.

**Bitiş kontrolü:** commerce.md §15 build checklist + design fidelity +
`npx ikas-component check --json` + `build` temiz.

**İçerik:**

```
skills/ikas-theme-builder/
├── SKILL.md                    # karar matrisi, görev iş akışları, pre-flight kontroller
└── references/commerce.md      # tasarımdan bağımsız e-ticaret kural seti (~940 satır)
```

---

### ikas-theme-audit

Mevcut bir ikas temasının **alışveriş deneyimi denetimi** — kod incelemesi değil.
Ölçüt, skill ile gelen `references/commerce.md` kural seti; her bulgu ya ihlal ettiği
bölümü zikreder (§7.1, §13.B…) ya da açıkça "kontrat dışı" etiketlenir. Denetim
**hiçbir şeyi değiştirmez**; düzeltmeler `ikas-theme-builder`'a yönlendirilir.

**Tetikleyiciler:** "temayı denetle", "eksik section var mı", "akışlar doğru mu",
"pre-launch review", "bu tema yayına hazır mı".

**Bulgu sınıflandırması:**

| Sınıf | Anlamı |
|---|---|
| İhlal (blocker) | commerce.md kontratını kırar (ör. sessiz sepet hatası) |
| Boşluk (gap) | Zorunlu bir surface/chrome fonksiyonu tamamen yok |
| Tema tercihi | Kural setinin izin verdiği tasarım sapması — engel değil |
| Kontrat dışı öneri | Faydalı olabilir ama hiçbir kural gerektirmiyor |

**Beş geçişli denetim prosedürü:** (1) surface envanteri — §4.1 sayfa + §4.2 chrome
yüzeyleri, (2) shopper journey yürüyüşü — keşiften satın almaya, kurtarma ve güven
dahil 7 aşama, (3) section bazında §13 zorunlu özellik kontrolü, (4) §14 anti-pattern
taraması, (5) merchant gerçeklik kontrolü — her metin/görsel düzenlenebilir mi,
sıfır-düzenleme kurulum yayınlanabilir mi. Sabit kapsam sayesinde aynı temanın iki
denetimi aynı sonucu verir.

**Rapor sözleşmesi:** Türkçe; karar cümlesi → ihlaller (kanıt + dayanak tablosu) →
boşluklar → tema tercihleri → kontrat dışı öneriler (maks 5) → öncelikli aksiyon
listesi. Kapsam argümanları: tam denetim, `surface <name>`, `section <Name>`, `quick`.

**İçerik:**

```
skills/ikas-theme-audit/
├── SKILL.md                    # severity taksonomisi, 5 geçişli prosedür, rapor sözleşmesi
└── references/commerce.md      # ölçüt kural seti (builder ile aynı dosya)
```

> **Not:** `commerce.md` iki skill'de bilinçli olarak duplike edilmiştir — her skill
> kendi başına taşınabilir. Kural setinde değişiklik yapılırsa **iki kopya birden**
> güncellenmelidir.
