// Swaps every <img src="/logo.svg"> for an inline SVG so Suki's ears can wiggle slowly on their own.
// The ears are not separate shapes: the head outline is redrawn each frame with only the ear points
// moved, so the line can never come apart from the head. Her eyes never move.
// Without JavaScript (or with reduced motion) the image stays as it is.
(async () => {
  const text = await fetch("/logo.svg").then((r) => r.text()).catch(() => null);
  if (!text || !text.includes('class="head"')) return;

  // The outline, point by point: [x, y, ear, weight]. Points without an ear stay fixed; the weight
  // says how much of the ear's rotation a point follows, so the base of each ear barely moves.
  const SEG = [
    ["M", [[19, 58]]],
    ["C", [[15, 44, "l", 0.3], [15, 28, "l", 0.8], [21, 10, "l", 1]]],
    ["C", [[22, 7.5, "l", 1], [25, 7.2, "l", 1], [27, 8.8, "l", 1]]],
    ["L", [[45, 24]]],
    ["C", [[54, 21.5], [66, 21.8], [75, 24.5]]],
    ["L", [[88, 15, "r", 1]]],
    ["L", [[90.4, 13.2, "r", 1]]],
    ["L", [[91.8, 20, "r", 1]]],
    ["L", [[96.8, 14.6, "r", 1]]],
    ["L", [[98.2, 21.2, "r", 1]]],
    ["C", [[101, 30, "r", 0.8], [102.5, 44, "r", 0.3], [100.5, 56]]],
    ["C", [[106, 63], [108, 73], [104, 82]]],
    ["C", [[97, 100], [79, 107.5], [61, 107.5]]],
    ["S", [[24, 100], [17, 82]]],
    ["C", [[13, 72], [14, 64], [19, 58]]],
  ];
  const PIVOT = { l: [31.5, 32], r: [88, 32] };
  // A slow, steady wiggle. Each ear has its own speed, so they drift in and out of step, and a small
  // faster ripple on top keeps it from looking like a metronome.
  const AMP = { l: 12, r: 10 }; // degrees
  const PERIOD = { l: 3.9, r: 4.9 }; // seconds for one full wiggle
  const PHASE = { l: 0, r: 1.7 };
  const angle = (side, t) => {
    const w = (2 * Math.PI * t) / PERIOD[side];
    return (AMP[side] * (Math.sin(w + PHASE[side]) + 0.25 * Math.sin(2.7 * w + 1.1))) / 1.25;
  };

  const num = (n) => Math.round(n * 100) / 100;
  function outline(a) {
    const rot = {};
    for (const side of ["l", "r"]) {
      const t = (a[side] * Math.PI) / 180;
      rot[side] = [Math.cos(t), Math.sin(t)];
    }
    const move = ([x, y, side, w]) => {
      if (!side || !w) return `${num(x)} ${num(y)}`;
      const [px, py] = PIVOT[side];
      const [c, s] = rot[side];
      const rx = px + (x - px) * c - (y - py) * s;
      const ry = py + (x - px) * s + (y - py) * c;
      return `${num(x + w * (rx - x))} ${num(y + w * (ry - y))}`;
    };
    return SEG.map(([cmd, pts]) => `${cmd} ${pts.map(move).join(" ")}`).join(" ") + " Z";
  }

  const sukis = new Set();
  const still = matchMedia("(prefers-reduced-motion: reduce)").matches;

  function upgrade(img) {
    const tpl = document.createElement("template");
    tpl.innerHTML = text.trim();
    const svg = tpl.content.firstElementChild;
    const size = img.getAttribute("width") || "48";
    svg.setAttribute("width", size);
    svg.setAttribute("height", img.getAttribute("height") || size);
    svg.setAttribute("class", "suki");
    svg.setAttribute("aria-hidden", "true");
    svg.removeAttribute("role");
    svg.removeAttribute("aria-label");
    img.replaceWith(svg);
    sukis.add({
      svg,
      heads: [...svg.querySelectorAll(".head")],
      hatch: { l: svg.querySelector('.hatch[data-side="l"]'), r: svg.querySelector('.hatch[data-side="r"]') },
    });
  }

  const scan = (root) => {
    if (root.matches?.('img[src="/logo.svg"]')) upgrade(root);
    root.querySelectorAll?.('img[src="/logo.svg"]').forEach(upgrade);
  };
  scan(document);
  new MutationObserver((muts) => muts.forEach((m) => m.addedNodes.forEach((n) => n.nodeType === 1 && scan(n)))).observe(document.body, { childList: true, subtree: true });

  if (still) return;

  function frame(now) {
    const t = now / 1000;
    const a = { l: angle("l", t), r: angle("r", t) };
    const d = outline(a);
    for (const s of sukis) {
      if (!s.svg.isConnected) {
        sukis.delete(s);
        continue;
      }
      s.heads.forEach((p) => p.setAttribute("d", d));
      for (const side of ["l", "r"]) {
        const [px, py] = PIVOT[side];
        s.hatch[side]?.setAttribute("transform", `rotate(${num(a[side])} ${px} ${py})`);
      }
    }
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
})();
