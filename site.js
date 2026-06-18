(function () {
  var body = document.body;
  var preferred = "fr";
  try {
    var stored = localStorage.getItem("recordpicker-language");
    preferred = stored || ((navigator.language || "").toLowerCase().startsWith("fr") ? "fr" : "en");
  } catch (error) {
    preferred = "fr";
  }
  function setLang(lang) {
    body.dataset.lang = lang;
    document.documentElement.lang = lang;
    try { localStorage.setItem("recordpicker-language", lang); } catch (error) {}
  }
  if (!document.getElementById("recordpicker-mobile-layout-fix")) {
    var mobileLayoutFix = document.createElement("style");
    mobileLayoutFix.id = "recordpicker-mobile-layout-fix";
    mobileLayoutFix.textContent = "@media (max-width:1040px){.hero-showcase{display:grid;gap:14px;min-height:0}.phone-shot{position:relative;right:auto;bottom:auto;width:min(340px,58%);margin-left:auto}}@media (max-width:720px){.phone-shot{width:min(320px,86%);margin:0 auto}}";
    document.head.appendChild(mobileLayoutFix);
  }
  var heroCopy = document.querySelector(".hero-copy");
  if (heroCopy && !heroCopy.querySelector(".tagline")) {
    var title = heroCopy.querySelector("h1");
    var tagline = document.createElement("p");
    tagline.className = "tagline";
    tagline.style.cssText = "margin:18px 0 0;max-width:620px;color:var(--ink);font-size:clamp(1.35rem,3vw,2.15rem);font-weight:850;line-height:1.16;";
    tagline.innerHTML = '<span class="lang-fr">Il y a toujours quelque chose dans votre collection qui vous appelle.</span><span class="lang-en">There\'s always something in your collection calling you back.</span>';
    if (title) {
      title.insertAdjacentElement("afterend", tagline);
    }
  }
  document.querySelectorAll("[data-set-lang]").forEach(function (button) {
    button.addEventListener("click", function () {
      setLang(button.getAttribute("data-set-lang") || "fr");
    });
  });
  setLang(preferred === "en" ? "en" : "fr");
})();
