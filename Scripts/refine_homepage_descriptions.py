#!/usr/bin/env python3
"""Keep every localized homepage promise accurate, natural, and auditable."""

from __future__ import annotations

import argparse
from html import escape, unescape
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]

# Each description says the same five things: cataloguing, three ways to choose,
# privacy, optional iCloud sync on iPhone/iPad/Mac, and Apple Watch availability.
COPY: dict[str, tuple[str, str]] = {
    "": (
        "Catalog vinyl records and CDs, import Discogs, check duplicates and use Random Pick, Mood Pick or Today’s Pick to choose what to play. Private and ad-free.",
        "Catalog your vinyl and CDs, then choose the next record with customizable Random Pick, Mood Pick, or Today’s Pick. Your collection stays private, can sync through iCloud across iPhone, iPad, and Mac, and is also available on Apple Watch.",
    ),
    "fr": (
        "Choisissez quel vinyle ou CD écouter avec Random Pick, Mood Pick ou le Disque du jour. Gratuit jusqu’à 100 disques, sans publicité ni abonnement.",
        "Cataloguez vos vinyles et vos CD, puis choisissez le prochain disque à écouter avec le tirage aléatoire personnalisable, Mood Pick ou le Disque du jour. Votre collection reste privée, peut se synchroniser via iCloud entre iPhone, iPad et Mac, et vous accompagne aussi sur Apple Watch.",
    ),
    "fr-ca": (
        "Choisissez quel vinyle ou CD écouter avec Random Pick, Mood Pick ou le Disque du jour. Gratuit jusqu’à 100 disques, sans publicité ni abonnement.",
        "Cataloguez vos vinyles et vos CD, puis choisissez le prochain disque à écouter avec le tirage aléatoire personnalisable, Mood Pick ou le Disque du jour. Votre collection reste privée, peut se synchroniser via iCloud entre iPhone, iPad et Mac, et vous accompagne aussi sur Apple Watch.",
    ),
    "en-au": (
        "Catalogue vinyl records and CDs, then choose what to play with Random Pick, Mood Pick or Today’s Pick. Made for collectors in Australia; free for up to 100 records.",
        "Catalogue your vinyl and CDs, then choose the next record with customisable Random Pick, Mood Pick or Today’s Pick. Your collection stays private, can sync through iCloud across iPhone, iPad and Mac, and is also available on Apple Watch.",
    ),
    "en-ca": (
        "Catalogue vinyl records and CDs, then choose what to play with Random Pick, Mood Pick or Today’s Pick. Made for collectors in Canada; free for up to 100 records.",
        "Catalogue your vinyl and CDs, then choose the next record with customizable Random Pick, Mood Pick or Today’s Pick. Your collection stays private, can sync through iCloud across iPhone, iPad and Mac, and is also available on Apple Watch.",
    ),
    "en-gb": (
        "Catalogue vinyl records and CDs, then choose what to play with Random Pick, Mood Pick or Today’s Pick. Made for collectors in the UK; free for up to 100 records.",
        "Catalogue your vinyl and CDs, then choose the next record with customisable Random Pick, Mood Pick or Today’s Pick. Your collection stays private, can sync through iCloud across iPhone, iPad and Mac, and is also available on Apple Watch.",
    ),
    "en-us": (
        "Catalog vinyl records and CDs, import Discogs, check duplicates and use Random Pick, Mood Pick or Today’s Pick to choose what to play. Private and ad-free.",
        "Catalog your vinyl and CDs, then choose the next record with customizable Random Pick, Mood Pick, or Today’s Pick. Your collection stays private, can sync through iCloud across iPhone, iPad, and Mac, and is also available on Apple Watch.",
    ),
    "ar": (
        "نظّم أسطوانات الفينيل والأقراص المدمجة، ثم اختر ما تستمع إليه بالسحب العشوائي وMood Pick وأسطوانة اليوم على أجهزة Apple.",
        "نظّم أسطوانات الفينيل والأقراص المدمجة، ثم اختر الأسطوانة التالية بالسحب العشوائي القابل للتخصيص أو Mood Pick أو أسطوانة اليوم. تظل مجموعتك خاصة، ويمكن مزامنتها عبر iCloud بين iPhone وiPad وMac، كما ترافقك على Apple Watch.",
    ),
    "ca": (
        "Cataloga els teus vinils i CD i tria què escoltar amb la selecció aleatòria, Mood Pick i el Disc del dia a l’iPhone, l’iPad, l’Apple Watch i el Mac.",
        "Cataloga els teus vinils i CD i tria el proper disc amb una selecció aleatòria personalitzable, Mood Pick o el Disc del dia. La col·lecció es manté privada, es pot sincronitzar amb iCloud entre l’iPhone, l’iPad i el Mac, i també t’acompanya a l’Apple Watch.",
    ),
    "da": (
        "Katalogiser dine vinylplader og cd’er, og vælg, hvad du vil høre, med et tilpasningsbart tilfældigt valg, Mood Pick og Dagens plade på dine Apple-enheder.",
        "Katalogiser dine vinylplader og cd’er, og vælg den næste plade med et tilpasningsbart tilfældigt valg, Mood Pick eller Dagens plade. Din samling forbliver privat, kan synkroniseres via iCloud mellem iPhone, iPad og Mac og følger også med på Apple Watch.",
    ),
    "de": (
        "Katalogisiere deine Schallplatten und CDs und finde mit anpassbarer Zufallsauswahl, Mood Pick und Platte des Tages die nächste Platte auf deinen Apple-Geräten.",
        "Katalogisiere deine Schallplatten und CDs und wähle die nächste Platte per anpassbarer Zufallsauswahl, Mood Pick oder Platte des Tages. Deine Sammlung bleibt privat, kann über iCloud zwischen iPhone, iPad und Mac synchronisiert werden und ist auch auf der Apple Watch dabei.",
    ),
    "el": (
        "Καταλογογραφήστε τα βινύλια και τα CD σας και επιλέξτε τι θα ακούσετε με προσαρμόσιμη τυχαία επιλογή, Mood Pick και Δίσκο της ημέρας στις συσκευές Apple.",
        "Καταλογογραφήστε τα βινύλια και τα CD σας και επιλέξτε τον επόμενο δίσκο με προσαρμόσιμη τυχαία επιλογή, Mood Pick ή Δίσκο της ημέρας. Η συλλογή σας παραμένει ιδιωτική, συγχρονίζεται προαιρετικά μέσω iCloud μεταξύ iPhone, iPad και Mac και είναι διαθέσιμη και στο Apple Watch.",
    ),
    "es-es": (
        "Cataloga tus vinilos y CD y elige qué escuchar con la selección aleatoria, Mood Pick y el Disco del día en iPhone, iPad, Apple Watch y Mac.",
        "Cataloga tus vinilos y CD y elige el próximo disco con una selección aleatoria personalizable, Mood Pick o el Disco del día. Tu colección permanece privada, puede sincronizarse mediante iCloud entre iPhone, iPad y Mac y también está disponible en el Apple Watch.",
    ),
    "es-mx": (
        "Cataloga tus vinilos y CD y elige qué escuchar con la selección aleatoria, Mood Pick y el Disco del día en iPhone, iPad, Apple Watch y Mac.",
        "Cataloga tus vinilos y CD y elige el próximo disco con una selección aleatoria personalizable, Mood Pick o el Disco del día. Tu colección permanece privada, puede sincronizarse mediante iCloud entre iPhone, iPad y Mac y también está disponible en el Apple Watch.",
    ),
    "fi": (
        "Luetteloi vinyylisi ja CD-levysi ja valitse kuunneltava levy mukautettavalla satunnaisvalinnalla, Mood Pickillä tai Päivän levy -toiminnolla Apple-laitteillasi.",
        "Luetteloi vinyylisi ja CD-levysi ja valitse seuraava levy mukautettavalla satunnaisvalinnalla, Mood Pickillä tai Päivän levy -toiminnolla. Kokoelmasi pysyy yksityisenä, voi synkronoitua iCloudin kautta iPhonen, iPadin ja Macin välillä ja kulkee mukana myös Apple Watchissa.",
    ),
    "he": (
        "קטלגו את תקליטי הוויניל והתקליטורים ובחרו מה לשמוע בעזרת בחירה אקראית ניתנת להתאמה, Mood Pick ותקליט היום במכשירי Apple.",
        "קטלגו את תקליטי הוויניל והתקליטורים ובחרו את התקליט הבא בעזרת בחירה אקראית ניתנת להתאמה, Mood Pick או תקליט היום. האוסף נשאר פרטי, יכול להסתנכרן דרך iCloud בין iPhone, iPad ו-Mac וזמין גם ב-Apple Watch.",
    ),
    "hi": (
        "अपने विनाइल रिकॉर्ड और CD सूचीबद्ध करें, फिर Apple डिवाइस पर कस्टमाइज़ किए जा सकने वाले Random Pick, Mood Pick और आज का रिकॉर्ड से चुनें कि क्या सुनना है।",
        "अपने विनाइल रिकॉर्ड और CD सूचीबद्ध करें, फिर कस्टमाइज़ किए जा सकने वाले Random Pick, Mood Pick या आज का रिकॉर्ड से अगला रिकॉर्ड चुनें। आपका संग्रह निजी रहता है, iCloud के ज़रिए iPhone, iPad और Mac के बीच सिंक हो सकता है और Apple Watch पर भी उपलब्ध रहता है।",
    ),
    "id": (
        "Katalogkan vinil dan CD, lalu pilih yang ingin diputar dengan pilihan acak, Mood Pick, dan Piringan hari ini di iPhone, iPad, Apple Watch, dan Mac.",
        "Katalogkan piringan vinil dan CD Anda, lalu pilih piringan berikutnya dengan pilihan acak yang dapat disesuaikan, Mood Pick, atau Piringan hari ini. Koleksi tetap pribadi, dapat diselaraskan melalui iCloud antara iPhone, iPad, dan Mac, serta tersedia di Apple Watch.",
    ),
    "it": (
        "Cataloga i tuoi vinili e CD e scegli cosa ascoltare con la selezione casuale, Mood Pick e il Disco del giorno su iPhone, iPad, Apple Watch e Mac.",
        "Cataloga i tuoi vinili e CD e scegli il prossimo disco con una selezione casuale personalizzabile, Mood Pick o il Disco del giorno. La collezione rimane privata, può sincronizzarsi tramite iCloud tra iPhone, iPad e Mac ed è disponibile anche su Apple Watch.",
    ),
    "ja": (
        "レコードやCDを整理し、カスタマイズできるランダム選択、Mood Pick、今日の一枚から、Appleデバイスで次に聴く一枚を選べます。",
        "レコードやCDを整理し、カスタマイズできるランダム選択、Mood Pick、今日の一枚から、次に聴く一枚を選べます。コレクションは非公開のまま、iCloudでiPhone、iPad、Mac間を同期でき、Apple Watchでも利用できます。",
    ),
    "ko": (
        "바이닐과 CD를 정리하고 맞춤 설정 가능한 무작위 선택, Mood Pick, 오늘의 음반으로 Apple 기기에서 다음에 들을 음반을 골라 보세요.",
        "바이닐과 CD를 정리하고 맞춤 설정 가능한 무작위 선택, Mood Pick 또는 오늘의 음반으로 다음 음반을 골라 보세요. 컬렉션은 비공개로 유지되며 iCloud를 통해 iPhone, iPad, Mac 간에 동기화할 수 있고 Apple Watch에서도 이용할 수 있습니다.",
    ),
    "nb": (
        "Katalogiser vinylplatene og CD-ene dine, og velg hva du vil høre med tilpassbart tilfeldig valg, Mood Pick og Dagens plate på Apple-enhetene dine.",
        "Katalogiser vinylplatene og CD-ene dine, og velg neste plate med et tilpassbart tilfeldig valg, Mood Pick eller Dagens plate. Samlingen forblir privat, kan synkroniseres via iCloud mellom iPhone, iPad og Mac og er også tilgjengelig på Apple Watch.",
    ),
    "nl": (
        "Catalogiseer je vinylplaten en cd’s en kies wat je wilt luisteren met een aanpasbare willekeurige keuze, Mood Pick en Plaat van de dag op je Apple-apparaten.",
        "Catalogiseer je vinylplaten en cd’s en kies de volgende plaat met een aanpasbare willekeurige keuze, Mood Pick of Plaat van de dag. Je collectie blijft privé, kan via iCloud worden gesynchroniseerd tussen iPhone, iPad en Mac en is ook beschikbaar op Apple Watch.",
    ),
    "pl": (
        "Skataloguj płyty winylowe i CD, a potem wybierz, czego posłuchać, korzystając z konfigurowalnego wyboru losowego, Mood Pick i Płyty dnia na urządzeniach Apple.",
        "Skataloguj płyty winylowe i CD, a potem wybierz następną płytę za pomocą konfigurowalnego wyboru losowego, Mood Pick lub Płyty dnia. Kolekcja pozostaje prywatna, może synchronizować się przez iCloud między iPhonem, iPadem i Makiem, a także jest dostępna na Apple Watch.",
    ),
    "pt-br": (
        "Catalogue seus vinis e CDs e escolha o que ouvir com a seleção aleatória, o Mood Pick e o Disco do dia no iPhone, iPad, Apple Watch e Mac.",
        "Catalogue seus vinis e CDs e escolha o próximo disco com uma seleção aleatória personalizável, o Mood Pick ou o Disco do dia. Sua coleção permanece privada, pode ser sincronizada pelo iCloud entre iPhone, iPad e Mac e também está disponível no Apple Watch.",
    ),
    "pt-pt": (
        "Catalogue os seus vinis e CD e escolha o que ouvir com a seleção aleatória, o Mood Pick e o Disco do dia no iPhone, iPad, Apple Watch e Mac.",
        "Catalogue os seus vinis e CD e escolha o próximo disco com uma seleção aleatória personalizável, o Mood Pick ou o Disco do dia. A coleção mantém-se privada, pode ser sincronizada pelo iCloud entre iPhone, iPad e Mac e também está disponível no Apple Watch.",
    ),
    "ru": (
        "Каталогизируйте виниловые пластинки и CD и выбирайте, что послушать, с помощью настраиваемого случайного выбора, Mood Pick и Пластинки дня на устройствах Apple.",
        "Каталогизируйте виниловые пластинки и CD и выбирайте следующую пластинку с помощью настраиваемого случайного выбора, Mood Pick или Пластинки дня. Коллекция остаётся конфиденциальной, может синхронизироваться через iCloud между iPhone, iPad и Mac и доступна на Apple Watch.",
    ),
    "sv": (
        "Katalogisera dina vinyl- och cd-skivor och välj vad du vill lyssna på med anpassningsbart slumpval, Mood Pick och Dagens skiva på dina Apple-enheter.",
        "Katalogisera dina vinyl- och cd-skivor och välj nästa skiva med ett anpassningsbart slumpval, Mood Pick eller Dagens skiva. Samlingen förblir privat, kan synkroniseras via iCloud mellan iPhone, iPad och Mac och är även tillgänglig på Apple Watch.",
    ),
    "th": (
        "จัดหมวดหมู่แผ่นเสียงไวนิลและ CD แล้วเลือกแผ่นที่จะฟังด้วยการสุ่มที่ปรับแต่งได้ Mood Pick และแผ่นประจำวันบนอุปกรณ์ Apple",
        "จัดหมวดหมู่แผ่นเสียงไวนิลและ CD แล้วเลือกแผ่นถัดไปด้วยการสุ่มที่ปรับแต่งได้ Mood Pick หรือแผ่นประจำวัน คอลเลกชันของคุณยังคงเป็นส่วนตัว ซิงค์ผ่าน iCloud ระหว่าง iPhone, iPad และ Mac ได้ และใช้งานบน Apple Watch ได้ด้วย",
    ),
    "tr": (
        "Plaklarınızı ve CD’lerinizi kataloglayın; Apple aygıtlarınızda özelleştirilebilir rastgele seçim, Mood Pick ve Günün Plağı ile ne dinleyeceğinizi seçin.",
        "Plaklarınızı ve CD’lerinizi kataloglayın, ardından özelleştirilebilir rastgele seçim, Mood Pick veya Günün Plağı ile sıradaki plağı seçin. Koleksiyonunuz gizli kalır, iCloud ile iPhone, iPad ve Mac arasında eşzamanlanabilir ve Apple Watch’ta da kullanılabilir.",
    ),
    "vi": (
        "Lập danh mục đĩa than và CD, rồi chọn đĩa để nghe bằng lựa chọn ngẫu nhiên có thể tùy chỉnh, Mood Pick và Đĩa nhạc hôm nay trên các thiết bị Apple.",
        "Lập danh mục đĩa than và CD, rồi chọn đĩa tiếp theo bằng lựa chọn ngẫu nhiên có thể tùy chỉnh, Mood Pick hoặc Đĩa nhạc hôm nay. Bộ sưu tập luôn riêng tư, có thể đồng bộ qua iCloud giữa iPhone, iPad và Mac, đồng thời cũng có trên Apple Watch.",
    ),
    "zh-hans": (
        "整理黑胶唱片和 CD，再通过可自定义的随机选择、Mood Pick 和今日唱片，在 Apple 设备上决定下一张听什么。",
        "整理黑胶唱片和 CD，再通过可自定义的随机选择、Mood Pick 或今日唱片决定下一张听什么。你的收藏始终保持私密，可通过 iCloud 在 iPhone、iPad 和 Mac 之间同步，也可在 Apple Watch 上使用。",
    ),
    "zh-hant": (
        "整理黑膠唱片和 CD，再透過可自訂的隨機選擇、Mood Pick 和今日唱片，在 Apple 裝置上決定下一張聽什麼。",
        "整理黑膠唱片和 CD，再透過可自訂的隨機選擇、Mood Pick 或今日唱片決定下一張聽什麼。你的收藏始終保持私密，可透過 iCloud 在 iPhone、iPad 和 Mac 之間同步，也可在 Apple Watch 上使用。",
    ),
}

FORBIDDEN = (
    "fair draws", "real collectors", "tirage équitable", "vrais collectionneurs",
    "sorteos justos", "coleccionistas reales", "sorteios justos",
    "verdadeiros colecionadores", "echte sammler", "richtige sammler",
    "公正な抽選", "本物のコレクター", "공정한 추첨", "실제 수집가",
    "公平抽奖", "真正收藏家", "公平抽獎", "真正收藏家",
)

RANDOM_TERMS: dict[str, tuple[tuple[str, str], ...]] = {
    "ar": (("عمليات السحب العادلة", "الاختيار العشوائي القابل للتخصيص"), ("اختيار عادل", "اختيار عشوائي قابل للتخصيص")),
    "ca": (("Sorteig equilibrat", "Selecció aleatòria personalitzable"),),
    "da": (("fair lodtrækninger", "tilpasningsbare tilfældige valg"), ("Retfærdigt valg", "Tilpasningsbart tilfældigt valg")),
    "de": (("Fairer Zufall", "Anpassbare Zufallsauswahl"),),
    "el": (("δίκαιες κληρώσεις", "προσαρμόσιμη τυχαία επιλογή"), ("Δίκαιη κλήρωση", "Προσαρμόσιμη τυχαία επιλογή")),
    "en-au": (("fair draws", "customisable Random Pick"), ("Fair draw", "Customisable Random Pick")),
    "en-ca": (("fair draws", "customizable Random Pick"), ("Fair draw", "Customizable Random Pick")),
    "en-gb": (("fair draws", "customisable Random Pick"), ("Fair draw", "Customisable Random Pick")),
    "en-us": (("fair draws", "customizable Random Pick"), ("Fair draw", "Customizable Random Pick")),
    "es-es": (("Sorteo equilibrado", "Selección aleatoria personalizable"),),
    "es-mx": (("Sorteo equilibrado", "Selección aleatoria personalizable"),),
    "fi": (("reilut arvonnat", "mukautettavan satunnaisvalinnan"), ("Tasapuolinen arvonta", "Mukautettava satunnaisvalinta")),
    "he": (("הגרלות הוגנת", "בחירה אקראית ניתנת להתאמה"), ("הגרלה הוגנת", "בחירה אקראית ניתנת להתאמה")),
    "hi": (("fair draws", "कस्टमाइज़ किया जा सकने वाला Random Pick"), ("निष्पक्ष चयन", "कस्टमाइज़ किया जा सकने वाला Random Pick")),
    "id": (("undian adil", "pilihan acak yang dapat disesuaikan"), ("pilihan adil", "pilihan acak yang dapat disesuaikan"), ("Pilihan yang adil", "Pilihan acak yang dapat disesuaikan")),
    "it": (("Sorteggio equo", "Selezione casuale personalizzabile"),),
    "ja": (("公平な抽選", "カスタマイズできるランダム選択"),),
    "ko": (("공정한 추첨", "맞춤 설정 가능한 무작위 선택"),),
    "nb": (("rettferdige trekninger", "tilpassbart tilfeldig valg"), ("Rettferdig trekning", "Tilpassbart tilfeldig valg")),
    "nl": (("eerlijke trekkingen", "aanpasbare willekeurige keuzes"), ("Eerlijke trekking", "Aanpasbare willekeurige keuze")),
    "pl": (("Sprawiedliwe losowanie", "Konfigurowalny wybór losowy"),),
    "pt-br": (("sorteios justos", "seleção aleatória personalizável"), ("Sorteio justo", "Seleção aleatória personalizável")),
    "pt-pt": (("sorteios justos", "seleção aleatória personalizável"), ("Sorteio justo", "Seleção aleatória personalizável")),
    "ru": (("справедливым выбором", "настраиваемым случайным выбором"), ("Справедливый выбор", "Настраиваемый случайный выбор")),
    "sv": (("rättvisa dragningar", "anpassningsbart slumpval"), ("Rättvis dragning", "Anpassningsbart slumpval")),
    "tr": (("Adil seçimler", "Özelleştirilebilir rastgele seçim"), ("adil seçimler", "özelleştirilebilir rastgele seçim"), ("Adil seçim", "Özelleştirilebilir rastgele seçim")),
    "zh-hans": (("公平抽奖", "可自定义随机选择"), ("公平抽取", "可自定义随机选择")),
    "zh-hant": (("公平抽獎", "可自訂隨機選擇"), ("公平抽取", "可自訂隨機選擇")),
}

HOME_RANDOM_BODY: dict[str, str] = {
    "ar": "اختر بين سحب عشوائي بحت أو وضع موزون اختياري يفضّل الأسطوانات الأقل تشغيلًا، ثم طبّق الفلاتر والاستثناءات.",
    "ca": "Tria entre una selecció purament aleatòria o un mode ponderat opcional que afavoreix els discos menys escoltats, i aplica-hi filtres i exclusions.",
    "da": "Vælg mellem et helt tilfældigt valg eller en valgfri vægtning af mindre spillede plader, og anvend derefter filtre og udelukkelser.",
    "de": "Wähle zwischen reiner Zufallsauswahl und einem optionalen gewichteten Modus für seltener gespielte Platten und wende anschließend Filter und Ausschlüsse an.",
    "el": "Επιλέξτε ανάμεσα σε εντελώς τυχαία επιλογή ή σε προαιρετική στάθμιση των λιγότερο παιγμένων δίσκων και εφαρμόστε φίλτρα και εξαιρέσεις.",
    "en-au": "Choose a purely random pick or optionally favour less-played records, then apply filters and exclusions before picking or undoing.",
    "en-ca": "Choose a purely random pick or optionally favor less-played records, then apply filters and exclusions before picking or undoing.",
    "en-gb": "Choose a purely random pick or optionally favour less-played records, then apply filters and exclusions before picking or undoing.",
    "en-us": "Choose a purely random pick or optionally favor less-played records, then apply filters and exclusions before picking or undoing.",
    "es-es": "Elige una selección totalmente aleatoria o un modo ponderado opcional que favorece los discos menos escuchados y aplica después filtros y exclusiones.",
    "es-mx": "Elige una selección totalmente aleatoria o un modo ponderado opcional que favorece los discos menos escuchados y aplica después filtros y exclusiones.",
    "fi": "Valitse täysin satunnainen valinta tai valinnainen painotus vähemmän soitetuille levyille ja käytä sitten suodattimia ja poissulkuja.",
    "he": "בחרו בין בחירה אקראית לחלוטין לבין מצב משוקלל אופציונלי שמעדיף תקליטים שהושמעו פחות, ולאחר מכן החילו מסננים והחרגות.",
    "hi": "पूरी तरह रैंडम चयन या कम सुने गए रिकॉर्ड को प्राथमिकता देने वाला वैकल्पिक वेटेड मोड चुनें, फिर फ़िल्टर और बहिष्करण लागू करें।",
    "id": "Pilih pilihan yang sepenuhnya acak atau mode berbobot opsional untuk piringan yang jarang diputar, lalu terapkan filter dan pengecualian.",
    "it": "Scegli una selezione puramente casuale oppure una modalità ponderata facoltativa che favorisca i dischi meno ascoltati, quindi applica filtri ed esclusioni.",
    "ja": "完全なランダム選択か、再生回数の少ないレコードを優先する任意の重み付けモードを選び、フィルターと除外条件を適用できます。",
    "ko": "완전한 무작위 선택 또는 재생 횟수가 적은 음반을 우선하는 선택적 가중 모드를 고른 뒤 필터와 제외 조건을 적용할 수 있습니다.",
    "nb": "Velg mellom et helt tilfeldig valg eller en valgfri vekting av mindre spilte plater, og bruk deretter filtre og utelukkelser.",
    "nl": "Kies een volledig willekeurige selectie of een optionele gewogen modus voor minder gedraaide platen en pas daarna filters en uitsluitingen toe.",
    "pl": "Wybierz całkowicie losowy wybór albo opcjonalny tryb ważony dla rzadziej słuchanych płyt, a następnie zastosuj filtry i wykluczenia.",
    "pt-br": "Escolha uma seleção totalmente aleatória ou um modo ponderado opcional que prioriza discos menos tocados e aplique filtros e exclusões.",
    "pt-pt": "Escolha uma seleção totalmente aleatória ou um modo ponderado opcional que favorece discos menos ouvidos e aplique filtros e exclusões.",
    "ru": "Выберите полностью случайный выбор или дополнительный взвешенный режим для редко прослушиваемых пластинок, а затем примените фильтры и исключения.",
    "sv": "Välj ett helt slumpmässigt val eller en valfri viktning av mindre spelade skivor och använd sedan filter och undantag.",
    "tr": "Tamamen rastgele seçim ile daha az çalınan plakları öne çıkaran isteğe bağlı ağırlıklı mod arasında seçim yapın; ardından filtreleri ve hariç tutmaları uygulayın.",
    "zh-hans": "可选择完全随机，也可选择优先考虑较少播放唱片的可选加权模式，然后应用筛选条件和排除项。",
    "zh-hant": "可選擇完全隨機，也可選擇優先考慮較少播放唱片的選用加權模式，然後套用篩選條件和排除項目。",
}


def page_for(locale: str) -> Path:
    return ROOT / locale / "index.html" if locale else ROOT / "index.html"


def visible_deck(text: str) -> str:
    match = re.search(r'<p class="deck">(.*?)</p>', text, flags=re.DOTALL)
    if not match:
        raise AssertionError("localized homepage has no normalized deck")
    return unescape(re.sub(r"<[^>]+>", "", match.group(1)))


def update(locale: str, meta: str, deck: str) -> None:
    path = page_for(locale)
    text = path.read_text(encoding="utf-8")
    encoded_meta = escape(meta, quote=True)
    for attr, name in (
        ("name", "description"),
        ("property", "og:description"),
        ("name", "twitter:description"),
    ):
        text = re.sub(
            rf'(<meta {attr}="{name}" content=")[^"]*(">)',
            rf"\g<1>{encoded_meta}\g<2>",
            text,
            count=1,
        )
    encoded_deck = escape(deck, quote=False)
    if '<p class="deck">' in text:
        text = re.sub(
            r'<p class="deck">.*?</p>',
            f'<p class="deck">{encoded_deck}</p>',
            text,
            count=1,
            flags=re.DOTALL,
        )
    else:
        text = re.sub(
            r'(<section class="hero"[^>]*><div class="hero-copy">.*?</h2>)<p>.*?</p>',
            rf'\g<1><p class="deck">{encoded_deck}</p>',
            text,
            count=1,
            flags=re.DOTALL,
        )
    path.write_text(text, encoding="utf-8")


def update_random_pick_copy() -> None:
    for locale, replacements in RANDOM_TERMS.items():
        for path in (ROOT / locale).rglob("*.html"):
            text = path.read_text(encoding="utf-8")
            for old, new in replacements:
                text = text.replace(old, new)
            path.write_text(text, encoding="utf-8")
        home = page_for(locale)
        text = home.read_text(encoding="utf-8")
        heading = RANDOM_TERMS[locale][-1][1]
        body = escape(HOME_RANDOM_BODY[locale], quote=False)
        text = re.sub(
            rf'(<article class="card"><h3>{re.escape(heading)}</h3><p>).*?(</p></article>)',
            rf"\g<1>{body}\g<2>",
            text,
            count=1,
            flags=re.DOTALL,
        )
        home.write_text(text, encoding="utf-8")


def audit() -> None:
    assert len(COPY) == 33, f"expected 33 localized homes, found {len(COPY)}"
    for locale, (meta, deck) in COPY.items():
        text = page_for(locale).read_text(encoding="utf-8")
        found_meta = re.search(
            r'<meta name="description" content="([^"]+)">', text
        )
        found_value = unescape(found_meta.group(1)) if found_meta else ""
        assert found_meta and (found_value == meta or found_value.startswith(meta + " · ")), locale or "root"
        assert visible_deck(text) == deck, locale or "root"
        lowered = unescape(text).casefold()
        for phrase in FORBIDDEN:
            assert phrase.casefold() not in lowered, (locale or "root", phrase)
        for required in ("Mood Pick", "iCloud", "iPhone", "iPad", "Apple Watch"):
            assert required in deck, (locale or "root", required)
        assert "Mac" in deck or "Makiem" in deck, locale or "root"
    for locale, replacements in RANDOM_TERMS.items():
        combined = "\n".join(
            unescape(path.read_text(encoding="utf-8"))
            for path in (ROOT / locale).rglob("*.html")
        )
        for old, _ in replacements:
            assert old.casefold() not in combined.casefold(), (locale, old)
        assert HOME_RANDOM_BODY[locale] in combined, locale
    print("OK: 33 localized homepage descriptions preserve the approved meaning.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        for locale, pair in COPY.items():
            update(locale, *pair)
        update_random_pick_copy()
    audit()


if __name__ == "__main__":
    main()
