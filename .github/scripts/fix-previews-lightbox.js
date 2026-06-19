const fs = require('fs');
const workflow = '.github/workflows/fix-previews-lightbox.yml';
const script = '.github/scripts/fix-previews-lightbox.js';
const replaceAll = (value, from, to) => value.split(from).join(to);
const attr = (value) => String(value).replace(/&/g, '&amp;').replace(/"/g, '&quot;');
const htmlFiles = ['index.html', 'support/index.html', 'privacy/index.html', 'readme/index.html', 'screenshots/index.html'];

for (const file of htmlFiles) {
  if (!fs.existsSync(file)) continue;
  let html = fs.readFileSync(file, 'utf8');
  html = replaceAll(html, '<span class="lang-fr">Captures</span><span class="lang-en">Screenshots</span>', '<span class="lang-fr">Aperçus</span><span class="lang-en">Screenshots</span>');
  html = replaceAll(html, '<span class="lang-fr">Captures</span><span class="lang-en">Screens</span>', '<span class="lang-fr">Aperçus</span><span class="lang-en">Screenshots</span>');
  html = replaceAll(html, 'Voir toutes les captures', 'Voir tous les aperçus');

  if (file === 'screenshots/index.html') {
    html = replaceAll(html, '<title>Screenshots - Record Picker</title>', '<title>Aperçus / Screenshots - Record Picker</title>');
    html = replaceAll(html, 'content="Record Picker screenshots and App Store video previews."', 'content="Record Picker app previews, screenshots, and App Store videos."');
    html = replaceAll(html, 'content="Screenshots - Record Picker"', 'content="Aperçus / Screenshots - Record Picker"');
    html = replaceAll(html, '<span class="lang-fr">Captures et vidéos</span><span class="lang-en">Screenshots and videos</span>', '<span class="lang-fr">Aperçus</span><span class="lang-en">Screenshots and videos</span>');
    html = replaceAll(html, '<h1><span class="lang-fr">Screenshots</span><span class="lang-en">Screenshots</span></h1>', '<h1><span class="lang-fr">Aperçus</span><span class="lang-en">Screenshots</span></h1>');
    html = replaceAll(html, "Une galerie plus aérée avec les captures qui ne sont pas déjà utilisées sur la page d'accueil, et les aperçus vidéo publics de l'App Store.", "Une galerie plus aérée avec les aperçus qui ne sont pas déjà utilisés sur la page d'accueil, et les vidéos App Store.");

    const videoPattern = /<a class="video-preview" href="([^"]+)" aria-label="([^"]+)"><img loading="lazy" alt="([^"]+)" src="([^"]+)"><span class="video-play" aria-hidden="true"><\/span><\/a><figcaption><span><span class="lang-fr">([^<]+)<\/span><span class="lang-en">([^<]+)<\/span><\/span><a href="\1"><span class="lang-fr">Ouvrir l'aperçu vidéo<\/span><span class="lang-en">Open video preview<\/span><\/a><\/figcaption>/g;
    html = html.replace(videoPattern, (_match, src, aria, alt, poster, titleFr, titleEn) => {
      const ariaText = aria.replace('Ouvrir ', 'Lire ').replace('Open ', 'Play ');
      const attrs = `data-video-src="${attr(src)}" data-video-poster="${attr(poster)}" data-title-fr="${attr(titleFr)}" data-title-en="${attr(titleEn)}"`;
      return `<button class="video-preview" type="button" ${attrs} aria-label="${attr(ariaText)}"><img loading="lazy" alt="${attr(alt)}" src="${attr(poster)}"><span class="video-play" aria-hidden="true"></span></button><figcaption><span><span class="lang-fr">${titleFr}</span><span class="lang-en">${titleEn}</span></span><button class="video-open" type="button" ${attrs}><span class="lang-fr">Lire l'aperçu vidéo</span><span class="lang-en">Play video preview</span></button></figcaption>`;
    });

    if (!html.includes('data-video-lightbox')) {
      const modal = '<div class="video-lightbox" data-video-lightbox hidden aria-hidden="true"><button class="video-lightbox-backdrop" type="button" data-video-close aria-label="Fermer / Close"></button><section class="video-lightbox-panel" role="dialog" aria-modal="true" aria-labelledby="video-lightbox-title"><div class="video-lightbox-head"><h3 id="video-lightbox-title" data-video-title></h3><button class="video-lightbox-close" type="button" data-video-close aria-label="Fermer / Close">&times;</button></div><video class="video-player" controls playsinline preload="metadata"></video></section></div>';
      html = html.replace('</div></section><section class="media-section"><div class="section-head"><p class="kicker">iPhone</p>', `</div>${modal}</section><section class="media-section"><div class="section-head"><p class="kicker">iPhone</p>`);
    }
  }

  fs.writeFileSync(file, html);
}

if (fs.existsSync('screenshots.html')) {
  let redirect = fs.readFileSync('screenshots.html', 'utf8');
  redirect = replaceAll(redirect, 'Screenshots - Record Picker', 'Aperçus / Screenshots - Record Picker');
  fs.writeFileSync('screenshots.html', redirect);
}

if (fs.existsSync('site.js')) {
  let js = fs.readFileSync('site.js', 'utf8');
  if (!js.includes('data-video-lightbox')) {
    const videoJs = `  var lightbox = document.querySelector("[data-video-lightbox]");
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
`;
    js = js.replace('  setLang(preferred === "en" ? "en" : "fr");', videoJs + '  setLang(preferred === "en" ? "en" : "fr");');
    fs.writeFileSync('site.js', js);
  }
}

if (fs.existsSync('styles.css')) {
  let css = fs.readFileSync('styles.css', 'utf8');
  if (!css.includes('recordpicker-video-lightbox')) {
    css += '\n/* recordpicker-video-lightbox */.video-preview{border:0;color:inherit;cursor:pointer;padding:0}.video-open{border:0;background:transparent;color:var(--red);cursor:pointer;font:inherit;font-weight:850;padding:0;white-space:nowrap}.video-lightbox[hidden]{display:none}.video-lightbox{position:fixed;inset:0;z-index:100;display:grid;place-items:center;padding:22px;background:rgba(0,0,0,.54);backdrop-filter:blur(18px) saturate(1.12)}.video-lightbox-backdrop{position:absolute;inset:0;border:0;background:transparent;cursor:pointer}.video-lightbox-panel{position:relative;z-index:1;display:grid;gap:12px;width:min(420px,100%);max-height:calc(100vh - 44px);border:1px solid var(--line);border-radius:8px;background:var(--surface-strong);box-shadow:var(--shadow);padding:12px}.video-lightbox-head{display:flex;align-items:center;justify-content:space-between;gap:12px}.video-lightbox-head h3{font-size:1rem}.video-lightbox-close{display:grid;place-items:center;width:38px;height:38px;border:1px solid var(--glass-border);border-radius:999px;background:var(--glass-surface);color:var(--ink);cursor:pointer;font-size:1.35rem;line-height:1}.video-player{width:100%;max-height:calc(100vh - 132px);aspect-ratio:9 / 19.5;border-radius:6px;background:#000;object-fit:contain}body.video-lightbox-open{overflow:hidden}\n';
    fs.writeFileSync('styles.css', css);
  }
}

if (fs.existsSync(workflow)) fs.unlinkSync(workflow);
if (fs.existsSync(script)) fs.unlinkSync(script);
