#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add the App's Mexican Spanish, Thai and Vietnamese website localizations."""

from __future__ import annotations

from html import escape
from datetime import date
from pathlib import Path
import re
import shutil


ROOT = Path(__file__).resolve().parents[1]
PAGE_KINDS = (
    "index.html", "choose-vinyl-record/index.html", "mac-app/index.html",
    "manage-vinyl-collection/index.html", "privacy/index.html",
    "random-vinyl-record-picker/index.html", "readme/index.html",
    "screenshots/index.html", "support/index.html",
)

DATA = {
    "th": {
        "html": "th", "name": "ไทย", "store": "th", "og": "th_TH",
        "nav": ("แอป", "เวอร์ชัน", "ภาพหน้าจอ", "ช่วยเหลือ", "ความเป็นส่วนตัว", "คุณสมบัติ", "แอป Mac", "ภาษา"),
        "available": "พร้อมให้ดาวน์โหลดแล้ว", "soon": "เร็ว ๆ นี้ · 1.10",
        "home_title": "เลือกแผ่นที่ใช่ - Record Picker",
        "home_desc": "จัดระเบียบคอลเลกชันเพลงและเลือกแผ่นถัดไปบน iPhone, iPad, Apple Watch และ Mac",
        "tagline": "เลือกแผ่นที่ใช่",
        "intro": "จัดระเบียบแผ่นเสียงไวนิล CD และอัลบั้มโปรด แล้วค้นพบคอลเลกชันของคุณอีกครั้งด้วยการสุ่มอย่างยุติธรรม Mood Pick, iCloud และเครื่องมือสำหรับนักสะสม",
        "today": "แผ่นประจำวัน",
        "today_desc": "เหตุผลที่เหมาะกับวันนี้เพื่อกลับมาฟังแผ่นที่คุณมีอยู่แล้ว โดยรักษาคอลเลกชันไว้บนอุปกรณ์ของคุณ",
        "today_points": ("จับคู่ข่าวดนตรีที่ตรวจสอบแล้ว วันครบรอบสำคัญ และคอนเสิร์ตใกล้เคียงกับคอลเลกชันบนอุปกรณ์เท่านั้น", "ทุกคำแนะนำอธิบายเหตุผลและแสดงแหล่งข้อมูลพร้อมวันที่", "การเตือนส่วนตัวและความคิดเห็นช่วยให้คำแนะนำมีประโยชน์ โดยไม่ส่งคอลเลกชันไปยังบริการข่าว"),
        "collection": "คอลเลกชันที่เป็นระเบียบและค้นพบได้เสมอ",
        "collection_desc": "เพิ่มอัลบั้มด้วยตนเอง สแกนบาร์โค้ด หรือนำเข้าไฟล์ เก็บข้อมูลฉบับ ภาพปก ประวัติ และรายการที่อยากได้อย่างชัดเจน",
        "mac_desc": "แอป Mac แบบเนทีฟสำหรับเรียกดู ปรับปรุง ตรวจสอบ และเลือกเพลงจากคอลเลกชันบนหน้าจอขนาดใหญ่",
        "privacy_desc": "ไม่มีบัญชี ไม่มีโฆษณา ไม่มีการติดตาม และไม่มีเซิร์ฟเวอร์ Record Picker ที่เก็บคอลเลกชันของคุณ",
        "features": ("นำเข้า CSV, สแกนบาร์โค้ด และเพิ่มข้อมูลด้วยตนเอง", "ค้นหาข้อมูลผ่าน MusicBrainz และ Discogs เมื่อคุณร้องขอ", "ตรวจสอบคุณภาพข้อมูล รายการซ้ำ และภาพปก", "เลือกแบบสุ่มหรือด้วย Mood Pick พร้อมตัวกรองและประวัติ", "ซิงค์ส่วนตัวผ่าน iCloud และสำรองข้อมูลเป็น JSON", "ฟรีสูงสุด 100 แผ่น ซื้อ Pro ครั้งเดียวเพื่อใช้คอลเลกชันไม่จำกัด"),
        "privacy_sections": (("ข้อมูลคอลเลกชัน", "อัลบั้ม รายการที่อยากได้ ประวัติ ภาพปก และบันทึกจะเก็บอยู่บนอุปกรณ์ และซิงค์กับฐานข้อมูล iCloud ส่วนตัวเมื่อคุณเปิดใช้ iCloud"), ("กล้องและบาร์โค้ด", "กล้องใช้เฉพาะเมื่อคุณเลือกสแกนบาร์โค้ด รูปจากกล้องจะไม่ถูกเก็บหรือแชร์"), ("การค้นหาข้อมูล", "MusicBrainz, Discogs และ Cover Art Archive จะถูกติดต่อเมื่อคุณเริ่มการค้นหาเท่านั้น"), ("คำแนะนำบนอุปกรณ์", "Mood Pick ใช้โมเดล Apple บนอุปกรณ์เมื่อพร้อมใช้งาน หรือคำนวณจากข้อมูลในคอลเลกชันโดยตรง"), ("นำเข้า ส่งออก และสำรองข้อมูล", "คุณเป็นผู้เลือกไฟล์และปลายทางทุกครั้ง ข้อมูลไม่ถูกล็อกในรูปแบบเฉพาะ"), ("การติดตามและโฆษณา", "Record Picker ไม่มี SDK โฆษณา ไม่ขายข้อมูล และไม่ใช้การติดตามโฆษณา")),
        "support_desc": "Record Picker ช่วยจัดการและค้นพบคอลเลกชันเพลงแบบกายภาพอีกครั้ง หากมีคำถามเกี่ยวกับแอป การนำเข้า การสำรองข้อมูล หรือความเป็นส่วนตัว โปรดติดต่อเรา",
        "guide_titles": ("วิธีเลือกแผ่นเสียงที่จะฟังต่อไป", "แอปสุ่มเลือกแผ่นเสียง", "จัดการและค้นพบคอลเลกชันแผ่นเสียงอีกครั้ง"),
        "guide_texts": ("เริ่มจากอารมณ์หรือเงื่อนไขง่าย ๆ แล้วใช้ปี ประเภท รูปแบบ รายการโปรด และประวัติเพื่อลดตัวเลือกโดยไม่เสียความสนุกของการค้นพบ", "การสุ่มที่ดีเคารพตัวกรอง รายการโปรด แผ่นที่งดชั่วคราว และความหลากหลายของศิลปิน จึงนำอัลบั้มที่ถูกลืมกลับมาฟังได้", "นำเข้าหรือเพิ่มคอลเลกชัน เติมข้อมูลและภาพปก สำรองข้อมูลเป็นประจำ แล้วใช้ตัวกรอง สถิติ และการเลือกเพื่อให้คอลเลกชันยังมีชีวิต"),
        "labels": ("หน้าหลัก", "ดูภาพหน้าจอ", "ติดต่อฝ่ายช่วยเหลือ", "คู่มือแผ่นเสียง", "คุณสมบัติทั้งหมด", "ความเป็นส่วนตัว", "ข้อกำหนด", "เวอร์ชันก่อนหน้า"),
    },
    "vi": {
        "html": "vi", "name": "Tiếng Việt", "store": "vn", "og": "vi_VN",
        "nav": ("Ứng dụng", "Phiên bản", "Ảnh chụp màn hình", "Hỗ trợ", "Quyền riêng tư", "Tính năng", "Ứng dụng Mac", "Ngôn ngữ"),
        "available": "Hiện đã có", "soon": "Sắp ra mắt · 1.10",
        "home_title": "Phát đúng đĩa nhạc - Record Picker",
        "home_desc": "Sắp xếp bộ sưu tập nhạc và chọn đĩa tiếp theo trên iPhone, iPad, Apple Watch và Mac.",
        "tagline": "Phát đúng đĩa nhạc",
        "intro": "Sắp xếp đĩa than, CD và album yêu thích, rồi khám phá lại bộ sưu tập bằng lựa chọn công bằng, Mood Pick, iCloud và các công cụ dành cho người sưu tầm.",
        "today": "Đĩa nhạc hôm nay",
        "today_desc": "Một lý do phù hợp với hôm nay để nghe lại đĩa bạn đã sở hữu, trong khi bộ sưu tập vẫn nằm trên thiết bị.",
        "today_points": ("Tin nhạc đã kiểm chứng, ngày kỷ niệm và buổi hòa nhạc gần đó được đối chiếu với bộ sưu tập ngay trên thiết bị", "Mỗi đề xuất giải thích lý do lựa chọn và dẫn nguồn có ngày tháng", "Lời nhắc riêng tư và phản hồi mức độ phù hợp cải thiện đề xuất mà không gửi bộ sưu tập đến dịch vụ tin tức"),
        "collection": "Bộ sưu tập gọn gàng, luôn dễ khám phá",
        "collection_desc": "Thêm album thủ công, quét mã vạch hoặc nhập tệp. Lưu đúng phiên bản, ảnh bìa, lịch sử và danh sách mong muốn trong một thư viện rõ ràng.",
        "mac_desc": "Ứng dụng Mac thuần native để duyệt, bổ sung, kiểm tra và chọn nhạc từ bộ sưu tập trên màn hình lớn.",
        "privacy_desc": "Không tài khoản, không quảng cáo, không theo dõi và không có máy chủ Record Picker lưu bộ sưu tập của bạn.",
        "features": ("Nhập CSV, quét mã vạch và thêm dữ liệu thủ công", "Tra cứu MusicBrainz và Discogs chỉ khi bạn yêu cầu", "Kiểm tra chất lượng dữ liệu, bản trùng lặp và ảnh bìa", "Chọn ngẫu nhiên hoặc Mood Pick với bộ lọc và lịch sử", "Đồng bộ riêng tư qua iCloud và sao lưu JSON", "Miễn phí tối đa 100 đĩa; mua Pro một lần để mở khóa bộ sưu tập không giới hạn"),
        "privacy_sections": (("Dữ liệu bộ sưu tập", "Album, danh sách mong muốn, lịch sử, ảnh bìa và ghi chú được lưu trên thiết bị và có thể đồng bộ với cơ sở dữ liệu iCloud riêng tư khi bạn bật iCloud."), ("Camera và mã vạch", "Camera chỉ được dùng khi bạn chủ động quét mã vạch. Ảnh camera không được Record Picker lưu hoặc chia sẻ."), ("Tra cứu siêu dữ liệu", "MusicBrainz, Discogs và Cover Art Archive chỉ được liên hệ khi bạn bắt đầu một lượt tìm kiếm."), ("Đề xuất trên thiết bị", "Mood Pick dùng mô hình Apple trên thiết bị khi có sẵn hoặc tính toán cục bộ từ dữ liệu bộ sưu tập."), ("Nhập, xuất và sao lưu", "Bạn luôn chọn tệp và đích đến. Dữ liệu không bị khóa trong một định dạng độc quyền."), ("Theo dõi và quảng cáo", "Record Picker không có SDK quảng cáo, không bán dữ liệu và không theo dõi quảng cáo.")),
        "support_desc": "Record Picker giúp bạn quản lý và khám phá lại bộ sưu tập nhạc vật lý. Nếu có câu hỏi về ứng dụng, nhập dữ liệu, sao lưu hoặc quyền riêng tư, hãy liên hệ với chúng tôi.",
        "guide_titles": ("Cách chọn đĩa than để nghe tiếp theo", "Ứng dụng chọn đĩa than ngẫu nhiên", "Quản lý và khám phá lại bộ sưu tập đĩa than"),
        "guide_texts": ("Hãy bắt đầu bằng tâm trạng hoặc một điều kiện đơn giản, sau đó dùng năm, thể loại, định dạng, mục yêu thích và lịch sử để thu hẹp lựa chọn mà vẫn giữ niềm vui khám phá.", "Một lượt chọn ngẫu nhiên tốt tôn trọng bộ lọc, mục yêu thích, loại trừ tạm thời và sự đa dạng nghệ sĩ, nhờ đó đưa album bị lãng quên trở lại vòng quay.", "Nhập hoặc thêm bộ sưu tập, hoàn thiện siêu dữ liệu và ảnh bìa, sao lưu thường xuyên, rồi dùng bộ lọc, thống kê và lượt chọn để giữ bộ sưu tập luôn sống động."),
        "labels": ("Trang chủ", "Xem ảnh chụp màn hình", "Liên hệ hỗ trợ", "Hướng dẫn đĩa than", "Tất cả tính năng", "Quyền riêng tư", "Yêu cầu", "Phiên bản trước"),
    },
}


def picture(prefix: str, name: str, width: int, height: int, css: str) -> str:
    base = f"{prefix}assets/screenshots/v19/en-us/{name}"
    stem = base.rsplit(".", 1)[0]
    return (f'<figure class="{css}"><picture><source srcset="{stem}.avif" type="image/avif">'
            f'<source srcset="{stem}.webp" type="image/webp"><img loading="lazy" alt="" '
            f'src="{base}" width="{width}" height="{height}" decoding="async"></picture>'
            f'<figcaption>Record Picker 1.9</figcaption></figure>')


def main_markup(kind: str, d: dict[str, object]) -> str:
    prefix = "../" if kind == "index.html" else "../../"
    available, soon = d["available"], d["soon"]
    home, shots, contact, guides, all_features, privacy, requirements, previous = d["labels"]
    iphone = picture(prefix, "iphone-today-pick.png", 1206, 2622, "current-screen v19-home-phone")
    mac = picture(prefix, "mac-today-pick.png", 1280, 900, "current-screen v19-home-mac")
    ipad = picture(prefix, "ipad-collection-grid.png", 1200, 1600, "current-screen v19-home-ipad")
    if kind == "index.html":
        points = "".join(f"<li>{x}</li>" for x in d["today_points"])
        facts = "".join(f'<article class="fact-card"><strong>{x}</strong></article>' for x in ("iPhone · iPad · Apple Watch · Mac", "Free · Pro", available))
        return (f'<main id="main-content"><section class="hero"><div class="hero-copy"><h1>Record Picker</h1><h2>{d["tagline"]}</h2><p>{d["intro"]}</p><div class="cta-row"><a class="button primary" href="https://apps.apple.com/{d["store"]}/app/recordpicker/id6780422305">App Store</a><a class="button glass" href="mac-app/">{d["nav"][6]}</a></div></div><div class="hero-showcase v19-hero-showcase">{mac}</div></section>'
                f'<section class="facts-band"><div class="facts-grid">{facts}</div></section>'
                f'<section class="section next-release" data-release-version="1.10"><div class="section-head"><p class="kicker">{soon}</p><h2>Record Picker 1.10</h2></div></section>'
                f'<section class="section upcoming-showcase" id="versions" data-release-version="1.9"><div class="section-head"><p class="kicker">{available}</p><h2>Record Picker 1.9 · {d["today"]}</h2><p class="lead">{d["today_desc"]}</p></div><ul>{points}</ul><div class="upcoming-platforms"><span class="is-available">iPhone · iPad · Mac · Apple Watch · {available}</span></div></section>'
                f'<section class="section mac-teaser"><h2>Record Picker for Mac</h2><p>{d["mac_desc"]}</p></section><section class="section split"><h2>{d["collection"]}</h2><p>{d["collection_desc"]}</p></section>'
                f'<section class="section privacy-compact" id="privacy"><div><h2>{privacy}</h2><p class="lead">{d["privacy_desc"]}</p><a class="button glass" href="privacy/">{privacy}</a></div></section>'
                f'<section class="section gallery"><h2>{shots}</h2><div class="screen-grid current-screens v19-home-screens">{iphone}{mac}{ipad}</div></section><section class="section seo-links"><h2>{guides}</h2></section><section class="contact-band"><h2>{contact}</h2><a href="mailto:support@recordpicker.app">support@recordpicker.app</a></section></main>')
    if kind == "screenshots/index.html":
        points = "".join(f"<li>{x}</li>" for x in d["today_points"])
        return (f'<main id="main-content" class="screens-shell"><section class="screens-hero"><h1>{shots}</h1><p>{d["intro"]}</p><a class="button glass" href="../index.html">{home}</a></section><section class="media-section next-release" data-release-version="1.10"><div class="section-head"><p class="kicker">{soon}</p><h2>Record Picker 1.10</h2></div></section><section class="media-section upcoming-gallery-intro" data-release-version="1.9"><div class="section-head"><p class="kicker">{available}</p><h2>Record Picker 1.9 · {d["today"]}</h2><p class="lead">{d["today_desc"]}</p></div><ul>{points}</ul></section><section class="media-section v19-screenshot-gallery" data-release-gallery="1.9"><div class="section-head"><h2>Record Picker 1.9</h2></div><div class="shot-grid v19-grid">{iphone}{mac}{ipad}</div></section><details class="screenshot-archive" data-previous-versions><summary>{previous} · Record Picker ≤ 1.8</summary><div class="screenshot-archive-content"><p>{d["collection_desc"]}</p></div></details></main>')
    if kind == "readme/index.html":
        features = "".join(f"<li>{x}</li>" for x in d["features"])
        points = "".join(f"<li>{x}</li>" for x in d["today_points"])
        return (f'<main id="main-content" class="doc-shell"><section class="doc-hero"><h1>{all_features}</h1><p>{d["intro"]}</p></section><section class="doc-content"><h2>{d["collection"]}</h2><ul>{features}</ul><h2>{d["today"]}</h2><div class="release-list"><article class="release-card release-preview release-upcoming" data-release-version="1.10"><div><h3>Record Picker 1.10</h3><p class="release-platform-summary"><strong>{soon}</strong></p></div></article><article class="release-card" data-release-version="1.9"><div><h3>Record Picker 1.9</h3><p class="release-platform-summary"><strong>iPhone · iPad · Mac · Apple Watch · {available}</strong></p></div><ul>{points}</ul></article><article class="release-card" data-release-version="1.8"><div><h3>Record Picker 1.8</h3></div><ul><li>{d["collection_desc"]}</li><li>{d["privacy_desc"]}</li></ul></article></div></section></main>')
    if kind == "privacy/index.html":
        sections = "".join(f"<section><h2>{h}</h2><p>{p}</p></section>" for h, p in d["privacy_sections"])
        return f'<main id="main-content" class="doc-shell"><section class="doc-hero"><h1>{privacy}</h1><p>{d["privacy_desc"]}</p></section><section class="doc-content">{sections}<section><h2>{contact}</h2><p><a href="mailto:support@recordpicker.app">support@recordpicker.app</a></p></section></section></main>'
    if kind == "support/index.html":
        return f'<main id="main-content" class="doc-shell"><section class="doc-hero"><h1>{d["nav"][3]}</h1><p>{d["support_desc"]}</p></section><section class="doc-content"><h2>{contact}</h2><p><a href="mailto:support@recordpicker.app">support@recordpicker.app</a></p><p>{d["privacy_desc"]} <a href="../privacy/">{privacy}</a></p></section></main>'
    if kind == "mac-app/index.html":
        items = "".join(f"<li>{x}</li>" for x in d["features"])
        return f'<main id="main-content" class="doc-shell"><section class="doc-hero mac-hero"><p class="eyebrow">Mac · Record Picker 1.9</p><h1>Record Picker for Mac</h1><p>{d["mac_desc"]}</p><a class="button primary" href="https://apps.apple.com/{d["store"]}/app/recordpicker/id6780422305">App Store</a></section><section class="doc-content mac-content"><h2>{d["collection"]}</h2><p>{d["collection_desc"]}</p><ul>{items}</ul>{mac}<section class="seo-checklist"><h2>{requirements}</h2><p>macOS 26.0+</p></section></section></main>'
    guide_index = {"choose-vinyl-record/index.html": 0, "random-vinyl-record-picker/index.html": 1, "manage-vinyl-collection/index.html": 2}[kind]
    title, body = d["guide_titles"][guide_index], d["guide_texts"][guide_index]
    takeaways = "".join(f"<li>{x}</li>" for x in d["features"][guide_index:guide_index + 4])
    return f'<main id="main-content" class="doc-shell"><section class="doc-content seo-content"><p class="eyebrow">{guides}</p><h1>{title}</h1><p class="lead">{body}</p><a class="button primary" href="../screenshots/">{shots}</a><section class="seo-section"><h2>{d["collection"]}</h2><p>{d["collection_desc"]}</p></section><section class="seo-section"><h2>{d["today"]}</h2><p>{d["today_desc"]}</p></section><section class="seo-checklist"><h2>{all_features}</h2><ul>{takeaways}</ul></section></section></main>'


def replace_meta(text: str, kind: str, locale: str, d: dict[str, object]) -> str:
    titles = {"index.html": d["home_title"], "screenshots/index.html": d["nav"][2] + " - Record Picker", "support/index.html": d["nav"][3] + " - Record Picker", "privacy/index.html": d["nav"][4] + " - Record Picker", "readme/index.html": d["nav"][5] + " - Record Picker", "mac-app/index.html": "Record Picker for Mac", "choose-vinyl-record/index.html": d["guide_titles"][0], "random-vinyl-record-picker/index.html": d["guide_titles"][1], "manage-vinyl-collection/index.html": d["guide_titles"][2]}
    title, description = titles[kind], d["home_desc"]
    suffix = "" if kind == "index.html" else kind.removesuffix("index.html")
    url = f"https://recordpicker.app/{locale}/{suffix}"
    text = re.sub(r'<html lang="[^"]+"(?: dir="rtl")?>', f'<html lang="{d["html"]}">', text, count=1)
    text = text.replace('data-page-lang="en-us"', f'data-page-lang="{locale}"')
    text = re.sub(r'<title>.*?</title>', f'<title>{escape(str(title))}</title>', text, count=1)
    for attr, name, value in (("name", "description", description), ("property", "og:title", title), ("property", "og:description", description), ("property", "og:url", url), ("name", "twitter:title", title), ("name", "twitter:description", description)):
        text = re.sub(rf'(<meta {attr}="{re.escape(name)}" content=")[^"]*(")', rf'\g<1>{escape(str(value), quote=True)}\2', text, count=1)
    text = re.sub(r'<link rel="canonical" href="[^"]+">', f'<link rel="canonical" href="{url}">', text, count=1)
    text = re.sub(r'<meta property="og:locale" content="[^"]+">', f'<meta property="og:locale" content="{d["og"]}">', text, count=1)
    text = re.sub(r'<main\b.*?</main>', main_markup(kind, d), text, count=1, flags=re.DOTALL)
    text = text.replace('aria-selected="true"', 'aria-selected="false"')
    replacements = dict(zip(("App", "Versions", "Screenshots", "Support", "Privacy", "Features", "Mac app", "Language"), d["nav"]))
    replacements.update({"Skip to content": d["nav"][0], "English (US)": d["name"], "Vinyl guides": d["labels"][3]})
    for source, target in replacements.items():
        text = text.replace(f">{source}<", f">{target}<")
    text = re.sub(r'https://apps\.apple\.com/[a-z-]+/app/recordpicker/id6780422305', f'https://apps.apple.com/{d["store"]}/app/recordpicker/id6780422305', text)
    return text


def language_option(locale: str, name: str, kind: str, selected: bool = False) -> str:
    suffix = "" if kind == "index.html" else kind.removesuffix("index.html")
    return f'<a class="language-option" href="/{locale}/{suffix}" hreflang="{locale}" role="option" data-language-option data-language-value="{locale}" data-language-name="{name}" aria-selected="{str(selected).lower()}">{name}</a>'


def add_language_links(text: str, kind: str, selected: str | None = None) -> str:
    for locale, name in (("es-mx", "Español (México)"), ("th", "ไทย"), ("vi", "Tiếng Việt")):
        if f'data-language-value="{locale}"' not in text:
            text = text.replace('</div></div></div></header>', language_option(locale, name, kind, locale == selected) + '</div></div></div></header>', 1)
        suffix = "" if kind == "index.html" else kind.removesuffix("index.html")
        hreflang = {"es-mx": "es-MX", "th": "th", "vi": "vi"}[locale]
        link = f'<link rel="alternate" hreflang="{hreflang}" href="https://recordpicker.app/{locale}/{suffix}">'
        if link not in text:
            text = text.replace('<link rel="alternate" hreflang="x-default"', link + '<link rel="alternate" hreflang="x-default"', 1)
    if selected:
        text = re.sub(
            r'(<a class="language-option"[^>]*aria-selected=")true(")',
            r'\1false\2',
            text,
        )
        text = re.sub(
            rf'(<a class="language-option"[^>]*data-language-value="{re.escape(selected)}"[^>]*aria-selected=")false(")',
            r'\1true\2',
            text,
            count=1,
        )
    return text


def update_sitemaps() -> None:
    today = date.today().isoformat()
    sitemap = ROOT / "sitemap.xml"
    text = sitemap.read_text(encoding="utf-8")
    for locale in ("es-mx", "th", "vi"):
        for kind in PAGE_KINDS:
            suffix = "" if kind == "index.html" else kind.removesuffix("index.html")
            url = f"https://recordpicker.app/{locale}/{suffix}"
            if f"<loc>{url}</loc>" not in text:
                text = text.replace(
                    "</urlset>",
                    f"  <url>\n    <loc>{url}</loc>\n    <lastmod>{today}</lastmod>\n  </url>\n</urlset>",
                    1,
                )
    sitemap.write_text(text, encoding="utf-8")

    media = ROOT / "sitemap-media.xml"
    text = media.read_text(encoding="utf-8")
    for locale in ("es-mx", "th", "vi"):
        for kind in PAGE_KINDS:
            suffix = "" if kind == "index.html" else kind.removesuffix("index.html")
            source_url = f"https://recordpicker.app/en-us/{suffix}"
            target_url = f"https://recordpicker.app/{locale}/{suffix}"
            if f"<loc>{target_url}</loc>" in text:
                continue
            block = re.search(
                rf"  <url>\n    <loc>{re.escape(source_url)}</loc>.*?  </url>\n",
                text,
                flags=re.DOTALL,
            )
            if not block:
                raise RuntimeError(f"No media sitemap template for {source_url}")
            localized = block.group(0).replace(
                f"<loc>{source_url}</loc>", f"<loc>{target_url}</loc>", 1
            )
            text = text.replace("</urlset>", localized + "</urlset>", 1)
    media.write_text(text, encoding="utf-8")


def main() -> None:
    # Mexican Spanish uses the fully reviewed Spanish site as its regional base.
    target = ROOT / "es-mx"
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(ROOT / "es-es", target)
    for path in target.rglob("*.html"):
        kind = path.relative_to(target).as_posix()
        text = path.read_text(encoding="utf-8")
        text = text.replace('<html lang="es-ES">', '<html lang="es-MX">')
        text = text.replace('data-page-lang="es-es"', 'data-page-lang="es-mx"')
        text = text.replace('https://recordpicker.app/es-es/', 'https://recordpicker.app/es-mx/')
        text = text.replace('/es-es/', '/es-mx/')
        text = text.replace(
            '<link rel="alternate" hreflang="es-ES" href="https://recordpicker.app/es-mx/',
            '<link rel="alternate" hreflang="es-ES" href="https://recordpicker.app/es-es/',
        )
        text = re.sub(
            r'(href=")/es-mx/([^" ]*" hreflang="es-ES"[^>]*data-language-value="es-es")',
            r'\1/es-es/\2',
            text,
        )
        text = text.replace(
            '<meta property="og:locale" content="es_ES">',
            '<meta property="og:locale" content="es_MX">',
        )
        text = text.replace('https://apps.apple.com/es/', 'https://apps.apple.com/mx/')
        text = text.replace(
            '<span data-language-current>Español</span>',
            '<span data-language-current>Español (México)</span>',
        )
        text = text.replace('aria-selected="true"', 'aria-selected="false"')
        text = add_language_links(text, kind, "es-mx")
        path.write_text(text, encoding="utf-8")
    for locale, data in DATA.items():
        target = ROOT / locale
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(ROOT / "en-us", target)
        for path in target.rglob("*.html"):
            kind = path.relative_to(target).as_posix()
            text = replace_meta(path.read_text(encoding="utf-8"), kind, locale, data)
            text = add_language_links(text, kind, locale)
            path.write_text(text, encoding="utf-8")
    for page in ROOT.rglob("*.html"):
        if "assets" in page.parts or "th" in page.parts or "vi" in page.parts or "es-mx" in page.parts:
            continue
        parts = page.relative_to(ROOT).parts
        kind = "/".join(parts[1:]) if parts and parts[0] in {p.name for p in ROOT.iterdir() if p.is_dir()} else "/".join(parts)
        if kind in PAGE_KINDS:
            page.write_text(add_language_links(page.read_text(encoding="utf-8"), kind), encoding="utf-8")
    for page in ROOT.rglob("*.html"):
        text = page.read_text(encoding="utf-8").replace(
            "site.js?v=20260807-quality", "site.js?v=20260808-v19-locales"
        )
        page.write_text(text, encoding="utf-8")
    update_sitemaps()
    print("Added complete es-MX, Thai and Vietnamese site trees.")


if __name__ == "__main__":
    main()
