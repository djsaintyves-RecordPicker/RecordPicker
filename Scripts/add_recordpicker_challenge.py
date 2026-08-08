#!/usr/bin/env python3
"""Add the 2026 #RecordPickerChallenge campaign to the localized website."""

from __future__ import annotations

from html import escape
from pathlib import Path
import re
import shutil
import sys


ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
SOURCE = Path("/Users/yvesdurand/Library/Mobile Documents/com~apple~CloudDocs/RecordPicker/Record Picker Instagram 3 Picks Challenge en-GB")

# short, title, lead, step 1, step 2, step 3, CTA, legal note
EN = (
    "70 Pro codes · 14 days · starts 9 August",
    "Three picks. One favourite. Win Pro for life.",
    "Take the 3 Picks Challenge from 9 to 22 August 2026 and put your own record collection in play.",
    "Add at least five records",
    "Make one Random Pick, one Today’s Pick and one Mood Pick",
    "Share your favourite on Instagram with #RecordPickerChallenge",
    "Follow the challenge on Instagram",
    "No purchase, App Store rating or review is required. Eligibility and selection details are published on Instagram.",
)

EN_US = (
    "70 Pro codes · 14 days · starts August 9",
    "Three picks. One favorite. Win Pro for life.",
    "Take the 3 Picks Challenge from August 9 to 22, 2026, and put your own record collection in play.",
    "Add at least five records",
    "Make one Random Pick, one Today’s Pick and one Mood Pick",
    "Share your favorite on Instagram with #RecordPickerChallenge",
    "Follow the challenge on Instagram",
    "No purchase, App Store rating or review is required. Eligibility and selection details are published on Instagram.",
)

COPY = {
    "ar": ("70 رمز Pro · 14 يومًا · يبدأ 9 أغسطس", "ثلاثة اختيارات. اختيار واحد مفضل. اربح Pro مدى الحياة.", "شارك في تحدي 3 Picks من 9 إلى 22 أغسطس 2026 واجعل مجموعتك جزءًا من اللعبة.", "أضف خمسة تسجيلات على الأقل", "استخدم Random Pick وToday’s Pick وMood Pick مرة واحدة", "شارك اختيارك المفضل على Instagram مع #RecordPickerChallenge", "تابع التحدي على Instagram", "لا يلزم شراء أو تقييم أو مراجعة على App Store. تُنشر شروط الأهلية والاختيار على Instagram."),
    "ca": ("70 codis Pro · 14 dies · comença el 9 d’agost", "Tres tries. Una preferida. Guanya Pro per sempre.", "Participa al 3 Picks Challenge del 9 al 22 d’agost de 2026 i posa en joc la teva col·lecció.", "Afegeix almenys cinc discos", "Fes un Random Pick, un Today’s Pick i un Mood Pick", "Comparteix el teu preferit a Instagram amb #RecordPickerChallenge", "Segueix el repte a Instagram", "No cal comprar, puntuar ni escriure cap ressenya a l’App Store. Els detalls d’elegibilitat i selecció es publiquen a Instagram."),
    "da": ("70 Pro-koder · 14 dage · starter 9. august", "Tre valg. Én favorit. Vind Pro for altid.", "Deltag i 3 Picks Challenge fra 9. til 22. august 2026, og sæt din egen pladesamling i spil.", "Tilføj mindst fem plader", "Lav ét Random Pick, ét Today’s Pick og ét Mood Pick", "Del din favorit på Instagram med #RecordPickerChallenge", "Følg udfordringen på Instagram", "Køb, App Store-bedømmelse eller anmeldelse er ikke påkrævet. Regler om deltagelse og udvælgelse offentliggøres på Instagram."),
    "de": ("70 Pro-Codes · 14 Tage · Start am 9. August", "Drei Picks. Ein Favorit. Pro für immer gewinnen.", "Mach vom 9. bis 22. August 2026 bei der 3 Picks Challenge mit und bring deine eigene Plattensammlung ins Spiel.", "Füge mindestens fünf Platten hinzu", "Nutze je einmal Random Pick, Today’s Pick und Mood Pick", "Teile deinen Favoriten auf Instagram mit #RecordPickerChallenge", "Challenge auf Instagram verfolgen", "Kein Kauf und keine App-Store-Bewertung oder Rezension erforderlich. Teilnahme- und Auswahlbedingungen werden auf Instagram veröffentlicht."),
    "el": ("70 κωδικοί Pro · 14 ημέρες · έναρξη 9 Αυγούστου", "Τρεις επιλογές. Μία αγαπημένη. Κέρδισε Pro για πάντα.", "Πάρε μέρος στο 3 Picks Challenge από 9 έως 22 Αυγούστου 2026 με τη δική σου συλλογή δίσκων.", "Πρόσθεσε τουλάχιστον πέντε δίσκους", "Κάνε ένα Random Pick, ένα Today’s Pick και ένα Mood Pick", "Μοιράσου την αγαπημένη επιλογή σου στο Instagram με #RecordPickerChallenge", "Ακολούθησε το challenge στο Instagram", "Δεν απαιτείται αγορά, βαθμολογία ή κριτική στο App Store. Οι όροι συμμετοχής και επιλογής δημοσιεύονται στο Instagram."),
    "en-au": EN, "en-ca": EN, "en-gb": EN, "en-us": EN_US,
    "es-es": ("70 códigos Pro · 14 días · empieza el 9 de agosto", "Tres selecciones. Una favorita. Gana Pro para siempre.", "Participa en el 3 Picks Challenge del 9 al 22 de agosto de 2026 y pon en juego tu propia colección.", "Añade al menos cinco discos", "Haz un Random Pick, un Today’s Pick y un Mood Pick", "Comparte tu favorito en Instagram con #RecordPickerChallenge", "Sigue el reto en Instagram", "No se requiere compra, valoración ni reseña en el App Store. Los detalles de participación y selección se publican en Instagram."),
    "es-mx": ("70 códigos Pro · 14 días · comienza el 9 de agosto", "Tres selecciones. Una favorita. Gana Pro para siempre.", "Participa en el 3 Picks Challenge del 9 al 22 de agosto de 2026 y pon en juego tu propia colección.", "Agrega al menos cinco discos", "Haz un Random Pick, un Today’s Pick y un Mood Pick", "Comparte tu favorito en Instagram con #RecordPickerChallenge", "Sigue el reto en Instagram", "No se requiere compra, calificación ni reseña en el App Store. Los detalles de participación y selección se publican en Instagram."),
    "fi": ("70 Pro-koodia · 14 päivää · alkaa 9. elokuuta", "Kolme valintaa. Yksi suosikki. Voita Pro pysyvästi.", "Osallistu 3 Picks Challenge -haasteeseen 9.–22. elokuuta 2026 omalla levykokoelmallasi.", "Lisää vähintään viisi levyä", "Tee yksi Random Pick, yksi Today’s Pick ja yksi Mood Pick", "Jaa suosikkisi Instagramissa tunnisteella #RecordPickerChallenge", "Seuraa haastetta Instagramissa", "Ostosta, App Store -arviota tai arvostelua ei vaadita. Osallistumis- ja valintatiedot julkaistaan Instagramissa."),
    "fr": ("70 codes Pro · 14 jours · dès le 9 août", "Trois choix. Un favori. Pro à vie à gagner.", "Relève le 3 Picks Challenge du 9 au 22 août 2026 et mets ta propre collection de disques en jeu.", "Ajoute au moins cinq disques", "Effectue un Random Pick, un Today’s Pick et un Mood Pick", "Partage ton favori sur Instagram avec #RecordPickerChallenge", "Suivre le challenge sur Instagram", "Aucun achat, aucune note et aucun avis App Store ne sont requis. Les conditions d’éligibilité et de sélection sont publiées sur Instagram."),
    "fr-ca": ("70 codes Pro · 14 jours · dès le 9 août", "Trois choix. Un favori. Pro à vie à gagner.", "Relève le 3 Picks Challenge du 9 au 22 août 2026 et mets ta propre collection de disques en jeu.", "Ajoute au moins cinq disques", "Effectue un Random Pick, un Today’s Pick et un Mood Pick", "Partage ton favori sur Instagram avec #RecordPickerChallenge", "Suivre le défi sur Instagram", "Aucun achat, aucune note et aucun avis dans l’App Store ne sont requis. Les conditions d’admissibilité et de sélection sont publiées sur Instagram."),
    "he": ("70 קודי Pro · 14 ימים · מתחיל ב־9 באוגוסט", "שלוש בחירות. אחת מועדפת. Pro לכל החיים.", "הצטרפו ל־3 Picks Challenge בין 9 ל־22 באוגוסט 2026 עם אוסף התקליטים שלכם.", "הוסיפו לפחות חמישה תקליטים", "בצעו Random Pick,‏ Today’s Pick ו־Mood Pick", "שתפו את הבחירה המועדפת ב־Instagram עם #RecordPickerChallenge", "עקבו אחר האתגר ב־Instagram", "אין צורך ברכישה, דירוג או ביקורת ב־App Store. תנאי הזכאות והבחירה מתפרסמים ב־Instagram."),
    "hi": ("70 Pro कोड · 14 दिन · 9 अगस्त से", "तीन चयन। एक पसंदीदा। हमेशा के लिए Pro जीतें।", "9 से 22 अगस्त 2026 तक 3 Picks Challenge में अपने रिकॉर्ड संग्रह के साथ हिस्सा लें।", "कम से कम पाँच रिकॉर्ड जोड़ें", "एक Random Pick, एक Today’s Pick और एक Mood Pick करें", "अपना पसंदीदा चयन Instagram पर #RecordPickerChallenge के साथ साझा करें", "Instagram पर चैलेंज देखें", "खरीदारी, App Store रेटिंग या समीक्षा आवश्यक नहीं है। पात्रता और चयन की जानकारी Instagram पर प्रकाशित की जाती है।"),
    "id": ("70 kode Pro · 14 hari · mulai 9 Agustus", "Tiga pilihan. Satu favorit. Menangkan Pro seumur hidup.", "Ikuti 3 Picks Challenge dari 9 hingga 22 Agustus 2026 dengan koleksi rekaman Anda sendiri.", "Tambahkan setidaknya lima rekaman", "Buat satu Random Pick, satu Today’s Pick, dan satu Mood Pick", "Bagikan favorit Anda di Instagram dengan #RecordPickerChallenge", "Ikuti tantangan di Instagram", "Tidak diperlukan pembelian, penilaian, atau ulasan App Store. Detail kelayakan dan pemilihan diterbitkan di Instagram."),
    "it": ("70 codici Pro · 14 giorni · dal 9 agosto", "Tre scelte. Una preferita. Vinci Pro per sempre.", "Partecipa alla 3 Picks Challenge dal 9 al 22 agosto 2026 e metti in gioco la tua collezione.", "Aggiungi almeno cinque dischi", "Fai un Random Pick, un Today’s Pick e un Mood Pick", "Condividi il tuo preferito su Instagram con #RecordPickerChallenge", "Segui la sfida su Instagram", "Non sono richiesti acquisti, valutazioni o recensioni sull’App Store. I dettagli su idoneità e selezione sono pubblicati su Instagram."),
    "ja": ("Proコード70本 · 14日間 · 8月9日開始", "3回選んで、お気に入りを1枚。Proを永久に獲得。", "2026年8月9日から22日まで、あなたのレコードコレクションで3 Picks Challengeに参加しよう。", "レコードを5枚以上追加", "Random Pick、Today’s Pick、Mood Pickを1回ずつ実行", "お気に入りをInstagramで#RecordPickerChallengeとともに共有", "Instagramでチャレンジを見る", "購入、App Storeでの評価やレビューは不要です。参加資格と選考方法はInstagramで公開します。"),
    "ko": ("Pro 코드 70개 · 14일 · 8월 9일 시작", "세 번 고르고, 하나를 선택하세요. 평생 Pro에 도전하세요.", "2026년 8월 9일부터 22일까지 내 음반 컬렉션으로 3 Picks Challenge에 참여하세요.", "음반을 5장 이상 추가", "Random Pick, Today’s Pick, Mood Pick을 한 번씩 실행", "가장 마음에 든 결과를 Instagram에 #RecordPickerChallenge와 함께 공유", "Instagram에서 챌린지 보기", "구매, App Store 평점 또는 리뷰는 필요하지 않습니다. 참가 자격과 선정 방식은 Instagram에 게시됩니다."),
    "nb": ("70 Pro-koder · 14 dager · starter 9. august", "Tre valg. Én favoritt. Vinn Pro for alltid.", "Delta i 3 Picks Challenge fra 9. til 22. august 2026 med din egen platesamling.", "Legg til minst fem plater", "Gjør ett Random Pick, ett Today’s Pick og ett Mood Pick", "Del favoritten din på Instagram med #RecordPickerChallenge", "Følg utfordringen på Instagram", "Kjøp, App Store-vurdering eller anmeldelse er ikke påkrevd. Vilkår for deltakelse og utvelgelse publiseres på Instagram."),
    "nl": ("70 Pro-codes · 14 dagen · start 9 augustus", "Drie keuzes. Eén favoriet. Win Pro voor altijd.", "Doe van 9 tot en met 22 augustus 2026 mee aan de 3 Picks Challenge met je eigen platencollectie.", "Voeg minstens vijf platen toe", "Doe één Random Pick, één Today’s Pick en één Mood Pick", "Deel je favoriet op Instagram met #RecordPickerChallenge", "Volg de challenge op Instagram", "Geen aankoop, App Store-beoordeling of recensie vereist. Details over deelname en selectie worden op Instagram gepubliceerd."),
    "pl": ("70 kodów Pro · 14 dni · start 9 sierpnia", "Trzy typy. Jeden faworyt. Wygraj Pro na zawsze.", "Weź udział w 3 Picks Challenge od 9 do 22 sierpnia 2026 ze swoją kolekcją płyt.", "Dodaj co najmniej pięć płyt", "Wykonaj po jednym Random Pick, Today’s Pick i Mood Pick", "Udostępnij swój typ na Instagramie z #RecordPickerChallenge", "Obserwuj wyzwanie na Instagramie", "Zakup, ocena ani recenzja w App Store nie są wymagane. Zasady udziału i wyboru są publikowane na Instagramie."),
    "pt-br": ("70 códigos Pro · 14 dias · começa em 9 de agosto", "Três escolhas. Uma favorita. Ganhe Pro para sempre.", "Participe do 3 Picks Challenge de 9 a 22 de agosto de 2026 com a sua própria coleção.", "Adicione pelo menos cinco discos", "Faça um Random Pick, um Today’s Pick e um Mood Pick", "Compartilhe seu favorito no Instagram com #RecordPickerChallenge", "Acompanhe o desafio no Instagram", "Não é necessário comprar, avaliar ou escrever uma resenha na App Store. Os detalhes de elegibilidade e seleção são publicados no Instagram."),
    "pt-pt": ("70 códigos Pro · 14 dias · começa a 9 de agosto", "Três escolhas. Uma favorita. Ganhe Pro para sempre.", "Participe no 3 Picks Challenge de 9 a 22 de agosto de 2026 com a sua própria coleção.", "Adicione pelo menos cinco discos", "Faça um Random Pick, um Today’s Pick e um Mood Pick", "Partilhe a sua favorita no Instagram com #RecordPickerChallenge", "Siga o desafio no Instagram", "Não é necessária qualquer compra, classificação ou avaliação na App Store. Os detalhes de elegibilidade e seleção são publicados no Instagram."),
    "ru": ("70 кодов Pro · 14 дней · старт 9 августа", "Три варианта. Один фаворит. Выиграйте Pro навсегда.", "Участвуйте в 3 Picks Challenge с 9 по 22 августа 2026 года со своей коллекцией пластинок.", "Добавьте не менее пяти пластинок", "Сделайте по одному Random Pick, Today’s Pick и Mood Pick", "Поделитесь своим фаворитом в Instagram с #RecordPickerChallenge", "Следить за конкурсом в Instagram", "Покупка, оценка или отзыв в App Store не требуются. Условия участия и выбора публикуются в Instagram."),
    "sv": ("70 Pro-koder · 14 dagar · start 9 augusti", "Tre val. En favorit. Vinn Pro för alltid.", "Delta i 3 Picks Challenge den 9–22 augusti 2026 med din egen skivsamling.", "Lägg till minst fem skivor", "Gör ett Random Pick, ett Today’s Pick och ett Mood Pick", "Dela din favorit på Instagram med #RecordPickerChallenge", "Följ utmaningen på Instagram", "Inget köp, App Store-betyg eller omdöme krävs. Villkor för deltagande och urval publiceras på Instagram."),
    "th": ("70 โค้ด Pro · 14 วัน · เริ่ม 9 สิงหาคม", "เลือกสามครั้ง หนึ่งรายการโปรด ลุ้นรับ Pro ตลอดชีพ", "ร่วม 3 Picks Challenge วันที่ 9–22 สิงหาคม 2026 ด้วยคอลเลกชันแผ่นเสียงของคุณเอง", "เพิ่มแผ่นเสียงอย่างน้อยห้าแผ่น", "ใช้ Random Pick, Today’s Pick และ Mood Pick อย่างละหนึ่งครั้ง", "แชร์รายการโปรดบน Instagram พร้อม #RecordPickerChallenge", "ติดตามชาเลนจ์บน Instagram", "ไม่จำเป็นต้องซื้อ ให้คะแนน หรือรีวิวใน App Store รายละเอียดสิทธิ์และการคัดเลือกเผยแพร่บน Instagram"),
    "tr": ("70 Pro kodu · 14 gün · 9 Ağustos’ta başlıyor", "Üç seçim. Bir favori. Ömür boyu Pro kazan.", "9–22 Ağustos 2026 tarihleri arasında kendi plak koleksiyonunla 3 Picks Challenge’a katıl.", "En az beş plak ekle", "Bir Random Pick, bir Today’s Pick ve bir Mood Pick yap", "Favorini Instagram’da #RecordPickerChallenge ile paylaş", "Challenge’ı Instagram’da takip et", "Satın alma, App Store puanı veya yorumu gerekmez. Uygunluk ve seçim ayrıntıları Instagram’da yayımlanır."),
    "vi": ("70 mã Pro · 14 ngày · bắt đầu 9 tháng 8", "Ba lượt chọn. Một lựa chọn yêu thích. Nhận Pro trọn đời.", "Tham gia 3 Picks Challenge từ ngày 9 đến 22 tháng 8 năm 2026 bằng chính bộ sưu tập của bạn.", "Thêm ít nhất năm đĩa", "Thực hiện một Random Pick, một Today’s Pick và một Mood Pick", "Chia sẻ lựa chọn yêu thích trên Instagram với #RecordPickerChallenge", "Theo dõi thử thách trên Instagram", "Không cần mua, xếp hạng hay đánh giá trên App Store. Điều kiện và cách lựa chọn được công bố trên Instagram."),
    "zh-hans": ("70 个 Pro 兑换码 · 14 天 · 8 月 9 日开始", "三次选择，一个最爱。赢取终身 Pro。", "2026 年 8 月 9 日至 22 日，用你自己的唱片收藏参加 3 Picks Challenge。", "添加至少五张唱片", "分别使用一次 Random Pick、Today’s Pick 和 Mood Pick", "在 Instagram 分享最喜欢的结果并添加 #RecordPickerChallenge", "在 Instagram 关注挑战", "无需购买、App Store 评分或评论。参与资格和评选方式将在 Instagram 公布。"),
    "zh-hant": ("70 個 Pro 兌換碼 · 14 天 · 8 月 9 日開始", "三次選擇，一個最愛。贏取終身 Pro。", "2026 年 8 月 9 日至 22 日，用你自己的唱片收藏參加 3 Picks Challenge。", "加入至少五張唱片", "分別使用一次 Random Pick、Today’s Pick 和 Mood Pick", "在 Instagram 分享最喜歡的結果並加入 #RecordPickerChallenge", "在 Instagram 關注挑戰", "無需購買、App Store 評分或評論。參加資格和評選方式將在 Instagram 公布。"),
}

RULES_LABELS = {
    "ar": "القواعد الرسمية", "ca": "Bases oficials", "da": "Officielle regler",
    "de": "Offizielle Regeln", "el": "Επίσημοι όροι", "en-au": "Official rules",
    "en-ca": "Official rules", "en-gb": "Official rules", "en-us": "Official rules",
    "es-es": "Reglamento oficial", "es-mx": "Reglamento oficial", "fi": "Viralliset säännöt",
    "fr": "Règlement officiel", "fr-ca": "Règlement officiel", "he": "התקנון הרשמי",
    "hi": "आधिकारिक नियम", "id": "Peraturan resmi", "it": "Regolamento ufficiale",
    "ja": "公式ルール", "ko": "공식 규정", "nb": "Offisielle regler",
    "nl": "Officiële regels", "pl": "Oficjalny regulamin", "pt-br": "Regulamento oficial",
    "pt-pt": "Regulamento oficial", "ru": "Официальные правила", "sv": "Officiella regler",
    "th": "กติกาอย่างเป็นทางการ", "tr": "Resmî kurallar", "vi": "Thể lệ chính thức",
    "zh-hans": "官方规则", "zh-hant": "官方規則",
}

LOCALES = tuple(COPY)
INSTAGRAM = "https://www.instagram.com/recordpicker/"
CSS_VERSION = "20260808-challenge"


def locale_for(path: Path) -> str:
    rel = path.relative_to(ROOT)
    if rel.parts and rel.parts[0] in COPY:
        return rel.parts[0]
    if rel == Path("contest/index.html"):
        return "en-gb"
    return "fr"


def home_href(path: Path, locale: str) -> str:
    rel = path.relative_to(ROOT)
    if rel.parts and rel.parts[0] in COPY:
        return f"/{locale}/#recordpicker-challenge"
    return "/#recordpicker-challenge"


def is_home(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    return rel == Path("index.html") or (len(rel.parts) == 2 and rel.name == "index.html" and rel.parts[0] in COPY)


def banner(copy: tuple[str, ...], href: str) -> str:
    short, title, *_rest, cta, _legal = copy
    label = escape(f"#RecordPickerChallenge — {title}", quote=True)
    return (
        f'<aside class="challenge-announcement" aria-label="{label}">'
        f'<a href="{href}"><strong dir="ltr">#RecordPickerChallenge</strong>'
        f'<span>{escape(short)}</span><b>{escape(cta)} <span aria-hidden="true">→</span></b></a>'
        "</aside>"
    )


def section(copy: tuple[str, ...], rules_label: str) -> str:
    short, title, lead, step1, step2, step3, cta, legal = copy
    step3_html = escape(step3).replace(
        "#RecordPickerChallenge",
        '<bdi dir="ltr">#RecordPickerChallenge</bdi>',
    )
    return (
        '<section class="challenge-section" id="recordpicker-challenge" aria-labelledby="challenge-title">'
        '<div class="challenge-copy">'
        f'<p class="challenge-kicker"><bdi dir="ltr">#RecordPickerChallenge</bdi> · {escape(short)}</p>'
        f'<h2 id="challenge-title">{escape(title)}</h2>'
        f'<p class="challenge-lead">{escape(lead)}</p>'
        '<ol class="challenge-steps">'
        f'<li><span>1</span><strong>{escape(step1)}</strong></li>'
        f'<li><span>2</span><strong>{escape(step2)}</strong></li>'
        f'<li><span>3</span><strong>{step3_html}</strong></li>'
        '</ol><div class="challenge-actions">'
        f'<a class="button challenge-button" href="{INSTAGRAM}" rel="me">{escape(cta)}</a>'
        f'<a class="button challenge-rules-button" href="/contest/">{escape(rules_label)}</a>'
        '</div>'
        f'<p class="challenge-legal">{escape(legal)}</p>'
        '</div><figure class="challenge-media">'
        '<video controls playsinline preload="metadata" poster="/assets/challenge/recordpicker-challenge-poster.png" aria-label="Record Picker 3 Picks Challenge">'
        '<source src="/assets/challenge/recordpicker-challenge-reel.mp4" type="video/mp4">'
        '</video><figcaption>#RecordPickerChallenge · Instagram Reel · 22.5 s</figcaption>'
        '</figure></section>'
    )


def update_html(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    text = re.sub(r'<aside class="challenge-announcement".*?</aside>', "", original, flags=re.DOTALL)
    text = re.sub(r'<section class="challenge-section".*?</section>', "", text, flags=re.DOTALL)
    text = re.sub(r'<section class="section contest-callout".*?</section>', "", text, flags=re.DOTALL)
    locale = locale_for(path)
    copy = COPY.get(locale, EN)
    rules_label = RULES_LABELS.get(locale, "Official rules")
    text = re.sub(
        r'(<a href="/contest/" data-campaign-link="three-picks-2026">).*?(</a>)',
        rf'\1{escape(rules_label)}\2',
        text,
    )
    text = text.replace("</header>", "</header>" + banner(copy, home_href(path, locale)), 1)
    if is_home(path):
        pattern = r'(<section class="facts-band">.*?</section>)'
        text, count = re.subn(pattern, r"\1" + section(copy, rules_label), text, count=1, flags=re.DOTALL)
        if count != 1:
            raise RuntimeError(f"facts-band not found in {path}")
    text = re.sub(r'quality\.css\?v=[^"\']+', f'quality.css?v={CSS_VERSION}', text)
    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


CSS = r'''

/* #RecordPickerChallenge campaign — 9–22 August 2026. */
.challenge-announcement {
  position: relative;
  z-index: 20;
  background: linear-gradient(110deg, #2a0715 0%, #3d0b20 48%, #21104d 100%);
  color: #fff;
  border-bottom: 1px solid rgba(255,255,255,.14);
}
.challenge-announcement a {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: clamp(10px, 2vw, 24px);
  min-height: 52px;
  padding: 10px 18px;
  text-align: center;
}
.challenge-announcement strong { color: #ff6b84; font-weight: 900; }
.challenge-announcement span { font-weight: 760; }
.challenge-announcement b { color: #fff; font-size: .9rem; font-weight: 900; }
.challenge-announcement a:hover b { color: #ff8ba0; }
.challenge-section {
  scroll-margin-top: 94px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(260px, 390px);
  align-items: center;
  gap: clamp(34px, 7vw, 86px);
  width: min(1240px, calc(100% - 32px));
  margin: 0 auto 72px;
  padding: clamp(34px, 6vw, 70px);
  overflow: hidden;
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 18px;
  background: radial-gradient(circle at 0 0, rgba(132,18,61,.68), transparent 38%), radial-gradient(circle at 100% 100%, rgba(54,31,124,.7), transparent 35%), #100812;
  color: #fff;
  box-shadow: 0 34px 90px rgba(28, 4, 17, .24);
}
.challenge-kicker { margin: 0; color: #ff6b84; font-size: .88rem; font-weight: 900; text-transform: uppercase; }
.challenge-section h2 { max-width: 14ch; margin-top: 15px; color: #fff; font-size: clamp(2.55rem, 5.5vw, 5rem); line-height: .96; text-wrap: balance; }
.challenge-lead { max-width: 650px; margin: 22px 0 0; color: rgba(255,255,255,.78); font-size: clamp(1.05rem, 1.7vw, 1.28rem); line-height: 1.6; }
.challenge-steps { display: grid; gap: 12px; margin: 28px 0 0; padding: 0; list-style: none; }
.challenge-steps li { display: grid; grid-template-columns: 38px minmax(0,1fr); align-items: center; gap: 12px; }
.challenge-steps li > span { display: grid; place-items: center; width: 38px; height: 38px; border-radius: 999px; background: #ff2d55; color: #fff; font-weight: 900; }
.challenge-steps strong { line-height: 1.4; }
.challenge-actions { margin-top: 30px; }
.challenge-actions { display: flex; flex-wrap: wrap; gap: 12px; }
.challenge-button { background: #ff2d55; color: #fff; box-shadow: 0 18px 44px rgba(255,45,85,.3); }
.challenge-button:hover { background: #ff5273; }
.challenge-rules-button { border-color: rgba(255,255,255,.2); background: rgba(255,255,255,.08); color: #fff; }
.challenge-rules-button:hover { background: rgba(255,255,255,.14); }
.challenge-legal { max-width: 680px; margin: 20px 0 0; color: rgba(255,255,255,.6); font-size: .82rem; line-height: 1.55; }
.challenge-media { width: min(100%, 350px); margin: 0 auto; overflow: hidden; border: 1px solid rgba(255,255,255,.16); border-radius: 18px; background: #09050b; box-shadow: 0 30px 70px rgba(0,0,0,.42); }
.challenge-media video { display: block; width: 100%; aspect-ratio: 9 / 16; background: #09050b; object-fit: cover; }
.challenge-media figcaption { padding: 12px 14px 14px; color: rgba(255,255,255,.62); font-size: .78rem; font-weight: 780; text-align: center; }
html[dir="rtl"] .challenge-steps li { grid-template-columns: minmax(0,1fr) 38px; }
html[dir="rtl"] .challenge-steps li > span { grid-column: 2; grid-row: 1; }
html[dir="rtl"] .challenge-steps strong { grid-column: 1; grid-row: 1; }
@media (max-width: 820px) {
  .challenge-announcement a { flex-wrap: wrap; gap: 4px 12px; }
  .challenge-announcement span { width: 100%; font-size: .82rem; }
  .challenge-section { grid-template-columns: 1fr; padding: 32px 22px; }
  .challenge-section h2 { font-size: clamp(2.5rem, 13vw, 4.2rem); }
  .challenge-media { width: min(100%, 320px); }
}
'''


def update_css() -> None:
    path = ROOT / "quality.css"
    original = path.read_text(encoding="utf-8")
    marker = "/* #RecordPickerChallenge campaign"
    text = original[: original.find(marker)].rstrip() if marker in original else original.rstrip()
    path.write_text(text + CSS, encoding="utf-8")


def copy_assets() -> None:
    target = ROOT / "assets" / "challenge"
    target.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE / "work/render/cards/07.png", target / "recordpicker-challenge-poster.png")
    shutil.copy2(SOURCE / "output/Record-Picker-3-Picks-Challenge-en-GB-Instagram-Reel.mp4", target / "recordpicker-challenge-reel.mp4")


def update_audit() -> None:
    path = ROOT / "Scripts" / "audit_site_quality.py"
    text = path.read_text(encoding="utf-8")
    requirement = '"quality.css?v=20260808-challenge",'
    if requirement not in text:
        text = text.replace(
            '"quality.css?v=20260808-contest1",',
            '"quality.css?v=20260808-contest1",\n                ' + requirement,
        )
    path.write_text(text, encoding="utf-8")


def main() -> None:
    changed = sum(update_html(path) for path in ROOT.rglob("*.html"))
    update_css()
    copy_assets()
    update_audit()
    print(f"Updated {changed} HTML pages; campaign section added to {len(COPY) + 1} home pages.")


if __name__ == "__main__":
    main()
