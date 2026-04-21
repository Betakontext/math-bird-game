# Math bird | Mobile UI build patch
# - DOCTYPE am Anfang sicherstellen (verhindert Quirks Mode)
# - Entfernt alte mobile-controls-Blöcke und injiziert aktualisierten SNIPPET
# - SNIPPET: combo-pad (4x4), Enter gestreckt, forceMobile/forcemobile, Android Tap-Through, Atem-Pfeile, dynamische Größen
# - iPad-Fix: Rekursion verhindert (gateClosed, isTrusted-Filter, Listener-Abbau, iOS ohne Pointer-Injektion)
# - CDN/ORB-Fix: Entfernt trailing slash in data-cdn/config.cdn und spiegelt BrowserFS lokal als Fallback
# https://github.com/betakontext/mathbird
# Licensed under the MIT License

from pathlib import Path
import re
import shutil
import subprocess
import sys
import urllib.request

WEB = Path("build/web")
INDEX = WEB / "index.html"
VENDOR_DIR = WEB / "vendor"
LOCAL_BROWSERFS = VENDOR_DIR / "browserfs.min.js"
BFS_URLS = [
    "https://unpkg.com/browserfs@1.4.3/dist/browserfs.min.js",
    "https://cdn.jsdelivr.net/npm/browserfs@1.4.3/dist/browserfs.min.js",
]

SNIPPET = r"""<!-- BEGIN mobile-controls -->
<style>
  :root {
    --btn-size: 64px;
    --gap: 10px;
    --btn-bg: rgba(0,0,0,0.35);
    --btn-border: rgba(255,255,255,0.85);
    --btn-fg: #fff;
    --btn-active-bg: rgba(255,255,255,0.35);
    --btn-active-fg: #000;
    --btn-arrow-bg: rgba(0,0,0,0.25);
    --pulse-duration: 1.6s;
    --gate-bg: rgba(0,0,0,0.55);
    --gate-fg: #fff;
    --gate-ring: rgba(255,255,255,0.85);
  }

  @media (max-width: 820px), (max-height: 680px) {
    :root { --btn-size: 56px; --gap: 8px; }
    #mobile-controls .combo-pad { left: 12px; bottom: 12px; }
    #mobile-controls .fs-float  { right: 12px; bottom: 12px; }
  }

  @media (max-width: 600px), (max-height: 500px) {
    :root { --btn-size: 32px; --gap: 8px; }
  }

  #mobile-controls.only-fs .combo-pad { display: none !important; }
  #mobile-controls.only-fs { visibility: visible !important; opacity: 1 !important; display: block !important; }

  #mobile-controls {
    position: fixed !important; inset: 0 !important; pointer-events: none;
    z-index: 2147483647 !important; visibility: hidden !important; opacity: 0 !important; display: none !important;
  }
  #mobile-controls.visible { visibility: visible !important; opacity: 1 !important; display: block !important; }

  #mobile-controls .btn {
    background: var(--btn-bg); color: var(--btn-fg);
    border: 2px solid var(--btn-border); border-radius: 12px;
    font: 600 14px/1 system-ui, sans-serif;
    width: var(--btn-size); height: var(--btn-size);
    display: grid; place-items: center; text-align: center;
    user-select: none; -webkit-user-select: none; touch-action: manipulation;
    box-sizing: border-box;
    transform-origin: center center;
    will-change: background, box-shadow, border-color, filter;
  }
  #mobile-controls .btn:active { background: var(--btn-active-bg); color: var(--btn-active-fg); }

  #mobile-controls .btn.is-arrow { background: var(--btn-arrow-bg); }
  #mobile-controls.arrow-active .combo-pad .btn.is-arrow.pulse-on {
    animation: arrowBreath var(--pulse-duration) ease-in-out infinite !important;
  }
  @keyframes arrowBreath {
    0%   { background-color: rgba(255,255,255,0.12); border-color: rgba(255,255,255,0.55); box-shadow: 0 0 0 rgba(255,255,255,0); filter: brightness(1.0); }
    50%  { background-color: rgba(255,255,255,0.28); border-color: rgba(255,255,255,0.98); box-shadow: 0 0 18px rgba(255,255,255,0.45); filter: brightness(1.15); }
    100% { background-color: rgba(255,255,255,0.12); border-color: rgba(255,255,255,0.55); box-shadow: 0 0 0 rgba(255,255,255,0); filter: brightness(1.0); }
  }

  #mobile-controls .combo-pad {
    position: fixed; left: 16px; bottom: 16px; pointer-events: auto;
    display: grid; gap: var(--gap);
    grid-template-columns: repeat(4, var(--btn-size));
    grid-auto-rows: var(--btn-size);
    grid-template-areas:
      "d1 d2 d3 keyF"
      "d4 d5 d6 keyBack"
      "d7 d8 d9 keyEnter"
      "left d0 minus keyEnter";
  }
  .combo-pad .btn[data-area="d1"]      { grid-area: d1; }
  .combo-pad .btn[data-area="d2"]      { grid-area: d2; }
  .combo-pad .btn[data-area="d3"]      { grid-area: d3; }
  .combo-pad .btn[data-area="keyF"]    { grid-area: keyF; }
  .combo-pad .btn[data-area="d4"]      { grid-area: d4; }
  .combo-pad .btn[data-area="d5"]      { grid-area: d5; }
  .combo-pad .btn[data-area="d6"]      { grid-area: d6; }
  .combo-pad .btn[data-area="keyBack"] { grid-area: keyBack; }
  .combo-pad .btn[data-area="d7"]      { grid-area: d7; }
  .combo-pad .btn[data-area="d8"]      { grid-area: d8; } /* Up */
  .combo-pad .btn[data-area="d9"]      { grid-area: d9; }

  .combo-pad .btn[data-area="keyEnter"]{
    grid-area: keyEnter;
    align-self: stretch !important;
    justify-self: stretch !important;
    height: auto !important;
    min-height: calc(var(--btn-size) * 2 + var(--gap)) !important;
  }

  .combo-pad .btn[data-area="left"]  { grid-area: left; }
  .combo-pad .btn[data-area="d0"]    { grid-area: d0; }
  .combo-pad .btn[data-area="minus"] { grid-area: minus; }

  #mobile-controls .fs-float { position: fixed; right: 16px; bottom: 16px; z-index: 2147483647; pointer-events: auto; }
  #mobile-controls .fs-float .btn { width: var(--btn-size); height: var(--btn-size); }

  #mobile-controls .play-gate {
    position: fixed; inset: 0; display: grid; place-items: center;
    pointer-events: auto; background: var(--gate-bg);
    transition: opacity .2s ease;
  }
  #mobile-controls .play-gate.hidden { opacity: 0; pointer-events: none; }

  #mobile-controls .play-gate .ring {
    width: 160px; height: 160px; border-radius: 50%;
    border: 4px solid var(--gate-ring);
    display: grid; place-items: center;
    animation: pulse 1.6s ease-in-out infinite;
    font: 700 18px/1.2 system-ui, sans-serif; color: var(--gate-fg);
    text-shadow: 0 1px 2px rgba(0,0,0,.35);
    user-select: none; -webkit-user-select: none;
  }
  @keyframes pulse {
    0% { transform: scale(0.96); box-shadow: 0 0 0 0 rgba(255,255,255,0.35); }
    50% { transform: scale(1.04); box-shadow: 0 0 22px 6px rgba(255,255,255,0.25); }
    100% { transform: scale(0.96); box-shadow: 0 0 0 0 rgba(255,255,255,0.0); }
  }

  canvas#canvas { z-index: 5 !important; position: absolute !important; inset: 0; }
</style>

<div id="mobile-controls" aria-hidden="true">
  <div class="play-gate" id="play-gate"><div class="ring">Play</div></div>

  <div class="combo-pad">
    <div class="btn" data-area="d1"     data-digit="1">1</div>
    <div class="btn" data-area="d2"     data-digit="2">2</div>
    <div class="btn" data-area="d3"     data-digit="3">3</div>
    <div class="btn" data-area="keyF"   data-key="KeyF">F</div>

    <div class="btn" data-area="d4"     data-digit="4">4</div>
    <div class="btn" data-area="d5"     data-digit="5">5</div>
    <div class="btn" data-area="d6"     data-digit="6">6</div>
    <div class="btn" data-area="keyBack" data-key="Backspace">⌫</div>

    <div class="btn" data-area="d7"     data-digit="7">7</div>
    <div class="btn is-arrow pulse-on" data-area="d8"     data-digit="8" data-arrow="ArrowUp">▲ 8</div>
    <div class="btn" data-area="d9"     data-digit="9">9</div>
    <div class="btn" data-area="keyEnter" data-key="Enter">⏎</div>

    <div class="btn is-arrow pulse-on" data-area="left"  data-arrow="ArrowLeft">◀︎</div>
    <div class="btn is-arrow pulse-on" data-area="d0"    data-digit="0" data-arrow="ArrowDown">▼ 0</div>
    <div class="btn is-arrow pulse-on" data-area="minus" data-char="−"  data-arrow="ArrowRight">− ▶︎</div>
  </div>

  <div class="fs-float"><div class="btn" data-action="fs" title="Fullscreen">⤢</div></div>
</div>

<script>
(function () {
  function ready(fn){ if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', fn, { once: true }); } else { fn(); } }

  // BrowserFS Fallback: lädt lokale Kopie, falls CDN blockiert/ORB aktiv ist
  function checkAndLoadBrowserFS() {
    try {
      if (window.BrowserFS) return;
      var local = (window.location.origin + window.location.pathname).replace(/\/[^\/]*$/,'') + '/vendor/browserfs.min.js';
      var s = document.createElement('script');
      s.src = local; s.async = true;
      s.onerror = function(){
        var s2 = document.createElement('script');
        s2.src = 'https://pygame-web.github.io/cdn/0.9.3/browserfs.min.js'; // ohne doppelten Slash
        document.head.appendChild(s2);
      };
      document.head.appendChild(s);
    } catch(e){}
  }

  ready(function initMobileControls() {
    if (window.__MB_UI_INITED__) return;           // Doppel-Init verhindern
    window.__MB_UI_INITED__ = true;

    checkAndLoadBrowserFS(); // früh versuchen

    const root = document.getElementById('mobile-controls');
    if (!root) return;

    function applyVisible() {
      root.classList.add('visible');
      root.style.setProperty('z-index', '2147483647', 'important');
    }
    function canvasOrWindow() { return document.querySelector('canvas') || window; }
    function focusCanvasRetries(){
      const c = document.querySelector('canvas'); if (!c) return;
      try{ c.focus({preventScroll:true}); }catch(e){}
      setTimeout(()=>{ try{ c.focus({preventScroll:true}); }catch(e){} }, 120);
      setTimeout(()=>{ try{ c.focus({preventScroll:true}); }catch(e){} }, 400);
      setTimeout(()=>{ try{ c.focus({preventScroll:true}); }catch(e){} }, 1000);
    }
    function dispatchEnterOnce() {
      const t = canvasOrWindow();
      try {
        t.dispatchEvent(new KeyboardEvent('keydown', { key:'Enter', code:'Enter', bubbles:true, cancelable:true }));
        setTimeout(()=>t.dispatchEvent(new KeyboardEvent('keyup', { key:'Enter', code:'Enter', bubbles:true, cancelable:true })), 10);
      } catch(e) {}
    }

    const isiOS = /iphone|ipad|ipod/i.test((navigator.userAgent||'') + (navigator.platform||''));
    function dispatchPointerToCanvas() {
      if (isiOS) return; // Auf iOS keine Pointer-Injektion (vermeidet Rekursion)
      const c = document.querySelector('canvas');
      if (!c) return;
      try {
        const rect = c.getBoundingClientRect();
        const cx = rect.left + Math.max(1, Math.min(rect.width - 1, rect.width * 0.5));
        const cy = rect.top  + Math.max(1, Math.min(rect.height - 1, rect.height * 0.5));
        const opts = { bubbles: true, cancelable: true, clientX: cx, clientY: cy, pointerId: 1, pointerType: 'touch' };
        c.dispatchEvent(new PointerEvent('pointerdown', opts));
        c.dispatchEvent(new PointerEvent('pointerup',   opts));
        c.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, clientX: cx, clientY: cy }));
      } catch(e) {
        try { c.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true })); } catch(_) {}
      }
    }

    root.querySelectorAll('.btn').forEach(b => { b.style.pointerEvents = 'auto'; });

    const qs = new URLSearchParams(location.search);
    const forceMobile = (qs.get('forceMobile') === '1') || (qs.get('forcemobile') === '1');

    let mobileSticky = null;
    function computeMobileSticky() {
      if (mobileSticky !== null) return mobileSticky;
      const ua = (navigator.userAgent || '').toLowerCase();
      const isAndroid = /android/.test(ua);
      const isIOSua = /iphone|ipad|ipod/.test(ua);
      const hasTouch = (('ontouchstart' in window) || (navigator.maxTouchPoints||0) > 0);
      mobileSticky = isAndroid || isIOSua || hasTouch;
      return mobileSticky;
    }

    function evaluate() {
      try {
        const isMob = computeMobileSticky();
        if (forceMobile || isMob) root.classList.remove('only-fs');
        else root.classList.add('only-fs');
        applyVisible();
      } catch(e) {
        root.classList.add('only-fs'); applyVisible();
      }
    }

    function stabilizeAudio() {
      try {
        const AC = window.AudioContext || window.webkitAudioContext;
        const ctx =
          (window.MM && (window.MM.ctx || window.MM.context)) ||
          window.__audioCtx ||
          (AC ? (window.__audioCtx = new AC()) : null);
        if (!ctx) return;
        if (ctx.state !== 'running') { ctx.resume?.(); }
        const seconds = 0.05;
        const sr = ctx.sampleRate || 48000;
        const buf = ctx.createBuffer(1, Math.max(1, Math.floor(sr * seconds)), sr);
        const src = ctx.createBufferSource();
        src.buffer = buf;
        src.connect(ctx.destination);
        src.start(0);
      } catch(e) {}
    }
    try { window.stabilizeAudio = stabilizeAudio; } catch(e) {}

    const gate = document.getElementById('play-gate');
    let gateJustClosedAt = 0;
    let gateClosed = false; // iOS: Einmal-Guard

    function closeGate() {
      if (gateClosed) return;
      gateClosed = true;

      gateJustClosedAt = Date.now();
      if (gate) {
        try { gate.style.pointerEvents = 'none'; } catch(e) {}
        gate.classList.add('hidden');
        try { gate.remove(); } catch(e) {}
      }
      try { root.style.pointerEvents = 'none'; } catch(e) {}

      applyVisible();
      focusCanvasRetries();

      dispatchEnterOnce();
      try { stabilizeAudio(); } catch(e) {}

      requestAnimationFrame(()=>dispatchPointerToCanvas());

      try {
        if (window.MM && typeof window.MM.unlock === 'function') window.MM.unlock();
        if (window.python && (window.python.run || window.python.eval)) (window.python.run || window.python.eval).call(window.python, "0");
        else if (window.pyodide?.runPython) window.pyodide.runPython("0");
      } catch(e) {}

      // Gate-Listener entfernen (Reentrancy verhindern)
      try {
        gate.removeEventListener('touchstart', onGateTouchStart, {passive:false});
        gate.removeEventListener('click', onGateClick);
        window.removeEventListener('keydown', onGateKeydown, {passive:true});
      } catch(e) {}
    }

    function onGateTouchStart(e){ e.preventDefault(); closeGate(); }
    function onGateClick(e){ e.preventDefault(); closeGate(); }
    function onGateKeydown(e){
      if (!e.isTrusted) return; // synthetische Events ignorieren
      if (e.key==='Enter' || e.key===' ') { closeGate(); }
    }

    gate.addEventListener('touchstart', onGateTouchStart, {passive:false});
    gate.addEventListener('click', onGateClick);
    window.addEventListener('keydown', onGateKeydown, {passive:true});

    document.addEventListener('pointerdown', (e) => {
      if (Date.now() - gateJustClosedAt < 600) {
        try { root.style.pointerEvents = 'none'; } catch(_) {}
      }
    }, true);

    const active = new Map();
    function dispatchKey(code, type) {
      const keyMap = {ArrowUp:'ArrowUp',ArrowDown:'ArrowDown',ArrowLeft:'ArrowLeft',ArrowRight:'ArrowRight',KeyF:'f',Enter:'Enter',Backspace:'Backspace'};
      const key = keyMap[code] || '';
      try { canvasOrWindow().dispatchEvent(new KeyboardEvent(type, { key, code, bubbles:true, cancelable:true })); } catch(e) {}
    }
    function startRepeat(code){ if(active.has(code)) return; dispatchKey(code,'keydown'); const itv=setInterval(()=>dispatchKey(code,'keydown'),55); active.set(code,itv); }
    function stopRepeat(code){ const id=active.get(code); if(id) clearInterval(id); active.delete(code); dispatchKey(code,'keyup'); }
    function stopAllRepeats(){ for (const [c,i] of active){ clearInterval(i); dispatchKey(c,'keyup'); } active.clear(); }

    function bindComboBtn(el) {
      const digit = el.getAttribute('data-digit');
      const ch    = el.getAttribute('data-char');
      const key   = el.getAttribute('data-key');
      const arrow = el.getAttribute('data-arrow');

      const onDown = (e)=>{
        e.preventDefault();
        closeGate();
        if ((digit || ch || key) && active.size && !arrow) stopAllRepeats();
        if (digit){ const k='Digit'+String(digit); const t=canvasOrWindow(); try {
          t.dispatchEvent(new KeyboardEvent('keydown',{key:String(digit),code:k,bubbles:true,cancelable:true}));
          setTimeout(()=>t.dispatchEvent(new KeyboardEvent('keyup',{key:String(digit),code:k,bubbles:true,cancelable:true})),10);
        } catch(e){} }
        if (ch){ const t=canvasOrWindow(); const code='Minus'; try {
          t.dispatchEvent(new KeyboardEvent('keydown',{key:'-',code,bubbles:true,cancelable:true}));
          setTimeout(()=>t.dispatchEvent(new KeyboardEvent('keyup',{key:'-',code,bubbles:true,cancelable:true})),10);
        } catch(e){} }
        if (key){ dispatchKey(key,'keydown'); if (key==='Backspace' || key==='KeyF') setTimeout(()=>dispatchKey(key,'keyup'),10); }
        if (arrow){ startRepeat(arrow); }
      };
      const onUp=(e)=>{ e.preventDefault(); if (key && key!=='Backspace' && key!=='KeyF') dispatchKey(key,'keyup'); if (arrow) stopRepeat(arrow); };

      el.addEventListener('touchstart', onDown, {passive:false});
      el.addEventListener('touchend',   onUp,   {passive:false});
      el.addEventListener('touchcancel',onUp,   {passive:false});
      el.addEventListener('mousedown',  onDown);
      el.addEventListener('mouseup',    onUp);
      el.addEventListener('mouseleave', onUp);
    }
    document.querySelectorAll('.combo-pad .btn').forEach(bindComboBtn);

    function isDomFS(){ return !!document.fullscreenElement; }
    function enterFS(){ try { focusCanvasRetries(); const p=document.documentElement.requestFullscreen(); p?.then?.(()=>{}).catch?.(()=>{});} catch(e){} }
    function exitFS(){ try { const p=document.exitFullscreen(); p?.then?.(()=>{}).catch?.(()=>{});} catch(e){} }
    const fsBtn = root.querySelector('.fs-float [data-action="fs"]');
    if (fsBtn) {
      const guard=(e)=>{ e.preventDefault(); const isMob = computeMobileSticky(); if (forceMobile || isMob) root.classList.remove('only-fs'); else root.classList.add('only-fs'); isDomFS()? exitFS() : enterFS(); const reap=()=>applyVisible(); reap(); setTimeout(reap,50); setTimeout(reap,200); };
      fsBtn.addEventListener('click', guard);
      fsBtn.addEventListener('touchstart', guard, {passive:false});
    }

    evaluate();
    window.addEventListener('resize', evaluate, { passive: true });
    window.addEventListener('orientationchange', evaluate, { passive: true });
    setTimeout(evaluate, 150); setTimeout(evaluate, 600); setTimeout(evaluate, 1200);
  });
})();
</script>
<!-- END mobile-controls -->
"""

def remove_old_blocks(html: str) -> str:
    start, end = "<!-- BEGIN mobile-controls -->", "<!-- END mobile-controls -->"
    while start in html and end in html:
        pre = html.split(start)[0]
        post = html.split(end)[-1]
        html = pre + post
    return html

def ensure_doctype_top(html: str) -> str:
    if re.match(r'^\s*<!doctype\s+html\s*>', html, flags=re.IGNORECASE):
        return html
    return "<!DOCTYPE html>\n" + html.lstrip()

def trim_cdn_trailing_slash(html: str) -> str:
    # data-cdn=".../0.9.3/" -> ".../0.9.3"
    html = re.sub(r'(data-cdn\s*=\s*")([^"]*?)(/)"', r'\1\2"', html)
    # config.cdn = ".../0.9.3/" -> ".../0.9.3"
    html = re.sub(r'(config\.cdn\s*=\s*")([^"]*?)(/)"', r'\1\2"', html)
    # src="https://.../pythons.js?#" bleibt unberührt
    return html

def mirror_browserfs_locally():
    VENDOR_DIR.mkdir(parents=True, exist_ok=True)
    if LOCAL_BROWSERFS.exists() and LOCAL_BROWSERFS.stat().st_size > 0:
        print(f"Local BrowserFS already present: {LOCAL_BROWSERFS}")
        return
    last_err = None
    for url in BFS_URLS:
        try:
            print(f"Downloading BrowserFS from {url} ...")
            with urllib.request.urlopen(url, timeout=30) as resp:
                data = resp.read()
            if not data or len(data) < 10_000:
                raise RuntimeError("Downloaded file too small – unexpected content")
            LOCAL_BROWSERFS.write_bytes(data)
            print(f"Saved {LOCAL_BROWSERFS}")
            return
        except Exception as e:
            last_err = e
            print(f"Warning: Could not download from {url}: {e}")
    print(f"Warning: All BrowserFS mirror attempts failed: {last_err}")

def main():
    if not WEB.exists() or not INDEX.exists():
        raise SystemExit("Build first: pygbag --build . (missing build/web/index.html)")

    # Spiegel BrowserFS lokal als Fallback gegen ORB/CDN-Probleme
    mirror_browserfs_locally()

    html = INDEX.read_text(encoding="utf-8")

    html = ensure_doctype_top(html)
    html = remove_old_blocks(html)
    html = trim_cdn_trailing_slash(html)

    if "</body>" not in html:
        raise SystemExit("No </body> tag found in build/web/index.html")
    html = html.replace("</body>", SNIPPET + "\n</body>")

    INDEX.write_text(html, encoding="utf-8")
    print("Patched build/web/index.html: DOCTYPE ensured + iPad-safe controls + CDN/ORB fixes (trailing slash + local BrowserFS) injected.")

if __name__ == "__main__":
    main()
