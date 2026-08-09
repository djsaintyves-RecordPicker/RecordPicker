(function () {
  var body = document.body;
  var locales = [{"id":"ar","code":"ar","name":"العربية","rtl":true},{"id":"de","code":"de","name":"Deutsch","rtl":false},{"id":"en-au","code":"en-AU","name":"English (Australia)","rtl":false},{"id":"en-ca","code":"en-CA","name":"English (Canada)","rtl":false},{"id":"en-us","code":"en-US","name":"English (US)","rtl":false},{"id":"en-gb","code":"en-GB","name":"English (UK)","rtl":false},{"id":"ca","code":"ca","name":"Català","rtl":false},{"id":"ko","code":"ko","name":"한국어","rtl":false},{"id":"zh-hans","code":"zh-Hans","name":"简体中文","rtl":false},{"id":"zh-hant","code":"zh-Hant","name":"繁體中文","rtl":false},{"id":"da","code":"da","name":"Dansk","rtl":false},{"id":"es-es","code":"es-ES","name":"Español","rtl":false},{"id":"es-mx","code":"es-MX","name":"Español (México)","rtl":false},{"id":"fi","code":"fi","name":"Suomi","rtl":false},{"id":"fr-ca","code":"fr-CA","name":"Français (Canada)","rtl":false},{"id":"fr","code":"fr-FR","name":"Français (France)","rtl":false},{"id":"el","code":"el","name":"Ελληνικά","rtl":false},{"id":"he","code":"he","name":"עברית","rtl":true},{"id":"hi","code":"hi","name":"हिन्दी","rtl":false},{"id":"id","code":"id","name":"Bahasa Indonesia","rtl":false},{"id":"it","code":"it","name":"Italiano","rtl":false},{"id":"ja","code":"ja","name":"日本語","rtl":false},{"id":"nl","code":"nl","name":"Nederlands","rtl":false},{"id":"nb","code":"nb","name":"Norsk","rtl":false},{"id":"pl","code":"pl","name":"Polski","rtl":false},{"id":"pt-br","code":"pt-BR","name":"Português (Brasil)","rtl":false},{"id":"pt-pt","code":"pt-PT","name":"Português (Portugal)","rtl":false},{"id":"ru","code":"ru","name":"Русский","rtl":false},{"id":"sv","code":"sv","name":"Svenska","rtl":false},{"id":"th","code":"th","name":"ไทย","rtl":false},{"id":"tr","code":"tr","name":"Türkçe","rtl":false},{"id":"vi","code":"vi","name":"Tiếng Việt","rtl":false}];
  var storefronts = {"ar":{"price":"Free · Lifetime Pro","market":"App Store المملكة العربية السعودية","url":"https://apps.apple.com/sa/app/recordpicker/id6780422305"},"de":{"price":"Free · Lifetime Pro","market":"App Store Deutschland","url":"https://apps.apple.com/de/app/recordpicker/id6780422305"},"en-au":{"price":"Free · Lifetime Pro","market":"App Store Australia","url":"https://apps.apple.com/au/app/recordpicker/id6780422305"},"en-ca":{"price":"Free · Lifetime Pro","market":"App Store Canada","url":"https://apps.apple.com/ca/app/recordpicker/id6780422305"},"en-us":{"price":"Free · Lifetime Pro","market":"App Store United States","url":"https://apps.apple.com/us/app/recordpicker/id6780422305"},"en-gb":{"price":"Free · Lifetime Pro","market":"App Store United Kingdom","url":"https://apps.apple.com/gb/app/recordpicker/id6780422305"},"ca":{"price":"Free · Lifetime Pro","market":"App Store Espanya","url":"https://apps.apple.com/es/app/recordpicker/id6780422305"},"ko":{"price":"Free · Lifetime Pro","market":"App Store 대한민국","url":"https://apps.apple.com/kr/app/recordpicker/id6780422305"},"zh-hans":{"price":"Free · Lifetime Pro","market":"App Store 中国","url":"https://apps.apple.com/cn/app/recordpicker/id6780422305"},"zh-hant":{"price":"Free · Lifetime Pro","market":"App Store 台灣","url":"https://apps.apple.com/tw/app/recordpicker/id6780422305"},"da":{"price":"Free · Lifetime Pro","market":"App Store Danmark","url":"https://apps.apple.com/dk/app/recordpicker/id6780422305"},"es-es":{"price":"Free · Lifetime Pro","market":"App Store España","url":"https://apps.apple.com/es/app/recordpicker/id6780422305"},"fi":{"price":"Free · Lifetime Pro","market":"App Store Suomi","url":"https://apps.apple.com/fi/app/recordpicker/id6780422305"},"fr-ca":{"price":"Gratuit · Pro à vie","market":"App Store Canada","url":"https://apps.apple.com/ca/app/recordpicker/id6780422305"},"fr":{"price":"Gratuit · Pro à vie","market":"App Store France","url":"https://apps.apple.com/fr/app/recordpicker/id6780422305"},"el":{"price":"Free · Lifetime Pro","market":"App Store Ελλάδα","url":"https://apps.apple.com/gr/app/recordpicker/id6780422305"},"he":{"price":"Free · Lifetime Pro","market":"App Store ישראל","url":"https://apps.apple.com/il/app/recordpicker/id6780422305"},"hi":{"price":"Free · Lifetime Pro","market":"App Store भारत","url":"https://apps.apple.com/in/app/recordpicker/id6780422305"},"id":{"price":"Free · Lifetime Pro","market":"App Store Indonesia","url":"https://apps.apple.com/id/app/recordpicker/id6780422305"},"it":{"price":"Free · Lifetime Pro","market":"App Store Italia","url":"https://apps.apple.com/it/app/recordpicker/id6780422305"},"ja":{"price":"Free · Lifetime Pro","market":"App Store 日本","url":"https://apps.apple.com/jp/app/recordpicker/id6780422305"},"nl":{"price":"Free · Lifetime Pro","market":"App Store Nederland","url":"https://apps.apple.com/nl/app/recordpicker/id6780422305"},"nb":{"price":"Free · Lifetime Pro","market":"App Store Norge","url":"https://apps.apple.com/no/app/recordpicker/id6780422305"},"pl":{"price":"Free · Lifetime Pro","market":"App Store Polska","url":"https://apps.apple.com/pl/app/recordpicker/id6780422305"},"pt-br":{"price":"Free · Lifetime Pro","market":"App Store Brasil","url":"https://apps.apple.com/br/app/recordpicker/id6780422305"},"pt-pt":{"price":"Free · Lifetime Pro","market":"App Store Portugal","url":"https://apps.apple.com/pt/app/recordpicker/id6780422305"},"ru":{"price":"Free · Lifetime Pro","market":"App Store Россия","url":"https://apps.apple.com/ru/app/recordpicker/id6780422305"},"sv":{"price":"Free · Lifetime Pro","market":"App Store Sverige","url":"https://apps.apple.com/se/app/recordpicker/id6780422305"},"tr":{"price":"Free · Lifetime Pro","market":"App Store Türkiye","url":"https://apps.apple.com/tr/app/recordpicker/id6780422305"},"fr-ch":{"price":"Free · Lifetime Pro","market":"App Store Suisse","url":"https://apps.apple.com/ch/app/recordpicker/id6780422305"},"de-ch":{"price":"Free · Lifetime Pro","market":"App Store Schweiz","url":"https://apps.apple.com/ch/app/recordpicker/id6780422305"},"it-ch":{"price":"Free · Lifetime Pro","market":"App Store Svizzera","url":"https://apps.apple.com/ch/app/recordpicker/id6780422305"},"en-ch":{"price":"Free · Lifetime Pro","market":"App Store Switzerland","url":"https://apps.apple.com/ch/app/recordpicker/id6780422305"}};
  var translations = [];
  storefronts["es-mx"] = {"price":"Gratis · Pro de por vida","market":"App Store México","url":"https://apps.apple.com/mx/app/recordpicker/id6780422305"};
  storefronts.th = {"price":"ฟรี · Pro ตลอดชีพ","market":"App Store ประเทศไทย","url":"https://apps.apple.com/th/app/recordpicker/id6780422305"};
  storefronts.vi = {"price":"Miễn phí · Pro trọn đời","market":"App Store Việt Nam","url":"https://apps.apple.com/vn/app/recordpicker/id6780422305"};
  var localeFallbacks = {"en-au":"en-gb","en-ca":"en-gb","es-mx":"es-es","fr-ca":"fr","pt-br":"pt-pt","th":"en-us","vi":"en-us"};
  var siteBasePath = "/";
  var publicPagePaths = ["","support/","privacy/","screenshots/","readme/","mac-app/","choose-vinyl-record/","random-vinyl-record-picker/","manage-vinyl-collection/"];
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
    if (lang.indexOf("es-mx") === 0) return "es-mx";
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
    if (lang.indexOf("th") === 0) return "th";
    if (lang.indexOf("tr") === 0) return "tr";
    if (lang.indexOf("vi") === 0) return "vi";
    return "";
  }
  function normalizeStorefront(value) {
    var lang = String(value || "").toLowerCase().replace(/_/g, "-");
    if (lang === "fr-ch" || lang.indexOf("fr-ch-") === 0) return "fr-ch";
    if (lang === "de-ch" || lang.indexOf("de-ch-") === 0) return "de-ch";
    if (lang === "it-ch" || lang.indexOf("it-ch-") === 0) return "it-ch";
    if (lang === "en-ch" || lang.indexOf("en-ch-") === 0) return "en-ch";
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
    document.querySelectorAll("[data-i18n-aria-label]").forEach(function (element) {
      if (element.__recordPickerFrAriaLabel === undefined) element.__recordPickerFrAriaLabel = element.getAttribute("aria-label") || "";
      element.setAttribute("aria-label", getTranslation(element.getAttribute("data-i18n-aria-label"), lang, element.__recordPickerFrAriaLabel));
    });
  }
  function applyStorefront(lang) {
    var storefront = storefronts[lang] || storefronts["en-gb"];
    if (!storefront) return;
    document.querySelectorAll("[data-price-current]").forEach(function (element) {
      element.textContent = storefront.price || "";
    });
    document.querySelectorAll("[data-store-current]").forEach(function (element) {
      element.textContent = storefront.market || "";
    });
    document.querySelectorAll("[data-app-store-link]").forEach(function (element) {
      if (storefront.url) element.setAttribute("href", storefront.url);
    });
  }
  function detectStorefront() {
    var languages = navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language || ""];
    for (var i = 0; i < languages.length; i += 1) {
      var storefront = normalizeStorefront(languages[i]);
      if (storefront) return storefront;
    }
    return "";
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
  function requestedStorefront() {
    try {
      var queryLang = new URLSearchParams(window.location.search).get("lang");
      var hashMatch = String(window.location.hash || "").match(/^#lang=([a-z0-9-]+)/i);
      return normalizeStorefront(queryLang || (hashMatch && hashMatch[1]) || "");
    } catch (error) {
      return "";
    }
  }
  function currentPublicPagePath() {
    var path = window.location.pathname || "/";
    if (path.indexOf(siteBasePath) === 0) {
      path = path.slice(siteBasePath.length);
    } else {
      path = path.replace(/^\/+/, "");
    }
    path = path.replace(/^\/+/, "").replace(/index\.html$/, "");
    if (path && path.charAt(path.length - 1) !== "/") path += "/";
    for (var i = 0; i < publicPagePaths.length; i += 1) {
      if (path === publicPagePaths[i]) return path;
    }
    return null;
  }
  function redirectToStaticLocale(lang) {
    if (body.hasAttribute("data-static-locale") || window.location.protocol === "file:") return false;
    var pagePath = currentPublicPagePath();
    if (pagePath === null) return false;
    var hash = String(window.location.hash || "");
    if (/^#lang=/i.test(hash)) hash = "";
    var targetPath = siteBasePath + lang + "/" + pagePath;
    if (window.location.pathname === targetPath) return false;
    window.location.replace(targetPath + hash);
    return true;
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
    applyStorefront(requestedStorefront() || detectStorefront() || lang);
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
  var siteNav = document.querySelector(".nav-links");
  var siteHeader = document.querySelector(".site-header");
  var navToggle = null;
  if (siteNav && siteHeader) {
    navToggle = document.createElement("button");
    navToggle.className = "nav-toggle";
    navToggle.type = "button";
    navToggle.setAttribute("aria-label", "Menu");
    navToggle.setAttribute("aria-controls", "site-navigation");
    navToggle.setAttribute("aria-expanded", "false");
    navToggle.innerHTML = '<span class="nav-toggle-icon" aria-hidden="true"></span>';
    siteNav.id = "site-navigation";
    var headerActions = siteHeader.querySelector(".header-actions");
    siteHeader.insertBefore(navToggle, headerActions || siteNav);
    var desktopStoreLink = siteHeader.querySelector(".store-link");
    if (desktopStoreLink && !siteNav.querySelector(".mobile-store-link")) {
      var mobileStoreLink = desktopStoreLink.cloneNode(true);
      mobileStoreLink.classList.remove("store-link");
      mobileStoreLink.classList.add("mobile-store-link");
      siteNav.appendChild(mobileStoreLink);
    }
  }
  function closeSiteNav(restoreFocus) {
    if (!siteNav || !navToggle) return;
    siteNav.classList.remove("is-open");
    navToggle.setAttribute("aria-expanded", "false");
    if (restoreFocus) navToggle.focus();
  }
  document.addEventListener("click", function (event) {
    var clickedNavToggle = closestFromEvent(event, ".nav-toggle");
    if (clickedNavToggle && siteNav) {
      event.preventDefault();
      var openNav = !siteNav.classList.contains("is-open");
      closeSiteNav(false);
      if (openNav) {
        siteNav.classList.add("is-open");
        clickedNavToggle.setAttribute("aria-expanded", "true");
      }
      return;
    }
    if (closestFromEvent(event, ".nav-links a")) closeSiteNav(false);
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
    if (event.key === "Escape") {
      closeLanguageMenus();
      closeSiteNav(true);
    }
  });
  var lightbox = document.querySelector("[data-video-lightbox]");
  if (lightbox) {
    var video = lightbox.querySelector("video");
    var videoTitle = lightbox.querySelector("[data-video-title]");
    var videoOpener = null;
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
      if (videoOpener) videoOpener.focus();
    }
    document.querySelectorAll("[data-video-src]").forEach(function (trigger) {
      trigger.addEventListener("click", function () {
        videoOpener = trigger;
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
        var closeButton = lightbox.querySelector(".video-lightbox-close");
        if (closeButton) closeButton.focus();
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
  document.querySelectorAll("[data-random-pick-demo]").forEach(function (demo) {
    var button = demo.querySelector(".random-pick-button");
    var revealTimer = 0;
    var repeatTimer = 0;
    var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var visible = false;
    if (!button) return;

    function playPickSound() {
      var AudioContextClass = window.AudioContext || window.webkitAudioContext;
      if (!AudioContextClass) return;
      var context = new AudioContextClass();
      var now = context.currentTime;
      [0, .12, .24, .37].forEach(function (offset, index) {
        var oscillator = context.createOscillator();
        var gain = context.createGain();
        oscillator.type = "triangle";
        oscillator.frequency.setValueAtTime(430 + index * 105, now + offset);
        gain.gain.setValueAtTime(.0001, now + offset);
        gain.gain.exponentialRampToValueAtTime(.045, now + offset + .01);
        gain.gain.exponentialRampToValueAtTime(.0001, now + offset + .07);
        oscillator.connect(gain).connect(context.destination);
        oscillator.start(now + offset);
        oscillator.stop(now + offset + .08);
      });
      window.setTimeout(function () { context.close(); }, 900);
    }

    function runPick(withSound) {
      window.clearTimeout(revealTimer);
      demo.classList.remove("is-picking");
      demo.classList.remove("is-revealed");
      void demo.offsetWidth;
      demo.classList.add("is-picking");
      if (withSound) playPickSound();
      revealTimer = window.setTimeout(function () {
        demo.classList.remove("is-picking");
        demo.classList.add("is-revealed");
      }, reducedMotion ? 80 : 1350);
    }

    function scheduleRepeat() {
      window.clearTimeout(repeatTimer);
      if (!visible || reducedMotion) return;
      repeatTimer = window.setTimeout(function () {
        runPick(false);
        scheduleRepeat();
      }, 6500);
    }

    button.addEventListener("click", function () {
      runPick(true);
      scheduleRepeat();
    });

    if ("IntersectionObserver" in window) {
      var observer = new IntersectionObserver(function (entries) {
        visible = entries[0] && entries[0].isIntersecting;
        if (visible) {
          runPick(false);
          scheduleRepeat();
        } else {
          window.clearTimeout(repeatTimer);
        }
      }, { threshold: .35 });
      observer.observe(demo);
    } else {
      visible = true;
      runPick(false);
      scheduleRepeat();
    }
  });
  if (!redirectToStaticLocale(preferred)) {
    setLang(preferred, false);
  }
})();
