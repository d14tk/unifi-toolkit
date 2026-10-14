// Deutsche Oberflaeche fuer UniFi Toolkit (HA-App).
// Upstream hat keine Uebersetzungen. nginx bindet dieses Skript in jede Seite ein,
// es ersetzt englische UI-Texte anhand von window.HA_I18N_DE und uebersetzt per
// MutationObserver auch alles, was Alpine.js oder die Tool-Skripte spaeter rendern.
// Unbekannte Texte bleiben englisch.
(function () {
  'use strict';

  var STORAGE_KEY = 'ha_toolkit_lang';
  var lang = window.HA_I18N_DEFAULT === 'en' ? 'en' : 'de';
  try {
    var stored = localStorage.getItem(STORAGE_KEY);
    if (stored === 'de' || stored === 'en') lang = stored;
  } catch (e) { /* kein Storage, Default bleibt */ }

  function setLang(value) {
    try { localStorage.setItem(STORAGE_KEY, value); } catch (e) { /* ignorieren */ }
    location.reload();
  }

  var SKIP_TAGS = { SCRIPT: 1, STYLE: 1, TEXTAREA: 1, CODE: 1, PRE: 1, NOSCRIPT: 1 };
  var ATTRS = ['title', 'placeholder', 'aria-label', 'alt'];

  function norm(s) { return s.replace(/\s+/g, ' ').trim(); }
  function escapeRe(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

  var exact = new Map();
  var patterns = [];
  var dict = window.HA_I18N_DE || {};
  Object.keys(dict).forEach(function (en) {
    var de = dict[en];
    if (!de || de === en) return;
    var key = norm(en);
    var holders = key.match(/\$\{[^}]*\}/g);
    if (!holders) { exact.set(key, de); return; }
    // "${a} of ${b}" -> /^(.+?) of (.+?)$/ ; Platzhalter im Deutschen auf $1..$n abbilden.
    // Kaum fester Text (z. B. "${secs}s") wuerde sonst jedes Wort auf "s" treffen,
    // dann duerfen die Platzhalter nur Zahlen sein.
    var literal = key.replace(/\$\{[^}]*\}/g, '').replace(/[^A-Za-z]/g, '');
    var capture = literal.length < 4 ? '([\\d.,]+)' : '([\\s\\S]+?)';
    var re = '^' + key.split(/\$\{[^}]*\}/).map(escapeRe).join(capture) + '$';
    var ok = true;
    var rep = de.replace(/\$\{[^}]*\}/g, function (h) {
      var i = holders.indexOf(h);
      if (i < 0) { ok = false; return h; }
      return '$' + (i + 1);
    });
    if (ok) patterns.push([new RegExp(re), rep.replace(/\$(?!\d)/g, '$$$$')]);
  });

  function lookup(core) {
    var out = exact.get(core);
    if (out !== undefined) return out;
    for (var i = 0; i < patterns.length; i++) {
      if (patterns[i][0].test(core)) return core.replace(patterns[i][0], patterns[i][1]);
    }
    // Satzzeichen am Rand, die durch Zusammensetzen im Upstream-Code entstehen
    var p = /^([.,;:!?)–—-]*\s*)([\s\S]*?)(\s*[.,;:!?(]*)$/.exec(core);
    if (p && (p[1] || p[3]) && p[2]) {
      out = exact.get(p[2]) || exact.get(p[2] + p[3].trim());
      if (out !== undefined) return p[1] + out + (exact.get(p[2]) !== undefined ? p[3] : '');
    }
    return undefined;
  }

  // Ergebnisse merken: Live-Updates (WebSocket, Tabellen) liefern immer wieder dieselben Texte
  var cache = new Map();
  var MAX_PARTS = 12;

  function tr(text) {
    if (!text) return text;
    var m = /^(\s*)([\s\S]*?)(\s*)$/.exec(text);
    var core = norm(m[2]);
    if (!core || !/[A-Za-z]/.test(core)) return text;
    var out;
    if (cache.has(core)) {
      out = cache.get(core);
    } else {
      out = translateCore(core);
      if (cache.size > 5000) cache.clear();
      cache.set(core, out);
    }
    return out === undefined ? text : m[1] + out + m[3];
  }

  function translateCore(core) {
    var out = lookup(core);
    if (out === undefined) {
      // Zusammengesetzte Texte: laengste bekannte Satzfolgen uebersetzen,
      // Unbekanntes bleibt stehen
      // (Satzfolgen begrenzt, damit lange Texte den Observer nicht blockieren)
      var parts = core.split(/(?<=[.!?:;])\s+/);
      if (parts.length > 1) {
        var hit = false;
        var res = [];
        for (var i = 0; i < parts.length;) {
          var found = false;
          for (var j = Math.min(parts.length, i + MAX_PARTS); j > i; j--) {
            var t = lookup(parts.slice(i, j).join(' '));
            if (t !== undefined) { res.push(t); i = j; hit = found = true; break; }
          }
          if (!found) { res.push(parts[i]); i++; }
        }
        if (hit) out = res.join(' ');
      }
    }
    return out;
  }

  function skipped(el) {
    for (var e = el; e; e = e.parentElement) {
      if (SKIP_TAGS[e.tagName] || e.isContentEditable || e.hasAttribute('data-no-i18n')) return true;
    }
    return false;
  }

  function translateText(node) {
    var parent = node.parentElement;
    if (!parent || skipped(parent)) return;
    var t = tr(node.nodeValue);
    if (t !== node.nodeValue) node.nodeValue = t;
  }

  function translateAttrs(el) {
    for (var i = 0; i < ATTRS.length; i++) {
      var v = el.getAttribute(ATTRS[i]);
      if (v) {
        var t = tr(v);
        if (t !== v) el.setAttribute(ATTRS[i], t);
      }
    }
    if (el.tagName === 'INPUT' && (el.type === 'button' || el.type === 'submit') && el.value) {
      var tv = tr(el.value);
      if (tv !== el.value) el.value = tv;
    }
  }

  function walk(root) {
    if (root.nodeType === 3) { translateText(root); return; }
    if (root.nodeType !== 1 || skipped(root)) return;
    translateAttrs(root);
    // Ausgeschlossene Unterbaeume komplett ueberspringen (Text und Attribute)
    var it = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        if (n.nodeType === 1 && (SKIP_TAGS[n.tagName] || n.isContentEditable || n.hasAttribute('data-no-i18n'))) {
          return NodeFilter.FILTER_REJECT;
        }
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    var n;
    while ((n = it.nextNode())) {
      if (n.nodeType === 3) {
        var t = tr(n.nodeValue);
        if (t !== n.nodeValue) n.nodeValue = t;
      } else {
        translateAttrs(n);
      }
    }
  }

  function injectToggle() {
    var body = document.querySelector('#config-modal .modal-body');
    if (!body || document.getElementById('ha-i18n-lang')) return;
    var box = document.createElement('div');
    box.className = 'form-group';
    box.setAttribute('data-no-i18n', '');
    box.innerHTML =
      '<label for="ha-i18n-lang">Sprache / Language</label>' +
      '<select id="ha-i18n-lang">' +
      '<option value="de">Deutsch</option>' +
      '<option value="en">English</option>' +
      '</select>' +
      '<small>Wird in diesem Browser gespeichert. / Saved in this browser.</small>';
    body.insertBefore(box, body.firstChild);
    var sel = box.querySelector('select');
    // Optik der vorhandenen Eingabefelder uebernehmen
    var ref = body.querySelector('.form-group input');
    if (ref) {
      var cs = getComputedStyle(ref);
      ['padding', 'border', 'borderRadius', 'background', 'color', 'font', 'width', 'boxSizing']
        .forEach(function (p) { sel.style[p] = cs[p]; });
    }
    sel.value = lang;
    sel.addEventListener('change', function () { setLang(sel.value); });
  }

  window.haToolkitSetLanguage = setLang;

  if (lang !== 'de') {
    document.addEventListener('DOMContentLoaded', injectToggle);
    return;
  }

  document.documentElement.setAttribute('lang', 'de');

  ['alert', 'confirm', 'prompt'].forEach(function (fn) {
    var orig = window[fn];
    if (typeof orig !== 'function') return;
    window[fn] = function (msg) {
      var args = Array.prototype.slice.call(arguments);
      if (typeof msg === 'string') args[0] = tr(msg);
      return orig.apply(window, args);
    };
  });

  new MutationObserver(function (records) {
    for (var i = 0; i < records.length; i++) {
      var r = records[i];
      if (r.type === 'characterData') translateText(r.target);
      else if (r.type === 'attributes') { if (!skipped(r.target)) translateAttrs(r.target); }
      else for (var j = 0; j < r.addedNodes.length; j++) walk(r.addedNodes[j]);
    }
    if (document.title) {
      var tt = tr(document.title);
      if (tt !== document.title) document.title = tt;
    }
  }).observe(document.documentElement, {
    subtree: true, childList: true, characterData: true,
    attributes: true, attributeFilter: ATTRS.concat(['value'])
  });

  document.addEventListener('DOMContentLoaded', function () {
    walk(document.body);
    document.title = tr(document.title);
    injectToggle();
  });
})();
