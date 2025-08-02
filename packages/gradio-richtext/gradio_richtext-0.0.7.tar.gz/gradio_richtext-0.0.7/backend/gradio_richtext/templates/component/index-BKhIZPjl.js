const a = document.createElement("i");
function o(r) {
  const t = "&" + r + ";";
  a.innerHTML = t;
  const e = a.textContent;
  return (
    // @ts-expect-error: TypeScript is wrong that `textContent` on elements can
    // yield `null`.
    e.charCodeAt(e.length - 1) === 59 && r !== "semi" || e === t ? !1 : e
  );
}
function d(r, t) {
  const e = Number.parseInt(r, t);
  return (
    // C0 except for HT, LF, FF, CR, space.
    e < 9 || e === 11 || e > 13 && e < 32 || // Control character (DEL) of C0, and C1 controls.
    e > 126 && e < 160 || // Lone high surrogates and low surrogates.
    e > 55295 && e < 57344 || // Noncharacters.
    e > 64975 && e < 65008 || /* eslint-disable no-bitwise */
    (e & 65535) === 65535 || (e & 65535) === 65534 || /* eslint-enable no-bitwise */
    // Out of range
    e > 1114111 ? "�" : String.fromCodePoint(e)
  );
}
const i = /\\([!-/:-@[-`{-~])|&(#(?:\d{1,7}|x[\da-f]{1,6})|[\da-z]{1,31});/gi;
function u(r) {
  return r.replace(i, s);
}
function s(r, t, e) {
  if (t)
    return t;
  if (e.charCodeAt(0) === 35) {
    const n = e.charCodeAt(1), c = n === 120 || n === 88;
    return d(e.slice(c ? 2 : 1), c ? 16 : 10);
  }
  return o(e) || r;
}
export {
  o as a,
  d as b,
  u as d
};
