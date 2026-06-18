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
