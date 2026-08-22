#!/usr/bin/env python3
"""Announce the Android and Windows work on every localized home page."""

from __future__ import annotations

from html import escape
from pathlib import Path
import re
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]

# Short, deliberately non-dated copy: the site announces active development
# without promising a release window that has not yet been set.
COPY = {
    "": ("In development", "Record Picker for Android and PC", "Release details will be announced when both versions are ready."),
    "ar": ("قيد التطوير", "Record Picker لنظام Android والكمبيوتر الشخصي", "سيتم الإعلان عن تفاصيل الإصدار عندما تصبح النسختان جاهزتين."),
    "ca": ("En desenvolupament", "Record Picker per a Android i PC", "Els detalls del llançament s’anunciaran quan totes dues versions estiguin preparades."),
    "da": ("Under udvikling", "Record Picker til Android og PC", "Udgivelsesdetaljer annonceres, når begge versioner er klar."),
    "de": ("In Entwicklung", "Record Picker für Android und PC", "Details zur Veröffentlichung folgen, sobald beide Versionen fertig sind."),
    "el": ("Υπό ανάπτυξη", "Record Picker για Android και PC", "Οι λεπτομέρειες κυκλοφορίας θα ανακοινωθούν όταν είναι έτοιμες και οι δύο εκδόσεις."),
    "en-au": ("In development", "Record Picker for Android and PC", "Release details will be announced when both versions are ready."),
    "en-ca": ("In development", "Record Picker for Android and PC", "Release details will be announced when both versions are ready."),
    "en-gb": ("In development", "Record Picker for Android and PC", "Release details will be announced when both versions are ready."),
    "en-us": ("In development", "Record Picker for Android and PC", "Release details will be announced when both versions are ready."),
    "es-es": ("En desarrollo", "Record Picker para Android y PC", "Los detalles del lanzamiento se anunciarán cuando ambas versiones estén listas."),
    "es-mx": ("En desarrollo", "Record Picker para Android y PC", "Los detalles del lanzamiento se anunciarán cuando ambas versiones estén listas."),
    "fi": ("Kehitteillä", "Record Picker Androidille ja PC:lle", "Julkaisutiedot kerrotaan, kun molemmat versiot ovat valmiita."),
    "fr": ("En développement", "Record Picker pour Android et PC", "Les informations de sortie seront annoncées lorsque les deux versions seront prêtes."),
    "fr-ca": ("En développement", "Record Picker pour Android et PC", "Les détails du lancement seront annoncés lorsque les deux versions seront prêtes."),
    "he": ("בפיתוח", "Record Picker ל-Android ולמחשב PC", "פרטי ההשקה יפורסמו כששתי הגרסאות יהיו מוכנות."),
    "hi": ("विकास जारी है", "Android और PC के लिए Record Picker", "दोनों संस्करण तैयार होने पर रिलीज़ की जानकारी घोषित की जाएगी।"),
    "id": ("Dalam pengembangan", "Record Picker untuk Android dan PC", "Detail peluncuran akan diumumkan saat kedua versi siap."),
    "it": ("In sviluppo", "Record Picker per Android e PC", "I dettagli sul lancio saranno annunciati quando entrambe le versioni saranno pronte."),
    "ja": ("開発中", "Android／PC版 Record Picker", "両バージョンの準備が整い次第、リリースの詳細をお知らせします。"),
    "ko": ("개발 중", "Android 및 PC용 Record Picker", "두 버전이 준비되면 출시 세부 정보를 안내하겠습니다."),
    "nb": ("Under utvikling", "Record Picker for Android og PC", "Lanseringsdetaljer kunngjøres når begge versjonene er klare."),
    "nl": ("In ontwikkeling", "Record Picker voor Android en pc", "De releasedetails worden bekendgemaakt zodra beide versies klaar zijn."),
    "pl": ("W trakcie tworzenia", "Record Picker na Androida i PC", "Szczegóły premiery zostaną ogłoszone, gdy obie wersje będą gotowe."),
    "pt-br": ("Em desenvolvimento", "Record Picker para Android e PC", "Os detalhes do lançamento serão anunciados quando as duas versões estiverem prontas."),
    "pt-pt": ("Em desenvolvimento", "Record Picker para Android e PC", "Os detalhes do lançamento serão anunciados quando ambas as versões estiverem prontas."),
    "ru": ("В разработке", "Record Picker для Android и ПК", "Подробности о выпуске появятся, когда обе версии будут готовы."),
    "sv": ("Under utveckling", "Record Picker för Android och PC", "Lanseringsinformation meddelas när båda versionerna är klara."),
    "th": ("อยู่ระหว่างการพัฒนา", "Record Picker สำหรับ Android และ PC", "เราจะประกาศรายละเอียดการเปิดตัวเมื่อทั้งสองเวอร์ชันพร้อมใช้งาน"),
    "tr": ("Geliştirme aşamasında", "Android ve PC için Record Picker", "Her iki sürüm de hazır olduğunda çıkış ayrıntıları duyurulacak."),
    "vi": ("Đang phát triển", "Record Picker cho Android và PC", "Thông tin phát hành sẽ được công bố khi cả hai phiên bản sẵn sàng."),
    "zh-hans": ("正在开发", "Android 和 PC 版 Record Picker", "两个版本准备就绪后将公布发布详情。"),
    "zh-hant": ("開發中", "Android 與 PC 版 Record Picker", "兩個版本準備就緒後將公布發佈詳情。"),
}

# Recruitment copy lives beside the platform announcement so rerunning this
# generator cannot silently remove the beta call-to-action.
BETA_COPY = {
    "": ("Android beta testers wanted", "We are looking for 15 to 20 volunteers with a Google Account and a compatible Android phone, tablet, or Chromebook. Testers must remain enrolled for at least 14 consecutive days and share feedback.", "Volunteer for the Android beta"),
    "ar": ("مطلوب مختبرو إصدار Android التجريبي", "نبحث عن 15 إلى 20 متطوعًا لديهم حساب Google وهاتف أو جهاز لوحي يعمل بنظام Android أو Chromebook متوافق. يجب أن يظل المختبرون مسجلين لمدة 14 يومًا متتاليًا على الأقل وأن يشاركوا ملاحظاتهم.", "تطوّع لاختبار إصدار Android التجريبي"),
    "ca": ("Busquem provadors beta per a Android", "Busquem entre 15 i 20 voluntaris amb un compte de Google i un telèfon, una tauleta Android o un Chromebook compatible. Cal mantenir-se inscrit durant almenys 14 dies consecutius i compartir comentaris.", "Participa en la beta d’Android"),
    "da": ("Android-betatestere søges", "Vi søger 15 til 20 frivillige med en Google-konto og en kompatibel Android-telefon, -tablet eller Chromebook. Testere skal forblive tilmeldt i mindst 14 sammenhængende dage og dele feedback.", "Deltag i Android-betaen"),
    "de": ("Android-Betatester gesucht", "Wir suchen 15 bis 20 Freiwillige mit einem Google-Konto und einem kompatiblen Android-Smartphone, Tablet oder Chromebook. Tester müssen mindestens 14 Tage in Folge angemeldet bleiben und Feedback geben.", "Für die Android-Beta anmelden"),
    "el": ("Ζητούνται δοκιμαστές beta για Android", "Αναζητούμε 15 έως 20 εθελοντές με Λογαριασμό Google και συμβατό τηλέφωνο ή tablet Android ή Chromebook. Οι δοκιμαστές πρέπει να παραμείνουν εγγεγραμμένοι για τουλάχιστον 14 συνεχόμενες ημέρες και να μοιραστούν σχόλια.", "Συμμετοχή στην beta του Android"),
    "en-au": ("Android beta testers wanted", "We are looking for 15 to 20 volunteers with a Google Account and a compatible Android phone, tablet or Chromebook. Testers must remain enrolled for at least 14 consecutive days and share feedback.", "Volunteer for the Android beta"),
    "en-ca": ("Android beta testers wanted", "We are looking for 15 to 20 volunteers with a Google Account and a compatible Android phone, tablet, or Chromebook. Testers must remain enrolled for at least 14 consecutive days and share feedback.", "Volunteer for the Android beta"),
    "en-gb": ("Android beta testers wanted", "We are looking for 15 to 20 volunteers with a Google Account and a compatible Android phone, tablet or Chromebook. Testers must remain enrolled for at least 14 consecutive days and share feedback.", "Volunteer for the Android beta"),
    "en-us": ("Android beta testers wanted", "We are looking for 15 to 20 volunteers with a Google Account and a compatible Android phone, tablet, or Chromebook. Testers must remain enrolled for at least 14 consecutive days and share feedback.", "Volunteer for the Android beta"),
    "es-es": ("Buscamos probadores beta para Android", "Buscamos entre 15 y 20 voluntarios con una cuenta de Google y un teléfono o tableta Android, o un Chromebook compatible. Los probadores deben permanecer inscritos durante al menos 14 días consecutivos y compartir sus comentarios.", "Participar en la beta de Android"),
    "es-mx": ("Buscamos testers beta para Android", "Buscamos de 15 a 20 voluntarios con una Cuenta de Google y un teléfono o tablet Android, o un Chromebook compatible. Los testers deben permanecer inscritos durante al menos 14 días consecutivos y compartir sus comentarios.", "Participar en la beta de Android"),
    "fi": ("Android-beetatestaajia etsitään", "Etsimme 15–20 vapaaehtoista, joilla on Google-tili ja yhteensopiva Android-puhelin, -tabletti tai Chromebook. Testaajien on pysyttävä mukana vähintään 14 peräkkäistä päivää ja annettava palautetta.", "Ilmoittaudu Android-beetaan"),
    "fr": ("Nous recherchons des bêta-testeurs Android", "Nous recherchons 15 à 20 volontaires disposant d’un compte Google et d’un téléphone ou d’une tablette Android, ou d’un Chromebook compatible. Il faudra rester inscrit pendant au moins 14 jours consécutifs et nous transmettre vos remarques.", "Devenir bêta-testeur Android"),
    "fr-ca": ("Nous recherchons des bêta-testeurs Android", "Nous recherchons de 15 à 20 volontaires disposant d’un compte Google et d’un téléphone ou d’une tablette Android, ou d’un Chromebook compatible. Il faudra rester inscrit pendant au moins 14 jours consécutifs et nous transmettre vos commentaires.", "Devenir bêta-testeur Android"),
    "he": ("דרושים בודקי בטא ל-Android", "אנו מחפשים 15 עד 20 מתנדבים עם חשבון Google ומכשיר טלפון או טאבלט Android או Chromebook תואם. על הבודקים להישאר רשומים לפחות 14 ימים רצופים ולשתף משוב.", "התנדבות לבטא של Android"),
    "hi": ("Android बीटा परीक्षकों की आवश्यकता है", "हम ऐसे 15 से 20 स्वयंसेवकों की तलाश कर रहे हैं जिनके पास Google खाता और संगत Android फ़ोन, टैबलेट या Chromebook हो। परीक्षकों को कम से कम लगातार 14 दिनों तक नामांकित रहना और प्रतिक्रिया साझा करना होगा।", "Android बीटा में भाग लें"),
    "id": ("Dicari penguji beta Android", "Kami mencari 15 hingga 20 sukarelawan dengan Akun Google dan ponsel atau tablet Android, atau Chromebook yang kompatibel. Penguji harus tetap terdaftar setidaknya selama 14 hari berturut-turut dan memberikan masukan.", "Ikuti beta Android"),
    "it": ("Cerchiamo beta tester Android", "Cerchiamo da 15 a 20 volontari con un Account Google e un telefono o tablet Android, oppure un Chromebook compatibile. I tester dovranno rimanere iscritti per almeno 14 giorni consecutivi e condividere il proprio feedback.", "Partecipa alla beta Android"),
    "ja": ("Android版ベータテスター募集", "Google アカウントと、対応する Android スマートフォン、タブレット、または Chromebookをお持ちのボランティアを15～20名募集しています。14日間連続でテストに参加し、フィードバックをお寄せください。", "Android版ベータに参加する"),
    "ko": ("Android 베타 테스터 모집", "Google 계정과 호환되는 Android 휴대전화, 태블릿 또는 Chromebook을 보유한 자원봉사자 15~20명을 찾고 있습니다. 테스터는 최소 14일 연속으로 등록 상태를 유지하고 의견을 공유해야 합니다.", "Android 베타 참여하기"),
    "nb": ("Vi søker Android-betatestere", "Vi søker 15 til 20 frivillige med en Google-konto og en kompatibel Android-telefon, et nettbrett eller en Chromebook. Testere må være registrert i minst 14 sammenhengende dager og dele tilbakemeldinger.", "Bli med i Android-betaen"),
    "nl": ("Android-bètatesters gezocht", "We zoeken 15 tot 20 vrijwilligers met een Google-account en een compatibele Android-telefoon, tablet of Chromebook. Testers moeten minstens 14 opeenvolgende dagen ingeschreven blijven en feedback delen.", "Doe mee aan de Android-bèta"),
    "pl": ("Poszukujemy beta testerów Androida", "Szukamy od 15 do 20 ochotników z kontem Google i zgodnym telefonem lub tabletem z Androidem albo Chromebookiem. Testerzy muszą pozostać zapisani przez co najmniej 14 kolejnych dni i podzielić się opinią.", "Dołącz do bety na Androida"),
    "pt-br": ("Procuramos testadores beta para Android", "Procuramos de 15 a 20 voluntários com uma Conta do Google e um celular ou tablet Android, ou Chromebook compatível. Os testadores devem permanecer inscritos por pelo menos 14 dias consecutivos e enviar comentários.", "Participar do beta para Android"),
    "pt-pt": ("Procuramos testadores beta para Android", "Procuramos 15 a 20 voluntários com uma Conta Google e um telemóvel ou tablet Android, ou Chromebook compatível. Os testadores terão de permanecer inscritos durante pelo menos 14 dias consecutivos e partilhar comentários.", "Participar na versão beta para Android"),
    "ru": ("Ищем бета-тестеров Android", "Мы ищем от 15 до 20 добровольцев с аккаунтом Google и совместимым телефоном или планшетом Android либо Chromebook. Тестеры должны оставаться участниками не менее 14 дней подряд и делиться отзывами.", "Стать бета-тестером Android"),
    "sv": ("Android-betatestare sökes", "Vi söker 15 till 20 frivilliga med ett Google-konto och en kompatibel Android-telefon, surfplatta eller Chromebook. Testare måste vara registrerade i minst 14 dagar i följd och dela återkoppling.", "Delta i Android-betan"),
    "th": ("รับสมัครผู้ทดสอบ Android รุ่นเบต้า", "เรากำลังมองหาอาสาสมัคร 15 ถึง 20 คนที่มีบัญชี Google และโทรศัพท์หรือแท็บเล็ต Android หรือ Chromebook ที่รองรับ ผู้ทดสอบต้องเข้าร่วมต่อเนื่องอย่างน้อย 14 วันและส่งความคิดเห็น", "เข้าร่วมทดสอบ Android รุ่นเบต้า"),
    "tr": ("Android beta test kullanıcıları aranıyor", "Google Hesabı ve uyumlu bir Android telefon, tablet veya Chromebook sahibi 15 ila 20 gönüllü arıyoruz. Test kullanıcılarının en az 14 gün kesintisiz kayıtlı kalması ve geri bildirim paylaşması gerekir.", "Android betasına katıl"),
    "vi": ("Tuyển người thử nghiệm beta Android", "Chúng tôi đang tìm 15 đến 20 tình nguyện viên có Tài khoản Google và điện thoại hoặc máy tính bảng Android, hoặc Chromebook tương thích. Người thử nghiệm cần duy trì đăng ký ít nhất 14 ngày liên tục và chia sẻ phản hồi.", "Tham gia bản beta Android"),
    "zh-hans": ("招募 Android Beta 测试者", "我们正在招募 15 至 20 名志愿者。您需要拥有 Google 账号以及兼容的 Android 手机、平板电脑或 Chromebook，并连续参与测试至少 14 天并提供反馈。", "参加 Android Beta 测试"),
    "zh-hant": ("招募 Android Beta 測試者", "我們正在招募 15 至 20 名志願者。您需要擁有 Google 帳戶以及相容的 Android 手機、平板電腦或 Chromebook，並連續參與測試至少 14 天並提供意見。", "參加 Android Beta 測試"),
}

ANNOUNCEMENT = re.compile(
    r'<section class="platform-expansion"[^>]*>.*?</section>', flags=re.DOTALL
)
FACTS = re.compile(r'<section class="facts-band">.*?</section>', flags=re.DOTALL)
BADGE_ROW = re.compile(r'<div class="badge-row">.*?</div>', flags=re.DOTALL)
CTA_ROW = re.compile(r'<div class="cta-row">')


def announcement(locale: str) -> str:
    kicker, title, detail = COPY[locale]
    beta_title, beta_detail, beta_button = BETA_COPY[locale]
    title = title.replace("PC", "Windows").replace("pc", "Windows")
    subject = quote("Record Picker Android beta volunteer")
    return (
        '<section class="platform-expansion" aria-labelledby="platform-expansion-title">'
        '<div class="platform-expansion-copy">'
        f'<p class="kicker">{escape(kicker)}</p>'
        f'<h2 id="platform-expansion-title">{escape(title)}</h2>'
        f'<p class="platform-expansion-detail">{escape(detail)}</p>'
        '<div class="platform-beta-callout">'
        f'<h3>{escape(beta_title)}</h3><p>{escape(beta_detail)}</p>'
        '<div class="cta-row compact">'
        f'<a class="button primary" href="mailto:support@recordpicker.app?subject={subject}">{escape(beta_button)}</a>'
        '</div></div></div>'
        f'<div class="platform-expansion-badges" aria-label="{escape(title)}">'
        '<span>Android</span><span>Windows</span>'
        f'<small>{escape(kicker)}</small></div></section>'
    )


def hero_badges(locale: str) -> str:
    kicker = escape(COPY[locale][0])
    return (
        '<div class="badge-row">'
        '<span>iPhone</span><span>iPad</span><span>Apple Watch</span><span>Mac</span>'
        f'<span class="future-platform"><b>Android</b><small>{kicker}</small></span>'
        f'<span class="future-platform"><b>Windows</b><small>{kicker}</small></span>'
        '</div>'
    )


def update(locale: str) -> bool:
    path = ROOT / locale / "index.html" if locale else ROOT / "index.html"
    text = path.read_text(encoding="utf-8")
    block = announcement(locale)
    if ANNOUNCEMENT.search(text):
        updated = ANNOUNCEMENT.sub(block, text, count=1)
    else:
        facts = FACTS.search(text)
        if not facts:
            raise RuntimeError(f"Facts band not found in {path}")
        updated = text[:facts.end()] + block + text[facts.end():]
    if BADGE_ROW.search(updated):
        updated = BADGE_ROW.sub(hero_badges(locale), updated, count=1)
    elif CTA_ROW.search(updated):
        updated = CTA_ROW.sub(hero_badges(locale) + '<div class="cta-row">', updated, count=1)
    else:
        raise RuntimeError(f"Hero actions not found in {path}")
    if updated == text:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def refresh_stylesheet_version(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    updated = re.sub(
        r'quality\.css\?v=[^"\']+',
        'quality.css?v=20260822-android-beta',
        text,
    )
    if updated == text:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def main() -> None:
    changed = sum(update(locale) for locale in COPY)
    refreshed = sum(refresh_stylesheet_version(path) for path in ROOT.rglob("*.html"))
    print(
        f"Announced Android and Windows development on {changed} localized home pages "
        f"and refreshed styles on {refreshed} pages."
    )


if __name__ == "__main__":
    main()
