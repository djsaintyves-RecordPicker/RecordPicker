(function () {
  var body = document.body;
  var locales = [{"id":"ar","code":"ar","name":"العربية","rtl":true},{"id":"de","code":"de","name":"Deutsch","rtl":false},{"id":"en-au","code":"en-AU","name":"English (Australia)","rtl":false},{"id":"en-ca","code":"en-CA","name":"English (Canada)","rtl":false},{"id":"en-us","code":"en-US","name":"English (US)","rtl":false},{"id":"en-gb","code":"en-GB","name":"English (UK)","rtl":false},{"id":"ca","code":"ca","name":"Català","rtl":false},{"id":"ko","code":"ko","name":"한국어","rtl":false},{"id":"zh-hans","code":"zh-Hans","name":"简体中文","rtl":false},{"id":"zh-hant","code":"zh-Hant","name":"繁體中文","rtl":false},{"id":"da","code":"da","name":"Dansk","rtl":false},{"id":"es-es","code":"es-ES","name":"Español","rtl":false},{"id":"fi","code":"fi","name":"Suomi","rtl":false},{"id":"fr-ca","code":"fr-CA","name":"Français (Canada)","rtl":false},{"id":"fr","code":"fr-FR","name":"Français (France)","rtl":false},{"id":"el","code":"el","name":"Ελληνικά","rtl":false},{"id":"he","code":"he","name":"עברית","rtl":true},{"id":"hi","code":"hi","name":"हिन्दी","rtl":false},{"id":"id","code":"id","name":"Bahasa Indonesia","rtl":false},{"id":"it","code":"it","name":"Italiano","rtl":false},{"id":"ja","code":"ja","name":"日本語","rtl":false},{"id":"nl","code":"nl","name":"Nederlands","rtl":false},{"id":"nb","code":"nb","name":"Norsk","rtl":false},{"id":"pl","code":"pl","name":"Polski","rtl":false},{"id":"pt-br","code":"pt-BR","name":"Português (Brasil)","rtl":false},{"id":"pt-pt","code":"pt-PT","name":"Português (Portugal)","rtl":false},{"id":"ru","code":"ru","name":"Русский","rtl":false},{"id":"sv","code":"sv","name":"Svenska","rtl":false},{"id":"tr","code":"tr","name":"Türkçe","rtl":false}];
  var translations = [];
  var localeFallbacks = {"en-au":"en-gb","en-ca":"en-gb","fr-ca":"fr","pt-br":"pt-pt"};
  var languageStorageKey = "recordpicker-language";
  var manualLanguageKey = "recordpicker-language-manual";
  var localeMap = {};
  var localeIndexes = {};
  locales.forEach(function (locale, index) {
    localeMap[locale.id] = locale;
    localeIndexes[locale.id] = index;
  });
  function normalizeLanguage(value) {
    var lang = String(value || "").toLowerCase().replace(/_/g, "-");
    if (localeMap[lang]) return lang;
    if (lang === "en") return "en-gb";
    if (lang === "pt-br" || lang.indexOf("pt-br") === 0) return "pt-br";
    if (lang === "pt" || lang.indexOf("pt-") === 0) return "pt-pt";
    if (lang === "zh" || lang === "zh-cn" || lang === "zh-sg" || lang.indexOf("zh-hans") === 0) return "zh-hans";
    if (lang === "zh-tw" || lang === "zh-hk" || lang === "zh-mo" || lang.indexOf("zh-hant") === 0) return "zh-hant";
    if (lang.indexOf("ar") === 0) return "ar";
    if (lang.indexOf("ko") === 0) return "ko";
    if (lang.indexOf("fr-ca") === 0) return "fr-ca";
    if (lang.indexOf("fr") === 0) return "fr";
    if (lang.indexOf("en-au") === 0) return "en-au";
    if (lang.indexOf("en-ca") === 0) return "en-ca";
    if (lang.indexOf("en-us") === 0) return "en-us";
    if (lang.indexOf("en-gb") === 0 || lang.indexOf("en-uk") === 0 || lang.indexOf("en-ie") === 0 || lang.indexOf("en-nz") === 0) return "en-gb";
    if (lang.indexOf("en") === 0) return "en-gb";
    if (lang.indexOf("ca") === 0) return "ca";
    if (lang.indexOf("da") === 0) return "da";
    if (lang.indexOf("es") === 0) return "es-es";
    if (lang.indexOf("fi") === 0) return "fi";
    if (lang.indexOf("it") === 0) return "it";
    if (lang.indexOf("de") === 0) return "de";
    if (lang.indexOf("nl") === 0) return "nl";
    if (lang.indexOf("ja") === 0) return "ja";
    if (lang.indexOf("he") === 0 || lang.indexOf("iw") === 0) return "he";
    if (lang.indexOf("hi") === 0) return "hi";
    if (lang.indexOf("id") === 0 || lang.indexOf("in") === 0) return "id";
    if (lang.indexOf("nb") === 0 || lang.indexOf("no") === 0 || lang.indexOf("nn") === 0) return "nb";
    if (lang.indexOf("pl") === 0) return "pl";
    if (lang.indexOf("el") === 0) return "el";
    if (lang.indexOf("ru") === 0) return "ru";
    if (lang.indexOf("sv") === 0) return "sv";
    if (lang.indexOf("tr") === 0) return "tr";
    return "";
  }
  function localizedValue(row, lang) {
    var pairs = row[1] || [];
    var index = localeIndexes[lang];
    for (var i = 0; i < pairs.length; i += 2) {
      if (pairs[i] === index) return pairs[i + 1];
    }
    return "";
  }
  function getTranslation(id, lang, frenchValue) {
    var row = translations[parseInt(id || "", 36)];
    if (!row) return frenchValue || "";
    var en = row[0] || "";
    if (lang === "fr") return frenchValue || en;
    if (lang === "fr-ca") return localizedValue(row, "fr-ca") || frenchValue || en;
    if (lang === "en-us") return en;
    var fallback = localeFallbacks[lang];
    return localizedValue(row, lang) || (fallback && fallback !== "fr" ? localizedValue(row, fallback) : "") || en;
  }
  function closestFromEvent(event, selector) {
    var node = event.target;
    var element = node && node.nodeType === 1 ? node : node && node.parentElement;
    return element && element.closest ? element.closest(selector) : null;
  }
  function applyTranslations(lang) {
    document.querySelectorAll("[data-i18n]").forEach(function (element) {
      if (element.__recordPickerFrHtml === undefined) element.__recordPickerFrHtml = element.innerHTML;
      element.innerHTML = getTranslation(element.getAttribute("data-i18n"), lang, element.__recordPickerFrHtml);
    });
    document.querySelectorAll("[data-i18n-title]").forEach(function (element) {
      if (element.__recordPickerFrTitle === undefined) element.__recordPickerFrTitle = element.getAttribute("title") || "";
      element.setAttribute("title", getTranslation(element.getAttribute("data-i18n-title"), lang, element.__recordPickerFrTitle));
    });
  }
  function detectLanguage() {
    var languages = navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language || ""];
    for (var i = 0; i < languages.length; i += 1) {
      var normalized = normalizeLanguage(languages[i]);
      if (normalized) return normalized;
    }
    return "en-gb";
  }
  function requestedLanguage() {
    try {
      var queryLang = new URLSearchParams(window.location.search).get("lang");
      var hashMatch = String(window.location.hash || "").match(/^#lang=([a-z0-9-]+)/i);
      return normalizeLanguage(queryLang || (hashMatch && hashMatch[1]) || "");
    } catch (error) {
      return "";
    }
  }
  var preferred = "en-gb";
  try {
    var stored = localStorage.getItem(languageStorageKey);
    var manualStored = localStorage.getItem(manualLanguageKey) === "1";
    var staticPageLanguage = body.hasAttribute("data-static-locale") ? normalizeLanguage(body.dataset.pageLang || body.dataset.lang || "") : "";
    preferred = requestedLanguage() || staticPageLanguage || (manualStored && normalizeLanguage(stored)) || detectLanguage();
  } catch (error) {
    preferred = requestedLanguage() || (body.hasAttribute("data-static-locale") && normalizeLanguage(body.dataset.pageLang || body.dataset.lang || "")) || "en-gb";
  }
  function setLang(lang, persist) {
    lang = normalizeLanguage(lang) || "en-gb";
    var locale = localeMap[lang] || localeMap["en-gb"];
    body.dataset.lang = lang;
    document.documentElement.lang = locale.code || lang;
    document.documentElement.dir = locale.rtl ? "rtl" : "ltr";
    applyTranslations(lang);
    document.querySelectorAll("[data-language-current]").forEach(function (label) {
      label.textContent = locale.name || lang;
    });
    document.querySelectorAll("[data-language-option]").forEach(function (option) {
      option.setAttribute("aria-selected", option.getAttribute("data-language-value") === lang ? "true" : "false");
    });
    if (persist) {
      try {
        localStorage.setItem(languageStorageKey, lang);
        localStorage.setItem(manualLanguageKey, "1");
      } catch (error) {}
    }
  }
  function closeLanguageMenus() {
    document.querySelectorAll("[data-language-panel]").forEach(function (panel) {
      panel.setAttribute("hidden", "");
    });
    document.querySelectorAll("[data-language-trigger]").forEach(function (trigger) {
      trigger.setAttribute("aria-expanded", "false");
    });
  }
  document.addEventListener("click", function (event) {
    var option = closestFromEvent(event, "[data-language-option]");
    if (option) {
      try {
        localStorage.setItem(languageStorageKey, normalizeLanguage(option.getAttribute("data-language-value") || "") || "en-gb");
        localStorage.setItem(manualLanguageKey, "1");
      } catch (error) {}
      closeLanguageMenus();
      return;
    }
    var trigger = closestFromEvent(event, "[data-language-trigger]");
    if (trigger) {
      event.preventDefault();
      var menu = trigger.closest("[data-language-menu]");
      var panel = menu && menu.querySelector("[data-language-panel]");
      var shouldOpen = panel && panel.hasAttribute("hidden");
      closeLanguageMenus();
      if (shouldOpen) {
        panel.removeAttribute("hidden");
        trigger.setAttribute("aria-expanded", "true");
      }
      return;
    }
    if (!closestFromEvent(event, "[data-language-menu]")) closeLanguageMenus();
  });
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") closeLanguageMenus();
  });
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
        var lang = normalizeLanguage(body.dataset.lang) || "fr";
        if (videoTitle) {
          if (trigger.__recordPickerFrTitle === undefined) trigger.__recordPickerFrTitle = trigger.getAttribute("title") || "";
          videoTitle.textContent = getTranslation(
            trigger.getAttribute("data-i18n-title"),
            lang,
            trigger.__recordPickerFrTitle
          );
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
  setLang(preferred, false);
})();
