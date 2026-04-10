# Math bird | Mobile UI build patch (stable Play gate, mobile-only pad)
# For further developments visit and fork:
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
    #mobile-controls .fs-float { right: 12px; bottom: 12px; }
  }

  /* Only-FS mode shows just the floating FS button */
  #mobile-controls.only-fs .combo-pad { display: none !important; }
  #mobile-controls.only-fs {
    visibility: visible !important; opacity: 1 !important; display: block !important;
  }

  /* Overlay container sits on top but does not block canvas except on buttons/gate */
  #mobile-controls {
    position: fixed !important; inset: 0 !important; pointer-events: none;
    z-index: 2147483647 !important; visibility: hidden !important; opacity: 0 !important; display: none !important;
  }

  #mobile-controls .btn {
    background: var(--btn-bg); color: var(--btn-fg);
    border: 2px solid var(--btn-border); border-radius: 12px;
    font: 600 14px/1 system-ui, sans-serif;
    width: var(--btn-size); height: var(--btn-size);
    display: grid; place-items: center; text-align: center;
    user-select: none; -webkit-user-select: none; touch-action: manipulation;
    transform-origin: center center;
    will-change: background, box-shadow, border-color, filter;
  }
  #mobile-controls .btn:active { background: var(--btn-active-bg); color: var(--btn-active-fg); }

  /* Arrow buttons slightly brighter */
  #mobile-controls .btn.is-arrow { background: var(--btn-arrow-bg); }

  /* Arrow breath animation during play */
  #mobile-controls.arrow-active .combo-pad .btn.is-arrow.pulse-on {
    animation: arrowBreath var(--pulse-duration) ease-in-out infinite !important;
  }
  @keyframes arrowBreath {
    0%   { background-color: rgba(255,255,255,0.12); border-color: rgba(255,255,255,0.55); box-shadow: 0 0 0 rgba(255,255,255,0); filter: brightness(1.0); }
    50%  { background-color: rgba(255,255,255,0.28); border-color: rgba(255,255,255,0.98); box-shadow: 0 0 18px rgba(255,255,255,0.45); filter: brightness(1.15); }
    100% { background-color: rgba(255,255,255,0.12); border-color: rgba(255,255,255,0.55); box-shadow: 0 0 0 rgba(255,255,255,0); filter: brightness(1.0); }
  }

  /* 4x4 combo pad bottom-left */
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

  #mobile-controls .combo-pad .btn[data-area="d1"]      { grid-area: d1; }
  #mobile-controls .combo-pad .btn[data-area="d2"]      { grid-area: d2; }
  #mobile-controls .combo-pad .btn[data-area="d3"]      { grid-area: d3; }
  #mobile-controls .combo-pad .btn[data-area="keyF"]    { grid-area: keyF; }

  #mobile-controls .combo-pad .btn[data-area="d4"]      { grid-area: d4; }
  #mobile-controls .combo-pad .btn[data-area="d5"]      { grid-area: d5; }
  #mobile-controls .combo-pad .btn[data-area="d6"]      { grid-area: d6; }
  #mobile-controls .combo-pad .btn[data-area="keyBack"] { grid-area: keyBack; }

  #mobile-controls .combo-pad .btn[data-area="d7"]      { grid-area: d7; }
  #mobile-controls .combo-pad .btn[data-area="d8"]      { grid-area: d8; }
  #mobile-controls .combo-pad .btn[data-area="d9"]      { grid-area: d9; }

  #mobile-controls .combo-pad .btn[data-area="keyEnter"] {
    grid-area: keyEnter; height: calc(var(--btn-size) * 2 + var(--gap));
  }

  /* Bottom row: left=ArrowLeft, middle=0/Down, right=−/Right */
  #mobile-controls .combo-pad .btn[data-area="left"]  { grid-area: left; }
  #mobile-controls .combo-pad .btn[data-area="d0"]    { grid-area: d0; }
  #mobile-controls .combo-pad .btn[data-area="minus"] { grid-area: minus; }

  /* Fullscreen button bottom-right */
  #mobile-controls .fs-float {
    position: fixed; right: 16px; bottom: 16px; z-index: 2147483647; pointer-events: auto;
  }
  #mobile-controls .fs-float .btn { width: var(--btn-size); height: var(--btn-size); }

  /* Play gate overlay: centered tappable area that guarantees 1st user gesture */
  #mobile-controls .play-gate {
    position: fixed; inset: 0; display: grid; place-items: center;
    pointer-events: auto; /* must receive the gesture */
    background: var(--gate-bg);
    transition: opacity .25s ease;
  }
  #mobile-controls .play-gate.hidden { opacity: 0; pointer-events: none; display: none; }

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

  /* Keep canvas absolute for pygbag preloader; our overlay floats above it */
  canvas#canvas {
    z-index: 5 !important; position: absolute !important; top: 0; left: 0; right: 0; bottom: 0;
  }
</style>

<div id="mobile-controls" aria-hidden="true">
  <!-- Play-gate sits on top until first interaction -->
  <div class="play-gate" id="play-gate">
    <div class="ring">Play</div>
  </div>

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
    <div class="btn is-arrow" data-area="d8"     data-digit="8" data-arrow="ArrowUp">▲ 8</div>
    <div class="btn" data-area="d9"     data-digit="9">9</div>
    <div class="btn" data-area="keyEnter" data-key="Enter">⏎</div>

    <div class="btn is-arrow" data-area="left"  data-arrow="ArrowLeft">◀︎</div>
    <div class="btn is-arrow" data-area="d0"    data-digit="0" data-arrow="ArrowDown">▼ 0</div>
    <div class="btn is-arrow" data-area="minus" data-char="−"  data-arrow="ArrowRight">− ▶︎</div>
  </div>

  <div class="fs-float"><div class="btn" data-action="fs" title="Fullscreen">⤢</div></div>
</div>

<script>
  (function () {
    function ready(fn){
      if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', fn, { once: true }); }
      else { fn(); }
    }

    ready(function initMobileControls() {
      const root = document.getElementById('mobile-controls');
      if (!root) return;

      function applyVisible() {
        root.style.setProperty('z-index', '2147483647', 'important');
        root.style.setProperty('visibility', 'visible', 'important');
        root.style.setProperty('opacity', '1', 'important');
        root.style.setProperty('display', 'block', 'important');
      }
      function canvasOrWindow() { return document.querySelector('canvas') || window; }

      // Make buttons clickable
      root.querySelectorAll('.btn').forEach(b => { b.style.pointerEvents = 'auto'; });

      // Stick to a simple, robust mobile detection (computed once)
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

      // Show overlay based on device: full pad on mobile, FS-only on desktop
      function evaluate() {
        try {
          const isMob = computeMobileSticky();
          if (isMob) {
            root.classList.remove('only-fs');  // show full control pad
          } else {
            root.classList.add('only-fs');     // desktop: FS button only
          }
          applyVisible();
        } catch(e) {
          root.classList.add('only-fs');
          applyVisible();
        }
      }

      // Play gate logic
      function dispatchEnterOnce() {
        const target = canvasOrWindow();
        const down = new KeyboardEvent('keydown', { key:'Enter', code:'Enter', bubbles:true, cancelable:true });
        const up   = new KeyboardEvent('keyup',   { key:'Enter', code:'Enter', bubbles:true, cancelable:true });
        target.dispatchEvent(down);
        setTimeout(()=>target.dispatchEvent(up), 10);
      }
      function hintUME() {
        try {
          if (window.MM && typeof window.MM.unlock === 'function') { try { window.MM.unlock(); } catch(e){} }
          if (window.python && (window.python.run || window.python.eval)) {
            (window.python.run || window.python.eval).call(window.python, "0");
          } else if (window.pyodide?.runPython) {
            window.pyodide.runPython("0");
          }
        } catch(e){}
      }
      const gate = document.getElementById('play-gate');
      function closeGate() {
        if (!gate || gate.classList.contains('hidden')) return;
        gate.classList.add('hidden');
        applyVisible();
        try { document.querySelector('canvas')?.focus?.({preventScroll:true}); } catch(e){}
        dispatchEnterOnce();
        hintUME();
      }
      ['touchstart','click','keydown'].forEach(ev=>{
        (ev === 'keydown' ? window : gate).addEventListener(ev, (e)=>{
          if (ev !== 'keydown' || e.key === 'Enter' || e.key === ' ') {
            e.preventDefault?.();
            closeGate();
          }
        }, { passive: ev!=='touchstart' });
      });

      // Key helpers for pad
      const active = new Map();
      function dispatchKey(code, type) {
        const keyMap = {ArrowUp:'ArrowUp',ArrowDown:'ArrowDown',ArrowLeft:'ArrowLeft',ArrowRight:'ArrowRight',KeyF:'f',Enter:'Enter',Backspace:'Backspace'};
        const key = keyMap[code] || '';
        const evt = new KeyboardEvent(type, { key, code, bubbles:true, cancelable:true });
        canvasOrWindow().dispatchEvent(evt);
      }
      function startRepeat(code){ if(active.has(code)) return; dispatchKey(code,'keydown'); const itv=setInterval(()=>dispatchKey(code,'keydown'),55); active.set(code,itv); }
      function stopRepeat(code){ const itv=active.get(code); if(itv) clearInterval(itv); active.delete(code); dispatchKey(code,'keyup'); }
      function stopAllRepeats(){ for (const [c,i] of active){ clearInterval(i); dispatchKey(c,'keyup'); } active.clear(); }

      function bindComboBtn(el) {
        const digit = el.getAttribute('data-digit');
        const ch    = el.getAttribute('data-char');
        const key   = el.getAttribute('data-key');
        const arrow = el.getAttribute('data-arrow');

        const onDown = (e)=>{
          e.preventDefault();
          closeGate(); // first gesture closes gate
          if ((digit || ch || key) && active.size && !arrow) stopAllRepeats();
          if (digit){ const k='Digit'+String(digit); const t=canvasOrWindow();
            const d=new KeyboardEvent('keydown',{key:String(digit),code:k,bubbles:true,cancelable:true});
            const u=new KeyboardEvent('keyup',{key:String(digit),code:k,bubbles:true,cancelable:true});
            t.dispatchEvent(d); setTimeout(()=>t.dispatchEvent(u),10);
          }
          if (ch){ const t=canvasOrWindow(); const code='Minus';
            const d=new KeyboardEvent('keydown',{key:'-',code, bubbles:true,cancelable:true});
            const u=new KeyboardEvent('keyup',  {key:'-',code, bubbles:true,cancelable:true});
            t.dispatchEvent(d); setTimeout(()=>t.dispatchEvent(u),10);
          }
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
      root.querySelectorAll('.combo-pad .btn').forEach(bindComboBtn);

      // Fullscreen minimal; keep pad only on mobile, FS button only on desktop
      function isDomFS(){ return !!document.fullscreenElement; }
      function enterFS(){ try { document.querySelector('canvas')?.focus?.({preventScroll:true}); const p=document.documentElement.requestFullscreen(); p?.then?.(()=>{}).catch?.(()=>{});} catch(e){} }
      function exitFS(){ try { const p=document.exitFullscreen(); p?.then?.(()=>{}).catch?.(()=>{});} catch(e){} }

      const fsBtn = root.querySelector('.fs-float [data-action="fs"]');
      if (fsBtn) {
        const guard=(e)=>{
          e.preventDefault();
          const isMob = computeMobileSticky();
          if (isMob) root.classList.remove('only-fs'); else root.classList.add('only-fs');
          isDomFS()? exitFS() : enterFS();
          const reap=()=>applyVisible(); reap(); setTimeout(reap,50); setTimeout(reap,200);
        };
        fsBtn.addEventListener('click', guard);
        fsBtn.addEventListener('touchstart', guard, {passive:false});
      }

      document.addEventListener('fullscreenchange', ()=>{
        try {
          const isMob = computeMobileSticky();
          if (isDomFS()) { if (isMob) root.classList.remove('only-fs'); else root.classList.add('only-fs'); }
          else { if (isMob) root.classList.remove('only-fs'); else root.classList.add('only-fs'); }
        } catch(e){}
        const reap=()=>applyVisible(); reap(); setTimeout(reap,50); setTimeout(reap,200);
      }, {passive:true});

      // Keep canvas focused enough for keys
      function focusCanvasSoon(){ const c=document.querySelector('canvas'); if(!c) return; try{ c.focus({preventScroll:true}); }catch(e){} }
      setTimeout(focusCanvasSoon, 80);
      setTimeout(focusCanvasSoon, 400);
      document.addEventListener('pointerdown', focusCanvasSoon, { passive: true });

      // Initial evaluation and follow-ups
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
    markers = [("<!-- BEGIN mobile-controls -->", "<!-- END mobile-controls -->")]
    for start_tag, end_tag in markers:
        while start_tag in html and end_tag in html:
            pre = html.split(start_tag)[0]
            post = html.split(end_tag)[-1]
            html = pre + post
    return html

def ensure_doctype_top(html: str) -> str:
    # Prevent Quirks Mode: add <!DOCTYPE html> if missing at the very top
    if re.match(r'^\s*<!doctype\s+html\s*>', html, flags=re.IGNORECASE):
        return html
    return "<!DOCTYPE html>\n" + html.lstrip()

def trim_debug_iframe_allow(html: str) -> str:
    # Reduce verbose allow list on pygbag’s internal debug iframe (id="iframe")
    def repl(m):
        tag = m.group(0)
        tag = re.sub(r'allow="[^"]*"', 'allow="fullscreen; autoplay; gamepad"', tag)
        return tag
    html = re.sub(r'<iframe\b([^>]*\bid="iframe"\b[^>]*)>', repl, html, flags=re.IGNORECASE)
    return html

def main():
    if not WEB.exists() or not INDEX.exists():
        raise SystemExit("Build first: pygbag --build . (missing build/web/index.html)")

    html = INDEX.read_text(encoding="utf-8")

    # 1) Ensure <!DOCTYPE html> (avoid Quirks Mode)
    html = ensure_doctype_top(html)

    # 2) Remove any previously injected blocks
    html = remove_old_blocks(html)

    # 3) Trim internal debug iframe allow (reduce console noise)
    html = trim_debug_iframe_allow(html)

    # 4) Inject overlay snippet
    if "</body>" not in html:
        raise SystemExit("No </body> tag found in build/web/index.html")
    html = html.replace("</body>", SNIPPET + "\n</body>")

    INDEX.write_text(html, encoding="utf-8")
    print("Patched build/web/index.html: <!DOCTYPE html> Play gate + mobile-only pad injected.")

if __name__ == "__main__":
    main()
