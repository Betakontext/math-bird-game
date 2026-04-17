# Math bird | Mobile UI build patch
# - Stellt <!DOCTYPE html> am Anfang sicher (verhindert Quirks Mode)
# - Entfernt alte mobile-controls-Blöcke und injiziert aktualisierten SNIPPET
# - SNIPPET: combo-pad (4x4), Enter gestreckt, forceMobile/forcemobile, Android Tap-Through, Atem-Pfeile, dynamische Größen
# https://github.com/betakontext/mathbird
# Licensed under the MIT License

from pathlib import Path
import re

WEB = Path("build/web")
INDEX = WEB / "index.html"

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

  ready(function initMobileControls() {
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
    function dispatchPointerToCanvas() {
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
      const isIOS = /iphone|ipad|ipod/.test(ua);
      const hasTouch = (('ontouchstart' in window) || (navigator.maxTouchPoints||0) > 0);
      mobileSticky = isAndroid || isIOS || hasTouch;
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
        // Bevorzugt vorhandenen Context der Engine nutzen
        const ctx =
          (window.MM && (window.MM.ctx || window.MM.context)) ||
          window.__audioCtx ||
          (AC ? (window.__audioCtx = new AC()) : null);
        if (!ctx) return;

        // Sicherstellen, dass der Context läuft (nach User-Geste erlaubt)
        if (ctx.state !== 'running') { ctx.resume?.(); }

        // Kurzes „Priming“, um Render-Pipeline aufzuwärmen (verringert Knistern am Start)
        const seconds = 0.05;
        const sr = ctx.sampleRate || 48000;
        const buf = ctx.createBuffer(1, Math.max(1, Math.floor(sr * seconds)), sr);
        const src = ctx.createBufferSource();
        src.buffer = buf;
        src.connect(ctx.destination);
        src.start(0);
      } catch(e) { /* still fine */ }
    }
    // Optional global verfügbar machen
    try { window.stabilizeAudio = stabilizeAudio; } catch(e) {}

    const gate = document.getElementById('play-gate');
    let gateJustClosedAt = 0;
    function closeGate() {
      gateJustClosedAt = Date.now();
      if (!gate) return;
      try { gate.style.pointerEvents = 'none'; } catch(e) {}
      gate.classList.add('hidden');
      try { gate.remove(); } catch(e) {}
      try { root.style.pointerEvents = 'none'; } catch(e) {}

      applyVisible();
      focusCanvasRetries();
      dispatchEnterOnce();
      try { window.stabilizeAudio?.(); } catch(e){}
      requestAnimationFrame(()=>dispatchPointerToCanvas());

      try {
        if (window.MM && typeof window.MM.unlock === 'function') window.MM.unlock();
        if (window.python && (window.python.run || window.python.eval)) (window.python.run || window.python.eval).call(window.python, "0");
        else if (window.pyodide?.runPython) window.pyodide.runPython("0");
      } catch(e) {}
    }

    gate.addEventListener('touchstart', (e)=>{ e.preventDefault(); closeGate(); }, {passive:false});
    gate.addEventListener('click',      (e)=>{ e.preventDefault(); closeGate(); });
    window.addEventListener('keydown',  (e)=>{ if (e.key==='Enter' || e.key===' ') { closeGate(); } }, {passive:true});

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
    # <!DOCTYPE html> ganz oben sicherstellen
    if re.match(r'^\s*<!doctype\s+html\s*>', html, flags=re.IGNORECASE):
        return html
    return "<!DOCTYPE html>\n" + html.lstrip()

def main():
    if not WEB.exists() or not INDEX.exists():
        raise SystemExit("Build first: pygbag --build . (missing build/web/index.html)")

    html = INDEX.read_text(encoding="utf-8")

    # 1) DOCTYPE am Anfang sichern (gegen Quirks Mode)
    html = ensure_doctype_top(html)

    # 2) Alte mobile-controls entfernen
    html = remove_old_blocks(html)

    # 3) SNIPPET vor </body> injizieren
    if "</body>" not in html:
        raise SystemExit("No </body> tag found in build/web/index.html")
    html = html.replace("</body>", SNIPPET + "\n</body>")

    INDEX.write_text(html, encoding="utf-8")
    print("Patched build/web/index.html: DOCTYPE ensured + mobile controls injected.")

if __name__ == "__main__":
    main()
