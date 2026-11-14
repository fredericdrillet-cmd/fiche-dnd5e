/* Fiche D&D 5e — client mobile.
 * Le personnage vit dans le navigateur (localStorage) au format JSON de l'application bureau ;
 * chaque modification est envoyée au serveur, qui applique les règles (core/) et renvoie la fiche calculée. */
"use strict";

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const sgn = (n) => (Number(n) >= 0 ? "+" : "") + Number(n);
const norm = (s) => String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
const uid = () => "p" + Date.now().toString(36) + Math.random().toString(36).slice(2, 7);

const STORE_KEY = "dnd5e.web.personnages.v1";
const PREF_KEY = "dnd5e.web.prefs.v1";
const S = {
  cat: null, char: null, sheet: null,
  store: { current: null, chars: {} },
  prefs: { theme: "bg3", tab: "perso", gm: false },
  queue: Promise.resolve(), sheetCtx: null,
};

/* ============================================================== stockage local */
function readJSON(key, fallback) {
  try { const v = JSON.parse(localStorage.getItem(key)); return v ?? fallback; } catch (e) { return fallback; }
}
function writeJSON(key, value) {
  try { localStorage.setItem(key, JSON.stringify(value)); return true; } catch (e) { return false; }
}
function persist() {
  if (!S.store.current || !S.char) return;
  S.store.chars[S.store.current] = {
    character: S.char, updated: Date.now(),
    label: S.sheet ? `${S.sheet.resume.race_txt} · ${S.sheet.resume.classes_txt}` : "",
  };
  if (!writeJSON(STORE_KEY, S.store)) toast("Stockage du navigateur plein : exportez vos personnages en JSON.", true);
}
const savePrefs = () => writeJSON(PREF_KEY, S.prefs);

/* ============================================================== API */
async function api(path, body) {
  const opt = body === undefined ? {} : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) };
  busy(1);
  try {
    const r = await fetch(path, opt);
    const ct = r.headers.get("Content-Type") || "";
    const data = ct.includes("json") ? await r.json() : await r.text();
    if (!r.ok) throw new Error((data && data.error) || `Erreur ${r.status}`);
    return data;
  } catch (e) {
    if (e instanceof TypeError) throw new Error("Serveur injoignable — vérifiez la connexion (le serveur gratuit peut mettre ~30 s à se réveiller).");
    throw e;
  } finally { busy(-1); }
}
let busyN = 0;
function busy(d) { busyN += d; $("#busy").hidden = busyN <= 0; }

/** Envoie des opérations au moteur (en file : jamais deux requêtes concurrentes sur le même personnage). */
/* v52 : une fiche suit une seule édition (2014 ou 2024) ; les listes de choix sont filtrées */
function sheetMode() { return (S.sheet && S.sheet.edition && S.sheet.edition.mode) || "2014"; }
function edOk(ed) { const m = sheetMode(); return m === "libre" || String(ed || 2014) === m; }
function edList(names, map, current) { return names.filter((n) => edOk((map || {})[n]) || n === current); }

function act(ops, opts = {}) {
  S.queue = S.queue.then(() => doAct(Array.isArray(ops) ? ops : [ops], opts)).catch((e) => toast(e.message, true));
  return S.queue;
}
async function doAct(ops, { character, silent } = {}) {
  let src = character !== undefined ? character : S.char;
  let portrait = "";
  if (src) { src = { ...src }; portrait = src.portrait || ""; delete src.portrait; }   // inutile au moteur
  const res = await api("/api/character", { character: src, ops });
  res.character.portrait = portrait;
  S.char = res.character; S.sheet = res.sheet;
  persist();
  if (!silent) {
    (res.messages || []).forEach((m) => toast(m));
    (res.errors || []).forEach((m) => toast(m, true));
  }
  if ((res.rolls || []).length) showRolls(res.rolls);
  render();
  if (S.sheetCtx && S.sheetCtx.refresh) S.sheetCtx.refresh();
  return res;
}

/* ============================================================== thèmes (ui/theme.py) */
function applyTheme(key) {
  const t = S.cat && S.cat.themes[key];
  if (!t) return;
  const serif = /serif/.test(t.font) && !/sans-serif/.test(t.font);
  const v = {
    "--bg": t.bg, "--panel": t.panel, "--panel-alt": t.panel_alt, "--input": t.input_bg, "--text": t.text,
    "--muted": t.muted, "--accent": t.accent_text, "--border": t.border, "--ornament": t.ornament, "--btn": t.button_bg,
    "--btn-hover": t.button_hover, "--btn-text": t.button_text, "--sel": t.select_bg, "--sel-text": t.select_text,
    "--warn": t.warn, "--good": t.good, "--locked": t.locked,
    "--font": serif ? `"EB Garamond", ${t.font}` : `${t.font}, system-ui, sans-serif`,
    "--font-title": serif ? `"Cinzel", ${t.font_title}` : `${t.font_title}, system-ui, sans-serif`,
  };
  const root = document.documentElement;
  Object.entries(v).forEach(([k, val]) => root.style.setProperty(k, val));
  const light = luminance(t.bg) > 0.5;
  root.style.colorScheme = light ? "light" : "dark";
  $('meta[name="theme-color"]').setAttribute("content", t.panel);
  S.prefs.theme = key; savePrefs();
}
function luminance(hex) {
  const n = parseInt(String(hex).replace("#", ""), 16);
  return (0.299 * ((n >> 16) & 255) + 0.587 * ((n >> 8) & 255) + 0.114 * (n & 255)) / 255;
}

/* ============================================================== notifications & dés */
function toast(msg, err = false) {
  if (!msg) return;
  const el = document.createElement("div");
  el.className = "toast" + (err ? " err" : "");
  el.textContent = msg;
  const box = $("#toasts");
  box.appendChild(el);
  while (box.children.length > 2) box.firstChild.remove();
  setTimeout(() => el.remove(), err ? 5000 : 2800);
  el.addEventListener("click", () => el.remove());
}
function rnd(sides) {
  const a = new Uint32Array(1); crypto.getRandomValues(a); return 1 + (a[0] % sides);
}
/** Jet de d20 : avantage / désavantage d'après les listes renvoyées par le moteur (ils s'annulent). */
function rollD20(title, bonus, row = {}) {
  const adv = (row.avantage || []).length > 0, dis = (row.desavantage || []).length > 0;
  const mode = adv && !dis ? "adv" : dis && !adv ? "dis" : "";
  const a = rnd(20), b = rnd(20);
  const kept = mode === "adv" ? Math.max(a, b) : mode === "dis" ? Math.min(a, b) : a;
  const extra = (row.des || []).join(" ");
  let detail = mode ? `${a} et ${b} (${mode === "adv" ? "avantage" : "désavantage"}) → ${kept}` : `d20 : ${kept}`;
  detail += ` ${sgn(bonus)}` + (extra ? ` ${extra} (à lancer en plus)` : "");
  const notes = [];
  if ((row.echec || []).length) notes.push("✖ Échec automatique : " + row.echec.join(", "));
  if (adv) notes.push("▲ " + row.avantage.join(", "));
  if (dis) notes.push("▼ " + row.desavantage.join(", "));
  showDice({ title, total: kept + Number(bonus), detail, notes, crit: kept === 20, fail: kept === 1 });
}
/** Formules de dégâts : « 2d6+3 », « 1d8 + 2 », « 3 × (1d4+1) ». */
function rollFormula(title, formula, type = "") {
  let f = String(formula || "").replace(/\s+/g, "");
  let times = 1;
  const m = f.match(/^(\d+)[×x\*]\(?(.+?)\)?([+-]\d+)?$/);
  let tail = 0;
  if (m) { times = +m[1]; f = m[2]; tail = m[3] ? +m[3] : 0; }
  const terms = [...f.matchAll(/([+-]?)(\d*)d(\d+)|([+-]?)(\d+)/g)];
  if (!terms.length) { toast("Formule non lançable : " + formula, true); return; }
  let total = tail; const parts = [];
  for (let k = 0; k < times; k++) {
    for (const t of terms) {
      if (t[3]) {
        const n = +(t[2] || 1), s = +t[3], sign = t[1] === "-" ? -1 : 1;
        const rolls = Array.from({ length: Math.min(n, 100) }, () => rnd(s));
        total += sign * rolls.reduce((x, y) => x + y, 0);
        parts.push(`${t[1] || ""}[${rolls.join(", ")}]`);
      } else if (t[5]) { const v = +t[5] * (t[4] === "-" ? -1 : 1); total += v; parts.push(sgn(v)); }
    }
  }
  if (tail) parts.push(sgn(tail));
  showDice({ title, total: Math.max(0, total), detail: `${formula} : ${parts.join(" ")}`, notes: type ? [type] : [] });
}
/** Plusieurs jets du moteur à la suite (attaque puis dégâts) dans une même carte. */
function showRolls(rolls) {
  const o = $("#dice");
  o.innerHTML = `<div class="dice-card" role="alert">${rolls.map((r) => `<div class="muted">${esc(r.titre)}</div>
    <div class="total ${r.crit ? "crit" : r.fail ? "fail" : ""}" style="${rolls.length > 1 ? "font-size:2.6rem" : ""}">${esc(r.total)}</div>
    <div class="detail">${esc(r.detail || "")}</div>${(r.notes || []).map((n) => `<div class="detail">${esc(n)}</div>`).join("")}
    ${r.crit ? '<div class="badge good">20 naturel !</div>' : r.fail ? '<div class="badge warn">1 naturel</div>' : ""}`).join("<hr>")}
    <div class="spacer"></div><button class="btn small ghost">Fermer</button></div>`;
  o.hidden = false;
  if (navigator.vibrate) navigator.vibrate(rolls.some((r) => r.crit) ? [40, 40, 80] : 25);
}
function showDice({ title, total, detail = "", notes = [], crit = false, fail = false }) {
  const o = $("#dice");
  o.innerHTML = `<div class="dice-card" role="alert"><div class="muted">${esc(title)}</div>
    <div class="total ${crit ? "crit" : fail ? "fail" : ""}">${esc(total)}</div>
    <div class="detail">${esc(detail)}</div>${notes.map((n) => `<div class="detail">${esc(n)}</div>`).join("")}
    ${crit ? '<div class="badge good">20 naturel !</div>' : fail ? '<div class="badge warn">1 naturel</div>' : ""}
    <div class="spacer"></div><button class="btn small ghost">Fermer</button></div>`;
  o.hidden = false;
  if (navigator.vibrate) navigator.vibrate(crit ? [40, 40, 80] : 25);
}

/* ============================================================== petits composants */
const opt = (v, cur, label) => `<option value="${esc(v)}"${String(v) === String(cur) ? " selected" : ""}>${esc(label ?? v)}</option>`;
const options = (list, cur) => list.map((x) => (typeof x === "object" ? opt(x.value, cur, x.label) : opt(x, cur))).join("");
const sw = (label, checked, attrs) => `<label class="switch"><span>${label}</span><input type="checkbox" ${checked ? "checked" : ""} ${attrs}></label>`;
const orbs = (total, used, attrs) =>
  `<div class="orbs">${Array.from({ length: total }, (_, i) => `<button class="orb${i < total - used ? "" : " empty"}" data-i="${i}" ${attrs} aria-label="Sphère ${i + 1}"></button>`).join("")}</div>`;
const card = (title, body, extra = "") => `<section class="card"><header><h2>${title}</h2>${extra}</header>${body}</section>`;
const fold = (title, body, open = false, extra = "") =>
  `<details class="card"${open ? " open" : ""}><summary><h2>${title}</h2>${extra}</summary>${body}</details>`;
function orbClick(total, used, i) { const avail = total - used; return Math.max(0, Math.min(total, i < avail ? used + 1 : used - 1)); }
function raceImg(ch) { return `/api/race-image?race=${encodeURIComponent(ch.race || "")}&sous_race=${encodeURIComponent(ch.sous_race || "")}`; }
function portraitURL(b64) { return b64 ? `data:image/${b64.startsWith("/9j/") ? "jpeg" : "png"};base64,${b64}` : ""; }

/* ============================================================== rendu */
function render() {
  if (!S.sheet) return;
  renderTop();
  const view = $("#view");
  const y = window.scrollY;
  const a = document.activeElement;
  const fkey = a && view.contains(a) ? focusKey(a) : "";
  view.innerHTML = (TABS[S.prefs.tab] || TABS.perso)();
  window.scrollTo(0, y);
  if (fkey) { const n = view.querySelector(fkey); if (n) n.focus({ preventScroll: true }); }
  $$("#tabbar button").forEach((b) => b.classList.toggle("active", b.dataset.tab === S.prefs.tab));
}
/** Sélecteur stable d'un champ : le focus est rendu au même champ après un nouveau rendu (clavier mobile). */
function focusKey(el) {
  if (el.id) return "#" + CSS.escape(el.id);
  for (const k of ["field", "setin", "change"]) {
    if (el.dataset[k]) {
      let sel = `[data-${k}="${CSS.escape(el.dataset[k])}"]`;
      for (const x of ["key", "idx", "ab", "k", "slot", "i"]) if (el.dataset[x] !== undefined) sel += `[data-${x}="${CSS.escape(el.dataset[x])}"]`;
      return sel;
    }
  }
  return "";
}
function renderTop() {
  const r = S.sheet.resume, c = S.sheet.combat, ch = S.char;
  $("#hero-name").textContent = r.nom;
  $("#hero-sub").textContent = `${r.race_txt} · ${r.classes_txt}`;
  const av = $("#hero-avatar");
  av.style.backgroundImage = `url("${ch.portrait ? portraitURL(ch.portrait) : raceImg(ch)}")`;
  const hp = $("#hero-hp");
  hp.textContent = `❤ ${c.pv}/${c.pv_max}` + (c.pv_temp ? ` +${c.pv_temp}` : "");
  hp.classList.toggle("low", c.pv <= c.pv_max / 4);
}

const TABS = {};
const TODO_TAB = { compagnons: "Alliés", classes: "Perso", race: "Carac", caracteristiques: "Carac", progression: "Carac", combat: "Combat", magie: "Magie" };

/* ---------------------------------------------------------------- Perso */
TABS.perso = () => {
  const s = S.sheet, ch = S.char, cat = S.cat, r = s.resume;
  const lvlXp = r.niveau_xp;
  const id = card("Identité", `
    <div class="portrait-wrap">
      <button class="portrait" data-act="portrait" aria-label="Changer le portrait" style="background-image:url('${ch.portrait ? portraitURL(ch.portrait) : raceImg(ch)}')"></button>
      <div class="grow" style="display:flex;flex-direction:column;gap:8px">
        <label class="field">Nom<input type="text" data-field="nom" value="${esc(ch.nom)}" placeholder="Nom du personnage" autocomplete="off"></label>
        <label class="field">Joueur<input type="text" data-field="joueur" value="${esc(ch.joueur)}" autocomplete="off"></label>
      </div>
    </div>
    <div class="grid2">
      <label class="field">Alignement<select data-field="alignement">${options(cat.alignements, ch.alignement)}</select></label>
      <label class="field">Expérience (XP)<input type="number" inputmode="numeric" min="0" data-field="experience" value="${ch.experience}"></label>
    </div>
    ${lvlXp !== r.niveau && ch.experience > 0 ? `<div class="banner">D'après l'XP : niveau ${lvlXp} (fiche : niveau ${r.niveau}).</div>` : ""}
    <div class="row wrap"><button class="btn small" data-act="portrait">📷 Portrait</button>${ch.portrait ? '<button class="btn small ghost" data-act="portrait-del">Retirer le portrait</button>' : ""}</div>`);

  const subs = s.sous_races.length ? `<label class="field">Sous-espèce<select data-change="subrace">${opt("", ch.sous_race, "—")}${options(s.sous_races, ch.sous_race)}</select></label>` : "";
  const race = card("Espèce", `
    <label class="field">Espèce<select data-change="race">${options(edList(cat.races, cat.editions && cat.editions.races, ch.race), ch.race)}</select></label>${subs}
    <img class="race-img" src="${raceImg(ch)}" alt="" loading="lazy" onerror="this.remove()">
    <div class="list">${s.race_traits.map((t, i) => `<div class="li tap" data-act="info" data-src="trait" data-i="${i}"><div class="name">${esc(t.nom)}</div><span class="muted">›</span></div>`).join("") || '<div class="empty">Aucun trait.</div>'}</div>`);

  const bg = s.historique || {};
  const bgCard = card("Historique", `
    <select data-change="background">${options(edList(cat.historiques, cat.editions && cat.editions.historiques, ch.historique), ch.historique)}</select>
    <div class="muted" style="font-size:.9rem">
      ${bg.competence_1 ? `Compétences : <b>${esc([bg.competence_1, bg.competence_2].filter(Boolean).join(", "))}</b><br>` : ""}
      ${bg.langues && bg.langues !== "-" ? `Langues : ${esc(bg.langues)}<br>` : ""}
      ${bg.outil_maitrise && bg.outil_maitrise !== "-" ? `Outils : ${esc(bg.outil_maitrise)}<br>` : ""}
      ${bg.inventaire_historique ? `Équipement : ${esc(bg.inventaire_historique)}${bg.or ? ` (+${bg.or} po)` : ""}` : ""}
    </div>
    <button class="btn small" data-act="bg-gear">🎒 Ajouter l'équipement d'historique</button>`);

  const classes = s.classes.map((c) => {
    const canSub = c.niveau >= c.niveau_sous_classe;
    return `<div class="card" style="padding:10px;background:var(--input)">
      <div class="row"><select class="grow" data-change="class_change" data-idx="${c.index}">${options((s.edition && s.edition.classes) || cat.classes, c.nom)}</select>
        <div class="stepper"><button data-act="lvl" data-idx="${c.index}" data-d="-1" ${c.niveau <= 1 ? "disabled" : ""} aria-label="Niveau moins">−</button><span>${c.niveau}</span><button data-act="lvl" data-idx="${c.index}" data-d="1" ${r.niveau >= 20 ? "disabled" : ""} aria-label="Niveau plus">+</button></div></div>
      <label class="field">Sous-classe ${canSub ? "" : `(niveau ${c.niveau_sous_classe})`}
        <select data-change="class_sub" data-idx="${c.index}" ${canSub ? "" : "disabled"}>${opt("", c.sous_classe, "—")}${options(c.sous_classes, c.sous_classe)}</select></label>
      ${c.ressources.length ? `<div class="chips">${c.ressources.map(([k, v]) => `<span class="chip">${esc(k)} : <b>${esc(v)}</b></span>`).join("")}</div>` : ""}
      ${s.classes.length > 1 ? `<button class="btn small danger" data-act="class-remove" data-idx="${c.index}">Retirer ${esc(c.nom)}</button>` : ""}
    </div>`;
  }).join("");
  const others = ((s.edition && s.edition.classes) || cat.classes).filter((n) => !s.classes.some((c) => c.nom === n));
  const clsCard = card("Classes", `<button class="btn primary block" data-act="levelup" ${s.niveau_max_atteint ? "disabled" : ""}>▲ Niveau supérieur (assistant)</button>${classes}
    ${sw("Multiclassage", ch.multiclassage, 'data-change="multiclass"')}
    ${ch.multiclassage ? `<select data-change="class_add">${opt("", "", "＋ Ajouter une classe…")}${options(others, "")}</select>` : ""}`,
    `<span class="tag muted">Niveau ${r.niveau} · Maîtrise ${sgn(r.maitrise)}</span>`);

  const feats = s.classes.map((c) => {
    const on = c.aptitudes.filter((f) => f.debloque), next = c.aptitudes.filter((f) => !f.debloque).slice(0, 4);
    return `<div class="li-group">${esc(c.nom)} ${c.niveau}${c.sous_classe ? " — " + esc(c.sous_classe) : ""}</div>
      ${on.map((f) => `<div class="li tap" data-act="info" data-src="feat" data-c="${c.index}" data-n="${esc(f.nom)}"><span class="badge">${f.niveau}</span><div class="name">${esc(f.nom)}${f.source !== c.nom ? `<small>${esc(f.source)}</small>` : ""}</div><span class="muted">›</span></div>`).join("")}
      ${next.map((f) => `<div class="li tap dim" data-act="info" data-src="feat" data-c="${c.index}" data-n="${esc(f.nom)}"><span class="badge">${f.niveau}</span><div class="name">${esc(f.nom)} <small>à venir</small></div></div>`).join("")}`;
  }).join("");
  const featsCard = fold("Aptitudes de classe", `<div class="list">${feats}</div>`);

  const rp = fold("Récit & notes", `
    <label class="field">Histoire du personnage<textarea data-field="histoire" rows="6">${esc(ch.histoire)}</textarea></label>
    <label class="field">Traits, idéaux, liens, défauts<textarea data-field="traits" rows="4">${esc(ch.traits)}</textarea></label>
    <label class="field">Notes de campagne<textarea data-field="notes" rows="6">${esc(ch.notes)}</textarea></label>`, !!(ch.histoire || ch.notes));

  const todo = (s.a_faire || []).length ? fold(`À faire (${s.a_faire.length})`, `<div class="list">${s.a_faire.map((m) => `<div class="li"><span class="badge acc">${esc(TODO_TAB[m.onglet] || m.onglet)}</span><div class="name">${esc(m.message)}</div></div>`).join("")}</div>`, false) : "";
  const warn = s.alertes.length ? `<div class="banner warn">⚠ ${s.alertes.map(esc).join("<br>⚠ ")}</div>` : "";
  return warn + todo + id + race + bgCard + clsCard + featsCard + rp;
};

/* ---------------------------------------------------------------- Caractéristiques & compétences */
TABS.carac = () => {
  const s = S.sheet, ch = S.char, cat = S.cat;
  const m = ch.methode;
  const methodBar = `<div class="seg">${[["achat", "Points (27)"], ["des", "Dés"], ["manuel", "Manuel"]].map(([k, l]) => `<button class="${m === k ? "on" : ""}" data-act="method" data-v="${k}">${l}</button>`).join("")}</div>`;
  let info = "";
  if (m === "achat") info = `<div class="row"><div class="banner grow">Points restants : <b>${s.point_buy.restant}</b> / ${s.point_buy.total}</div><button class="btn small" data-act="reset-scores">Réinitialiser</button></div>`;
  if (m === "des") info = `<div class="row wrap"><button class="btn small primary" data-act="roll-scores">🎲 Lancer 4d6 (×6)</button>${s.tirages.length ? '<button class="btn small" data-act="auto-assign">Répartition auto</button>' : ""}</div>
    ${s.tirages.length ? `<div class="chips">${s.tirages.map((t, i) => `<span class="chip" title="${esc(t.des.join(", "))}">#${i + 1} : <b>${t.total}</b></span>`).join("")}</div>` : '<div class="muted">Lancez les dés pour obtenir six valeurs.</div>'}`;
  const abs = s.abilities.map((a) => {
    let ctl = "";
    if (m === "achat") ctl = `<div class="stepper"><button data-act="buy" data-ab="${esc(a.nom)}" data-d="-1" ${a.achat <= 8 ? "disabled" : ""} aria-label="Moins">−</button><span>${a.achat}</span><button data-act="buy" data-ab="${esc(a.nom)}" data-d="1" ${a.peut_monter ? "" : "disabled"} aria-label="Plus">+</button></div>`;
    if (m === "des") ctl = `<select data-change="assign_roll" data-ab="${esc(a.nom)}">${opt(-1, a.tirage, "—")}${s.tirages.map((t, i) => opt(i, a.tirage, `${t.total} (#${i + 1})`)).join("")}</select>`;
    if (m === "manuel") ctl = `<input type="number" inputmode="numeric" min="1" max="30" value="${a.manuel}" data-setin="scores_manuel" data-key="${esc(a.nom)}" aria-label="${esc(a.nom)}">`;
    return `<div class="ab"><span class="abbr">${a.abbr}</span><button class="roll" data-act="check" data-ab="${esc(a.nom)}" aria-label="Test de ${esc(a.nom)}"><div class="mod">${sgn(a.mod)}</div></button><span class="score">${a.score}</span>${ctl}</div>`;
  }).join("");
  const parts = `<div class="list">${s.abilities.map((a) => {
    const p = a.parts;
    const txt = [`base ${p.base}`, p.race ? `espèce ${sgn(p.race)}` : "", p.asi ? `amélior. ${sgn(p.asi)}` : "", p.divers ? `divers ${sgn(p.divers)}` : "", p.effets ? `effets ${sgn(p.effets)}` : ""].filter(Boolean).join(" · ");
    return `<div class="li"><div class="name">${esc(a.nom)} <b>${a.score}</b><small>${esc(txt)}</small></div><input style="width:76px" type="number" inputmode="numeric" value="${a.divers}" data-setin="bonus_divers" data-key="${esc(a.nom)}" aria-label="Bonus divers ${esc(a.nom)}"></div>`;
  }).join("")}</div><small>Le champ de droite est le bonus divers (objet, MJ…).</small>`;

  const rr = s.race_rule;
  const fixed = Object.entries(rr.fixe || {}).map(([k, v]) => `${cat.abbr[k]} ${sgn(v)}`).join(", ");
  const picks = (rr.libres || []).map((b, k) => `<label class="field">Bonus ${sgn(b)}<select data-change="free_pick" data-k="${k}">${opt("", ch.bonus_libres[k] || "", "—")}${options(cat.caracteristiques, ch.bonus_libres[k] || "")}</select></label>`).join("");
  const raceBonus = fold("Bonus d'espèce", `
    ${fixed ? `<div>Fixes : <b>${esc(fixed)}</b></div>` : ""}
    ${picks ? `<div class="grid3">${picks}</div>` : ""}
    ${sw("Règle libre (Tasha : +2 / +1 au choix)", ch.regle_libre, 'data-change="free_rule"')}
    ${(rr.alternative || []).length ? sw("Variante +1 / +1 / +1", ch.bonus_alt, 'data-change="alt_rule"') : ""}`, (rr.libres || []).some((_, k) => !ch.bonus_libres[k]));

  const asi = s.asi.map((sl) => {
    const c = sl.choix || { mode: "aucun" };
    const feat = S.cat.dons.find((d) => d.nom === c.don);
    const abSel = (k, v) => `<select data-change="asi" data-slot="${esc(sl.id)}" data-k="${k}">${options(cat.caracteristiques, v)}</select>`;
    return `<div class="card" style="padding:10px;background:var(--input)"><b>${esc(sl.label)}</b>
      <select data-change="asi" data-slot="${esc(sl.id)}" data-k="mode" ${sl.don_seul ? "disabled" : ""}>${options([{ value: "aucun", label: "— À choisir —" }, { value: "plus2", label: "+2 à une caractéristique" }, { value: "plus1x2", label: "+1 à deux caractéristiques" }, { value: "don", label: "Un don" }], c.mode)}</select>
      ${c.mode === "plus2" ? abSel("a1", c.a1 || "Force") : ""}
      ${c.mode === "plus1x2" ? `<div class="grid2">${abSel("a1", c.a1 || "Force")}${abSel("a2", c.a2 || "Dextérité")}</div>` : ""}
      ${c.mode === "don" ? `<button class="btn block" data-act="pick-feat" data-slot="${esc(sl.id)}" ${sl.mj ? "disabled" : ""}>${c.don ? "🏅 " + esc(c.don) : "Choisir un don…"}</button>
        ${feat && feat.carac_choix.length > 1 ? `<label class="field">Caractéristique +1<select data-change="asi" data-slot="${esc(sl.id)}" data-k="don_carac">${options(feat.carac_choix, c.don_carac || feat.carac_choix[0])}</select></label>` : ""}
        ${sl.etat ? `<small class="${sl.etat[0] === "ok" ? "" : "badge warn"}">${sl.etat[0] === "ok" ? "✔ prérequis rempli" : "✖ " + esc(sl.etat[1])}</small>` : ""}` : ""}
    </div>`;
  }).join("");
  const asiCard = fold("Améliorations & dons", `${asi || '<div class="empty">Aucune amélioration de caractéristique à ce niveau.</div>'}
    ${s.dons.length ? `<div>Dons : ${s.dons.map((d) => `<span class="chip" data-act="info" data-src="don" data-n="${esc(d)}">${esc(d)}</span>`).join(" ")}</div>` : ""}
    <div class="row wrap">${s.dons_mj.map((d) => `<span class="chip">${esc(d)} <button class="icon-btn" style="min-width:28px;height:28px;font-size:.9rem" data-act="gm-feat-del" data-n="${esc(d)}" aria-label="Retirer">✕</button></span>`).join("")}
    <button class="btn small" data-act="pick-feat" data-slot="">＋ Don accordé par le MJ</button></div>`, s.asi.some((x) => !x.choix || x.choix.mode === "aucun"));

  const saves = `<div class="list">${s.saves.map((r) => {
    const locked = s.resilient.includes(r.carac);
    return `<div class="li"><button class="dot ${r.maitrise ? "on" : ""} ${locked ? "locked" : ""}" data-act="save" data-ab="${esc(r.carac)}" aria-label="Maîtrise">${r.maitrise ? "●" : ""}</button>
      <div class="name">${esc(r.carac)}${(r.avantage || []).length ? ' <span class="badge good">▲</span>' : ""}${(r.desavantage || []).length ? ' <span class="badge warn">▼</span>' : ""}</div>
      <span class="val">${sgn(r.bonus)}</span><button class="d20" data-act="roll-save" data-ab="${esc(r.carac)}" aria-label="Lancer">🎲</button></div>`;
  }).join("")}</div>`;
  const cs = s.class_skills || {};
  const skills = `${cs.nombre ? `<div class="banner">Compétences de classe : ${(cs.choisies || []).length} / ${cs.nombre} — ${esc((cs.options || []).join(", "))}</div>` : ""}
    <div class="list">${s.skills.map((r) => `<div class="li">
      <button class="dot ${r.maitrise ? "on" : ""}" data-act="skill" data-n="${esc(r.nom)}" aria-label="Maîtrise">${r.maitrise ? "●" : ""}</button>
      <button class="dot star ${r.expertise ? "on" : ""}" data-act="skill" data-k="expertise" data-n="${esc(r.nom)}" ${r.maitrise ? "" : 'disabled style="opacity:.25"'} aria-label="Expertise">${r.expertise ? "★" : "☆"}</button>
      <div class="name">${esc(r.nom)} <small>${cat.abbr[r.carac] || ""}${r.historique ? " · historique" : ""}${(r.avantage || []).length ? " · ▲" : ""}${(r.desavantage || []).length ? " · ▼" : ""}</small></div>
      <span class="val">${sgn(r.bonus)}</span><button class="d20" data-act="roll-skill" data-n="${esc(r.nom)}" aria-label="Lancer">🎲</button></div>`).join("")}</div>
    <div class="banner">Perception passive : <b>${s.perception_passive}</b></div>`;

  const L = s.langues;
  const langs = card("Langues", `
    <div class="${L.connues === L.permises ? "" : "banner warn"}">Langues choisies : <b>${L.connues} / ${L.permises}</b>${L.connues < L.permises ? ` — ${L.permises - L.connues} à choisir` : L.connues > L.permises ? ` — ${L.connues - L.permises} de trop` : ""}</div>
    <div class="chips">${ch.langues_liste.map((l) => `<span class="chip on">${esc(l)}</span>`).join("")}</div>
    <button class="btn small" data-act="pick-langs">Choisir les langues…</button>
    <label class="field">Autres langues (texte libre)<input type="text" data-field="langues" value="${esc(ch.langues)}"></label>`);
  const pr = s.maitrises || {};
  const profs = fold("Maîtrises d'armes & d'armures", `<div><b>Armures :</b> ${esc((pr.armures || []).join(", ") || "aucune")}</div><div><b>Armes :</b> ${esc((pr.armes || []).join(", ") || "aucune")}</div>`);

  return card("Caractéristiques", `${methodBar}${info}<div class="grid3 abilities">${abs}</div>
    <small>Touchez un modificateur pour lancer un test.</small>`) + fold("Détail & bonus divers", parts) + raceBonus + asiCard +
    card("Jets de sauvegarde", saves) + card("Compétences", skills) + langs + profs;
};

/* ---------------------------------------------------------------- Combat */
TABS.combat = () => {
  const s = S.sheet, c = s.combat, ch = S.char, cat = S.cat;
  const stats = `<div class="grid4">
    <button class="stat" data-act="info" data-src="ca"><div class="k">CA</div><div class="v">${c.ca}</div><div class="s">${esc(c.ca_formule)}</div></button>
    <button class="stat" data-act="roll-init"><div class="k">INIT.</div><div class="v">${sgn(c.initiative)}</div><div class="s">🎲 lancer</div></button>
    <div class="stat"><div class="k">VITESSE</div><div class="v" style="font-size:1.1rem;padding:6px 0">${esc(c.vitesse.split(" (")[0])}</div><div class="s">${esc((c.vitesse.match(/\((.*)\)/) || [])[1] || "")}</div></div>
    <div class="stat"><div class="k">MAÎTRISE</div><div class="v">${sgn(s.resume.maitrise)}</div><div class="s">niv. ${s.resume.niveau}</div></div></div>`;
  const pct = c.pv_max ? Math.max(0, Math.min(100, (c.pv / c.pv_max) * 100)) : 0;
  const tpct = c.pv_max ? Math.min(100 - pct, (c.pv_temp / c.pv_max) * 100) : 0;
  const death = c.pv <= 0 ? `<div class="banner warn"><b>Jets contre la mort</b>
      <div class="row" style="margin-top:6px"><span style="width:70px">Réussites</span>${[0, 1, 2].map((i) => `<button class="dot ${i < c.mort[0] ? "on" : ""}" data-act="death" data-k="ok" data-i="${i}" aria-label="Réussite ${i + 1}"></button>`).join("")}</div>
      <div class="row" style="margin-top:6px"><span style="width:70px">Échecs</span>${[0, 1, 2].map((i) => `<button class="dot ${i < c.mort[1] ? "on" : ""}" style="${i < c.mort[1] ? "background:var(--warn);border-color:var(--warn)" : ""}" data-act="death" data-k="ko" data-i="${i}" aria-label="Échec ${i + 1}"></button>`).join("")}</div>
      <button class="btn small" style="margin-top:8px" data-act="roll-death">🎲 Jet contre la mort</button></div>` : "";
  const hp = card("Points de vie", `
    ${c.forme ? `<div class="banner">🐾 Forme : <b>${esc(c.forme.nom)}</b> — ${c.forme.pv} PV (les dégâts touchent d'abord la bête)</div>` : ""}
    <div class="row"><div class="hpbig">${c.pv}<span class="muted" style="font-size:1.2rem"> / ${c.pv_max}</span></div>${c.pv_temp ? `<span class="badge acc">+${c.pv_temp} temp.</span>` : ""}</div>
    <div class="hpbar ${pct <= 25 ? "low" : ""}"><i style="width:${pct}%"></i><i class="temp" style="left:${pct}%;width:${tpct}%"></i></div>
    <div class="row"><input id="hp-amt" class="grow" type="number" inputmode="numeric" min="0" placeholder="Montant" aria-label="Montant">
      <button class="btn danger" data-act="hp" data-k="damage">− Dégâts</button><button class="btn good" data-act="hp" data-k="heal">＋ Soins</button></div>
    <div class="grid2"><label class="field">PV temporaires<input type="number" inputmode="numeric" min="0" data-field="pv_temporaires" value="${c.pv_temp}"></label>
      <label class="field">PV actuels<input type="number" inputmode="numeric" min="0" max="${c.pv_max}" data-field="pv_actuels" value="${c.pv}"></label></div>
    ${death}`);
  const conc = c.concentration ? `<div class="banner row"><span class="grow">🧠 Concentration : <b>${esc(c.concentration)}</b></span><button class="btn small" data-act="break-conc">Rompre</button></div>` : "";
  const fx = card("États & effets", `<div class="chips">${c.effets.map((e) => `<button class="chip" data-act="effect" data-key="${esc(e.key)}">${esc(e.icone)} ${esc(e.nom)}</button>`).join("") || '<span class="muted">Aucun effet actif.</span>'}</div>
    <button class="btn small" data-act="pick-effect">＋ Ajouter un état / effet</button>`);
  const res = c.ressources.length ? card("Ressources", c.ressources.map((t) => `<div><div class="row"><b class="grow">${esc(t.label)}</b><span class="muted">${t.total == null ? "illimité" : `${t.total - t.used} / ${t.total}`}</span></div>
      ${t.total != null && t.total <= 30 ? orbs(t.total, t.used, `data-act="res" data-key="${esc(t.key)}" data-total="${t.total}" data-used="${t.used}"`) : ""}
      ${t.info ? `<small>${esc(t.info)}</small>` : ""}</div>`).join("<hr>")) : "";
  const rest = card("Dés de vie & repos", `${c.des_vie.map((d) => `<div class="row"><span class="grow">Dés de vie <b>${d.de}</b> : ${d.restants} / ${d.total}</span><button class="btn small" data-act="hit-die" data-die="${d.de}" ${d.restants ? "" : "disabled"}>Dépenser</button></div>`).join("")}
    <div class="grid2"><button class="btn" data-act="rest" data-k="short">☕ Repos court</button><button class="btn" data-act="rest" data-k="long">🌙 Repos long</button></div>`);
  const weaponRow = (w) => {
    const st = w.stats;
    return `<div class="weapon"><button class="li tap" style="border:0;background:none;padding:0;text-align:left;min-height:40px" data-act="weapon-edit" data-key="${w.key}" data-i="${w.index}">
        <div class="name">${esc(w.nom)}${w.bonus ? ` +${w.bonus}` : ""}<small>${st ? esc([st.type_degats, (st.proprietes || []).join(", "), st.portee ? "portée " + st.portee : ""].filter(Boolean).join(" · ")) : ""}${st && !st.maitrise ? ' · <span class="badge warn">non maîtrisée</span>' : ""}</small></div></button>
      ${st ? `<button class="pillbtn" data-act="roll-atk" data-key="${w.key}" data-i="${w.index}" aria-label="Attaque">${sgn(st.attaque)}</button><button class="pillbtn" data-act="roll-dmg" data-key="${w.key}" data-i="${w.index}" aria-label="Dégâts">${esc(st.degats)}</button>` : "<span></span><span></span>"}</div>`;
  };
  const filled = c.armes.filter((w) => w.nom);
  const weapons = card("Armes", `${filled.map(weaponRow).join("<hr>") || '<div class="empty">Aucune arme équipée.</div>'}
    <div class="grid2"><button class="btn small" data-act="weapon-add" data-key="armes_cac">＋ Corps à corps</button><button class="btn small" data-act="weapon-add" data-key="armes_distance">＋ Distance</button></div>
    <small>Touchez le bonus pour l'attaque, la formule pour les dégâts.</small>`);
  const a = c.armure;
  const armor = card("Armure & bouclier", `
    <label class="field">Armure<select data-change="armor" data-k="nom">${options(cat.armures.map((x) => ({ value: x.nom, label: x.nom })), a.nom)}</select></label>
    <div class="grid2"><label class="field">Bonus magique<select data-change="armor" data-k="bonus">${options([0, 1, 2, 3].map((n) => ({ value: n, label: n ? "+" + n : "Aucun" })), a.bonus || 0)}</select></label>
    <label class="field">Bouclier<select data-change="armor" data-k="bouclier">${opt("", a.bouclier ? a.bouclier_nom : "", "Aucun")}${options(cat.boucliers, a.bouclier ? (a.bouclier_nom || cat.boucliers[0]) : "")}</select></label></div>
    <div class="banner">CA ${c.ca} = ${esc(c.ca_calcul || c.ca_formule)}${c.ca_note ? `<br><small>${esc(c.ca_note)}</small>` : ""}</div>
    ${(c.equipement_non_maitrise || []).map((g) => `<div class="banner warn">⚠ ${esc(g.affichage || g.nom)} : ${esc(g.message)}</div>`).join("")}`);
  const styles = (c.styles || []).length ? card("Style de combat", c.styles.map((sl) => {
    const cur = sl.options.find((o) => o.nom === sl.choix);
    return `<label class="field">${esc(sl.kind === "modele" ? "Modèle d'armure" : "Style")} — ${esc(sl.source)} (niv. ${sl.niveau_requis})${sl.debloque ? "" : " 🔒"}
      <select data-change="style" data-slot="${esc(sl.id)}" ${sl.debloque ? "" : "disabled"}>${opt("", sl.choix, "— Choisir —")}${options(sl.options.map((o) => o.nom), sl.choix)}</select></label>
      ${cur && cur.description ? `<small>${esc(cur.description)}</small>` : ""}`;
  }).join("")) : "";
  const o = s.options || {};
  const colorSel = (kind, cur) => `<select data-change="ancestry" data-k="${kind}">${opt("", cur, "— Choisir la couleur —")}${options(o.couleurs.map((x) => ({ value: x.nom, label: `${x.nom} (${x.description})` })), cur)}</select>`;
  let optBody = "";
  if (o.dragon_race) optBody += `<label class="field">🐉 Dragon ancestral (${esc(ch.race)})${colorSel("race", o.dragon_race.couleur)}</label>${o.dragon_race.info ? `<small>${esc(o.dragon_race.info)}</small>` : ""}`;
  if (o.dragon_sorc) optBody += `<label class="field">🔥 Lignée draconique (Ensorceleur)${colorSel("sorc", o.dragon_sorc.couleur)}</label>${o.dragon_sorc.info ? `<small>${esc(o.dragon_sorc.info)}</small>` : ""}`;
  for (const st of o.ensembles || []) {
    optBody += `<h3>${esc(st.label)} — ${st.chosen.length} / ${st.total}</h3>` + Array.from({ length: st.total }, (_, i) => {
      const cur = st.chosen[i] || ""; const d = st.options.find((x) => x.nom === cur);
      const avail = st.options.filter((x) => x.nom === cur || !st.chosen.includes(x.nom)).map((x) => x.nom);
      return `<select data-change="class_option" data-key="${esc(st.key)}" data-i="${i}">${opt("", cur, "— Choisir —")}${options(avail, cur)}</select>${d ? `<small class="feature-desc">${esc(d.description)}</small>` : ""}`;
    }).join("");
  }
  if (o.technique) {
    const d = o.technique.options.find((x) => x.nom === o.technique.choix);
    optBody += `<label class="field">Technique supérieure — manœuvre<select data-change="maneuver">${opt("", o.technique.choix, "— Choisir —")}${options(o.technique.options.map((x) => x.nom), o.technique.choix)}</select></label>${d ? `<small>${esc(d.description)}</small>` : ""}`;
  }
  const optCard = optBody ? card("Options de classe & d'espèce", optBody) : "";
  return stats + turnCard() + hp + formCard() + conc + fx + res + weapons + styles + optCard + armor + rest;
};

/* ---------------------------------------------------------------- suivi du tour & forme sauvage */
const TURN_GROUPS = [["attaques", "⚔ Attaques"], ["magie", "✨ Magie"], ["capacites", "★ Capacités"], ["reactions", "↺ Réactions"], ["objets", "💍 Objets"], ["generiques", "Actions courantes"]];
const ECO = [["Action", "Action"], ["Action bonus", "Bonus"], ["Réaction", "Réaction"]];
function turnCard() {
  const t = S.sheet.tour; if (!t) return "";
  const eco = ECO.map(([k, l]) => `<button class="chip ${t.etat[k] ? "" : "on"}" data-act="turn-toggle" data-k="${k}" title="${t.etat[k] ? "utilisée" : "disponible"}">${t.etat[k] ? "✖" : "●"} ${l}</button>`).join("");
  const groups = TURN_GROUPS.map(([g, label]) => {
    const tiles = t.actions.filter((a) => a.groupe === g);
    if (!tiles.length) return "";
    const body = `<div class="chips">${tiles.map((a) => `<button class="chip tile ${a.disponible ? "" : "off"}" data-act="tile" data-id="${esc(a.id)}">${esc(a.icone || "")} ${esc(a.nom)} <span class="badge">${esc(a.type === "Action bonus" ? "Bonus" : a.type)}</span></button>`).join("")}</div>`;
    return g === "generiques" ? `<details><summary class="muted" style="cursor:pointer;min-height:36px">${label} (${tiles.length})</summary>${body}</details>` : `<h3>${label}</h3>${body}`;
  }).join("");
  return card("Tour de combat", `<div class="row wrap">${eco}<button class="btn small" data-act="turn-new">↻ Nouveau tour</button></div>
    <div class="row"><span class="grow">Déplacement : <b>${String(t.deplacement).replace(".", ",")} / ${String(t.vitesse).replace(".", ",")} m</b></span>
      <div class="stepper"><button data-act="turn-move" data-d="-1.5" aria-label="Moins 1,5 m">−</button><span style="min-width:44px;font-size:.8rem">1,5 m</span><button data-act="turn-move" data-d="1.5" aria-label="Plus 1,5 m">+</button></div></div>
    ${t.attaques > 1 ? `<small>Attaques de l'action Attaquer : ${t.attaques_faites} / ${t.attaques}</small>` : ""}
    ${groups}<small>Touchez une attaque pour la lancer (attaque + dégâts). Les autres tuiles affichent d'abord leur description.</small>`);
}
function formCard() {
  const f = S.sheet.formes || {}; const fs = f.forme, d = f.druide;
  if (!fs && !d) return "";
  let body = "";
  if (fs) {
    const all = [...((d && d.betes) || []), ...(f.metamorphose || [])];
    const b = all.find((x) => x.nom === fs.bete);
    body += `<div class="banner">${esc(fs.icone)} <b>${esc(fs.bete)}</b> — ${fs.pv} / ${fs.pv_max} PV · CA ${fs.ca}${fs.metamorphose ? " · Métamorphose (concentration)" : ""}</div>
      ${b ? `<small>${esc(b.vitesse)}</small><div class="list">${(b.actions || []).map((a) => `<div class="li"><div class="name">${esc(a)}</div></div>`).join("")}${(b.traits || []).map((a) => `<div class="li"><div class="name muted">${esc(a)}</div></div>`).join("")}</div>` : ""}
      <button class="btn" data-act="form-end">Reprendre ma forme normale</button>`;
  }
  if (d) {
    body += `<small>Druide ${d.regles.niveau}${d.regles.lune ? " (Cercle de la Lune)" : ""} : FP max ${esc(d.fp_max_txt)}, ${esc(d.regles.mouvements)}. ${d.betes.length} bête(s) autorisée(s).</small>
      ${fs ? "" : '<button class="btn primary" data-act="form-pick">🐾 Adopter une forme</button>'}`;
  }
  return card(fs && fs.metamorphose ? "Métamorphose" : "Forme sauvage", body);
}
function beastPicker(title, list, onPick) {
  openPicker(title, list.map((b) => ({ value: b.nom, label: b.nom, sub: `FP ${b.fp} · ${b.pv} PV · CA ${b.ca} · ${b.vitesse}` })), onPick);
}
function useTile(a) {
  if (!a.disponible) { toast(`${a.nom} : ${a.raison || "indisponible"}`, true); return; }
  if (a.sort) { spellSheet(a.sort, "", [{ op: "turn_use", tile: a.id }]); return; }
  if (a.id === "potion:boire") {
    const ps = S.sheet.tour.potions;
    if (!ps.length) { toast("Aucune potion dans l'inventaire.", true); return; }
    openPicker("Boire une potion (action bonus)", ps.map((p, i) => ({ value: String(i), label: p.nom, sub: "× " + p.qte })), (i) => act({ op: "turn_use", tile: a.id, potion: +i }));
    return;
  }
  if (a.id === "classe:cap:forme_sauvage") {
    beastPicker("Forme sauvage — quelle bête ?", ((S.sheet.formes || {}).druide || {}).betes || [], (beast) => act({ op: "turn_use", tile: a.id, beast }));
    return;
  }
  act({ op: "turn_use", tile: a.id });
}

/* ---------------------------------------------------------------- Magie */
TABS.magie = () => {
  const s = S.sheet, m = s.magie;
  const o = s.options || {};
  const any = true;
  const block = m.bloque ? `<div class="banner warn">🔒 ${esc(m.bloque)}</div>` : "";
  const slotRows = m.emplacements.map((n, i) => (n ? `<div class="row"><span style="width:58px" class="muted">Niv. ${i + 1}</span>${orbs(n, m.utilises[i], `data-act="slot" data-l="${i + 1}" data-total="${n}" data-used="${m.utilises[i]}"`)}</div>` : "")).join("");
  const pact = m.pacte.n ? `<div class="row"><span style="width:58px" class="muted">Pacte ${m.pacte.niveau}</span>${orbs(m.pacte.n, m.pacte.utilises, `data-act="pact" data-total="${m.pacte.n}" data-used="${m.pacte.utilises}"`)}</div>` : "";
  const slots = slotRows || pact ? card("Emplacements de sorts", slotRows + pact + "<small>Sphère pleine = disponible. Touchez pour dépenser / récupérer.</small>") : "";
  const conc = m.concentration ? `<div class="banner row"><span class="grow">🧠 Concentration : <b>${esc(m.concentration)}</b></span><button class="btn small" data-act="break-conc">Rompre</button></div>` : "";
  const casters = m.lanceurs.map((c) => {
    const k = c.compte || {};
    const counts = [`Mineurs ${k.mineurs || 0}/${c.mineurs_max || 0}`, c.connus_max != null ? `Connus ${k.sorts || 0}/${c.connus_max}` : "", c.prepares_max != null ? `Préparés ${k.prepares || 0}/${c.prepares_max}` : ""].filter(Boolean);
    let lvl = -1, rows = "";
    for (const sp of c.sorts) {
      if (sp.niveau !== lvl) { lvl = sp.niveau; rows += `<div class="li-group">${lvl ? "Niveau " + lvl : "Sorts mineurs"}</div>`; }
      const canPrep = c.mode === "prepared" && sp.niveau > 0 && !sp.domaine && !sp.accorde;
      rows += `<div class="li ${!sp.prepare && sp.niveau ? "dim" : ""}">
        ${canPrep ? `<button class="dot ${sp.prepare ? "on" : ""}" data-act="prep" data-cls="${esc(c.classe)}" data-n="${esc(sp.nom)}" aria-label="Préparé">${sp.prepare ? "✔" : ""}</button>` : `<span class="dot locked ${sp.niveau ? "on" : ""}" style="opacity:${sp.niveau ? 0.5 : 0.25}">${sp.niveau ? "✔" : "∞"}</span>`}
        <button class="name tap" style="border:0;background:none;text-align:left;padding:4px 0" data-act="spell" data-cls="${esc(c.classe)}" data-n="${esc(sp.nom)}">${esc(sp.nom)}
          ${sp.concentration ? '<span class="badge">C</span>' : ""}${sp.rituel ? '<span class="badge">R</span>' : ""}${sp.domaine || sp.accorde ? '<span class="badge acc">accordé</span>' : ""}
          <small>${esc([sp.ecole, sp.temps, sp.portee].filter(Boolean).join(" · "))}</small></button>
        ${sp.calcul && (sp.calcul.degats || sp.calcul.soins) ? `<button class="pillbtn" data-act="roll-spell" data-cls="${esc(c.classe)}" data-n="${esc(sp.nom)}">${esc(sp.calcul.degats || sp.calcul.soins)}</button>` : ""}
      </div>`;
    }
    return card(`${esc(c.classe)} ${c.niveau}`, `
      <div class="grid3"><div class="stat"><div class="k">DD</div><div class="v">${c.dc}</div></div><button class="stat" data-act="roll-spellatk" data-b="${c.attaque}" data-cls="${esc(c.classe)}"><div class="k">ATTAQUE</div><div class="v">${sgn(c.attaque)}</div></button><div class="stat"><div class="k">${esc(S.cat.abbr[c.carac] || c.carac)}</div><div class="v">${sgn(c.mod)}</div></div></div>
      <div class="chips">${counts.map((x) => `<span class="chip">${esc(x)}</span>`).join("")}<span class="chip">Niveau max ${c.niveau_max}</span></div>
      ${c.sorts.length ? `<div class="list">${rows}</div>` : '<div class="empty">Aucun sort pour l\'instant.</div>'}
      <button class="btn primary block" data-act="library" data-cls="${esc(c.classe)}">📖 Ajouter des sorts</button>`);
  }).join("");
  const extra = (title, list) => (list.length ? card(title, `<div class="list">${list.map((g) => `<button class="li tap" style="border:0;text-align:left;width:100%" data-act="spell" data-cls="" data-n="${esc(g.nom)}"><div class="name">${esc(g.nom)}<small>${esc([g.source, g.usage, g.niveau ? "niveau " + g.niveau : ""].filter(Boolean).join(" · "))}</small></div><span class="muted">›</span></button>`).join("")}</div>`) : "");
  let occ = "";
  if (o.pacte) occ += `<label class="field">Faveur de pacte${o.pacte.disponible ? "" : " (Occultiste niveau 3)"}<select data-change="pact" ${o.pacte.disponible ? "" : "disabled"}>${opt("", o.pacte.choix, "— Aucun —")}${options(o.pacte.options, o.pacte.choix)}</select></label>`;
  if (o.manifestations) {
    const mf = o.manifestations;
    occ += `<div class="${mf.choisies.length < mf.total ? "banner warn" : "muted"}">Manifestations : <b>${mf.choisies.length} / ${mf.total}</b></div>
      <div class="list">${mf.choisies.map((x) => `<button class="li tap" style="border:0;text-align:left;width:100%" data-act="manif" data-n="${esc(x.nom)}"><div class="name">${esc(x.nom)}${x.etat !== "ok" ? ' <span class="badge warn">prérequis</span>' : ""}<small>${esc(x.sorts ? "Sort : " + x.sorts : x.description.slice(0, 90) + (x.description.length > 90 ? "…" : ""))}</small></div><span class="muted">›</span></button>`).join("") || '<div class="empty">Aucune manifestation.</div>'}</div>
      ${mf.choisies.length < mf.total ? '<button class="btn small" data-act="manif-add">＋ Choisir une manifestation</button>' : ""}`;
  }
  if (o.rituels) {
    const r = o.rituels;
    occ += `<h3>Livre des secrets anciens</h3><small>Rituels jusqu'au niveau ${r.max}${r.manquants ? ` — ${r.manquants} rituel(s) de niveau 1 à choisir` : ""}.</small>
      <div class="chips">${r.choisis.map((n) => `<button class="chip on" data-act="ritual-del" data-n="${esc(n)}">${esc(n)} ✕</button>`).join("")}</div>
      <button class="btn small" data-act="ritual-add">＋ Inscrire un rituel</button>`;
  }
  const occCard = occ ? card("Pacte & manifestations occultes", occ) : "";
  const mj = S.sheet.sorts_mj || [];
  const gmCard = fold(`Sorts accordés par le MJ${mj.length ? ` (${mj.length})` : ""}`, `${mj.length ? `<div class="list">${mj.map((x) => `<div class="li"><button class="name tap" style="border:0;background:none;text-align:left;padding:4px 0" data-act="spell" data-cls="" data-n="${esc(x.nom)}">${esc(x.nom)}<small>${esc([x.usage, x.note].filter(Boolean).join(" · "))}</small></button><button class="pillbtn" data-act="gm-spell-del" data-n="${esc(x.nom)}" aria-label="Retirer">✕</button></div>`).join("")}</div>` : '<div class="empty">Aucun.</div>'}
    <button class="btn small" data-act="gm-spell-add">＋ Sort accordé par le MJ</button>`, mj.length > 0);
  const none = !(m.lanceurs.length || m.accordes.length || m.raciaux.length || occ) ? card("Magie", '<div class="empty">Ce personnage ne lance pas de sorts.<br><small>Les sorts d\'espèce, de sous-classe ou accordés par le MJ apparaîtront ici.</small></div>') : "";
  return none + block + slots + conc + casters + occCard + extra("Sorts accordés", m.accordes) + extra("Sorts d'espèce", m.raciaux) + gmCard;
};

/* ---------------------------------------------------------------- Sac */
TABS.sac = () => {
  const s = S.sheet, inv = s.inventaire, ch = S.char;
  const coins = ["pc", "pa", "pe", "po", "pp"];
  const purse = card("Bourse", `<div class="grid5">${coins.map((k) => `<label class="field" style="text-align:center">${k.toUpperCase()}<input type="number" inputmode="numeric" min="0" style="text-align:center;padding:8px 4px" data-setin="pieces" data-key="${k}" value="${inv.pieces[k] || 0}"></label>`).join("")}</div>`);
  const ch_ = inv.charge;
  const pct = ch_.capacite ? Math.min(100, (ch_.poids / ch_.capacite) * 100) : 0;
  const load = card("Charge", `<div class="row"><b class="grow">${String(ch_.poids).replace(".", ",")} kg</b><span class="muted">capacité ${String(ch_.capacite).replace(".", ",")} kg</span></div>
    <div class="hpbar ${ch_.etat !== "ok" ? "low" : ""}"><i style="width:${pct}%"></i></div><small>${esc(ch_.message)}</small>
    ${sw("Possède un Sac sans fond", ch.sac_sans_fond, 'data-field="sac_sans_fond"')}`);
  const items = card("Objets", `${inv.objets.length ? `<div class="list">${inv.objets.map((o) => `<div class="li">
      <button class="name tap" style="border:0;background:none;text-align:left;padding:4px 0" data-act="item" data-i="${o.index}">${esc(o.nom)}<small>${esc(o.categorie)}${o.poids ? ` · ${String(o.poids * o.qte).replace(".", ",")} kg` : ""}</small></button>
      <div class="stepper"><button data-act="qty" data-i="${o.index}" data-q="${o.qte - 1}" aria-label="Moins">−</button><span>${o.qte}</span><button data-act="qty" data-i="${o.index}" data-q="${o.qte + 1}" aria-label="Plus">+</button></div></div>`).join("")}</div>` : '<div class="empty">Sac vide.</div>'}
    <div class="grid2"><button class="btn small" data-act="item-add">＋ Objet</button><button class="btn small" data-act="pack-add">＋ Paquetage</button></div>`);
  const magic = card("Objets magiques", `<div class="${inv.harmonises > inv.harmonisation_max ? "banner warn" : "muted"}">Harmonisation : <b>${inv.harmonises} / ${inv.harmonisation_max}</b></div>
    ${inv.magiques.length ? `<div class="list">${inv.magiques.map((o) => `<div class="li" style="flex-wrap:wrap">
      <button class="name tap" style="border:0;background:none;text-align:left;padding:4px 0" data-act="magic" data-i="${o.index}">${esc(o.nom)} <span class="badge acc">${esc(o.rarete)}</span>${o.prerequis === "ko" ? '<span class="badge warn">prérequis</span>' : ""}<small>${esc(o.type)}${o.lien ? " · harmonisation" : ""}</small></button>
      <label class="chip ${o.equipe ? "on" : ""}"><input type="checkbox" hidden data-change="magic_equip" data-i="${o.index}" ${o.equipe ? "checked" : ""}>Équipé</label>
      ${o.lien ? `<label class="chip ${o.harmonise ? "on" : ""}"><input type="checkbox" hidden data-change="magic_attune" data-i="${o.index}" ${o.harmonise ? "checked" : ""}>Lié</label>` : ""}</div>`).join("")}</div>` : '<div class="empty">Aucun objet magique.</div>'}
    <div class="grid2"><button class="btn small" data-act="magic-add">＋ Objet magique</button><button class="btn small" data-act="custom-magic">✎ Sur mesure</button></div>`);
  const notes = fold("Notes d'inventaire", `<textarea data-field="inventaire" rows="5">${esc(ch.inventaire)}</textarea>`, !!ch.inventaire);
  return purse + load + items + magic + notes;
};

/* ---------------------------------------------------------------- Alliés (ménagerie : familiers, compagnons, invocations, montures) */
TABS.allies = () => {
  const list = S.sheet.menagerie || [], hints = S.sheet.conseils_compagnons || [];
  const tips = hints.map((h) => `<div class="banner ${h.niveau === "warning" ? "warn" : ""}">${esc(h.texte)}${h.recommandes.length ? `<div class="chips" style="margin-top:6px">${h.recommandes.map((id) => { const e = S.cat.entites.find((x) => x.id === id); return e ? `<button class="chip" data-act="ally-add-id" data-id="${esc(id)}">＋ ${esc(e.nom)}</button>` : ""; }).join("")}</div>` : ""}</div>`).join("");
  const cards = list.map((m) => {
    const pct = m.pv_max ? Math.max(0, Math.min(100, (m.pv / m.pv_max) * 100)) : 0;
    const stats = Object.entries(m.stats).map(([ab, v]) => `<button class="ab" style="padding:6px 2px" data-act="ally-check" data-uid="${m.uid}" data-ab="${esc(ab)}"><span class="abbr">${esc(S.cat.abbr[ab] || ab)}</span><span class="mod" style="font-size:1.15rem">${sgn(m.mods[ab])}</span><span class="score">${v}</span></button>`).join("");
    const acts = m.actions.map((a, i) => `<div class="li" style="flex-wrap:wrap"><div class="name"><b>${esc(a.nom)}</b><small>${esc(a.description)}</small></div>
      ${a.attaque != null ? `<button class="pillbtn" data-act="ally-atk" data-uid="${m.uid}" data-i="${i}">${sgn(a.attaque)}</button>` : ""}
      ${/d\d/.test(a.degats) ? `<button class="pillbtn" data-act="ally-dmg" data-uid="${m.uid}" data-i="${i}">${esc(a.degats)}</button>` : ""}</div>`).join("");
    return `<details class="card" ${list.length === 1 ? "open" : ""}><summary><h2>${esc(m.nom)} <small class="muted" style="font-family:var(--font)">${m.pv}/${m.pv_max} PV · CA ${esc(m.ca)}${m.statut !== "Actif" ? " · " + esc(m.statut) : ""}</small></h2></summary>
      <small>${esc([m.taille, m.type].filter(Boolean).join(" · "))}${m.auto ? " · ajouté d'office" : ""}</small>
      <div class="hpbar ${pct <= 25 ? "low" : ""}"><i style="width:${pct}%"></i></div>
      <div class="grid3"><label class="field">PV<input type="number" inputmode="numeric" min="0" max="${m.pv_max}" value="${m.pv}" data-change="ally" data-uid="${m.uid}" data-k="pv"></label>
        <label class="field">PV temp.<input type="number" inputmode="numeric" min="0" value="${m.pv_temp || 0}" data-change="ally" data-uid="${m.uid}" data-k="pv_temp"></label>
        <label class="field">Statut<select data-change="ally" data-uid="${m.uid}" data-k="statut">${options(S.cat.statuts_compagnons, m.statut)}</select></label></div>
      ${m.niveau_sort_min ? `<label class="field">Niveau du sort de convocation<select data-change="ally" data-uid="${m.uid}" data-k="niveau_sort">${options(Array.from({ length: 10 - m.niveau_sort_min }, (_, i) => m.niveau_sort_min + i), m.niveau_sort || m.niveau_sort_min)}</select></label>` : ""}
      <div class="muted" style="font-size:.9rem">CA ${esc(m.ca)}${m.ca_note ? ` (${esc(m.ca_note)})` : ""} · ${esc(Object.entries(m.vitesses).map(([k, v]) => `${k} ${v}`).join(", "))}${m.dd ? ` · DD ${m.dd}` : ""}${m.perception_passive ? ` · Perception passive ${esc(m.perception_passive)}` : ""}${m.sens ? ` · ${esc(m.sens)}` : ""}</div>
      <div class="grid3 abilities">${stats}</div>
      ${acts ? `<h3>Actions</h3><div class="list">${acts}</div>` : ""}
      ${m.traits.length ? `<h3>Traits</h3><div class="list">${m.traits.map((t) => `<div class="li"><div class="name"><b>${esc(t.nom)}</b><small>${esc(t.description)}</small></div></div>`).join("")}</div>` : ""}
      ${m.reactions.length ? `<h3>Réactions</h3><div class="list">${m.reactions.map((t) => `<div class="li"><div class="name"><b>${esc(t.nom)}</b><small>${esc(t.description)}</small></div></div>`).join("")}</div>` : ""}
      <label class="field">Nom<input type="text" value="${esc(m.nom)}" data-change="ally" data-uid="${m.uid}" data-k="nom"></label>
      ${m.auto ? "" : `<button class="btn small danger" data-act="ally-del" data-uid="${m.uid}">Retirer de la ménagerie</button>`}</details>`;
  }).join("");
  return tips + (cards || card("Alliés", '<div class="empty">Aucun familier, compagnon, invocation ni monture.</div>')) +
    '<button class="btn primary" data-act="ally-add">＋ Ajouter une créature</button>';
};

/* ============================================================== feuille du bas (sélecteurs / détails) */
function openSheet(title, renderBody, ctx = {}) {
  $("#sheet-title").textContent = title;
  $("#sheet").classList.remove("full");
  S.sheetCtx = { ...ctx, renderBody, refresh: () => { $("#sheet-body").innerHTML = renderBody(); ctx.after && ctx.after(); } };
  $("#sheet-body").innerHTML = renderBody();
  $("#sheet").hidden = false; $("#scrim").hidden = false;
  ctx.after && ctx.after();
  const f = $("#sheet-body input[type=search]");
  if (f && matchMedia("(min-width: 760px)").matches) f.focus();
}
function closeSheet() {
  $("#sheet").hidden = true; $("#sheet").classList.remove("full"); S.sheetCtx = null;
  if (!$("#drawer").classList.contains("open")) $("#scrim").hidden = true;
}
/** Liste filtrable : items = [{value, label, sub, badge}] ; onPick(value). */
function openPicker(title, items, onPick, { free = false, filters = null, placeholder = "Rechercher…", extra = "" } = {}) {
  let q = "", f = "";
  const body = () => {
    const nq = norm(q);
    const list = items.filter((it) => (!nq || norm(it.label).includes(nq) || norm(it.sub).includes(nq)) && (!f || it.filter === f));
    const shown = list.slice(0, 200);
    return `<input type="search" id="pick-q" value="${esc(q)}" placeholder="${esc(placeholder)}" autocomplete="off">
      ${filters ? `<div class="chips">${[["", "Tous"], ...filters].map(([v, l]) => `<button class="chip ${f === v ? "on" : ""}" data-pf="${esc(v)}">${esc(l)}</button>`).join("")}</div>` : ""}
      ${extra}
      ${free && q.trim() ? `<button class="btn block" data-pick="${esc(q.trim())}">＋ Ajouter « ${esc(q.trim())} »</button>` : ""}
      <div class="list">${shown.map((it) => `<button class="li tap" style="border:0;text-align:left;width:100%" data-pick="${esc(it.value)}"><div class="name">${esc(it.label)}${it.badge ? ` <span class="badge acc">${esc(it.badge)}</span>` : ""}${it.sub ? `<small>${esc(it.sub)}</small>` : ""}</div></button>`).join("") || '<div class="empty">Aucun résultat.</div>'}</div>
      ${list.length > shown.length ? `<small>${list.length - shown.length} résultat(s) de plus : affinez la recherche.</small>` : ""}`;
  };
  openSheet(title, body, {
    after: () => {
      const inp = $("#pick-q");
      inp.addEventListener("input", () => { q = inp.value; const pos = inp.selectionStart; S.sheetCtx.refresh(); const n = $("#pick-q"); n.focus(); n.setSelectionRange(pos, pos); });
      $$("[data-pf]", $("#sheet-body")).forEach((b) => b.addEventListener("click", () => { f = b.dataset.pf; S.sheetCtx.refresh(); }));
      $$("[data-pick]", $("#sheet-body")).forEach((b) => b.addEventListener("click", () => { closeSheet(); onPick(b.dataset.pick); }));
    },
  });
}
function infoSheet(title, html, actions = "") {
  openSheet(title, () => `<div class="feature-desc">${html}</div>${actions}`);
}

/* ---------------------------------------------------------------- sorts */
async function spellSheet(name, cls, preOps = []) {
  const known = (S.sheet.magie.lanceurs.find((c) => c.classe === cls) || { sorts: [] }).sorts.find((s) => s.nom === name);
  let sp = known;
  if (!sp) {
    const ch = { ...S.char }; delete ch.portrait;
    try { sp = await api("/api/spell", { nom: name, character: ch }); } catch (e) { toast(e.message, true); return; }
  }
  let target = "soi", ritual = false;
  const m = S.sheet.magie;
  const body = () => {
    const lvls = [];
    if (sp.niveau) {
      m.emplacements.forEach((n, i) => { if (i + 1 >= sp.niveau && n - m.utilises[i] > 0) lvls.push({ value: i + 1, label: `Niveau ${i + 1} (${n - m.utilises[i]} restant${n - m.utilises[i] > 1 ? "s" : ""})` }); });
      if (m.pacte.n && m.pacte.niveau >= sp.niveau && m.pacte.n - m.pacte.utilises > 0) lvls.push({ value: m.pacte.niveau, label: `Pacte, niveau ${m.pacte.niveau}` });
    }
    const calc = sp.calcul || {};
    return `<div class="chips"><span class="chip">${sp.niveau ? "Niveau " + sp.niveau : "Sort mineur"}</span>${sp.ecole ? `<span class="chip">${esc(sp.ecole)}</span>` : ""}${sp.concentration ? '<span class="chip">Concentration</span>' : ""}${sp.rituel ? '<span class="chip">Rituel</span>' : ""}</div>
      <div class="list">${[["Incantation", sp.temps], ["Portée", sp.portee], ["Composantes", sp.composantes], ["Durée", sp.duree]].filter((x) => x[1]).map(([k, v]) => `<div class="li"><div class="name muted">${k}</div><div>${esc(v)}</div></div>`).join("")}</div>
      <div class="feature-desc">${esc(sp.description)}</div>
      ${calc.degats ? `<div class="banner">Dégâts : <b>${esc(calc.degats)}</b> ${esc(calc.type_degats || sp.type_degats || "")}</div>` : ""}
      ${calc.soins ? `<div class="banner good">Soins : <b>${esc(calc.soins)}</b></div>` : ""}
      ${calc.pv_temp ? `<div class="banner">PV temporaires : <b>${esc(calc.pv_temp)}</b></div>` : ""}
      ${calc.regle_sup ? `<small>Au niveau supérieur : ${esc(calc.regle_sup)}</small>` : ""}
      ${sp.buff ? `<div class="seg"><button class="${target === "soi" ? "on" : ""}" data-t="soi">Sur moi</button><button class="${target === "allie" ? "on" : ""}" data-t="allie">Sur un allié</button></div>` : ""}
      ${sp.niveau ? (lvls.length ? `<label class="field">Emplacement<select id="cast-lvl">${options(lvls, lvls[0].value)}</select></label>` : '<div class="banner warn">Plus d\'emplacement disponible.</div>') : ""}
      <div class="grid2">
        <button class="btn primary" id="cast-go" ${sp.niveau && !lvls.length ? "disabled" : ""}>✨ Lancer</button>
        ${sp.rituel ? '<button class="btn" id="cast-ritual">Rituel (sans emplacement)</button>' : calc.degats || calc.soins ? `<button class="btn" id="cast-roll">🎲 ${esc(calc.degats || calc.soins)}</button>` : "<span></span>"}
      </div>
      ${known && !known.accorde && cls ? `<button class="btn danger small" id="spell-del">Retirer de mes sorts</button>` : ""}`;
  };
  openSheet(sp.nom, body, {
    after: () => {
      $$("[data-t]", $("#sheet-body")).forEach((b) => b.addEventListener("click", () => { target = b.dataset.t; S.sheetCtx.refresh(); }));
      const go = (useSlot) => {
        const lvl = $("#cast-lvl") ? +$("#cast-lvl").value : 0;
        closeSheet();
        if (norm(sp.nom) === "metamorphose") {               // Métamorphose sur soi : choix de la bête
          const list = (S.sheet.formes || {}).metamorphose || [];
          if (!list.length) { toast("Aucune bête disponible pour Métamorphose.", true); return; }
          openPicker("Métamorphose — choisissez la bête", list.map((b) => ({ value: b.nom, label: b.nom, sub: `FP ${b.fp} · ${b.pv} PV · CA ${b.ca} · ${b.vitesse}` })),
            (beast) => act([...preOps, { op: "cast", nom: sp.nom, use_slot: useSlot, slot_level: lvl, beast }]));
          return;
        }
        act([...preOps, { op: "cast", nom: sp.nom, use_slot: useSlot, slot_level: lvl, target }]);
      };
      $("#cast-go") && $("#cast-go").addEventListener("click", () => go(true));
      $("#cast-ritual") && $("#cast-ritual").addEventListener("click", () => go(false));
      $("#cast-roll") && $("#cast-roll").addEventListener("click", () => rollFormula(sp.nom, (sp.calcul || {}).degats || (sp.calcul || {}).soins, (sp.calcul || {}).type_degats || ""));
      $("#spell-del") && $("#spell-del").addEventListener("click", () => { closeSheet(); act({ op: "spell_remove", cls, nom: sp.nom }); });
    },
  });
}
function librarySheet(cls) {
  let q = "", lvl = "";
  const caster = () => S.sheet.magie.lanceurs.find((c) => c.classe === cls);
  const body = () => {
    const c = caster(); if (!c) return '<div class="empty">Classe introuvable.</div>';
    const known = new Set(c.sorts.map((s) => s.nom));
    const allowed = new Set(c.apprenables);
    const nq = norm(q);
    const list = S.cat.sorts.filter((s) => (S.prefs.gm ? edOk(s.edition) : allowed.has(s.nom) || known.has(s.nom))
      && (lvl === "" || s.niveau === +lvl) && (!nq || norm(s.nom).includes(nq)))
      .sort((a, b) => a.niveau - b.niveau || a.nom.localeCompare(b.nom, "fr"));
    const levels = [...new Set(S.cat.sorts.filter((s) => S.prefs.gm || allowed.has(s.nom)).map((s) => s.niveau))].sort((a, b) => a - b);
    return `<input type="search" id="lib-q" value="${esc(q)}" placeholder="Rechercher un sort…" autocomplete="off">
      <div class="chips"><button class="chip ${lvl === "" ? "on" : ""}" data-lv="">Tous</button>${levels.map((n) => `<button class="chip ${String(n) === lvl ? "on" : ""}" data-lv="${n}">${n ? "Niv. " + n : "Mineurs"}</button>`).join("")}</div>
      ${sw("Mode MJ (tous les sorts, sans restriction)", S.prefs.gm, 'id="lib-gm"')}
      <div class="list">${list.slice(0, 200).map((s) => `<div class="li"><button class="name tap" style="border:0;background:none;text-align:left;padding:4px 0" data-sp="${esc(s.nom)}">${esc(s.nom)}${s.concentration ? ' <span class="badge">C</span>' : ""}${s.rituel ? ' <span class="badge">R</span>' : ""}<small>${s.niveau ? "Niveau " + s.niveau : "Mineur"} · ${esc(s.ecole)}${allowed.has(s.nom) ? "" : " · hors liste"}</small></button>
        <button class="pillbtn" data-add="${esc(s.nom)}" aria-label="${known.has(s.nom) ? "Retirer" : "Ajouter"}">${known.has(s.nom) ? "✓" : "＋"}</button></div>`).join("") || '<div class="empty">Aucun sort.</div>'}</div>
      ${list.length > 200 ? `<small>${list.length - 200} sort(s) de plus : affinez la recherche.</small>` : ""}`;
  };
  openSheet(`Sorts — ${cls}`, body, {
    after: () => {
      const inp = $("#lib-q");
      inp.addEventListener("input", () => { q = inp.value; const p = inp.selectionStart; S.sheetCtx.refresh(); const n = $("#lib-q"); n.focus(); n.setSelectionRange(p, p); });
      $$("[data-lv]", $("#sheet-body")).forEach((b) => b.addEventListener("click", () => { lvl = b.dataset.lv; S.sheetCtx.refresh(); }));
      $("#lib-gm").addEventListener("change", (e) => { S.prefs.gm = e.target.checked; savePrefs(); S.sheetCtx.refresh(); });
      $$("[data-add]", $("#sheet-body")).forEach((b) => b.addEventListener("click", () => {
        const c = caster(); const nom = b.dataset.add;
        const has = c.sorts.some((s) => s.nom === nom);
        act(has ? { op: "spell_remove", cls, nom } : { op: "spell_add", cls, nom, force: S.prefs.gm });
      }));
      $$("[data-sp]", $("#sheet-body")).forEach((b) => b.addEventListener("click", () => spellSheet(b.dataset.sp, cls)));
    },
  });
}

/* ============================================================== assistant de montée de niveau (core/levelup.py) */
const LU_STEPS = ["Classe", "Points de vie", "Aptitudes", "Choix", "Sorts", "Récapitulatif"];
const LU = { cls: "", ops: [], view: null, step: 0, q: {}, lvl: {} };

function luChar() { const ch = { ...S.char }; delete ch.portrait; return ch; }
async function luCall(op) {
  if (op) LU.ops.push(op);
  try {
    const v = await api("/api/levelup", { character: luChar(), classe: LU.cls, ops: LU.ops });
    if (op && v.errors && v.errors.length) { LU.ops.pop(); v.errors.forEach((e) => toast(e, true)); }
    LU.view = v; LU.cls = v.classe;
  } catch (e) { if (op) LU.ops.pop(); toast(e.message, true); }
  if (S.sheetCtx && S.sheetCtx.lu) S.sheetCtx.refresh();
}
async function openLevelUp() {
  LU.cls = ""; LU.ops = []; LU.step = 0; LU.q = {}; LU.lvl = {}; LU.view = null;
  await luCall();
  if (!LU.view) return;
  openSheet("▲ Niveau supérieur", luBody, { lu: true, after: luAfter });
  $("#sheet").classList.add("full");
}
function luDone(v) {
  const m = v.manquants || [];
  const choices = m.filter((x) => x.kind !== "sorts").length, spells = m.filter((x) => x.kind === "sorts").length;
  return { done: [true, true, true, !choices, !spells, !m.length], counts: [0, 0, 0, choices, spells, 0] };
}
function luBody() {
  const v = LU.view; if (!v) return '<div class="empty">Chargement…</div>';
  const { done, counts } = luDone(v);
  const steps = `<div class="chips lu-steps">${LU_STEPS.map((n, i) => `<button class="chip ${i === LU.step ? "on" : ""}" data-lu-step="${i}">${done[i] ? "✔" : "○"} ${i + 1}. ${n}${counts[i] ? ` (${counts[i]})` : ""}</button>`).join("")}</div>`;
  const head = `<div class="banner"><b>${esc(v.titre)}</b> · niveau global ${v.niveau_global[0]} → ${v.niveau_global[1]}</div>`;
  const body = [luStepClass, luStepHP, luStepFeats, luStepChoices, luStepSpells, luStepRecap][LU.step](v);
  const last = LU.step === LU_STEPS.length - 1;
  const nav = `<div class="grid2 lu-nav"><button class="btn" data-lu-go="-1" ${LU.step ? "" : "disabled"}>◀ Précédent</button>
    ${last ? `<button class="btn primary" data-lu-confirm ${v.pret ? "" : "disabled"}>✔ Confirmer</button>` : `<button class="btn primary" data-lu-go="1">Suivant ▶</button>`}</div>`;
  return steps + head + body + nav;
}
function luStepClass(v) {
  return `<div class="list">${v.options.map((o) => `<button class="li tap" style="border:0;text-align:left;width:100%" data-lu-cls="${esc(o.classe)}">
      <span class="dot ${o.classe === v.classe ? "on" : ""}">${o.classe === v.classe ? "●" : ""}</span>
      <div class="name">${esc(o.classe)} <small>${o.nouvelle ? "nouvelle classe (multiclassage)" : `niveau ${o.avant} → ${o.apres}`}</small>
      ${o.prerequis ? `<small class="badge warn">⚠ ${esc(o.prerequis)}</small>` : ""}</div></button>`).join("")}</div>
    ${v.prerequis ? `<div class="banner warn">⚠ Prérequis de multiclassage non remplis : ${esc(v.prerequis)}. (Possible avec l'accord du MJ.)</div>` : ""}
    ${!S.char.multiclassage ? '<small>Pour prendre une autre classe, activez « Multiclassage » dans la carte Classes.</small>' : ""}
    <div class="muted">Dé de vie ${esc(v.pv.de)}. Changer de classe annule les choix déjà faits dans l'assistant.</div>`;
}
function luStepHP(v) {
  const p = v.pv;
  const how = p.premier ? `maximum du dé de vie (${p.moyenne})` : `moyenne du ${p.de} : ${p.moyenne}`;
  return `<div class="card" style="background:var(--input)"><div class="hpbig">+${p.gain} PV</div>
    <div>${esc(how)} ${sgn(p.con)} (Constitution)${p.bonus ? ` ${sgn(p.bonus)} (aptitudes, espèce)` : ""}</div>
    <div>PV maximum : ${p.avant} → <b>${p.apres}</b></div></div>
    <small>La fiche applique la moyenne fixe du dé de vie à chaque niveau (règle du Manuel des Joueurs).</small>`;
}
function luStepFeats(v) {
  const list = v.aptitudes.length ? v.aptitudes.map((f) => `<details class="card" style="background:var(--input)" open><summary><h3>✦ ${esc(f.nom)}</h3></summary>
      ${f.sous_classe ? `<small>${esc(f.source)}</small>` : ""}<div class="feature-desc">${esc(f.description)}</div></details>`).join("")
    : '<div class="empty">Aucune nouvelle aptitude à ce niveau (progression des valeurs seulement).</div>';
  return list + (v.prochain ? `<small>Prochain palier : niveau ${v.prochain.niveau} ${esc(v.prochain.icones)} — ${esc(v.prochain.texte)}</small>` : "");
}
function luStepChoices(v) {
  const c = v.choix, cat = S.cat; let out = "";
  if (c.sous_classe) out += card("◆ Sous-classe", `<select data-lu="sub">${opt("", c.sous_classe.choix, "— Choisir —")}${options(c.sous_classe.options, c.sous_classe.choix)}</select>`);
  for (const sl of c.asi) {
    const ch = sl.choix || { mode: "aucun" };
    const feat = cat.dons.find((d) => d.nom === ch.don);
    const ab = (k, val) => `<select data-lu="asi" data-slot="${esc(sl.id)}" data-k="${k}">${options(cat.caracteristiques, val)}</select>`;
    out += card(`▲ ${esc(sl.label)}`, `
      <select data-lu="asi" data-slot="${esc(sl.id)}" data-k="mode" ${sl.don_seul ? "disabled" : ""}>${options([{ value: "aucun", label: "— À choisir —" }, { value: "plus2", label: "+2 à une caractéristique" }, { value: "plus1x2", label: "+1 à deux caractéristiques" }, { value: "don", label: "Un don" }], ch.mode)}</select>
      ${ch.mode === "plus2" ? ab("a1", ch.a1 || "Force") : ""}
      ${ch.mode === "plus1x2" ? `<div class="grid2">${ab("a1", ch.a1 || "Force")}${ab("a2", ch.a2 || "Dextérité")}</div>` : ""}
      ${ch.mode === "don" ? `<button class="btn block" data-lu-feat="${esc(sl.id)}">${ch.don ? "🏅 " + esc(ch.don) : "Choisir un don…"}</button>
        ${feat && feat.carac_choix.length > 1 ? `<label class="field">Caractéristique +1<select data-lu="asi" data-slot="${esc(sl.id)}" data-k="don_carac">${options(feat.carac_choix, ch.don_carac || feat.carac_choix[0])}</select></label>` : ""}
        ${feat ? `<small>${esc(feat.description)}</small>` : ""}
        ${sl.etat ? `<small class="${sl.etat[0] === "ok" ? "" : "badge warn"}">${sl.etat[0] === "ok" ? "✔ prérequis rempli" : "✖ " + esc(sl.etat[1])}</small>` : ""}` : ""}`);
  }
  for (const sl of c.styles) {
    const cur = sl.options.find((o) => o.nom === sl.choix);
    out += card(`⚔ ${sl.kind === "modele" ? "Modèle d'armure" : "Style de combat"} — ${esc(sl.classe)}`, `
      <select data-lu="style" data-slot="${esc(sl.id)}">${opt("", sl.choix, "— Choisir —")}${options(sl.options.map((o) => o.nom), sl.choix)}</select>
      ${cur ? `<small>${esc(cur.description)}</small>` : ""}`);
  }
  if (c.pacte) out += card("✧ Faveur de pacte", `<select data-lu="pact">${opt("", c.pacte.choix, "— Choisir —")}${options(c.pacte.options, c.pacte.choix)}</select>`);
  if (c.manifestations) {
    const m = c.manifestations;
    out += card(`✧ Manifestations occultes — ${m.nombre} à choisir`, `<small>${m.connues} / ${m.total} connues. Seules celles dont les prérequis sont remplis sont proposées.</small>` +
      Array.from({ length: m.nombre }, (_, i) => {
        const cur = m.choisies[i] || ""; const info = m.options.find((o) => o.nom === cur);
        return `<label class="field">Manifestation ${i + 1}<select data-lu="invocation" data-i="${i}">${opt("", cur, "— Choisir —")}${options(m.options.map((o) => o.nom), cur)}</select></label>
          ${info ? `<small>${esc(info.description)}${info.sorts ? `<br><i>Sort accordé : ${esc(info.sorts)}</i>` : ""}</small>` : ""}`;
      }).join(""));
  }
  if (!out) out = '<div class="empty">Aucun choix à faire dans l\'assistant à ce niveau.</div>';
  if (v.ensuite.length) out += `<div class="banner"><b>À faire ensuite</b> (après confirmation)<br>${v.ensuite.map((m) => `○ ${esc(m.onglet)} — ${esc(m.message)}`).join("<br>")}</div>`;
  return out;
}
function luSpellRow(sp, right) {
  return `<div class="li"><button class="name tap" style="border:0;background:none;text-align:left;padding:4px 0" data-lu-info="${esc(sp.nom)}">${sp.nouveau ? "✦ " : ""}${esc(sp.nom)}${sp.concentration ? ' <span class="badge">C</span>' : ""}${sp.rituel ? ' <span class="badge">R</span>' : ""}<small>${sp.niveau ? "Niveau " + sp.niveau : "Mineur"} · ${esc(sp.ecole)}</small></button>${right}</div>`;
}
function luStepSpells(v) {
  if (!v.sorts.length) return '<div class="empty">Cette classe ne lance pas de sorts à ce niveau.</div>';
  return v.sorts.map((b) => {
    const q = norm(LU.q[b.classe] || ""), lv = LU.lvl[b.classe] ?? "";
    const avail = b.options.filter((s) => (!q || norm(s.nom).includes(q)) && (lv === "" || String(s.niveau) === lv));
    const levels = [...new Set(b.options.map((s) => s.niveau))].sort((a, c) => a - c);
    const p = b.prepares;
    const mine = b.mes_sorts.map((s) => luSpellRow(s,
      (s.nouveau ? `<button class="pillbtn" data-lu-unlearn="${esc(s.nom)}" data-cls="${esc(b.classe)}" aria-label="Retirer">✕</button>` : "") +
      (s.niveau && p && !p.toujours && !s.accorde ? `<button class="dot ${s.prepare ? "on" : ""}" data-lu-prep="${esc(s.nom)}" data-cls="${esc(b.classe)}" data-on="${s.prepare ? 0 : 1}" aria-label="Préparé">${s.prepare ? "✔" : ""}</button>` : ""))).join("");
    let swap = "";
    if (b.echange) {
      const e = b.echange, st = e.etat;
      swap = card("🔁 Remplacer un sort connu (facultatif)", `<small>${esc(e.regle)}</small>
        <label class="field">1. Sort à oublier<select data-lu="swap_forget" data-cls="${esc(b.classe)}" ${st.nouveau ? "disabled" : ""}>${opt("", st.oublie, "— garder tous mes sorts —")}${options([...new Set([...(st.oublie ? [st.oublie] : []), ...e.candidats.map((s) => s.nom)])], st.oublie)}</select></label>
        ${st.oublie && !st.nouveau ? `<div>2. Remplaçant :</div><div class="list">${e.options.slice(0, 120).map((s) => luSpellRow(s, `<button class="pillbtn" data-lu-swap="${esc(s.nom)}" data-cls="${esc(b.classe)}">＋</button>`)).join("")}</div>` : ""}
        <div class="row"><span class="grow">${st.nouveau ? `✔ Échange : ${esc(st.oublie)} → ${esc(st.nouveau)}` : st.oublie ? `⚠ Choisissez le remplaçant de ${esc(st.oublie)}.` : "Aucun échange."}</span>
        ${st.oublie ? `<button class="btn small" data-lu-swapcancel="${esc(b.classe)}">Annuler</button>` : ""}</div>`);
    }
    return card(`${esc(b.classe)} — niveau de sort max ${b.niveau_max}`, `
      <div class="chips"><span class="chip">Mineurs ${b.mineurs[0]} / ${b.mineurs[1]}${b.gain_mineurs ? ` (+${b.gain_mineurs})` : ""}</span>
        ${b.quota ? `<span class="chip">${esc(b.quota_label)} ${b.quota[0]} / ${b.quota[1]}${b.gain_sorts ? ` (+${b.gain_sorts})` : ""}</span>` : ""}
        ${p ? `<span class="chip">Préparés ${p.prepares} / ${p.maximum}${p.toujours ? " (sorts connus)" : ""}</span>` : ""}</div>
      ${b.liste_complete ? `<small>${esc(b.classe)} prépare ses sorts dans toute sa liste ; vous pourrez changer la préparation après chaque repos long (onglet Magie).</small>` : ""}
      <h3>Vos sorts</h3><div class="list">${mine || '<div class="empty">Aucun.</div>'}</div>
      <h3>Disponibles</h3>
      <input type="search" data-lu-q="${esc(b.classe)}" value="${esc(LU.q[b.classe] || "")}" placeholder="Rechercher…" autocomplete="off">
      <div class="chips"><button class="chip ${lv === "" ? "on" : ""}" data-lu-lv="" data-cls="${esc(b.classe)}">Tous</button>${levels.map((n) => `<button class="chip ${String(n) === lv ? "on" : ""}" data-lu-lv="${n}" data-cls="${esc(b.classe)}">${n ? "Niv. " + n : "Mineurs"}</button>`).join("")}</div>
      <div class="list">${avail.slice(0, 150).map((s) => luSpellRow(s, `<button class="pillbtn" data-lu-learn="${esc(s.nom)}" data-cls="${esc(b.classe)}" aria-label="Apprendre">＋</button>`)).join("") || '<div class="empty">Quota atteint ou aucun sort disponible.</div>'}</div>
      ${avail.length > 150 ? `<small>${avail.length - 150} de plus : affinez la recherche.</small>` : ""}`) + swap;
  }).join("");
}
function luStepRecap(v) {
  return `<div class="list">${v.recap.map(([k, a, b]) => `<div class="li"><div class="name">${esc(k)}</div><span class="muted">${esc(a)}</span><span>→</span><b>${esc(b)}</b></div>`).join("")}</div>
    ${v.manquants.length ? `<div class="banner warn"><b>Choix manquants</b><br>${v.manquants.map((m) => "○ " + esc(m.message)).join("<br>")}</div>` : '<div class="banner good">✔ Tout est prêt : confirmez pour appliquer le niveau.</div>'}
    ${v.ensuite.length ? `<small>Ensuite : ${esc(v.ensuite.map((m) => m.message).join(" ; "))}</small>` : ""}`;
}
function luAfter() {
  const body = $("#sheet-body");
  const on = (sel, ev, fn) => $$(sel, body).forEach((el) => el.addEventListener(ev, () => fn(el)));
  on("[data-lu-step]", "click", (el) => { LU.step = +el.dataset.luStep; S.sheetCtx.refresh(); body.scrollTop = 0; });
  on("[data-lu-go]", "click", (el) => { LU.step = Math.max(0, Math.min(LU_STEPS.length - 1, LU.step + +el.dataset.luGo)); S.sheetCtx.refresh(); body.scrollTop = 0; });
  on("[data-lu-cls]", "click", (el) => { LU.cls = el.dataset.luCls; LU.ops = []; luCall(); });
  on("select[data-lu]", "change", (el) => {
    const k = el.dataset.lu, v = el.value;
    if (k === "sub") return luCall({ op: "sub", name: v });
    if (k === "style") return luCall({ op: "style", slot: el.dataset.slot, name: v });
    if (k === "pact") return luCall({ op: "pact", name: v });
    if (k === "invocation") return luCall({ op: "invocation", index: +el.dataset.i, name: v });
    if (k === "swap_forget") return luCall({ op: "swap_forget", cls: el.dataset.cls, name: v });
    if (k === "asi") {
      const sl = LU.view.choix.asi.find((x) => x.id === el.dataset.slot);
      const c = { mode: "aucun", a1: "Force", a2: "Dextérité", don: "", don_carac: "", ...(sl.choix || {}) };
      c[el.dataset.k] = v;
      return luCall({ op: "asi", slot: sl.id, ...c });
    }
  });
  on("[data-lu-feat]", "click", (el) => luFeatPicker(el.dataset.luFeat));
  on("[data-lu-learn]", "click", (el) => luCall({ op: "learn", cls: el.dataset.cls, name: el.dataset.luLearn }));
  on("[data-lu-unlearn]", "click", (el) => luCall({ op: "unlearn", cls: el.dataset.cls, name: el.dataset.luUnlearn }));
  on("[data-lu-prep]", "click", (el) => luCall({ op: "prepare", cls: el.dataset.cls, name: el.dataset.luPrep, on: el.dataset.on === "1" }));
  on("[data-lu-swap]", "click", (el) => luCall({ op: "swap_choose", cls: el.dataset.cls, name: el.dataset.luSwap }));
  on("[data-lu-swapcancel]", "click", (el) => luCall({ op: "swap_cancel", cls: el.dataset.luSwapcancel }));
  on("[data-lu-lv]", "click", (el) => { LU.lvl[el.dataset.cls] = el.dataset.luLv; S.sheetCtx.refresh(); });
  on("[data-lu-info]", "click", (el) => {
    const all = LU.view.sorts.flatMap((b) => [...b.options, ...b.mes_sorts, ...(b.echange ? [...b.echange.options, ...b.echange.candidats] : [])]);
    const sp = all.find((s) => s.nom === el.dataset.luInfo); if (!sp) return;
    toast(`${sp.nom} : ${sp.description}`);
  });
  on("[data-lu-q]", "input", (el) => {
    LU.q[el.dataset.luQ] = el.value; const pos = el.selectionStart, key = el.dataset.luQ;
    S.sheetCtx.refresh();
    const n = $(`[data-lu-q="${CSS.escape(key)}"]`); if (n) { n.focus(); n.setSelectionRange(pos, pos); }
  });
  on("[data-lu-confirm]", "click", async () => {
    try {
      const portrait = S.char.portrait || "";
      const res = await api("/api/levelup", { character: luChar(), classe: LU.cls, ops: LU.ops, confirm: true });
      res.character.portrait = portrait;
      S.char = res.character; S.sheet = res.sheet; persist();
      closeSheet(); render();
      (res.messages || []).forEach((m) => toast(m));
      showDice({ title: "Niveau supérieur !", total: S.sheet.resume.niveau, detail: S.sheet.resume.classes_txt });
    } catch (e) { toast(e.message, true); }
  });
}
function luFeatPicker(slot) {
  const back = () => openSheet("▲ Niveau supérieur", luBody, { lu: true, after: luAfter });
  openPicker("Choisir un don", S.cat.dons.filter((d) => edOk(d.edition)).map((d) => ({ value: d.nom, label: d.nom, sub: [d.prerequis && d.prerequis !== "Aucun" ? "Prérequis : " + d.prerequis : "", d.asi].filter(Boolean).join(" · ") })), async (nom) => {
    const sl = LU.view.choix.asi.find((x) => x.id === slot);
    const c = { a1: "Force", a2: "Dextérité", ...(sl.choix || {}) };
    const feat = S.cat.dons.find((d) => d.nom === nom);
    back(); $("#sheet").classList.add("full");
    await luCall({ op: "asi", slot, mode: "don", a1: c.a1, a2: c.a2, don: nom, don_carac: (feat.carac_choix || [])[0] || "" });
  });
}

/* ============================================================== actions (clics) */
const ACT = {
  levelup: () => openLevelUp(),
  "ally-add": () => {
    const types = [...new Set(S.cat.entites.map((e) => e.type))];
    openPicker("Ajouter une créature", S.cat.entites.map((e) => ({ value: e.id, label: e.nom, sub: [e.type_label, e.creature, e.fp !== "" ? "FP " + e.fp : "", e.sources].filter(Boolean).join(" · "), filter: e.type })),
      (id) => act({ op: "menagerie_add", id }), { filters: types.map((t) => [t, (S.cat.entites.find((e) => e.type === t) || {}).type_label || t]) });
  },
  "ally-add-id": (el) => act({ op: "menagerie_add", id: el.dataset.id }),
  "ally-del": (el) => confirm("Retirer cette créature ?") && act({ op: "menagerie_remove", uid: el.dataset.uid }),
  "ally-check": (el) => { const m = S.sheet.menagerie.find((x) => x.uid === el.dataset.uid); rollD20(`${m.nom} — ${el.dataset.ab}`, m.mods[el.dataset.ab]); },
  "ally-atk": (el) => { const m = S.sheet.menagerie.find((x) => x.uid === el.dataset.uid); const a = m.actions[+el.dataset.i]; rollD20(`${m.nom} — ${a.nom}`, a.attaque); },
  "ally-dmg": (el) => { const m = S.sheet.menagerie.find((x) => x.uid === el.dataset.uid); const a = m.actions[+el.dataset.i]; rollFormula(`${m.nom} — ${a.nom}`, a.degats, a.type_degats); },
  "turn-toggle": (el) => act({ op: "turn_toggle", kind: el.dataset.k }),
  "turn-new": () => act({ op: "turn_new" }),
  "turn-move": (el) => act({ op: "turn_move", meters: Math.max(0, S.sheet.tour.deplacement + +el.dataset.d) }),
  tile: (el) => {
    const a = S.sheet.tour.actions.find((x) => x.id === el.dataset.id); if (!a) return;
    if (a.groupe === "attaques" || a.groupe === "reactions" || a.sort || !a.disponible) { useTile(a); return; }
    infoSheet(`${a.icone || ""} ${a.nom}`, `<small>${esc(a.type)}${a.origine ? " · " + esc(a.origine) : ""}${a.cout ? " · " + esc(a.cout) : ""}</small>\n\n${esc(a.description || "")}`,
      '<button class="btn primary block" id="tile-go">Utiliser</button>');
    $("#tile-go").addEventListener("click", () => { closeSheet(); useTile(a); });
  },
  "form-end": () => act({ op: "form_end" }),
  "form-pick": () => beastPicker("Forme sauvage — quelle bête ?", S.sheet.formes.druide.betes, (n) => act({ op: "form_assume", name: n })),
  "gm-spell-add": () => openPicker("Sort accordé par le MJ", S.cat.sorts.filter((x) => edOk(x.edition)).map((x) => ({ value: x.nom, label: x.nom, sub: (x.niveau ? "Niveau " + x.niveau : "Mineur") + " · " + x.ecole })), (nom) => {
    openSheet("Sort du MJ — " + nom, () => `<label class="field">Utilisation<select id="gm-usage">${options(S.cat.usages_mj, S.cat.usages_mj[0])}</select></label>
      <label class="field">Note (facultatif)<input type="text" id="gm-note" maxlength="300"></label><button class="btn primary" id="gm-ok">Accorder</button>`, {
      after: () => $("#gm-ok").addEventListener("click", () => { const u = $("#gm-usage").value, n = $("#gm-note").value; closeSheet(); act({ op: "gm_spell_add", nom, usage: u, note: n }); }),
    });
  }, { free: true }),
  "gm-spell-del": (el) => act({ op: "gm_spell_remove", nom: el.dataset.n }),
  "custom-magic": () => openSheet("Objet magique sur mesure", () => `
    <label class="field">Nom<input type="text" id="cm-nom" maxlength="100"></label>
    <div class="grid2"><label class="field">Type<select id="cm-type">${options(["Objet merveilleux", "Anneau", "Arme", "Armure", "Baguette", "Bâton", "Potion", "Parchemin", "Sceptre"], "Objet merveilleux")}</select></label>
    <label class="field">Rareté<select id="cm-rar">${options(["commun", "peu commun", "rare", "très rare", "légendaire", "artefact"], "peu commun")}</select></label></div>
    ${sw("Harmonisation requise", false, 'id="cm-lien"')}
    <div class="grid2"><label class="field">Bonus de CA<input type="number" inputmode="numeric" id="cm-ca" value="0" min="0" max="10"></label>
    <label class="field">Poids (kg)<input type="number" inputmode="decimal" id="cm-poids" value="0" min="0" step="0.1"></label></div>
    <label class="field">Description<textarea id="cm-desc" rows="5"></textarea></label>
    <button class="btn primary" id="cm-ok">Créer l'objet</button>`, {
    after: () => $("#cm-ok").addEventListener("click", () => {
      const v = { op: "custom_magic", nom: $("#cm-nom").value.trim(), type: $("#cm-type").value, rarete: $("#cm-rar").value, lien: $("#cm-lien").checked, ca: +$("#cm-ca").value || 0, poids: parseFloat(String($("#cm-poids").value).replace(",", ".")) || 0, description: $("#cm-desc").value };
      if (!v.nom) { toast("Donnez un nom à l'objet.", true); return; }
      closeSheet(); act(v);
    }),
  }),
  manif: (el) => {
    const x = S.sheet.options.manifestations.choisies.find((m) => m.nom === el.dataset.n);
    infoSheet(x.nom, `${x.pacte ? `<small>Requiert : ${esc(x.pacte)}</small>\n` : ""}${x.niveau ? `<small>Occultiste niveau ${x.niveau}</small>\n` : ""}\n${esc(x.description)}${x.sorts ? `\n\n<b>Sort accordé :</b> ${esc(x.sorts)}` : ""}${x.etat !== "ok" ? `\n\n⚠ ${esc(x.raison)}` : ""}`,
      '<button class="btn danger block" id="mf-del">Retirer cette manifestation</button>');
    $("#mf-del").addEventListener("click", () => { closeSheet(); act({ op: "manifestation_remove", name: x.nom }); });
  },
  "manif-add": () => {
    const mf = S.sheet.options.manifestations;
    openPicker("Manifestation occulte", mf.options.map((x) => ({ value: x.nom, label: x.nom, badge: x.etat === "ok" ? "" : "🔒", sub: (x.etat === "ok" ? "" : x.raison + " — ") + (x.sorts ? "Sort : " + x.sorts : x.description.slice(0, 110)), filter: x.etat === "ok" ? "ok" : "ko" })),
      (nom) => act({ op: "manifestation_add", name: nom }), { filters: [["ok", "Disponibles"], ["ko", "Prérequis manquants"]] });
  },
  "ritual-add": () => openPicker("Inscrire un rituel", S.sheet.options.rituels.options.map((x) => ({ value: x.nom, label: x.nom, sub: "Niveau " + x.niveau })), (nom) => act({ op: "ritual_add", name: nom })),
  "ritual-del": (el) => act({ op: "ritual_remove", name: el.dataset.n }),
  portrait: () => $("#file-portrait").click(),
  "portrait-del": () => { S.char.portrait = ""; persist(); render(); },
  "bg-gear": () => act({ op: "background_gear" }),
  lvl: (el) => {
    const c = S.sheet.classes[+el.dataset.idx];
    act({ op: "class_level", idx: c.index, level: c.niveau + +el.dataset.d });
  },
  "class-remove": (el) => confirm("Retirer cette classe ?") && act({ op: "class_remove", idx: +el.dataset.idx }),
  info: (el) => {
    const s = S.sheet;
    if (el.dataset.src === "trait") { const t = s.race_traits[+el.dataset.i]; infoSheet(t.nom, esc(t.description)); }
    if (el.dataset.src === "feat") {
      const c = s.classes[+el.dataset.c]; const f = c.aptitudes.find((x) => x.nom === el.dataset.n);
      infoSheet(f.nom, `<small>${esc(f.source)} — niveau ${f.niveau}${f.debloque ? "" : " (à venir)"}</small>\n\n${esc(f.description)}`);
    }
    if (el.dataset.src === "don") { const d = S.cat.dons.find((x) => x.nom === el.dataset.n) || {}; infoSheet(el.dataset.n, `<small>Prérequis : ${esc(d.prerequis || "aucun")}${d.asi ? " · " + esc(d.asi) : ""}</small>\n\n${esc(d.description)}`); }
    if (el.dataset.src === "ca") { const c = s.combat; infoSheet("Classe d'armure", `<b>CA ${c.ca}</b>\n${esc(c.ca_formule)}\n${esc(c.ca_calcul)}${c.ca_note ? "\n\n" + esc(c.ca_note) : ""}`); }
  },
  method: (el) => act({ op: "set", field: "methode", value: el.dataset.v }),
  "reset-scores": () => act({ op: "reset_scores" }),
  "roll-scores": () => act({ op: "roll_scores" }),
  "auto-assign": () => act({ op: "auto_assign" }),
  buy: (el) => act({ op: "buy", ability: el.dataset.ab, delta: +el.dataset.d }),
  check: (el) => { const a = S.sheet.abilities.find((x) => x.nom === el.dataset.ab); rollD20(`Test de ${a.nom}`, a.mod); },
  save: (el) => act({ op: "toggle_save", ability: el.dataset.ab }),
  "roll-save": (el) => { const r = S.sheet.saves.find((x) => x.carac === el.dataset.ab); rollD20(`Sauvegarde de ${r.carac}`, r.bonus, r); },
  skill: (el) => act({ op: "toggle_skill", name: el.dataset.n, kind: el.dataset.k || "maitrise" }),
  "roll-skill": (el) => { const r = S.sheet.skills.find((x) => x.nom === el.dataset.n); rollD20(r.nom, r.bonus, r); },
  "pick-feat": (el) => {
    const slot = el.dataset.slot;
    openPicker(slot ? "Choisir un don" : "Don accordé par le MJ", S.cat.dons.filter((d) => edOk(d.edition)).map((d) => ({ value: d.nom, label: d.nom, sub: [d.prerequis && d.prerequis !== "Aucun" ? "Prérequis : " + d.prerequis : "", d.asi].filter(Boolean).join(" · ") })), (nom) => {
      if (!slot) return act({ op: "gm_feat_add", name: nom });
      const c = (S.sheet.asi.find((x) => x.id === slot) || {}).choix || {};
      const feat = S.cat.dons.find((d) => d.nom === nom);
      act({ op: "asi", slot, mode: "don", a1: c.a1 || "Force", a2: c.a2 || "Dextérité", don: nom, don_carac: (feat.carac_choix || [])[0] || "" });
    });
  },
  "gm-feat-del": (el) => act({ op: "gm_feat_remove", name: el.dataset.n }),
  "pick-langs": () => openSheet("Langues", () => {
    const groups = {};
    S.cat.langues.forEach((l) => (groups[l.categorie || "Autres"] ||= []).push(l.nom));
    const L = S.sheet.langues;
    return `<div class="banner">Langues choisies : <b>${L.connues} / ${L.permises}</b></div>` + Object.entries(groups).map(([g, ls]) => `<h3>${esc(g)}</h3><div class="chips">${ls.map((n) => `<button class="chip ${S.char.langues_liste.includes(n) ? "on" : ""}" data-lang="${esc(n)}">${esc(n)}</button>`).join("")}</div>`).join("");
  }, { after: () => $$("[data-lang]", $("#sheet-body")).forEach((b) => b.addEventListener("click", () => act({ op: "toggle_language", name: b.dataset.lang }))) }),
  "roll-init": () => rollD20("Initiative", S.sheet.combat.initiative),
  hp: (el) => {
    const v = parseInt($("#hp-amt").value, 10);
    if (!(v > 0)) { toast("Saisissez un montant.", true); $("#hp-amt").focus(); return; }
    act({ op: el.dataset.k === "damage" ? "damage" : "heal", amount: v });
  },
  death: (el) => {
    const c = S.sheet.combat; const i = +el.dataset.i;
    const cur = el.dataset.k === "ok" ? c.mort[0] : c.mort[1];
    act({ op: "set", field: el.dataset.k === "ok" ? "mort_reussites" : "mort_echecs", value: i < cur ? i : i + 1 });
  },
  "roll-death": () => {
    const d = rnd(20); const c = S.sheet.combat;
    if (d === 20) { act({ op: "heal", amount: 1 }); showDice({ title: "Jet contre la mort", total: d, detail: "20 naturel : vous reprenez 1 PV !", crit: true }); return; }
    const ok = d >= 10; const n = d === 1 ? 2 : 1;
    act({ op: "set", field: ok ? "mort_reussites" : "mort_echecs", value: Math.min(3, (ok ? c.mort[0] : c.mort[1]) + n) });
    showDice({ title: "Jet contre la mort", total: d, detail: ok ? "Réussite" : d === 1 ? "1 naturel : deux échecs" : "Échec", fail: !ok });
  },
  "break-conc": () => act({ op: "break_concentration" }),
  effect: (el) => {
    const e = S.sheet.combat.effets.find((x) => x.key === el.dataset.key);
    infoSheet(`${e.icone} ${e.nom}`, esc(e.description || e.categorie), `<button class="btn danger block" id="fx-del">Retirer cet effet</button>`);
    $("#fx-del").addEventListener("click", () => { closeSheet(); act({ op: "effect_remove", key: e.key }); });
  },
  "pick-effect": () => openPicker("Ajouter un état / effet", S.cat.effets.map((e) => ({ value: e.key, label: `${e.icone} ${e.nom}`, sub: e.categorie, filter: e.categorie })), (k) => act({ op: "effect_add", key: k }), { filters: [["État", "États"], ["Bonus", "Bonus"], ["Malus", "Malus"]] }),
  res: (el) => act({ op: "resource", key: el.dataset.key, used: orbClick(+el.dataset.total, +el.dataset.used, +el.dataset.i) }),
  "hit-die": (el) => act({ op: "hit_die", die: el.dataset.die }),
  rest: (el) => {
    const long = el.dataset.k === "long";
    if (confirm(long ? "Repos long : PV, emplacements et ressources récupérés. Continuer ?" : "Repos court : emplacements de Pacte et ressources « repos court » récupérés. (Dépensez vos dés de vie juste au-dessus.) Continuer ?"))
      act({ op: long ? "long_rest" : "short_rest" });
  },
  "weapon-add": (el) => {
    const key = el.dataset.key;
    const slot = S.sheet.combat.armes.find((w) => w.key === key && !w.nom);
    if (!slot) { toast("Les 4 emplacements sont occupés.", true); return; }
    weaponPicker(key, slot.index);
  },
  "weapon-edit": (el) => {
    const w = S.sheet.combat.armes.find((x) => x.key === el.dataset.key && x.index === +el.dataset.i);
    const st = w.stats || {};
    openSheet(w.nom, () => `<div class="feature-desc">${esc(st.calcul || "")}\n${esc((st.proprietes || []).join(", "))}</div>
      <label class="field">Bonus magique<select id="w-bonus">${options([0, 1, 2, 3].map((n) => ({ value: n, label: n ? "+" + n : "Aucun" })), w.bonus)}</select></label>
      <div class="grid2"><button class="btn" id="w-change">Changer d'arme</button><button class="btn danger" id="w-del">Retirer</button></div>`, {
      after: () => {
        $("#w-bonus").addEventListener("change", (e) => act({ op: "weapon", key: w.key, i: w.index, nom: w.nom, bonus: +e.target.value }));
        $("#w-change").addEventListener("click", () => weaponPicker(w.key, w.index, w.bonus));
        $("#w-del").addEventListener("click", () => { closeSheet(); act({ op: "weapon", key: w.key, i: w.index, nom: "", bonus: 0 }); });
      },
    });
  },
  "roll-atk": (el) => { const w = S.sheet.combat.armes.find((x) => x.key === el.dataset.key && x.index === +el.dataset.i); rollD20(`Attaque — ${w.nom}`, w.stats.attaque); },
  "roll-dmg": (el) => { const w = S.sheet.combat.armes.find((x) => x.key === el.dataset.key && x.index === +el.dataset.i); rollFormula(`Dégâts — ${w.nom}`, w.stats.degats, w.stats.type_degats); },
  slot: (el) => act({ op: "slot_used", level: +el.dataset.l, used: orbClick(+el.dataset.total, +el.dataset.used, +el.dataset.i) }),
  pact: (el) => act({ op: "pact_used", used: orbClick(+el.dataset.total, +el.dataset.used, +el.dataset.i) }),
  prep: (el) => act({ op: "spell_prepare", cls: el.dataset.cls, nom: el.dataset.n }),
  spell: (el) => spellSheet(el.dataset.n, el.dataset.cls),
  "roll-spell": (el) => {
    const c = S.sheet.magie.lanceurs.find((x) => x.classe === el.dataset.cls);
    const sp = c.sorts.find((x) => x.nom === el.dataset.n);
    rollFormula(sp.nom, sp.calcul.degats || sp.calcul.soins, sp.calcul.type_degats || "");
  },
  "roll-spellatk": (el) => rollD20(`Attaque de sort (${el.dataset.cls})`, +el.dataset.b),
  library: (el) => librarySheet(el.dataset.cls),
  qty: (el) => act({ op: "item_qty", idx: +el.dataset.i, qte: +el.dataset.q }),
  item: (el) => {
    const o = S.sheet.inventaire.objets[+el.dataset.i];
    infoSheet(o.nom, `<small>${esc(o.categorie)}${o.poids ? " · " + String(o.poids).replace(".", ",") + " kg l'unité" : ""}</small>\n\n${esc(o.description || "")}`, `<button class="btn danger block" id="it-del">Retirer de l'inventaire</button>`);
    $("#it-del").addEventListener("click", () => { closeSheet(); act({ op: "item_remove", idx: o.index }); });
  },
  "item-add": () => openPicker("Ajouter un objet", S.cat.objets.map((o) => ({ value: o.nom, label: o.nom, sub: [o.categorie, o.prix, o.poids].filter(Boolean).join(" · "), filter: o.categorie })),
    (nom) => act({ op: "item_add", nom, qte: 1 }), { free: true, placeholder: "Rechercher ou saisir un objet…" }),
  "pack-add": () => openPicker("Ajouter un paquetage", S.cat.paquetages.map((n) => ({ value: n, label: n })), (nom) => act({ op: "pack_add", nom })),
  magic: (el) => {
    const o = S.sheet.inventaire.magiques[+el.dataset.i];
    infoSheet(o.nom, `<small>${esc(o.type)} · ${esc(o.rarete)}${o.lien ? " · harmonisation requise" : ""}${o.condition ? " (" + esc(o.condition) + ")" : ""}</small>\n\n${esc(o.description)}`, `<button class="btn danger block" id="mi-del">Retirer</button>`);
    $("#mi-del").addEventListener("click", () => { closeSheet(); act({ op: "magic_remove", idx: o.index }); });
  },
  "magic-add": () => {
    const rar = [...new Set(S.cat.objets_magiques.map((m) => m.rarete))].filter(Boolean);
    openPicker("Ajouter un objet magique", S.cat.objets_magiques.map((m) => ({ value: m.nom, label: m.nom, badge: m.rarete, sub: m.type + (m.lien ? " · harmonisation" : ""), filter: m.rarete })),
      (nom) => act({ op: "magic_add", nom }), { filters: rar.map((r) => [r, r]) });
  },
};
function weaponPicker(key, i, bonus = 0) {
  const dist = key === "armes_distance";
  const cat = { courante: "Arme courante", guerre: "Arme de guerre" };
  const items = S.cat.armes.filter((w) => (dist ? w.type === "distance" || w.lancer : w.type !== "distance"))
    .map((w) => ({ value: w.nom, label: w.nom, sub: [cat[w.categorie] || w.categorie, w.degats, w.lancer ? "lancer" : ""].filter(Boolean).join(" · "), filter: w.categorie }));
  openPicker(dist ? "Arme à distance" : "Arme de corps à corps", items,
    (nom) => act({ op: "weapon", key, i, nom, bonus }), { filters: [["courante", "Courantes"], ["guerre", "De guerre"]] });
}

/* ============================================================== modifications de champs (change) */
const CHANGE = {
  race: (v) => act({ op: "race", name: v }),
  subrace: (v) => act({ op: "subrace", name: v }),
  background: (v) => act({ op: "background", name: v }),
  class_change: (v, el) => act({ op: "class_change", idx: +el.dataset.idx, name: v }),
  class_sub: (v, el) => act({ op: "class_sub", idx: +el.dataset.idx, name: v }),
  class_add: (v) => v && act({ op: "class_add", name: v }),
  multiclass: (v, el) => act({ op: "multiclass", enabled: el.checked }),
  assign_roll: (v, el) => act({ op: "assign_roll", ability: el.dataset.ab, index: +v }),
  free_pick: (v, el) => act({ op: "free_pick", k: +el.dataset.k, ability: v }),
  free_rule: (v, el) => act({ op: "free_rule", enabled: el.checked }),
  alt_rule: (v, el) => act({ op: "alt_rule", enabled: el.checked }),
  asi: (v, el) => {
    const sl = S.sheet.asi.find((x) => x.id === el.dataset.slot);
    const c = { mode: "aucun", a1: "Force", a2: "Dextérité", don: "", don_carac: "", ...(sl.choix || {}) };
    c[el.dataset.k] = v;
    act({ op: "asi", slot: sl.id, mode: c.mode, a1: c.a1, a2: c.a2, don: c.don, don_carac: c.don_carac });
  },
  armor: (v, el) => {
    const a = S.sheet.combat.armure;
    const cur = { nom: a.nom, bonus: a.bonus || 0, bouclier: a.bouclier ? (a.bouclier_nom || S.cat.boucliers[0]) : "" };
    cur[el.dataset.k] = el.dataset.k === "bonus" ? +v : v;
    act({ op: "armor", ...cur });
  },
  style: (v, el) => act({ op: "style", slot: el.dataset.slot, name: v }),
  ally: (v, el) => act({ op: "menagerie_set", uid: el.dataset.uid, field: el.dataset.k, value: ["pv", "pv_temp", "niveau_sort"].includes(el.dataset.k) ? parseInt(v || "0", 10) : v }),
  ancestry: (v, el) => act({ op: "ancestry", kind: el.dataset.k, color: v }),
  class_option: (v, el) => act({ op: "class_option", key: el.dataset.key, index: +el.dataset.i, name: v }),
  maneuver: (v) => act({ op: "maneuver", name: v }),
  pact: (v) => act({ op: "pact", name: v }),
  magic_equip: (v, el) => act({ op: "magic_equip", idx: +el.dataset.i, value: el.checked }),
  magic_attune: (v, el) => act({ op: "magic_attune", idx: +el.dataset.i, value: el.checked }),
};

const LOCAL_TEXT = new Set(["nom", "joueur", "histoire", "traits", "notes", "langues", "inventaire"]);
function onViewChange(e) {
  const el = e.target;
  if (el.dataset.change) { CHANGE[el.dataset.change](el.value, el); return; }
  if (el.dataset.field && LOCAL_TEXT.has(el.dataset.field)) {   // texte libre : aucune règle, pas d'aller-retour serveur
    S.char[el.dataset.field] = el.value.slice(0, 20000);
    if (el.dataset.field === "nom") S.sheet.resume.nom = el.value || "Sans nom";
    persist(); renderTop();
    return;
  }
  if (el.dataset.field) {
    const v = el.type === "checkbox" ? el.checked : el.type === "number" ? parseInt(el.value || "0", 10) : el.value;
    act({ op: "set", field: el.dataset.field, value: v });
    return;
  }
  if (el.dataset.setin) act({ op: "setin", field: el.dataset.setin, key: el.dataset.key, value: parseInt(el.value || "0", 10) });
}

/* ============================================================== tiroir : personnages, import / export */
function renderDrawer() {
  const list = Object.entries(S.store.chars).sort((a, b) => b[1].updated - a[1].updated);
  $("#drawer").innerHTML = `
    <div class="row"><h2 class="grow">Mes personnages</h2><button class="icon-btn" data-d="close" aria-label="Fermer">✕</button></div>
    <div class="list">${list.map(([id, c]) => `<div class="li ${id === S.store.current ? "" : "tap"}" ${id === S.store.current ? "" : `data-d="open" data-id="${id}"`}>
      <span class="avatar" style="width:34px;height:34px;background-image:url('${c.character.portrait ? portraitURL(c.character.portrait) : raceImg(c.character)}')"></span>
      <div class="name">${id === S.store.current ? "▶ " : ""}${esc(c.character.nom || "Sans nom")}<small>${esc(c.label || "")}</small></div>
      <button class="icon-btn" style="font-size:1rem" data-d="del" data-id="${id}" aria-label="Supprimer">🗑</button></div>`).join("")}</div>
    <button class="btn primary" data-d="new">＋ Nouveau personnage</button>
    <button class="btn" data-d="rules">⚖ Règles de la table (édition ${esc(sheetMode())})</button>
    <h3>Import / export</h3>
    <button class="btn" data-d="import">📥 Importer (.json)</button>
    <div class="grid2"><button class="btn" data-d="export-json">📤 JSON</button><button class="btn" data-d="export-txt">📄 Texte</button></div>
    <div class="grid2"><button class="btn" data-d="share">🔗 Partager</button><button class="btn" data-d="print">🖨 PDF</button></div>
    <button class="btn ghost" data-d="export-all">💾 Sauvegarde de tous les personnages</button>
    <small>Le JSON est le format de l'application bureau : il s'ouvre des deux côtés. Vos personnages sont gardés dans ce navigateur ; exportez-les pour les retrouver sur un autre appareil.</small>
    <h3>Thème</h3>
    <select data-d="theme">${Object.entries(S.cat.themes).map(([k, t]) => opt(k, S.prefs.theme, t.name)).join("")}</select>
    <h3>Lancer de dés</h3>
    <div class="row"><input type="text" id="free-roll" placeholder="1d20+5, 2d6+3…" autocomplete="off" inputmode="text"><button class="btn" data-d="roll">🎲</button></div>
    <div class="chips">${["d4", "d6", "d8", "d10", "d12", "d20", "d100"].map((d) => `<button class="chip" data-d="quick" data-v="1${d}">${d}</button>`).join("")}</div>
    <small class="muted">Moteur de règles : application bureau v47 (core/). ${S.cat.classes.length} classes · ${S.cat.races.length} espèces · ${S.cat.sorts.length} sorts.</small>`;
}
function openDrawer() { renderDrawer(); $("#drawer").classList.add("open"); $("#drawer").setAttribute("aria-hidden", "false"); $("#scrim").hidden = false; }
function closeDrawer() { $("#drawer").classList.remove("open"); $("#drawer").setAttribute("aria-hidden", "true"); if ($("#sheet").hidden) $("#scrim").hidden = true; }

function fileName(ext) { return (S.char.nom || "personnage").trim().replace(/[^\p{L}\p{N}_-]+/gu, "_") + ext; }
function download(name, content, type) {
  const blob = content instanceof Blob ? content : new Blob([content], { type });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob); a.download = name;
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 2000);
}
const charJSON = () => JSON.stringify(S.char, null, 2);

async function importFile(file) {
  if (!file) return;
  if (file.size > 4 * 1024 * 1024) { toast("Fichier trop volumineux (4 Mo maximum).", true); return; }
  let data;
  try { data = JSON.parse(await file.text()); }
  catch (e) { toast("Format non reconnu : importez un fichier .json (sauvegarde de l'application bureau ou export web). L'export texte sert à la lecture et ne peut pas être réimporté.", true); return; }
  let chars = [];
  if (Array.isArray(data)) chars = data;
  else if (data && data.format === "dnd5e-fiche-collection") chars = data.personnages || [];
  else if (data && data.format === "dnd5e-fiche" && data.personnage) chars = [data.personnage];
  else chars = [data];
  let ok = 0;
  for (const c of chars) {
    const prev = S.store.current, prevChar = S.char, prevSheet = S.sheet;
    try {
      S.store.current = uid();
      await doAct([], { character: c, silent: true });
      ok++;
    } catch (e) {
      S.store.current = prev; S.char = prevChar; S.sheet = prevSheet;
      toast(`Import refusé : ${e.message}`, true);
    }
  }
  writeJSON(STORE_KEY, S.store);
  if (ok) { toast(`${ok} personnage(s) importé(s).`); closeDrawer(); render(); }
}

async function onDrawer(e) {
  const el = e.target.closest("[data-d]"); if (!el) return;
  const d = el.dataset.d;
  if (d === "close") closeDrawer();
  if (d === "open") { switchTo(el.dataset.id); closeDrawer(); }
  if (d === "del") {
    e.stopPropagation();
    const c = S.store.chars[el.dataset.id];
    if (!confirm(`Supprimer « ${c.character.nom || "Sans nom"} » de ce navigateur ? (Pensez à l'exporter avant.)`)) return;
    delete S.store.chars[el.dataset.id];
    if (S.store.current === el.dataset.id) {
      const next = Object.keys(S.store.chars)[0];
      if (next) switchTo(next); else await newCharacter();
    }
    writeJSON(STORE_KEY, S.store); renderDrawer();
  }
  if (d === "new") { closeDrawer(); await newCharacter(); }
  if (d === "rules") { closeDrawer(); openTableRules(); }
  if (d === "import") $("#file-import").click();
  if (d === "export-json") download(fileName(".json"), charJSON(), "application/json");
  if (d === "export-all") download("personnages_dnd5e.json", JSON.stringify({ format: "dnd5e-fiche-collection", version: 1, personnages: Object.values(S.store.chars).map((c) => c.character) }, null, 2), "application/json");
  if (d === "export-txt") {
    try { const ch = { ...S.char }; delete ch.portrait; download(fileName(".txt"), await api("/api/export/text", { character: ch }), "text/plain;charset=utf-8"); }
    catch (err) { toast(err.message, true); }
  }
  if (d === "share") {
    const file = new File([charJSON()], fileName(".json"), { type: "application/json" });
    if (navigator.canShare && navigator.canShare({ files: [file] })) {
      try { await navigator.share({ files: [file], title: S.char.nom || "Personnage D&D" }); } catch (err) { /* annulé */ }
    } else { download(file.name, file, "application/json"); toast("Partage non disponible : fichier téléchargé."); }
  }
  if (d === "print") {
    try {
      const ch = { ...S.char }; delete ch.portrait;
      const txt = await api("/api/export/text", { character: ch });
      let el2 = $(".print-sheet"); if (!el2) { el2 = document.createElement("div"); el2.className = "print-sheet"; document.body.appendChild(el2); }
      el2.innerHTML = esc(txt).replace(/^### (.*)$/gm, "<h3>$1</h3>").replace(/^## (.*)$/gm, "<h2>$1</h2>").replace(/^# (.*)$/gm, "<h1>$1</h1>");
      closeDrawer(); setTimeout(() => window.print(), 100);
    } catch (err) { toast(err.message, true); }
  }
  if (d === "roll") { const v = $("#free-roll").value.trim(); if (v) freeRoll(v); }
  if (d === "quick") freeRoll(el.dataset.v);
}
function freeRoll(expr) {
  if (/^1d20$/i.test(expr)) { rollD20("d20", 0); return; }
  rollFormula(expr, expr);
}

function switchTo(id) {
  const c = S.store.chars[id]; if (!c) return;
  S.store.current = id; writeJSON(STORE_KEY, S.store);
  act([], { character: c.character, silent: true });
}
function newCharacter() {
  return new Promise((resolve) => {
    openPicker("Nouveau personnage : édition des règles", [
      { value: "2014", label: "Édition 2014", sub: "Manuel des joueurs 2014 et suppléments (Xanathar, Tasha…)" },
      { value: "2024", label: "Édition 2024", sub: "Manuel des joueurs 2024 : classes, espèces, historiques, dons et sorts 2024" },
    ], async (mode) => {
      S.store.current = uid();
      await doAct([{ op: "set_edition", mode }], { character: null, silent: true });
      S.prefs.tab = "perso"; savePrefs(); render();
      toast(`Nouveau personnage créé (édition ${mode}).`);
      resolve();
    }, { placeholder: "2014 ou 2024" });
  });
}

/* v52 : règles de la table (et bottes d'arme), comme la fenêtre du bureau */
function openTableRules() {
  const e = (S.sheet && S.sheet.edition) || { regles: [], bottes: {} };
  const items = e.regles.map((r) => ({ value: "rule:" + r.cle, label: (r.actif ? "✔ " : "○ ") + r.nom, sub: r.description }));
  items.unshift({ value: "edition", label: `Édition de la fiche : ${e.mode}`, sub: "Changer d'édition remplace les classes par leur version de l'autre édition (niveaux conservés)." });
  const b = e.bottes || {};
  if (b.nombre) items.push({ value: "bottes", label: `Bottes d'arme : ${(b.choisies || []).length} / ${b.nombre}`, sub: (b.choisies || []).join(", ") || "armes équipées par défaut" });
  openPicker("Règles de la table", items, (v) => {
    if (v === "edition") {
      const other = e.mode === "2024" ? "2014" : "2024";
      if (confirm(`Passer la fiche en édition ${other} ?`)) act([{ op: "set_edition", mode: other }]);
    } else if (v === "bottes") {
      openPicker(`Bottes d'arme (${b.nombre} au maximum)`, (b.candidates || []).map((n) => ({ value: n, label: ((b.choisies || []).includes(n) ? "✔ " : "○ ") + n })), (n) => {
        const cur = [...(b.choisies || [])];
        const next = cur.includes(n) ? cur.filter((x) => x !== n) : [...cur, n];
        act([{ op: "set_masteries", weapons: next }]);
      });
    } else {
      const r = e.regles.find((x) => "rule:" + x.cle === v);
      if (r) act([{ op: "set_house_rule", key: r.cle, active: !r.actif }]);
    }
  }, { placeholder: "Filtrer les règles" });
}

/* ============================================================== portrait (redimensionné à 512 px, JPEG) */
async function setPortrait(file) {
  if (!file) return;
  try {
    const bmp = await createImageBitmap(file);
    const k = Math.min(1, 512 / Math.max(bmp.width, bmp.height));
    const cv = document.createElement("canvas");
    cv.width = Math.round(bmp.width * k); cv.height = Math.round(bmp.height * k);
    cv.getContext("2d").drawImage(bmp, 0, 0, cv.width, cv.height);
    S.char.portrait = cv.toDataURL("image/jpeg", 0.85).split(",")[1];
    persist(); render(); toast("Portrait enregistré dans la fiche.");
  } catch (e) { toast("Image illisible.", true); }
}

/* ============================================================== démarrage */
async function boot() {
  S.prefs = { ...S.prefs, ...readJSON(PREF_KEY, {}) };
  S.store = readJSON(STORE_KEY, null) || { current: null, chars: {} };
  try { S.cat = await api("/api/catalog"); }
  catch (e) { $("#view").innerHTML = card("Connexion", `<div class="banner warn">${esc(e.message)}</div><button class="btn" onclick="location.reload()">Réessayer</button>`); return; }
  applyTheme(S.prefs.theme in S.cat.themes ? S.prefs.theme : "bg3");

  $("#tabbar").addEventListener("click", (e) => {
    const b = e.target.closest("button[data-tab]"); if (!b) return;
    S.prefs.tab = b.dataset.tab; savePrefs(); render(); window.scrollTo({ top: 0 });
  });
  $("#view").addEventListener("click", (e) => {
    const el = e.target.closest("[data-act]"); if (!el || el.disabled) return;
    const fn = ACT[el.dataset.act]; if (fn) { e.preventDefault(); fn(el, e); }
  });
  $("#view").addEventListener("change", onViewChange);
  let typing;
  $("#view").addEventListener("input", (e) => {          // sauvegarde pendant la frappe (fermeture brutale de l'appli)
    const el = e.target;
    if (!el.dataset.field || !LOCAL_TEXT.has(el.dataset.field)) return;
    clearTimeout(typing);
    typing = setTimeout(() => { S.char[el.dataset.field] = el.value.slice(0, 20000); persist(); }, 500);
  });
  $("#btn-menu").addEventListener("click", openDrawer);
  $("#btn-hero").addEventListener("click", () => { S.prefs.tab = "perso"; savePrefs(); render(); window.scrollTo({ top: 0, behavior: "smooth" }); });
  $("#hero-hp").addEventListener("click", () => { S.prefs.tab = "combat"; savePrefs(); render(); window.scrollTo({ top: 0, behavior: "smooth" }); });
  $("#drawer").addEventListener("click", onDrawer);
  $("#drawer").addEventListener("change", (e) => { if (e.target.dataset.d === "theme") applyTheme(e.target.value); });
  $("#drawer").addEventListener("keydown", (e) => { if (e.key === "Enter" && e.target.id === "free-roll") freeRoll(e.target.value.trim()); });
  $("#scrim").addEventListener("click", () => { closeSheet(); closeDrawer(); });
  $("#sheet-close").addEventListener("click", closeSheet);
  $("#dice").addEventListener("click", () => { $("#dice").hidden = true; });
  $("#file-import").addEventListener("change", (e) => { importFile(e.target.files[0]); e.target.value = ""; });
  $("#file-portrait").addEventListener("change", (e) => { setPortrait(e.target.files[0]); e.target.value = ""; });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") { closeSheet(); closeDrawer(); $("#dice").hidden = true; } });

  const cur = S.store.current && S.store.chars[S.store.current];
  try {
    if (cur) await doAct([], { character: cur.character, silent: true });
    else await newCharacter();
  } catch (e) { toast(e.message, true); }

  if ("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js").catch(() => {});
}
boot();
