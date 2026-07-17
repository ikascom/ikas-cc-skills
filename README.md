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
