const s = i(/[A-Za-z]/), u = i(/[\dA-Za-z]/), c = i(/[#-'*+\--9=?A-Z^-~]/);
function r(n) {
  return (
    // Special whitespace codes (which have negative values), C0 and Control
    // character DEL
    n !== null && (n < 32 || n === 127)
  );
}
const o = i(/\d/), e = i(/[\dA-Fa-f]/), l = i(/[!-/:-@[-`{-~]/);
function f(n) {
  return n !== null && n < -2;
}
function p(n) {
  return n !== null && (n < 0 || n === 32);
}
function g(n) {
  return n === -2 || n === -1 || n === 32;
}
const h = i(new RegExp("\\p{P}|\\p{S}", "u")), A = i(/\s/);
function i(n) {
  return t;
  function t(a) {
    return a !== null && a > -1 && n.test(String.fromCharCode(a));
  }
}
export {
  h as a,
  g as b,
  f as c,
  u as d,
  s as e,
  r as f,
  c as g,
  l as h,
  e as i,
  o as j,
  p as m,
  A as u
};
