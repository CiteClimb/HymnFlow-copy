(() => {
  const overlayEl = document.getElementById('overlay');
  const titleBarEl = document.getElementById('titleBar');
  const contentEl = document.getElementById('content');
  const STORAGE_KEY = 'hymnflow-lowerthird-command';
  const TEXTSLIDE_KEY = 'hymnflow-textslide-command';
  let isVisible = false;

  const HEX_COLOR = /^#[0-9a-fA-F]{6}$/;
  function safeColor(val, fallback) {
    return HEX_COLOR.test(val) ? val : fallback;
  }

  const FONT_ALLOWLIST = new Set([
    'Inter, sans-serif',
    "'Segoe UI', sans-serif",
    "'Roboto', sans-serif",
    "'Georgia', serif",
    "'Times New Roman', serif",
    "'Montserrat', sans-serif",
  ]);
  function safeFont(val) {
    return FONT_ALLOWLIST.has(val) ? val : 'Inter, sans-serif';
  }

  // Serif stack for scripture prose — system fonts so it works offline (file://).
  const SCRIPTURE_FONT = "'Georgia', 'Times New Roman', serif";

  function escapeHtml(text) {
    const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
    return String(text == null ? '' : text).replace(/[&<>"']/g, (c) => map[c]);
  }

  // Hides the title bar entirely when it has no content, so empty/announce
  // slides don't render a floating styled strip.
  function syncTitleBarVisibility() {
    const hasContent = titleBarEl.textContent.trim().length > 0;
    titleBarEl.classList.toggle('empty', !hasContent);
  }

  function applyStyles(settings) {
    const s = {
      ...settings,
      textColor: safeColor(settings.textColor, '#ffffff'),
      outlineColor: safeColor(settings.outlineColor, '#000000'),
      bgColorA: safeColor(settings.bgColorA, '#000000'),
      bgColorB: safeColor(settings.bgColorB, '#000000'),
    };
    contentEl.style.fontFamily = safeFont(s.fontFamily);
    contentEl.style.fontSize = s.fontSize + 'px';
    contentEl.style.fontWeight = s.bold ? '700' : '400';
    contentEl.style.fontStyle = s.italic ? 'italic' : 'normal';
    contentEl.style.color = s.textColor;

    let shadow = '';
    if (s.shadow) shadow += '0 2px 8px rgba(0,0,0,0.8)';
    if (s.glow) shadow += (shadow ? ', ' : '') + `0 0 20px ${s.textColor}`;
    contentEl.style.textShadow = shadow;
    titleBarEl.style.textShadow = shadow;

    // Apply text outline (stroke) with fallback
    if (s.outline && s.outlineWidth > 0) {
      const strokeWidth = Math.max(1, Math.min(s.outlineWidth, 15)); // Clamp between 1-15px
      contentEl.style.webkitTextStrokeWidth = strokeWidth + 'px';
      contentEl.style.webkitTextStrokeColor = s.outlineColor;
      titleBarEl.style.webkitTextStrokeWidth = strokeWidth + 'px';
      titleBarEl.style.webkitTextStrokeColor = s.outlineColor;
      
      // Fallback: CSS text-shadow outline for browsers without webkit support
      const offsetPx = strokeWidth;
      const shadowArray = [
        `-${offsetPx}px -${offsetPx}px 0 ${s.outlineColor}`,
        `${offsetPx}px -${offsetPx}px 0 ${s.outlineColor}`,
        `-${offsetPx}px ${offsetPx}px 0 ${s.outlineColor}`,
        `${offsetPx}px ${offsetPx}px 0 ${s.outlineColor}`,
        `0px -${offsetPx}px 0 ${s.outlineColor}`,
        `0px ${offsetPx}px 0 ${s.outlineColor}`,
        `-${offsetPx}px 0px 0 ${s.outlineColor}`,
        `${offsetPx}px 0px 0 ${s.outlineColor}`
      ];
      const fallbackShadow = shadowArray.join(', ');
      
      // Preserve existing text shadow if any
      const existingShadow = contentEl.style.textShadow;
      contentEl.style.textShadow = fallbackShadow + (existingShadow ? ', ' + existingShadow : '');
      titleBarEl.style.textShadow = fallbackShadow + (titleBarEl.style.textShadow ? ', ' + titleBarEl.style.textShadow : '');
    } else {
      contentEl.style.webkitTextStrokeWidth = '0';
      titleBarEl.style.webkitTextStrokeWidth = '0';
    }

    const opacity = typeof s.bgOpacity === 'number' ? s.bgOpacity / 100 : 0.8;

    function hexToRgba(hex, alpha) {
      const r = parseInt(hex.slice(1, 3), 16);
      const g = parseInt(hex.slice(3, 5), 16);
      const b = parseInt(hex.slice(5, 7), 16);
      return `rgba(${r},${g},${b},${alpha})`;
    }

    if (s.bgType === 'transparent') {
      titleBarEl.style.background = 'transparent';
      contentEl.style.background = 'transparent';
    } else if (s.bgType === 'solid') {
      const color = hexToRgba(s.bgColorA, opacity);
      titleBarEl.style.background = color;
      contentEl.style.background = color;
    } else if (s.bgType === 'gradient') {
      const colorA = hexToRgba(s.bgColorA, opacity);
      const colorB = hexToRgba(s.bgColorB, opacity);
      const grad = `linear-gradient(135deg, ${colorA}, ${colorB})`;
      titleBarEl.style.background = grad;
      contentEl.style.background = grad;
    }

    overlayEl.className = `overlay ${s.position}`;
  }

  // Shrinks contentEl font size until the overlay fits within the viewport.
  // applyStyles() must have already set the desired base size before this is called.
  function fitTextToOverlay() {
    const MIN_PX = 16;
    const STEP   = 2;
    while (parseFloat(contentEl.style.fontSize) > MIN_PX) {
      const r = overlayEl.getBoundingClientRect();
      if (r.top >= 0 && r.bottom <= window.innerHeight) break;
      contentEl.style.fontSize = (parseFloat(contentEl.style.fontSize) - STEP) + 'px';
    }
  }

  function show(data) {
    const { title, verseNumber, totalVerses, lines, settings } = data;
    const sourceAbbr = data.metadata?.sourceAbbr || '';
    const hymnNumber = data.metadata?.number ? `${data.metadata.number}` : '';
    const hymnRef = sourceAbbr && hymnNumber
      ? `${sourceAbbr} ${hymnNumber} • `
      : hymnNumber
        ? `${hymnNumber} • `
        : '';
    
    applyStyles(settings);
    overlayEl.classList.remove('scripture');

    if (data.isChorus) {
      titleBarEl.textContent = `${hymnRef}${title} • Chorus`;
    } else {
      titleBarEl.textContent = `${hymnRef}${title} • Verse ${verseNumber}/${totalVerses}`;
    }
    syncTitleBarVisibility();

    // Ensure lines is an array and join properly
    const displayText = Array.isArray(lines) ? lines.join('\n') : String(lines);
    contentEl.textContent = displayText;
    fitTextToOverlay();

    overlayEl.classList.remove('hidden', 'fade-out', 'slide-out', 'fade-in', 'slide-in');
    overlayEl.classList.add('visible');

    if (settings.animation === 'fade' || settings.animation === 'slide') {
      // Force reflow so removing+re-adding the class restarts the CSS animation
      void overlayEl.offsetWidth;
      overlayEl.classList.add(settings.animation === 'fade' ? 'fade-in' : 'slide-in');
    }
    isVisible = true;
  }

  function hide(settings) {
    if (!isVisible) return;
    overlayEl.classList.remove('fade-in', 'slide-in');
    if (settings && settings.animation === 'fade') {
      overlayEl.classList.add('fade-out');
    } else if (settings && settings.animation === 'slide') {
      overlayEl.classList.add('slide-out');
    }
    setTimeout(() => {
      overlayEl.classList.add('hidden');
      overlayEl.classList.remove('visible', 'fade-out', 'slide-out');
    }, 600);
    isVisible = false;
  }

  function showTextSlide(data) {
    const { lines, settings } = data;
    applyStyles(settings);
    const text = Array.isArray(lines) ? lines.join('\n') : String(lines);

    // scriptureMode is an additive v2 field. Older docks omit it, in which case
    // we fall back to the plain text-slide rendering (graceful degradation).
    if (data.scriptureMode) {
      overlayEl.classList.add('scripture');
      const reference = escapeHtml(data.reference || data.title || '');
      const translation = escapeHtml(data.translation || '');
      const badge = translation
        ? `<span class="translation-badge">${translation}</span>`
        : '';
      titleBarEl.innerHTML = reference || translation
        ? `<span class="scripture-icon">📖</span><span class="scripture-reference">${reference}</span>${badge}`
        : '';
      // Serif prose look — distinct from hymn lyrics. Overrides applyStyles' font.
      contentEl.style.fontFamily = SCRIPTURE_FONT;
      contentEl.style.fontStyle = 'italic';
    } else {
      overlayEl.classList.remove('scripture');
      titleBarEl.textContent = data.title || '';
    }
    syncTitleBarVisibility();

    contentEl.textContent = text;
    fitTextToOverlay();
    overlayEl.classList.remove('hidden', 'fade-out', 'slide-out', 'fade-in', 'slide-in');
    overlayEl.classList.add('visible');
    if (settings.animation === 'fade' || settings.animation === 'slide') {
      void overlayEl.offsetWidth;
      overlayEl.classList.add(settings.animation === 'fade' ? 'fade-in' : 'slide-in');
    }
    isVisible = true;
  }

  window.addEventListener('storage', (e) => {
    if (e.key === STORAGE_KEY && e.newValue) {
      try {
        const cmd = JSON.parse(e.newValue);
        if (cmd.type === 'show') {
          show(cmd);
        } else if (cmd.type === 'hide') {
          hide(cmd.settings);
        }
      } catch (err) {
        console.error('[Overlay Storage Error]', err);
      }
    }
    if (e.key === TEXTSLIDE_KEY && e.newValue) {
      try {
        const cmd = JSON.parse(e.newValue);
        if (cmd.type === 'textslide') {
          showTextSlide(cmd);
        } else if (cmd.type === 'hide') {
          hide(cmd.settings);
        }
      } catch (err) {
        console.error('[Text Slide Storage Error]', err);
      }
    }
  });

  // Re-render the last live slide after a reload. OBS refreshes browser sources
  // on scene changes, cache clears, and GPU recovery; without this the screen
  // goes blank mid-service until the operator pushes again. We replay whichever
  // of the two command channels holds the most recent command.
  function replayLastState() {
    let latest = null;
    for (const key of [STORAGE_KEY, TEXTSLIDE_KEY]) {
      try {
        const cmd = JSON.parse(localStorage.getItem(key) || 'null');
        if (cmd && (!latest || (cmd.timestamp || 0) > (latest.timestamp || 0))) {
          latest = cmd;
        }
      } catch (err) { /* ignore malformed entry */ }
    }
    if (!latest || latest.type === 'hide') return;
    try {
      if (latest.type === 'show') show(latest);
      else if (latest.type === 'textslide') showTextSlide(latest);
    } catch (err) {
      console.error('[Overlay Replay Error]', err);
    }
  }

  // Initial state
  overlayEl.classList.add('hidden');
  replayLastState();
})();
