import { w as a, s as l, h as N } from "./index-DGhvCri1.js";
function b(t, e) {
  return i(t, e || {}) || { type: "root", children: [] };
}
function i(t, e) {
  const n = h(t, e);
  return n && e.afterTransform && e.afterTransform(t, n), n;
}
function h(t, e) {
  switch (t.nodeType) {
    case 1:
      return w(
        /** @type {Element} */
        t,
        e
      );
    case 3:
      return g(
        /** @type {Text} */
        t
      );
    case 8:
      return y(
        /** @type {Comment} */
        t
      );
    case 9:
      return d(
        /** @type {Document} */
        t,
        e
      );
    case 10:
      return p();
    case 11:
      return d(
        /** @type {DocumentFragment} */
        t,
        e
      );
    default:
      return;
  }
}
function d(t, e) {
  return { type: "root", children: f(t, e) };
}
function p() {
  return { type: "doctype" };
}
function g(t) {
  return { type: "text", value: t.nodeValue || "" };
}
function y(t) {
  return { type: "comment", value: t.nodeValue || "" };
}
function w(t, e) {
  const n = t.namespaceURI, o = n === a.svg ? l : N, r = n === a.html ? t.tagName.toLowerCase() : t.tagName, c = (
    // @ts-expect-error: DOM types are wrong, content can exist.
    n === a.html && r === "template" ? t.content : t
  ), s = t.getAttributeNames(), m = {};
  let u = -1;
  for (; ++u < s.length; )
    m[s[u]] = t.getAttribute(s[u]) || "";
  return o(r, m, f(c, e));
}
function f(t, e) {
  const n = t.childNodes, o = [];
  let r = -1;
  for (; ++r < n.length; ) {
    const c = i(n[r], e);
    c !== void 0 && o.push(c);
  }
  return o;
}
export {
  b as fromDom
};
