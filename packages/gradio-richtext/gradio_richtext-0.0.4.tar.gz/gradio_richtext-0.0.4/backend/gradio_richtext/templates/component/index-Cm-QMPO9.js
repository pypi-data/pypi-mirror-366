import { z as x } from "./index-qZRjazc5.js";
import { f as w, a as y, e as C, p as B, h as F } from "./index-B4gOUn38.js";
import { d as L } from "./index-BKhIZPjl.js";
const j = {}.hasOwnProperty;
function A(e, n) {
  let a = -1, t;
  if (n.extensions)
    for (; ++a < n.extensions.length; )
      A(e, n.extensions[a]);
  for (t in n)
    if (j.call(n, t))
      switch (t) {
        case "extensions":
          break;
        case "unsafe": {
          b(e[t], n[t]);
          break;
        }
        case "join": {
          b(e[t], n[t]);
          break;
        }
        case "handlers": {
          S(e[t], n[t]);
          break;
        }
        default:
          e.options[t] = n[t];
      }
  return e;
}
function b(e, n) {
  n && e.push(...n);
}
function S(e, n) {
  n && Object.assign(e, n);
}
const v = [I];
function I(e, n, a, t) {
  if (n.type === "code" && w(n, t) && (e.type === "list" || e.type === n.type && w(e, t)))
    return !1;
  if ("spread" in a && typeof a.spread == "boolean")
    return e.type === "paragraph" && // Two paragraphs.
    (e.type === n.type || n.type === "definition" || // Paragraph followed by a setext heading.
    n.type === "heading" && y(n, t)) ? void 0 : a.spread ? 1 : 0;
}
const k = [
  "autolink",
  "destinationLiteral",
  "destinationRaw",
  "reference",
  "titleQuote",
  "titleApostrophe"
], T = [
  { character: "	", after: "[\\r\\n]", inConstruct: "phrasing" },
  { character: "	", before: "[\\r\\n]", inConstruct: "phrasing" },
  {
    character: "	",
    inConstruct: ["codeFencedLangGraveAccent", "codeFencedLangTilde"]
  },
  {
    character: "\r",
    inConstruct: [
      "codeFencedLangGraveAccent",
      "codeFencedLangTilde",
      "codeFencedMetaGraveAccent",
      "codeFencedMetaTilde",
      "destinationLiteral",
      "headingAtx"
    ]
  },
  {
    character: `
`,
    inConstruct: [
      "codeFencedLangGraveAccent",
      "codeFencedLangTilde",
      "codeFencedMetaGraveAccent",
      "codeFencedMetaTilde",
      "destinationLiteral",
      "headingAtx"
    ]
  },
  { character: " ", after: "[\\r\\n]", inConstruct: "phrasing" },
  { character: " ", before: "[\\r\\n]", inConstruct: "phrasing" },
  {
    character: " ",
    inConstruct: ["codeFencedLangGraveAccent", "codeFencedLangTilde"]
  },
  // An exclamation mark can start an image, if it is followed by a link or
  // a link reference.
  {
    character: "!",
    after: "\\[",
    inConstruct: "phrasing",
    notInConstruct: k
  },
  // A quote can break out of a title.
  { character: '"', inConstruct: "titleQuote" },
  // A number sign could start an ATX heading if it starts a line.
  { atBreak: !0, character: "#" },
  { character: "#", inConstruct: "headingAtx", after: `(?:[\r
]|$)` },
  // Dollar sign and percentage are not used in markdown.
  // An ampersand could start a character reference.
  { character: "&", after: "[#A-Za-z]", inConstruct: "phrasing" },
  // An apostrophe can break out of a title.
  { character: "'", inConstruct: "titleApostrophe" },
  // A left paren could break out of a destination raw.
  { character: "(", inConstruct: "destinationRaw" },
  // A left paren followed by `]` could make something into a link or image.
  {
    before: "\\]",
    character: "(",
    inConstruct: "phrasing",
    notInConstruct: k
  },
  // A right paren could start a list item or break out of a destination
  // raw.
  { atBreak: !0, before: "\\d+", character: ")" },
  { character: ")", inConstruct: "destinationRaw" },
  // An asterisk can start thematic breaks, list items, emphasis, strong.
  { atBreak: !0, character: "*", after: `(?:[ 	\r
*])` },
  { character: "*", inConstruct: "phrasing", notInConstruct: k },
  // A plus sign could start a list item.
  { atBreak: !0, character: "+", after: `(?:[ 	\r
])` },
  // A dash can start thematic breaks, list items, and setext heading
  // underlines.
  { atBreak: !0, character: "-", after: `(?:[ 	\r
-])` },
  // A dot could start a list item.
  { atBreak: !0, before: "\\d+", character: ".", after: `(?:[ 	\r
]|$)` },
  // Slash, colon, and semicolon are not used in markdown for constructs.
  // A less than can start html (flow or text) or an autolink.
  // HTML could start with an exclamation mark (declaration, cdata, comment),
  // slash (closing tag), question mark (instruction), or a letter (tag).
  // An autolink also starts with a letter.
  // Finally, it could break out of a destination literal.
  { atBreak: !0, character: "<", after: "[!/?A-Za-z]" },
  {
    character: "<",
    after: "[!/?A-Za-z]",
    inConstruct: "phrasing",
    notInConstruct: k
  },
  { character: "<", inConstruct: "destinationLiteral" },
  // An equals to can start setext heading underlines.
  { atBreak: !0, character: "=" },
  // A greater than can start block quotes and it can break out of a
  // destination literal.
  { atBreak: !0, character: ">" },
  { character: ">", inConstruct: "destinationLiteral" },
  // Question mark and at sign are not used in markdown for constructs.
  // A left bracket can start definitions, references, labels,
  { atBreak: !0, character: "[" },
  { character: "[", inConstruct: "phrasing", notInConstruct: k },
  { character: "[", inConstruct: ["label", "reference"] },
  // A backslash can start an escape (when followed by punctuation) or a
  // hard break (when followed by an eol).
  // Note: typical escapes are handled in `safe`!
  { character: "\\", after: "[\\r\\n]", inConstruct: "phrasing" },
  // A right bracket can exit labels.
  { character: "]", inConstruct: ["label", "reference"] },
  // Caret is not used in markdown for constructs.
  // An underscore can start emphasis, strong, or a thematic break.
  { atBreak: !0, character: "_" },
  { character: "_", inConstruct: "phrasing", notInConstruct: k },
  // A grave accent can start code (fenced or text), or it can break out of
  // a grave accent code fence.
  { atBreak: !0, character: "`" },
  {
    character: "`",
    inConstruct: ["codeFencedLangGraveAccent", "codeFencedMetaGraveAccent"]
  },
  { character: "`", inConstruct: "phrasing", notInConstruct: k },
  // Left brace, vertical bar, right brace are not used in markdown for
  // constructs.
  // A tilde can start code (fenced).
  { atBreak: !0, character: "~" }
];
function G(e) {
  return e.label || !e.identifier ? e.label || "" : L(e.identifier);
}
function M(e) {
  if (!e._compiled) {
    const n = (e.atBreak ? "[\\r\\n][\\t ]*" : "") + (e.before ? "(?:" + e.before + ")" : "");
    e._compiled = new RegExp(
      (n ? "(" + n + ")" : "") + (/[|\\{}()[\]^$+*?.-]/.test(e.character) ? "\\" : "") + e.character + (e.after ? "(?:" + e.after + ")" : ""),
      "g"
    );
  }
  return e._compiled;
}
function P(e, n, a) {
  const t = n.indexStack, c = e.children || [], r = [];
  let o = -1, i = a.before, l;
  t.push(-1);
  let u = n.createTracker(a);
  for (; ++o < c.length; ) {
    const s = c[o];
    let f;
    if (t[t.length - 1] = o, o + 1 < c.length) {
      let d = n.handle.handlers[c[o + 1].type];
      d && d.peek && (d = d.peek), f = d ? d(c[o + 1], e, n, {
        before: "",
        after: "",
        ...u.current()
      }).charAt(0) : "";
    } else
      f = a.after;
    r.length > 0 && (i === "\r" || i === `
`) && s.type === "html" && (r[r.length - 1] = r[r.length - 1].replace(
      /(\r?\n|\r)$/,
      " "
    ), i = " ", u = n.createTracker(a), u.move(r.join("")));
    let h = n.handle(s, e, n, {
      ...u.current(),
      after: f,
      before: i
    });
    l && l === h.slice(0, 1) && (h = C(l.charCodeAt(0)) + h.slice(1));
    const p = n.attentionEncodeSurroundingInfo;
    n.attentionEncodeSurroundingInfo = void 0, l = void 0, p && (r.length > 0 && p.before && i === r[r.length - 1].slice(-1) && (r[r.length - 1] = r[r.length - 1].slice(0, -1) + C(i.charCodeAt(0))), p.after && (l = f)), u.move(h), r.push(h), i = h.slice(-1);
  }
  return t.pop(), r.join("");
}
function E(e, n, a) {
  const t = n.indexStack, c = e.children || [], r = n.createTracker(a), o = [];
  let i = -1;
  for (t.push(-1); ++i < c.length; ) {
    const l = c[i];
    t[t.length - 1] = i, o.push(
      r.move(
        n.handle(l, e, n, {
          before: `
`,
          after: `
`,
          ...r.current()
        })
      )
    ), l.type !== "list" && (n.bulletLastUsed = void 0), i < c.length - 1 && o.push(
      r.move(z(l, c[i + 1], e, n))
    );
  }
  return t.pop(), o.join("");
}
function z(e, n, a, t) {
  let c = t.join.length;
  for (; c--; ) {
    const r = t.join[c](e, n, a, t);
    if (r === !0 || r === 1)
      break;
    if (typeof r == "number")
      return `
`.repeat(1 + r);
    if (r === !1)
      return `

<!---->

`;
  }
  return `

`;
}
const R = /\r?\n|\r/g;
function _(e, n) {
  const a = [];
  let t = 0, c = 0, r;
  for (; r = R.exec(e); )
    o(e.slice(t, r.index)), a.push(r[0]), t = r.index + r[0].length, c++;
  return o(e.slice(t)), a.join("");
  function o(i) {
    a.push(n(i, c, !i));
  }
}
function $(e, n, a) {
  const t = (a.before || "") + (n || "") + (a.after || ""), c = [], r = [], o = {};
  let i = -1;
  for (; ++i < e.unsafe.length; ) {
    const s = e.unsafe[i];
    if (!B(e.stack, s))
      continue;
    const f = e.compilePattern(s);
    let h;
    for (; h = f.exec(t); ) {
      const p = "before" in s || !!s.atBreak, d = "after" in s, g = h.index + (p ? h[1].length : 0);
      c.includes(g) ? (o[g].before && !p && (o[g].before = !1), o[g].after && !d && (o[g].after = !1)) : (c.push(g), o[g] = { before: p, after: d });
    }
  }
  c.sort(D);
  let l = a.before ? a.before.length : 0;
  const u = t.length - (a.after ? a.after.length : 0);
  for (i = -1; ++i < c.length; ) {
    const s = c[i];
    s < l || s >= u || s + 1 < u && c[i + 1] === s + 1 && o[s].after && !o[s + 1].before && !o[s + 1].after || c[i - 1] === s - 1 && o[s].before && !o[s - 1].before && !o[s - 1].after || (l !== s && r.push(m(t.slice(l, s), "\\")), l = s, /[!-/:-@[-`{-~]/.test(t.charAt(s)) && (!a.encode || !a.encode.includes(t.charAt(s))) ? r.push("\\") : (r.push(C(t.charCodeAt(s))), l++));
  }
  return r.push(m(t.slice(l, u), a.after)), r.join("");
}
function D(e, n) {
  return e - n;
}
function m(e, n) {
  const a = /\\(?=[!-/:-@[-`{-~])/g, t = [], c = [], r = e + n;
  let o = -1, i = 0, l;
  for (; l = a.exec(r); )
    t.push(l.index);
  for (; ++o < t.length; )
    i !== t[o] && c.push(e.slice(i, t[o])), c.push("\\"), i = t[o];
  return c.push(e.slice(i)), c.join("");
}
function Z(e) {
  const n = e || {}, a = n.now || {};
  let t = n.lineShift || 0, c = a.line || 1, r = a.column || 1;
  return { move: l, current: o, shift: i };
  function o() {
    return { now: { line: c, column: r }, lineShift: t };
  }
  function i(u) {
    t += u;
  }
  function l(u) {
    const s = u || "", f = s.split(/\r?\n|\r/g), h = f[f.length - 1];
    return c += f.length - 1, r = f.length === 1 ? r + h.length : 1 + h.length + t, s;
  }
}
function O(e, n) {
  const a = n || {}, t = {
    associationId: G,
    containerPhrasing: q,
    containerFlow: J,
    createTracker: Z,
    compilePattern: M,
    enter: r,
    // @ts-expect-error: GFM / frontmatter are typed in `mdast` but not defined
    // here.
    handlers: { ...F },
    // @ts-expect-error: add `handle` in a second.
    handle: void 0,
    indentLines: _,
    indexStack: [],
    join: [...v],
    options: {},
    safe: K,
    stack: [],
    unsafe: [...T]
  };
  A(t, a), t.options.tightDefinitions && t.join.push(U), t.handle = x("type", {
    invalid: Q,
    unknown: H,
    handlers: t.handlers
  });
  let c = t.handle(e, void 0, t, {
    before: `
`,
    after: `
`,
    now: { line: 1, column: 1 },
    lineShift: 0
  });
  return c && c.charCodeAt(c.length - 1) !== 10 && c.charCodeAt(c.length - 1) !== 13 && (c += `
`), c;
  function r(o) {
    return t.stack.push(o), i;
    function i() {
      t.stack.pop();
    }
  }
}
function Q(e) {
  throw new Error("Cannot handle value `" + e + "`, expected node");
}
function H(e) {
  const n = (
    /** @type {Nodes} */
    e
  );
  throw new Error("Cannot handle unknown node `" + n.type + "`");
}
function U(e, n) {
  if (e.type === "definition" && e.type === n.type)
    return 0;
}
function q(e, n) {
  return P(e, this, n);
}
function J(e, n) {
  return E(e, this, n);
}
function K(e, n) {
  return $(this, e, n);
}
function X(e) {
  const n = this;
  n.compiler = a;
  function a(t) {
    return O(t, {
      ...n.data("settings"),
      ...e,
      // Note: this option is not in the readme.
      // The goal is for it to be set by plugins on `data` instead of being
      // passed by users.
      extensions: n.data("toMarkdownExtensions") || []
    });
  }
}
export {
  X as default
};
