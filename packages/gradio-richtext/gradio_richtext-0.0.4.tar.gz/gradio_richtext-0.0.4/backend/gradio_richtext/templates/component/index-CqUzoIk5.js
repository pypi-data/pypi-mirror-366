import { c as w } from "./index-DPVDNjDQ.js";
import { w as N } from "./index-qIqGBAea.js";
const l = (
  // Note: overloads in JSDoc can’t yet use different `@template`s.
  /**
   * @type {(
   *   (<Condition extends TestFunction>(element: unknown, test: Condition, index?: number | null | undefined, parent?: Parents | null | undefined, context?: unknown) => element is Element & Predicate<Condition, Element>) &
   *   (<Condition extends string>(element: unknown, test: Condition, index?: number | null | undefined, parent?: Parents | null | undefined, context?: unknown) => element is Element & {tagName: Condition}) &
   *   ((element?: null | undefined) => false) &
   *   ((element: unknown, test?: null | undefined, index?: number | null | undefined, parent?: Parents | null | undefined, context?: unknown) => element is Element) &
   *   ((element: unknown, test?: Test, index?: number | null | undefined, parent?: Parents | null | undefined, context?: unknown) => boolean)
   * )}
   */
  /**
   * @param {unknown} [element]
   * @param {Test | undefined} [test]
   * @param {number | null | undefined} [index]
   * @param {Parents | null | undefined} [parent]
   * @param {unknown} [context]
   * @returns {boolean}
   */
  // eslint-disable-next-line max-params
  function(e, t, r, i, n) {
    const a = c(t);
    return m(e) ? a.call(n, e, r, i) : !1;
  }
), c = (
  // Note: overloads in JSDoc can’t yet use different `@template`s.
  /**
   * @type {(
   *   (<Condition extends TestFunction>(test: Condition) => (element: unknown, index?: number | null | undefined, parent?: Parents | null | undefined, context?: unknown) => element is Element & Predicate<Condition, Element>) &
   *   (<Condition extends string>(test: Condition) => (element: unknown, index?: number | null | undefined, parent?: Parents | null | undefined, context?: unknown) => element is Element & {tagName: Condition}) &
   *   ((test?: null | undefined) => (element?: unknown, index?: number | null | undefined, parent?: Parents | null | undefined, context?: unknown) => element is Element) &
   *   ((test?: Test) => Check)
   * )}
   */
  /**
   * @param {Test | null | undefined} [test]
   * @returns {Check}
   */
  function(e) {
    if (e == null)
      return v;
    if (typeof e == "string")
      return x(e);
    if (typeof e == "object")
      return k(e);
    if (typeof e == "function")
      return p(e);
    throw new Error("Expected function, string, or array as `test`");
  }
);
function k(e) {
  const t = [];
  let r = -1;
  for (; ++r < e.length; )
    t[r] = c(e[r]);
  return p(i);
  function i(...n) {
    let a = -1;
    for (; ++a < t.length; )
      if (t[a].apply(this, n)) return !0;
    return !1;
  }
}
function x(e) {
  return p(t);
  function t(r) {
    return r.tagName === e;
  }
}
function p(e) {
  return t;
  function t(r, i, n) {
    return !!(m(r) && e.call(
      this,
      r,
      typeof i == "number" ? i : void 0,
      n || void 0
    ));
  }
}
function v(e) {
  return !!(e && typeof e == "object" && "type" in e && e.type === "element" && "tagName" in e && typeof e.tagName == "string");
}
function m(e) {
  return e !== null && typeof e == "object" && "type" in e && "tagName" in e;
}
const h = c(
  /**
   * @param element
   * @returns {element is {tagName: 'audio' | 'canvas' | 'embed' | 'iframe' | 'img' | 'math' | 'object' | 'picture' | 'svg' | 'video'}}
   */
  function(e) {
    return e.tagName === "audio" || e.tagName === "canvas" || e.tagName === "embed" || e.tagName === "iframe" || e.tagName === "img" || e.tagName === "math" || e.tagName === "object" || e.tagName === "picture" || e.tagName === "svg" || e.tagName === "video";
  }
), A = [
  "address",
  // Flow content.
  "article",
  // Sections and headings.
  "aside",
  // Sections and headings.
  "blockquote",
  // Flow content.
  "body",
  // Page.
  "br",
  // Contribute whitespace intrinsically.
  "caption",
  // Similar to block.
  "center",
  // Flow content, legacy.
  "col",
  // Similar to block.
  "colgroup",
  // Similar to block.
  "dd",
  // Lists.
  "dialog",
  // Flow content.
  "dir",
  // Lists, legacy.
  "div",
  // Flow content.
  "dl",
  // Lists.
  "dt",
  // Lists.
  "figcaption",
  // Flow content.
  "figure",
  // Flow content.
  "footer",
  // Flow content.
  "form",
  // Flow content.
  "h1",
  // Sections and headings.
  "h2",
  // Sections and headings.
  "h3",
  // Sections and headings.
  "h4",
  // Sections and headings.
  "h5",
  // Sections and headings.
  "h6",
  // Sections and headings.
  "head",
  // Page.
  "header",
  // Flow content.
  "hgroup",
  // Sections and headings.
  "hr",
  // Flow content.
  "html",
  // Page.
  "legend",
  // Flow content.
  "li",
  // Block-like.
  "li",
  // Similar to block.
  "listing",
  // Flow content, legacy
  "main",
  // Flow content.
  "menu",
  // Lists.
  "nav",
  // Sections and headings.
  "ol",
  // Lists.
  "optgroup",
  // Similar to block.
  "option",
  // Similar to block.
  "p",
  // Flow content.
  "plaintext",
  // Flow content, legacy
  "pre",
  // Flow content.
  "section",
  // Sections and headings.
  "summary",
  // Similar to block.
  "table",
  // Similar to block.
  "tbody",
  // Similar to block.
  "td",
  // Block-like.
  "td",
  // Similar to block.
  "tfoot",
  // Similar to block.
  "th",
  // Block-like.
  "th",
  // Similar to block.
  "thead",
  // Similar to block.
  "tr",
  // Similar to block.
  "ul",
  // Lists.
  "wbr",
  // Contribute whitespace intrinsically.
  "xmp"
  // Flow content, legacy
], S = [
  // Form.
  "button",
  "input",
  "select",
  "textarea"
], B = [
  "area",
  "base",
  "basefont",
  "dialog",
  "datalist",
  "head",
  "link",
  "meta",
  "noembed",
  "noframes",
  "param",
  "rp",
  "script",
  "source",
  "style",
  "template",
  "track",
  "title"
], E = {}, f = w(["comment", "doctype"]);
function K(e, t) {
  g(e, {
    collapse: L(
      (t || E).newlines ? O : q
    ),
    whitespace: "normal"
  });
}
function g(e, t) {
  if ("children" in e) {
    const r = { ...t };
    return (e.type === "root" || d(e)) && (r.before = !0, r.after = !0), r.whitespace = $(e, t), F(e, r);
  }
  if (e.type === "text") {
    if (t.whitespace === "normal")
      return j(e, t);
    t.whitespace === "nowrap" && (e.value = t.collapse(e.value));
  }
  return { ignore: f(e), stripAtStart: !1, remove: !1 };
}
function j(e, t) {
  const r = t.collapse(e.value), i = { ignore: !1, stripAtStart: !1, remove: !1 };
  let n = 0, a = r.length;
  return t.before && u(r.charAt(0)) && n++, n !== a && u(r.charAt(a - 1)) && (t.after ? a-- : i.stripAtStart = !0), n === a ? i.remove = !0 : e.value = r.slice(n, a), i;
}
function F(e, t) {
  let r = t.before;
  const i = t.after, n = e.children;
  let a = n.length, o = -1;
  for (; ++o < a; ) {
    const s = g(n[o], {
      ...t,
      after: y(n, o, i),
      before: r
    });
    s.remove ? (n.splice(o, 1), o--, a--) : s.ignore || (r = s.stripAtStart), b(n[o]) && (r = !1);
  }
  return { ignore: !1, stripAtStart: !!(r || i), remove: !1 };
}
function y(e, t, r) {
  for (; ++t < e.length; ) {
    const i = e[t];
    let n = P(i);
    if (n === void 0 && "children" in i && !W(i) && (n = y(i.children, -1)), typeof n == "boolean")
      return n;
  }
  return r;
}
function P(e) {
  if (e.type === "element") {
    if (b(e))
      return !1;
    if (d(e))
      return !0;
  } else if (e.type === "text") {
    if (!N(e))
      return !1;
  } else if (!f(e))
    return !1;
}
function b(e) {
  return h(e) || l(e, S);
}
function d(e) {
  return l(e, A);
}
function W(e) {
  return !!(e.type === "element" && e.properties.hidden) || f(e) || l(e, B);
}
function u(e) {
  return e === " " || e === `
`;
}
function O(e) {
  const t = /\r?\n|\r/.exec(e);
  return t ? t[0] : " ";
}
function q() {
  return " ";
}
function L(e) {
  return t;
  function t(r) {
    return String(r).replace(/[\t\n\v\f\r ]+/g, e);
  }
}
function $(e, t) {
  if ("tagName" in e && e.properties)
    switch (e.tagName) {
      case "listing":
      case "plaintext":
      case "script":
      case "style":
      case "xmp":
        return "pre";
      case "nobr":
        return "nowrap";
      case "pre":
        return e.properties.wrap ? "pre-wrap" : "pre";
      case "td":
      case "th":
        return e.properties.noWrap ? "nowrap" : t.whitespace;
      case "textarea":
        return "pre-wrap";
    }
  return t.whitespace;
}
const T = {}.hasOwnProperty;
function z(e, t) {
  const r = e.type === "element" && T.call(e.properties, t) && e.properties[t];
  return r != null && r !== !1;
}
const C = /* @__PURE__ */ new Set(["pingback", "prefetch", "stylesheet"]);
function D(e) {
  if (e.type !== "element" || e.tagName !== "link")
    return !1;
  if (e.properties.itemProp)
    return !0;
  const t = e.properties.rel;
  let r = -1;
  if (!Array.isArray(t) || t.length === 0)
    return !1;
  for (; ++r < t.length; )
    if (!C.has(String(t[r])))
      return !1;
  return !0;
}
const G = c([
  "a",
  "abbr",
  // `area` is in fact only phrasing if it is inside a `map` element.
  // However, since `area`s are required to be inside a `map` element, and it’s
  // a rather involved check, it’s ignored here for now.
  "area",
  "b",
  "bdi",
  "bdo",
  "br",
  "button",
  "cite",
  "code",
  "data",
  "datalist",
  "del",
  "dfn",
  "em",
  "i",
  "input",
  "ins",
  "kbd",
  "keygen",
  "label",
  "map",
  "mark",
  "meter",
  "noscript",
  "output",
  "progress",
  "q",
  "ruby",
  "s",
  "samp",
  "script",
  "select",
  "small",
  "span",
  "strong",
  "sub",
  "sup",
  "template",
  "textarea",
  "time",
  "u",
  "var",
  "wbr"
]), H = c("meta");
function M(e) {
  return !!(e.type === "text" || G(e) || h(e) || D(e) || H(e) && z(e, "itemProp"));
}
export {
  c,
  h as e,
  K as m,
  M as p
};
