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
  document.querySelectorAll("[data-set-lang]").forEach(function (button) {
    button.addEventListener("click", function () {
      setLang(button.getAttribute("data-set-lang") || "fr");
    });
  });
  setLang(preferred === "en" ? "en" : "fr");
})();
