(function () {
  var body = document.body;
  var locales = [
    { id: "ar", label: "العربية", dir: "rtl" },
    { id: "de", label: "Deutsch", dir: "ltr" },
    { id: "en-us", label: "English (US)", dir: "ltr" },
    { id: "en-gb", label: "English (UK)", dir: "ltr" },
    { id: "ko", label: "한국어", dir: "ltr" },
    { id: "zh-hans", label: "简体中文", dir: "ltr" },
    { id: "zh-hant", label: "繁體中文", dir: "ltr" },
    { id: "es-es", label: "Español", dir: "ltr" },
    { id: "fr", label: "Français", dir: "ltr" },
    { id: "el", label: "Ελληνικά", dir: "ltr" },
    { id: "he", label: "עברית", dir: "rtl" },
    { id: "it", label: "Italiano", dir: "ltr" },
    { id: "ja", label: "日本語", dir: "ltr" },
    { id: "nl", label: "Nederlands", dir: "ltr" },
    { id: "pl", label: "Polski", dir: "ltr" },
    { id: "pt-pt", label: "Português", dir: "ltr" }
  ];
  var localeMap = locales.reduce(function (map, locale) {
    map[locale.id] = locale;
    return map;
  }, {});
  function normalizeLanguage(value) {
    var lang = (value || "").toLowerCase().replace("_", "-");
    if (!lang) return "fr";
    if (localeMap[lang]) return lang;
    if (lang === "en") return "en-us";
    if (lang === "pt" || lang.indexOf("pt-") === 0) return "pt-pt";
    if (lang.indexOf("zh") === 0) {
      return lang.indexOf("hant") !== -1 || lang.indexOf("tw") !== -1 || lang.indexOf("hk") !== -1 ? "zh-hant" : "zh-hans";
    }
    var prefix = lang.split("-")[0];
    var prefixMap = { ar: "ar", de: "de", ko: "ko", es: "es-es", fr: "fr", el: "el", he: "he", it: "it", ja: "ja", nl: "nl", pl: "pl" };
    return prefixMap[prefix] || "en-us";
  }
  function browserLanguage() {
    var languages = navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language || ""];
    for (var i = 0; i < languages.length; i += 1) {
      var normalized = normalizeLanguage(languages[i]);
      if (normalized) return normalized;
    }
    return "fr";
  }
  function preferredLanguage() {
    try {
      return normalizeLanguage(localStorage.getItem("recordpicker-language") || browserLanguage());
    } catch (error) {
      return "fr";
    }
  }
  function addLanguageStyle() {
    if (document.querySelector("[data-language-patch-style]")) return;
    var style = document.createElement("style");
    style.setAttribute("data-language-patch-style", "");
    style.textContent = ".language-menu{display:inline-flex;align-items:center;border:1px solid rgba(17,17,20,.08);border-radius:999px;background:rgba(255,255,255,.66);box-shadow:0 12px 32px rgba(17,17,20,.07);backdrop-filter:blur(22px) saturate(1.28);padding:4px 8px}.language-menu select{max-width:168px;border:0;border-radius:999px;background:transparent;color:var(--red);cursor:pointer;font-weight:650;padding:7px 2px;outline:none}html[dir='rtl'] .language-menu select{direction:rtl}.visually-hidden{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;border:0}";
    document.head.appendChild(style);
  }
  function installLanguageMenu(selected) {
    addLanguageStyle();
    var existing = document.querySelector("[data-language-select]");
    if (existing) return existing;
    var label = document.createElement("label");
    label.className = "language-menu";
    var hidden = document.createElement("span");
    hidden.className = "visually-hidden";
    hidden.textContent = "Language";
    var select = document.createElement("select");
    select.setAttribute("data-language-select", "");
    select.setAttribute("aria-label", "Language");
    locales.forEach(function (locale) {
      var option = document.createElement("option");
      option.value = locale.id;
      option.textContent = locale.label;
      select.appendChild(option);
    });
    select.value = selected;
    select.addEventListener("change", function () {
      setLang(select.value);
    });
    label.appendChild(hidden);
    label.appendChild(select);
    var oldSwitch = document.querySelector(".lang-switch");
    if (oldSwitch && oldSwitch.parentNode) {
      oldSwitch.parentNode.replaceChild(label, oldSwitch);
    } else {
      var actions = document.querySelector(".header-actions");
      if (actions) actions.appendChild(label);
    }
    return select;
  }

  var liveLocaleText = { el: {"App":"Εφαρμογή","Versions":"Εκδόσεις","Screenshots":"Στιγμιότυπα","Support":"Υποστήριξη","Privacy":"Απόρρητο","Features":"Λειτουργίες","Never wonder what record to play next":"Μην αναρωτιέστε ξανά ποιον δίσκο να παίξετε μετά","Rediscover your music collection with smart random picks, a clear record bin, a wishlist, statistics, and import/export tools built for real collectors.":"Ανακαλύψτε ξανά τη μουσική συλλογή σας με έξυπνες τυχαίες επιλογές, καθαρό κατάλογο δίσκων, λίστα επιθυμιών, στατιστικά και εργαλεία εισαγωγής/εξαγωγής.","Music":"Μουσική","View on the App Store":"Προβολή στο App Store","iPad draw view and controls":"Προβολή επιλογής και ελέγχων στο iPad","June 18, 2026":"18 Ιουνίου 2026","EUR 2.99":"2,99 EUR","Choose what to play without losing control":"Επιλέξτε τι θα παίξει χωρίς να χάνετε τον έλεγχο","Record Picker catalogs vinyl, CDs, and favorite albums, then suggests the next record to play based on filters, favorites, exclusions, and the mood of the moment.":"Το Record Picker καταλογογραφεί βινύλια, CD και αγαπημένα άλμπουμ και προτείνει τον επόμενο δίσκο με βάση φίλτρα, αγαπημένα, εξαιρέσεις και διάθεση.","Controlled random draw":"Ελεγχόμενη τυχαία επιλογή","Pick an available album, avoid repeating the same artist, favor favorites, and keep temporary exclusions under control.":"Επιλέξτε διαθέσιμο άλμπουμ, αποφύγετε τον ίδιο καλλιτέχνη, δώστε προτεραιότητα στα αγαπημένα και ελέγξτε προσωρινές εξαιρέσεις.","Readable record bin":"Καθαρή θήκη δίσκων","Browse the collection with search, sorting, filters, large covers, and quick access to editable record details.":"Περιηγηθείτε στη συλλογή με αναζήτηση, ταξινόμηση, φίλτρα, μεγάλες εικόνες εξωφύλλων και γρήγορη πρόσβαση σε επεξεργάσιμες λεπτομέρειες.","Moods and history":"Διαθέσεις και ιστορικό","Choose by mood and keep a listening trail so the collection keeps revealing itself over time.":"Επιλέξτε με βάση τη διάθεση και κρατήστε ιστορικό ακρόασης ώστε η συλλογή να αποκαλύπτεται με τον χρόνο.","Data under control":"Δεδομένα υπό έλεγχο","CSV import, backups, restore, MusicBrainz, Discogs, and artwork lookups are always started deliberately.":"Η εισαγωγή CSV, τα αντίγραφα ασφαλείας, η επαναφορά, το MusicBrainz, το Discogs και η αναζήτηση εξωφύλλων ξεκινούν πάντα σκόπιμα.","App Store Version History":"Ιστορικό εκδόσεων App Store","Notes retrieved from the French App Store listing for Record Picker on June 18, 2026.":"Σημειώσεις από τη γαλλική καταχώριση App Store του Record Picker στις 18 Ιουνίου 2026.","Current App Store version":"Τρέχουσα έκδοση στο App Store","Full music collection catalog for imports, manual album entry, and barcode scanning.":"Πλήρης μουσικός κατάλογος για εισαγωγές, χειροκίνητη καταχώριση και σάρωση κωδίκων.","Animated random draw, year filters, favorites, temporary exclusions, listening history, and collection statistics.":"Κινούμενη τυχαία επιλογή, φίλτρα έτους, αγαπημένα, προσωρινές εξαιρέσεις, ιστορικό και στατιστικά.","Mood-based picking with local Apple models when available, otherwise on-device matching from collection metadata.":"Επιλογή διάθεσης με τοπικά μοντέλα Apple όταν υπάρχουν, αλλιώς τοπική αντιστοίχιση από μεταδεδομένα.","MusicBrainz metadata lookup, Cover Art Archive artwork or manual artwork import, backup/restore, Siri Shortcuts, and Apple Watch companion.":"Αναζήτηση MusicBrainz, Cover Art Archive ή χειροκίνητα εξώφυλλα, αντίγραφα/επαναφορά, Siri Shortcuts και Apple Watch.","The collection stays stored locally; metadata and artwork lookups happen only when the user starts them.":"Η συλλογή μένει τοπική· οι αναζητήσεις μεταδεδομένων και εξωφύλλων γίνονται μόνο όταν τις ξεκινά ο χρήστης.","App Store improvements":"Βελτιώσεις App Store","Interface and internal foundations refined for a smoother experience.":"Βελτιώθηκαν η διεπαφή και τα εσωτερικά θεμέλια για πιο ομαλή εμπειρία.","Improved iPad support.":"Βελτιωμένη υποστήριξη iPad.","Mood-based picking with better use of critical reviews.":"Επιλογή διάθεσης με καλύτερη αξιοποίηση κριτικών.","Data quality: record detail sheets, manual row deletion, Discogs/MusicBrainz searches.":"Ποιότητα δεδομένων: καρτέλες δίσκου, χειροκίνητη διαγραφή γραμμών και αναζητήσεις Discogs/MusicBrainz.","Missing tracks: MusicBrainz search followed by Discogs search.":"Ελλιπή κομμάτια: αναζήτηση MusicBrainz και μετά Discogs.","Initial release":"Πρώτη κυκλοφορία","No public note is displayed in the App Store history.":"Δεν εμφανίζεται δημόσια σημείωση στο ιστορικό App Store.","User support":"Υποστήριξη χρήστη","The support page answers quickly about import, backups, external lookups, privacy, and direct contact.":"Η σελίδα υποστήριξης απαντά γρήγορα για εισαγωγή, αντίγραφα, εξωτερικές αναζητήσεις, απόρρητο και επαφή.","Open support":"Άνοιγμα υποστήριξης","Import":"Εισαγωγή","CSV import, backup restore, barcode scanning, and manual entry help users start even with an incomplete catalog.":"Η εισαγωγή CSV, η επαναφορά αντιγράφων, η σάρωση κωδικών και η χειροκίνητη καταχώριση βοηθούν ακόμη και με ελλιπή κατάλογο.","Export":"Εξαγωγή","Backups, readable CSV, and JSON exports are deliberately started by the user and saved to the destination they choose.":"Τα αντίγραφα και οι εξαγωγές CSV/JSON ξεκινούν από τον χρήστη και αποθηκεύονται στον προορισμό που επιλέγει.","Complete":"Συμπλήρωση","MusicBrainz, Discogs, and Cover Art Archive are used only when a lookup or enrichment action is started.":"MusicBrainz, Discogs και Cover Art Archive χρησιμοποιούνται μόνο όταν ξεκινά αναζήτηση ή εμπλουτισμός.","Privacy Policy":"Πολιτική απορρήτου","iPhone reference screenshot":"Στιγμιότυπο αναφοράς iPhone","The iPhone screenshot complements the iPad home view without reusing the same image twice.":"Το στιγμιότυπο iPhone συμπληρώνει την προβολή iPad της αρχικής σελίδας χωρίς να επαναχρησιμοποιεί την ίδια εικόνα.","View all screenshots":"Δείτε όλα τα στιγμιότυπα","iPhone draw view":"Προβολή επιλογής στο iPhone","Record Picker Support":"Υποστήριξη Record Picker","For questions about the app, import, backups, or privacy, use the public support contact.":"Για ερωτήσεις σχετικά με την εφαρμογή, την εισαγωγή, τα αντίγραφα ή το απόρρητο, χρησιμοποιήστε τη δημόσια επαφή υποστήριξης.","Record Picker v1.2 - discovery/support":"Record Picker v1.2 - γνωριμία/υποστήριξη"} };
  function applyLocaleText(locale) {
    var dictionary = liveLocaleText[locale] || null;
    document.querySelectorAll(".lang-en").forEach(function (node) {
      if (!node.dataset.sourceText) {
        node.dataset.sourceText = node.textContent;
      }
      var source = node.dataset.sourceText;
      node.textContent = dictionary && dictionary[source] ? dictionary[source] : source;
    });
  }
  function setLang(lang) {
    var locale = localeMap[lang] ? lang : normalizeLanguage(lang);
    var displayLang = locale === "fr" ? "fr" : "en";
    body.dataset.lang = displayLang;
    body.dataset.locale = locale;
    document.documentElement.lang = locale;
    document.documentElement.dir = localeMap[locale] && localeMap[locale].dir === "rtl" ? "rtl" : "ltr";
    document.querySelectorAll("[data-language-select]").forEach(function (select) {
      select.value = locale;
    });
    applyLocaleText(locale);
    try { localStorage.setItem("recordpicker-language", locale); } catch (error) {}
  }
  document.querySelectorAll(".hero-note").forEach(function (note) {
    note.remove();
  });
  document.querySelectorAll(".hero-copy .glass-pill.eyebrow").forEach(function (badge) {
    badge.remove();
  });
  var heroCopy = document.querySelector(".hero-copy");
  if (heroCopy && !heroCopy.querySelector(".tagline")) {
    var title = heroCopy.querySelector("h1");
    var tagline = document.createElement("p");
    tagline.className = "tagline";
    tagline.style.cssText = "margin:18px 0 0;max-width:620px;color:var(--ink);font-size:clamp(1.35rem,3vw,2.15rem);font-weight:850;line-height:1.16;";
    tagline.innerHTML = '<span class="lang-fr">Ne vous demandez plus jamais quel disque écouter ensuite.</span><span class="lang-en">Never wonder what record to play next</span>';
    if (title) {
      title.insertAdjacentElement("afterend", tagline);
    }
  }
  document.querySelectorAll("[data-set-lang]").forEach(function (button) {
    button.addEventListener("click", function () {
      setLang(button.getAttribute("data-set-lang") === "fr" ? "fr" : "en-us");
    });
  });
  var preferred = preferredLanguage();
  installLanguageMenu(preferred);
  var lightbox = document.querySelector("[data-video-lightbox]");
  if (lightbox) {
    var video = lightbox.querySelector("video");
    var videoTitle = lightbox.querySelector("[data-video-title]");
    function closeVideo() {
      lightbox.setAttribute("hidden", "");
      lightbox.setAttribute("aria-hidden", "true");
      body.classList.remove("video-lightbox-open");
      if (video) {
        video.pause();
        video.removeAttribute("src");
        video.removeAttribute("poster");
        video.load();
      }
    }
    document.querySelectorAll("[data-video-src]").forEach(function (trigger) {
      trigger.addEventListener("click", function () {
        var lang = body.dataset.lang === "en" ? "en" : "fr";
        if (videoTitle) {
          videoTitle.textContent = trigger.getAttribute(lang === "en" ? "data-title-en" : "data-title-fr") || "";
        }
        if (video) {
          video.setAttribute("poster", trigger.getAttribute("data-video-poster") || "");
          video.setAttribute("src", trigger.getAttribute("data-video-src") || "");
          video.load();
        }
        lightbox.removeAttribute("hidden");
        lightbox.setAttribute("aria-hidden", "false");
        body.classList.add("video-lightbox-open");
        if (video) {
          var playback = video.play();
          if (playback && playback.catch) {
            playback.catch(function () {});
          }
        }
      });
    });
    lightbox.querySelectorAll("[data-video-close]").forEach(function (button) {
      button.addEventListener("click", closeVideo);
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && !lightbox.hasAttribute("hidden")) {
        closeVideo();
      }
    });
  }
  setLang(preferred);
})();
