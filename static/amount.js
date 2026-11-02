// Reads a money amount the way people type it in Belgium: "444,00", "1.234,56", "1 234,56", "€ 444.5", "444".
// Comma is the decimal mark unless the number clearly uses a dot; a lone separator followed by exactly
// three digits is a thousands separator ("1.234" is 1234). Returns a number rounded to cents, or NaN.
function parseAmount(raw) {
  let s = String(raw ?? "").replace(/[\s  '’]/g, "").replace(/[€]|eur(os)?/gi, "");
  if (!/^[\d.,]+$/.test(s) || !/\d/.test(s)) return NaN;
  const lastComma = s.lastIndexOf(",");
  const lastDot = s.lastIndexOf(".");
  let decimal = null;
  if (lastComma !== -1 && lastDot !== -1) {
    decimal = lastComma > lastDot ? "," : "."; // the last mark is the decimal one
  } else {
    const mark = lastComma !== -1 ? "," : lastDot !== -1 ? "." : null;
    if (mark) {
      const parts = s.split(mark);
      const tail = parts[parts.length - 1];
      if (parts.length === 2 && tail.length !== 3) decimal = mark; // "444,00", "444.5"
      // otherwise: repeated marks or exactly three digits after one mark are thousands separators
    }
  }
  // Thousands groups must be well formed: one to three digits, then groups of exactly three.
  const grouped = (t) => {
    const g = t.split(/[.,]/);
    return g.length === 1 || (/^\d{1,3}$/.test(g[0]) && g.slice(1).every((x) => /^\d{3}$/.test(x)));
  };
  if (decimal) {
    const i = s.lastIndexOf(decimal);
    const wholeRaw = s.slice(0, i);
    const frac = s.slice(i + 1);
    if (/[.,]/.test(frac) || frac.length > 2 || !grouped(wholeRaw)) return NaN;
    s = `${wholeRaw.replace(/[.,]/g, "") || "0"}.${frac}`;
  } else {
    if (!grouped(s)) return NaN;
    s = s.replace(/[.,]/g, "");
  }
  const n = Math.round(Number(s) * 100) / 100;
  return Number.isFinite(n) ? n : NaN;
}

if (typeof module !== "undefined") module.exports = parseAmount;
