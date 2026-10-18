/* Anonymous campaign attribution: no analytics request or user identifier. */
(function () {
  "use strict";
  var apps = { "6780422305": "RP", "6820177689": "ST", "6820104318": "MPR" };
  var aliases = { ig: "instagram", instagram: "instagram", tt: "tiktok", tiktok: "tiktok", website: "website", facebook: "facebook", youtube: "youtube", threads: "threads" };
  var storageKey = "recordpicker-acquisition-source";

  function source() {
    var requested = aliases[(new URLSearchParams(window.location.search).get("utm_source") || "").toLowerCase()];
    var cached = "";
    try { cached = aliases[sessionStorage.getItem(storageKey)]; } catch (_) {}
    var referring = "";
    try {
      var host = new URL(document.referrer).hostname;
      if (/(^|\.)instagram\.com$/i.test(host)) referring = "instagram";
      if (/(^|\.)tiktok\.com$/i.test(host)) referring = "tiktok";
    } catch (_) {}
    var result = requested || referring || cached || "website";
    try {
      if (result === "website") sessionStorage.removeItem(storageKey);
      else sessionStorage.setItem(storageKey, result);
    } catch (_) {}
    return result;
  }

  var channel = source();
  function token(prefix, existing) {
    if (prefix === "RP" && channel === "instagram") return "RP19_InstagramBio";
    if (channel === "instagram") return prefix + "_Instagram";
    if (channel === "tiktok") return prefix + "_TikTok";
    if (prefix === "RP" && channel === "website") {
      var locale = (document.documentElement.lang || "").toLowerCase();
      if (locale === "ja") return "RP_Website_JP";
      if (locale === "ko") return "RP_Website_KR";
    }
    if (channel === "website") return prefix + "_Website";
    // Keep existing attribution for the other social channels.
    return existing || prefix + "_" + channel;
  }

  function decorate(href) {
    var url;
    try { url = new URL(href, window.location.href); } catch (_) { return href; }
    if (url.protocol !== "https:") return href;
    if (url.hostname === "apps.apple.com") {
      var match = url.pathname.match(/\/id(\d+)(?:\/|$)/);
      var prefix = match && apps[match[1]];
      if (!prefix) return href;
      url.searchParams.set("pt", "129016722");
      url.searchParams.set("ct", token(prefix, url.searchParams.get("ct")));
      url.searchParams.set("mt", "8");
    } else if (url.hostname === "apps.microsoft.com" && /\/9N2ZWRL4M3JC\/?$/i.test(url.pathname)) {
      url.searchParams.set("cid", token("RP", url.searchParams.get("cid")));
    } else return href;
    return url.toString();
  }

  function apply() {
    document.querySelectorAll("a[href]").forEach(function (link) {
      var original = link.getAttribute("href");
      var updated = decorate(original);
      if (updated !== original) link.setAttribute("href", updated);
    });
  }
  window.recordPickerCampaigns = { decorate: decorate, apply: apply, source: channel };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", apply);
  else apply();
}());
