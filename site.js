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
  document.querySelectorAll(".hero-note").forEach(function (note) {
    note.remove();
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
      setLang(button.getAttribute("data-set-lang") || "fr");
    });
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
  setLang(preferred === "en" ? "en" : "fr");
})();
