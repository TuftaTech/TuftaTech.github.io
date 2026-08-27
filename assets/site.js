"use strict";

var LANG_KEY = "yukaribox.lang";

function pickLang() {
  var fromUrl = new URLSearchParams(location.search).get("lang");
  if (fromUrl === "ru" || fromUrl === "en") return fromUrl;
  try {
    var saved = localStorage.getItem(LANG_KEY);
    if (saved === "ru" || saved === "en") return saved;
  } catch (e) { /* private mode: fall through to the browser's own preference */ }
  return (navigator.language || "en").toLowerCase().indexOf("ru") === 0 ? "ru" : "en";
}

function applyLang(code) {
  document.documentElement.lang = code;
  var buttons = document.querySelectorAll(".langswitch button[data-set-lang]");
  for (var i = 0; i < buttons.length; i++) {
    buttons[i].setAttribute("aria-pressed", String(buttons[i].dataset.setLang === code));
  }
  try { localStorage.setItem(LANG_KEY, code); } catch (e) { /* nothing to do */ }
  renderSize();
  labelTheme();
}

document.addEventListener("DOMContentLoaded", function () {
  applyLang(pickLang());
  var switcher = document.querySelector(".langswitch");
  if (switcher) {
    switcher.addEventListener("click", function (event) {
      var target = event.target.closest("button[data-set-lang]");
      if (target) applyLang(target.dataset.setLang);
    });
  }
});

var REPO = "TuftaTech/YukariBox";
var ASSET = "YukariBox-arm64.apk";

// The unit follows the page's language, and keeps following it: the byte count stays
// on the element so `applyLang` can re-render it when the switcher is used. Formatting
// once, when the fetch lands, left "MB" on the Russian page.
function renderSize() {
  var el = document.getElementById("dl-size");
  if (!el || !el.dataset.bytes) return;
  var mb = (parseInt(el.dataset.bytes, 10) / (1024 * 1024)).toFixed(1).replace(/\.0$/, "");
  el.textContent = mb + (document.documentElement.lang === "ru" ? " МБ" : " MB");
}

function fillRelease(release) {
  var asset = (release.assets || []).filter(function (a) { return a.name === ASSET; })[0];
  var version = document.getElementById("dl-version");
  if (version && release.tag_name) version.textContent = release.tag_name;
  if (!asset) return;
  var size = document.getElementById("dl-size");
  if (size) { size.dataset.bytes = String(asset.size); renderSize(); }
  var digest = (asset.digest || "").indexOf("sha256:") === 0 ? asset.digest.slice(7) : "";
  if (digest) {
    document.getElementById("dl-sha").textContent = digest;
    document.getElementById("dl-verify").hidden = false;
  }
}

document.addEventListener("DOMContentLoaded", function () {
  if (!document.getElementById("dl-version")) return;   // help.html has no hero
  fetch("https://api.github.com/repos/" + REPO + "/releases/latest", {
    headers: { Accept: "application/vnd.github+json" }
  })
    .then(function (r) { return r.ok ? r.json() : Promise.reject(r.status); })
    .then(fillRelease)
    .catch(function () { /* Nothing is written, nothing is shown. The link to the
                            release page is already in the page and stays the
                            only claim about the version. */ });

  var copy = document.getElementById("dl-copy");
  if (copy) {
    copy.addEventListener("click", function () {
      var text = document.getElementById("dl-sha").textContent;
      navigator.clipboard.writeText(text).then(function () {
        copy.classList.add("copied");
        setTimeout(function () { copy.classList.remove("copied"); }, 1200);
      });
    });
  }
});

// ---- theme -----------------------------------------------------------------
//
// Two states, and the reason is a bug report. It used to have three -- system, light,
// dark -- and the state that matched the visitor's OS was pixel-identical to `system`,
// so one click in every cycle changed nothing on screen. On a light desktop that is the
// first click, which reads as "the button is broken"; on a dark one it is the last,
// which reads as "two of the three themes are dark". Measured in both Chromium and
// Firefox: identical tables, so it was never a browser difference. Two states cannot
// have that failure, because every click flips the page.
//
// The page still follows the OS until the visitor touches the control: nothing is
// stored and no attribute is set before the first click. What is lost is handing the
// decision back afterwards, and that is the trade -- a control that always does
// something beats a third state nobody can see.
//
// The stored value is applied before first paint by a small inline script in the
// <head>; this half owns the toggle and the label.

var THEME_KEY = "yukaribox.theme";

var THEME_LABEL = {
  en: { light: "Switch to the dark theme", dark: "Switch to the light theme" },
  ru: { light: "Переключить на тёмную тему", dark: "Переключить на светлую тему" }
};

/** The theme showing right now: the stored choice, or whatever the system asks for. */
function currentTheme() {
  var set = document.documentElement.dataset.theme;
  if (set === "light" || set === "dark") return set;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function applyTheme(mode) {
  document.documentElement.dataset.theme = mode;
  try { localStorage.setItem(THEME_KEY, mode); } catch (e) { /* private mode */ }
  labelTheme();
}

function labelTheme() {
  var button = document.getElementById("themebtn");
  if (!button) return;
  var lang = document.documentElement.lang === "ru" ? "ru" : "en";
  var text = THEME_LABEL[lang][currentTheme()];
  button.setAttribute("aria-label", text);
  button.setAttribute("title", text);
}

document.addEventListener("DOMContentLoaded", function () {
  labelTheme();
  var button = document.getElementById("themebtn");
  if (button) {
    button.addEventListener("click", function () {
      applyTheme(currentTheme() === "dark" ? "light" : "dark");
    });
  }
  // The label follows the system while nothing is stored, so a visitor who changes
  // their OS theme with the page open does not get a button offering the wrong swap.
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", labelTheme);
});
