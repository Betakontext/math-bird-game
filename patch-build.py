# Math bird | Mobile UI build patch
# For further developments visit and fork:
# https://github.com/betakontext/mathbird
# Copyright (c) 2026 Christoph Medicus
# Licensed under the MIT License

from pathlib import Path

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
  }

  @media (max-width: 820px), (max-height: 680px) {
    :root { --btn-size: 56px; --gap: 8px; }
    #mobile-controls .combo-pad { left: 12px; bottom: 12px; }
    #mobile-controls .fs-float { right: 12px; bottom: 12px; }
  }

  #mobile-controls.only-fs .combo-pad { display: none !important; }
  #mobile-controls.only-fs {
    visibility: visible !important; opacity: 1 !important; display: block !important;
  }

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

  /* Pfeil-Dualtasten heller als Standard */
  #mobile-controls .btn.is-arrow { background: var(--btn-arrow-bg); }

  /* Breath-Animation (Helligkeit) im Flugzustand – hohe Spezifität + !important */
  #mobile-controls.arrow-active .combo-pad .btn.is-arrow.pulse-on {
    animation: arrowBreath var(--pulse-duration) ease-in-out infinite !important;
  }
  @keyframes arrowBreath {
    0% {
      background-color: rgba(255,255,255,0.12);
      border-color: rgba(255,255,255,0.55);
      box-shadow: 0 0 0 rgba(255,255,255,0);
      filter: brightness(1.0);
    }
    50% {
      background-color: rgba(255,255,255,0.28);
      border-color: rgba(255,255,255,0.98);
      box-shadow: 0 0 18px rgba(255,255,255,0.45);
      filter: brightness(1.15);
    }
    100% {
      background-color: rgba(255,255,255,0.12);
      border-color: rgba(255,255,255,0.55);
      box-shadow: 0 0 0 rgba(255,255,255,0);
      filter: brightness(1.0);
    }
  }

  /* Kombi-Pad unten links (4x4) */
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

  /* Untere Reihe: Links = ArrowLeft (ohne Plus-Eingabe), Mitte = 0/Down, Rechts = −/Right */
  #mobile-controls .combo-pad .btn[data-area="left"]  { grid-area: left; }
  #mobile-controls .combo-pad .btn[data-area="d0"]    { grid-area: d0; }
  #mobile-controls .combo-pad .btn[data-area="minus"] { grid-area: minus; }

  /* Fullscreen unten rechts */
  #mobile-controls .fs-float {
    position: fixed; right: 16px; bottom: 16px; z-index: 2147483647; pointer-events: auto;
  }
  #mobile-controls .fs-float .btn { width: var(--btn-size); height: var(--btn-size); }

  canvas#canvas {
    z-index: 5 !important; position: absolute !important; top: 0; left: 0; right: 0; bottom: 0;
  }
</style>

<div id="mobile-controls" aria-hidden="true">
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

    <!-- Linker Pfeil: KEINE Plus-Eingabe mehr, nur noch ArrowLeft -->
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

      // Bridge
      function pyCall(expr){
        let ok = false;
        try {
          if (window.python && (window.python.run || window.python.eval)) {
            (window.python.run || window.python.eval).call(window.python, expr); ok = true;
          }
        } catch(e){}
        if (!ok) try { if (window.pyodide?.runPython) { window.pyodide.runPython(expr); ok = true; } } catch(e){}
        return ok;
      }

      function hardMute() {
        let hit = false;
        try { hit = pyCall("stop_all_audio()") || hit; } catch(e){}
        try { hit = pyCall("import pygame; pygame.mixer.stop()") || hit; } catch(e){}
        try { hit = pyCall("import pygame; [pygame.mixer.Channel(i).stop() for i in range(32)]") || hit; } catch(e){}
        return hit;
      }

      root.querySelectorAll('.btn').forEach(b => { b.style.pointerEvents = 'auto'; });

      function getQS(name, def=null){
        try { const qs = new URLSearchParams(location.search); return qs.has(name) ? qs.get(name) : def; } catch { return def; }
      }
      function applyVisible() {
        root.style.setProperty('z-index', '2147483647', 'important');
        root.style.setProperty('visibility', 'visible', 'important');
        root.style.setProperty('opacity', '1', 'important');
        root.style.setProperty('display', 'block', 'important');
      }

      function isMobileLike() {
        const ua = (navigator.userAgent || '').toLowerCase();
        const isAndroid = /android/.test(ua);
        const isIOS = /iphone|ipad|ipod/.test(ua);
        const isMobileUA = /mobile/.test(ua) || isAndroid || isIOS;
        const hasTouch = (('ontouchstart' in window) || (navigator.maxTouchPoints||0) > 0 || (navigator.msMaxTouchPoints||0) > 0);
        let pointerCoarse=false, pointerFine=false;
        try { pointerCoarse = matchMedia('(pointer: coarse)').matches; pointerFine = matchMedia('(pointer: fine)').matches; } catch(e){}
        const w = Math.min(innerWidth||0, document.documentElement.clientWidth||0);
        const h = Math.min(innerHeight||0, document.documentElement.clientHeight||0);
        const shorter = Math.min(w||0, h||0);
        const smallViewport = shorter > 0 && shorter <= 900;
        if (isAndroid || isIOS) return true;
        if (hasTouch && (pointerCoarse || (!pointerFine && smallViewport))) return true;
        if (isMobileUA && (hasTouch || pointerCoarse || smallViewport)) return true;
        return false;
      }

      let mobileSticky = null;
      function evaluate() {
        try {
          const forceMobile = getQS('forceMobile') === '1' || getQS('forceMobile') === 'true';
          const forceFS     = getQS('forceFS') === '1'     || getQS('forceFS') === 'true';
          if (mobileSticky === null) mobileSticky = isMobileLike();
          root.classList.remove('only-fs');
          if (forceMobile || mobileSticky) { applyVisible(); return; }
          if (forceFS) { root.classList.add('only-fs'); applyVisible(); return; }
          root.classList.add('only-fs'); applyVisible();
        } catch(e) { root.classList.add('only-fs'); applyVisible(); }
      }

      function canvasOrWindow() { return document.querySelector('canvas') || window; }

      // Key dispatch helpers
      function dispatchKey(code, type) {
        const map = {
          'ArrowUp':'ArrowUp','ArrowDown':'ArrowDown','ArrowLeft':'ArrowLeft','ArrowRight':'ArrowRight',
          'KeyF':'f','KeyR':'r','KeyQ':'q','Enter':'Enter','Escape':'Escape','Backspace':'Backspace'
        };
        const key = map[code] || '';
        const evt = new KeyboardEvent(type, { key, code, bubbles:true, cancelable:true });
        canvasOrWindow().dispatchEvent(evt);
      }

      function dispatchKeyCombo(key, code, opts) {
        const target = canvasOrWindow();
        const down = new KeyboardEvent('keydown', { key, code, ...opts, bubbles:true, cancelable:true });
        const up   = new KeyboardEvent('keyup',   { key, code, ...opts, bubbles:true, cancelable:true });
        target.dispatchEvent(down);
        setTimeout(()=>target.dispatchEvent(up), 10);
      }

      function dispatchDigitOnce(d) { dispatchKeyCombo(String(d), 'Digit'+String(d), {}); }

      // Plus ist entfernt; Minus bleibt für negative Resultate
      function dispatchCharOnce(ch) {
        const mapping = {
          '-': { key: '-', code: 'Minus',  shiftKey: false },
          '−': { key: '-', code: 'Minus',  shiftKey: false }
        };
        const m = mapping[ch]; if (!m) return;
        dispatchKeyCombo(m.key, m.code, { shiftKey: !!m.shiftKey });
      }

      function dispatchBackspaceOnce() { dispatchKeyCombo('Backspace', 'Backspace', {}); }

      // Arrow repeat
      const active = new Map();
      function startRepeat(code) {
        if (active.has(code)) return;
        dispatchKey(code, 'keydown');
        const itv = setInterval(()=>dispatchKey(code, 'keydown'), 55);
        active.set(code, itv);
      }
      function stopRepeat(code) {
        const itv = active.get(code);
        if (itv) clearInterval(itv);
        active.delete(code);
        dispatchKey(code, 'keyup');
      }
      function stopAllRepeats() {
        for (const [code, itv] of active.entries()) { clearInterval(itv); dispatchKey(code, 'keyup'); }
        active.clear();
      }

      // Bindings
      function bindComboBtn(el) {
        const digit = el.getAttribute('data-digit');
        const ch    = el.getAttribute('data-char');
        const key   = el.getAttribute('data-key');     // Enter/Backspace/KeyF
        const arrow = el.getAttribute('data-arrow');   // ArrowUp etc.

        const onDown = (e) => {
          e.preventDefault();
          if ((digit || ch || key) && active.size && !arrow) stopAllRepeats();

          if (digit) dispatchDigitOnce(digit);
          if (ch)    dispatchCharOnce(ch);
          if (key) {
            dispatchKey(key, 'keydown');
            if (key === 'Backspace' || key === 'KeyF') setTimeout(()=>dispatchKey(key,'keyup'), 10);
          }

          if (arrow) startRepeat(arrow);
        };

        const onUp = (e) => {
          e.preventDefault();
          if (key && key !== 'Backspace' && key !== 'KeyF') dispatchKey(key, 'keyup');
          if (arrow) stopRepeat(arrow);
        };

        el.addEventListener('touchstart', onDown, {passive:false});
        el.addEventListener('touchend',   onUp,   {passive:false});
        el.addEventListener('touchcancel',onUp,   {passive:false});
        el.addEventListener('mousedown',  onDown);
        el.addEventListener('mouseup',    onUp);
        el.addEventListener('mouseleave', onUp);
      }
      root.querySelectorAll('.combo-pad .btn').forEach(bindComboBtn);

      // Fullscreen
      function isDomFS(){ return !!document.fullscreenElement; }
      function enterFS(){ try { const p=document.documentElement.requestFullscreen(); p?.then?.(()=>{}).catch?.(()=>{}); } catch(e){} }
      function exitFS(){ try { const p=document.exitFullscreen(); p?.then?.(()=>{}).catch?.(()=>{}); } catch(e){} }
      const fsBtn = root.querySelector('.fs-float [data-action="fs"]');
      if (fsBtn) {
        const guard = (e)=>{ e.preventDefault(); applyVisible(); try { if (isMobileLike()) root.classList.remove('only-fs'); } catch(e){}; isDomFS()? exitFS() : enterFS(); };
        fsBtn.addEventListener('click', guard); fsBtn.addEventListener('touchstart', guard, {passive:false});
      }
      document.addEventListener('fullscreenchange', ()=>{ try { evaluate(); } catch(e){}; applyVisible(); setTimeout(applyVisible,50); setTimeout(applyVisible,200); }, {passive:true});

      // Canvas-Fokus
      function focusCanvasSoon() {
        const c = document.querySelector('canvas');
        if (!c) return;
        try { c.focus({preventScroll:true}); } catch(e){}
      }
      setTimeout(focusCanvasSoon, 80);
      setTimeout(focusCanvasSoon, 400);
      document.addEventListener('pointerdown', focusCanvasSoon, { passive: true });

      // Pfeil-Buttons sammeln für Pulse-Steuerung
      const arrowBtns = Array.from(root.querySelectorAll('.btn.is-arrow'));
      function enablePulse() {
        root.classList.add('arrow-active');
        arrowBtns.forEach(b => {
          b.classList.add('pulse-on');
          b.style.animation = 'arrowBreath var(--pulse-duration) ease-in-out infinite';
        });
        void root.offsetHeight; // reflow
      }
      function disablePulse() {
        root.classList.remove('arrow-active');
        arrowBtns.forEach(b => {
          b.classList.remove('pulse-on');
          b.style.animation = '';
        });
        stopAllRepeats();
      }

      // Heuristiken/Fallbacks für Standalone
      let maybePlay = false;
      let statePlayAcknowledged = False = false; // harmless alias

      // Fallback: wenn keine State-Message, dann nach 2.2s vorsichtig aktivieren
      setTimeout(() => {
        if (!statePlayAcknowledged) {
          enablePulse();
          maybePlay = true;
        }
      }, 2200);

      // Messages: State + ACK
      const DEBUG_PULSE = false;
      window.addEventListener('message', (evt) => {
        try {
          const data = evt?.data || {};
          if (!data || !data.type) return;

          if (data.type === 'game_state' || data.type === 'game_state_self') {
            const st = data.state || '';
            if (DEBUG_PULSE) console.log('[mobile-controls] game_state:', st);
            if (st === 'play') {
              statePlayAcknowledged = true;
              maybePlay = true;
              enablePulse();
            } else {
              statePlayAcknowledged = false;
              maybePlay = false;
              disablePulse();
            }
            return;
          }

          const reply = (note) => { try { evt.source?.postMessage({ type: 'game_ack', ok: true, note }, '*'); } catch(e){} };

          if (data.type === 'pause_audio') {
            hardMute(); setTimeout(hardMute, 40); setTimeout(hardMute, 140);
            setTimeout(() => reply('audio_stopped'), 160);
            return;
          }
          if (data.type === 'close_game' || data.type === 'reset_game') {
            hardMute();
            setTimeout(() => { try { pyCall("reset_to_boot()"); } catch(e){}; reply('reset_done'); }, 60);
            return;
          }
        } catch(e){}
      });

      // Bei Pfeilinteraktion Puls sicher anzeigen (falls State-Heuristik aktiv)
      function pulseOnArrowInteraction() {
        if (!statePlayAcknowledged && !maybePlay) return;
        enablePulse();
      }
      arrowBtns.forEach(b => {
        b.addEventListener('touchstart', pulseOnArrowInteraction, {passive:false});
        b.addEventListener('mousedown',  pulseOnArrowInteraction);
      });

      // Init
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
    markers = [
        ("<!-- BEGIN mobile-controls -->", "<!-- END mobile-controls -->"),
    ]
    for start_tag, end_tag in markers:
        while start_tag in html and end_tag in html:
            pre = html.split(start_tag)[0]
            post = html.split(end_tag)[-1]
            html = pre + post
    return html

def main():
    if not WEB.exists() or not INDEX.exists():
        raise SystemExit("Build first: pygbag --build . (missing build/web/index.html)")

    html = INDEX.read_text(encoding="utf-8")
    html = remove_old_blocks(html)

    if "</body>" not in html:
        raise SystemExit("No </body> tag found in build/web/index.html")

    html = html.replace("</body>", SNIPPET + "\n</body>")
    INDEX.write_text(html, encoding="utf-8")
    print("Patched build/web/index.html with arrow breath pulse (play-only, robust), left arrow kept (no plus), input/focus fixes, bridge/mute/ack.")

if __name__ == "__main__":
    main()
