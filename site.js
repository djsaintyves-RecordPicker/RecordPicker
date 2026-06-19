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
