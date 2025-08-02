import { g as _ } from "./Index-Bo5_uwJz.js";
import { V as k } from "./index-DMnw81c_.js";
function z(n) {
  if (n)
    throw n;
}
var m = Object.prototype.hasOwnProperty, F = Object.prototype.toString, A = Object.defineProperty, I = Object.getOwnPropertyDescriptor, T = function(e) {
  return typeof Array.isArray == "function" ? Array.isArray(e) : F.call(e) === "[object Array]";
}, C = function(e) {
  if (!e || F.call(e) !== "[object Object]")
    return !1;
  var t = m.call(e, "constructor"), r = e.constructor && e.constructor.prototype && m.call(e.constructor.prototype, "isPrototypeOf");
  if (e.constructor && !t && !r)
    return !1;
  var s;
  for (s in e)
    ;
  return typeof s > "u" || m.call(e, s);
}, S = function(e, t) {
  A && t.name === "__proto__" ? A(e, t.name, {
    enumerable: !0,
    configurable: !0,
    value: t.newValue,
    writable: !0
  }) : e[t.name] = t.newValue;
}, j = function(e, t) {
  if (t === "__proto__")
    if (m.call(e, t)) {
      if (I)
        return I(e, t).value;
    } else return;
  return e[t];
}, L = function n() {
  var e, t, r, s, a, c, o = arguments[0], u = 1, i = arguments.length, f = !1;
  for (typeof o == "boolean" && (f = o, o = arguments[1] || {}, u = 2), (o == null || typeof o != "object" && typeof o != "function") && (o = {}); u < i; ++u)
    if (e = arguments[u], e != null)
      for (t in e)
        r = j(o, t), s = j(e, t), o !== s && (f && s && (C(s) || (a = T(s))) ? (a ? (a = !1, c = r && T(r) ? r : []) : c = r && C(r) ? r : {}, S(o, { name: t, newValue: n(f, c, s) })) : typeof s < "u" && S(o, { name: t, newValue: s }));
  return o;
};
const w = /* @__PURE__ */ _(L);
function x(n) {
  if (typeof n != "object" || n === null)
    return !1;
  const e = Object.getPrototypeOf(n);
  return (e === null || e === Object.prototype || Object.getPrototypeOf(e) === null) && !(Symbol.toStringTag in n) && !(Symbol.iterator in n);
}
function N() {
  const n = [], e = { run: t, use: r };
  return e;
  function t(...s) {
    let a = -1;
    const c = s.pop();
    if (typeof c != "function")
      throw new TypeError("Expected function as last argument, not " + c);
    o(null, ...s);
    function o(u, ...i) {
      const f = n[++a];
      let l = -1;
      if (u) {
        c(u);
        return;
      }
      for (; ++l < s.length; )
        (i[l] === null || i[l] === void 0) && (i[l] = s[l]);
      s = i, f ? U(f, o)(...i) : c(null, ...i);
    }
  }
  function r(s) {
    if (typeof s != "function")
      throw new TypeError(
        "Expected `middelware` to be a function, not " + s
      );
    return n.push(s), e;
  }
}
function U(n, e) {
  let t;
  return r;
  function r(...c) {
    const o = n.length > c.length;
    let u;
    o && c.push(s);
    try {
      u = n.apply(this, c);
    } catch (i) {
      const f = (
        /** @type {Error} */
        i
      );
      if (o && t)
        throw f;
      return s(f);
    }
    o || (u && u.then && typeof u.then == "function" ? u.then(a, s) : u instanceof Error ? s(u) : a(u));
  }
  function s(c, ...o) {
    t || (t = !0, e(c, ...o));
  }
  function a(c) {
    s(null, c);
  }
}
const B = (
  /**
   * @type {new <Parameters extends Array<unknown>, Result>(property: string | symbol) => (...parameters: Parameters) => Result}
   */
  /** @type {unknown} */
  /**
   * @this {Function}
   * @param {string | symbol} property
   * @returns {(...parameters: Array<unknown>) => unknown}
   */
  function(n) {
    const r = (
      /** @type {Record<string | symbol, Function>} */
      // Prototypes do exist.
      // type-coverage:ignore-next-line
      this.constructor.prototype
    ), s = r[n], a = function() {
      return s.apply(a, arguments);
    };
    return Object.setPrototypeOf(a, r), a;
  }
), $ = {}.hasOwnProperty;
class O extends B {
  /**
   * Create a processor.
   */
  constructor() {
    super("copy"), this.Compiler = void 0, this.Parser = void 0, this.attachers = [], this.compiler = void 0, this.freezeIndex = -1, this.frozen = void 0, this.namespace = {}, this.parser = void 0, this.transformers = N();
  }
  /**
   * Copy a processor.
   *
   * @deprecated
   *   This is a private internal method and should not be used.
   * @returns {Processor<ParseTree, HeadTree, TailTree, CompileTree, CompileResult>}
   *   New *unfrozen* processor ({@linkcode Processor}) that is
   *   configured to work the same as its ancestor.
   *   When the descendant processor is configured in the future it does not
   *   affect the ancestral processor.
   */
  copy() {
    const e = (
      /** @type {Processor<ParseTree, HeadTree, TailTree, CompileTree, CompileResult>} */
      new O()
    );
    let t = -1;
    for (; ++t < this.attachers.length; ) {
      const r = this.attachers[t];
      e.use(...r);
    }
    return e.data(w(!0, {}, this.namespace)), e;
  }
  /**
   * Configure the processor with info available to all plugins.
   * Information is stored in an object.
   *
   * Typically, options can be given to a specific plugin, but sometimes it
   * makes sense to have information shared with several plugins.
   * For example, a list of HTML elements that are self-closing, which is
   * needed during all phases.
   *
   * > **Note**: setting information cannot occur on *frozen* processors.
   * > Call the processor first to create a new unfrozen processor.
   *
   * > **Note**: to register custom data in TypeScript, augment the
   * > {@linkcode Data} interface.
   *
   * @example
   *   This example show how to get and set info:
   *
   *   ```js
   *   import {unified} from 'unified'
   *
   *   const processor = unified().data('alpha', 'bravo')
   *
   *   processor.data('alpha') // => 'bravo'
   *
   *   processor.data() // => {alpha: 'bravo'}
   *
   *   processor.data({charlie: 'delta'})
   *
   *   processor.data() // => {charlie: 'delta'}
   *   ```
   *
   * @template {keyof Data} Key
   *
   * @overload
   * @returns {Data}
   *
   * @overload
   * @param {Data} dataset
   * @returns {Processor<ParseTree, HeadTree, TailTree, CompileTree, CompileResult>}
   *
   * @overload
   * @param {Key} key
   * @returns {Data[Key]}
   *
   * @overload
   * @param {Key} key
   * @param {Data[Key]} value
   * @returns {Processor<ParseTree, HeadTree, TailTree, CompileTree, CompileResult>}
   *
   * @param {Data | Key} [key]
   *   Key to get or set, or entire dataset to set, or nothing to get the
   *   entire dataset (optional).
   * @param {Data[Key]} [value]
   *   Value to set (optional).
   * @returns {unknown}
   *   The current processor when setting, the value at `key` when getting, or
   *   the entire dataset when getting without key.
   */
  data(e, t) {
    return typeof e == "string" ? arguments.length === 2 ? (P("data", this.frozen), this.namespace[e] = t, this) : $.call(this.namespace, e) && this.namespace[e] || void 0 : e ? (P("data", this.frozen), this.namespace = e, this) : this.namespace;
  }
  /**
   * Freeze a processor.
   *
   * Frozen processors are meant to be extended and not to be configured
   * directly.
   *
   * When a processor is frozen it cannot be unfrozen.
   * New processors working the same way can be created by calling the
   * processor.
   *
   * It’s possible to freeze processors explicitly by calling `.freeze()`.
   * Processors freeze automatically when `.parse()`, `.run()`, `.runSync()`,
   * `.stringify()`, `.process()`, or `.processSync()` are called.
   *
   * @returns {Processor<ParseTree, HeadTree, TailTree, CompileTree, CompileResult>}
   *   The current processor.
   */
  freeze() {
    if (this.frozen)
      return this;
    const e = (
      /** @type {Processor} */
      /** @type {unknown} */
      this
    );
    for (; ++this.freezeIndex < this.attachers.length; ) {
      const [t, ...r] = this.attachers[this.freezeIndex];
      if (r[0] === !1)
        continue;
      r[0] === !0 && (r[0] = void 0);
      const s = t.call(e, ...r);
      typeof s == "function" && this.transformers.use(s);
    }
    return this.frozen = !0, this.freezeIndex = Number.POSITIVE_INFINITY, this;
  }
  /**
   * Parse text to a syntax tree.
   *
   * > **Note**: `parse` freezes the processor if not already *frozen*.
   *
   * > **Note**: `parse` performs the parse phase, not the run phase or other
   * > phases.
   *
   * @param {Compatible | undefined} [file]
   *   file to parse (optional); typically `string` or `VFile`; any value
   *   accepted as `x` in `new VFile(x)`.
   * @returns {ParseTree extends undefined ? Node : ParseTree}
   *   Syntax tree representing `file`.
   */
  parse(e) {
    this.freeze();
    const t = d(e), r = this.parser || this.Parser;
    return g("parse", r), r(String(t), t);
  }
  /**
   * Process the given file as configured on the processor.
   *
   * > **Note**: `process` freezes the processor if not already *frozen*.
   *
   * > **Note**: `process` performs the parse, run, and stringify phases.
   *
   * @overload
   * @param {Compatible | undefined} file
   * @param {ProcessCallback<VFileWithOutput<CompileResult>>} done
   * @returns {undefined}
   *
   * @overload
   * @param {Compatible | undefined} [file]
   * @returns {Promise<VFileWithOutput<CompileResult>>}
   *
   * @param {Compatible | undefined} [file]
   *   File (optional); typically `string` or `VFile`]; any value accepted as
   *   `x` in `new VFile(x)`.
   * @param {ProcessCallback<VFileWithOutput<CompileResult>> | undefined} [done]
   *   Callback (optional).
   * @returns {Promise<VFile> | undefined}
   *   Nothing if `done` is given.
   *   Otherwise a promise, rejected with a fatal error or resolved with the
   *   processed file.
   *
   *   The parsed, transformed, and compiled value is available at
   *   `file.value` (see note).
   *
   *   > **Note**: unified typically compiles by serializing: most
   *   > compilers return `string` (or `Uint8Array`).
   *   > Some compilers, such as the one configured with
   *   > [`rehype-react`][rehype-react], return other values (in this case, a
   *   > React tree).
   *   > If you’re using a compiler that doesn’t serialize, expect different
   *   > result values.
   *   >
   *   > To register custom results in TypeScript, add them to
   *   > {@linkcode CompileResultMap}.
   *
   *   [rehype-react]: https://github.com/rehypejs/rehype-react
   */
  process(e, t) {
    const r = this;
    return this.freeze(), g("process", this.parser || this.Parser), b("process", this.compiler || this.Compiler), t ? s(void 0, t) : new Promise(s);
    function s(a, c) {
      const o = d(e), u = (
        /** @type {HeadTree extends undefined ? Node : HeadTree} */
        /** @type {unknown} */
        r.parse(o)
      );
      r.run(u, o, function(f, l, p) {
        if (f || !l || !p)
          return i(f);
        const h = (
          /** @type {CompileTree extends undefined ? Node : CompileTree} */
          /** @type {unknown} */
          l
        ), y = r.stringify(h, p);
        Y(y) ? p.value = y : p.result = y, i(
          f,
          /** @type {VFileWithOutput<CompileResult>} */
          p
        );
      });
      function i(f, l) {
        f || !l ? c(f) : a ? a(l) : t(void 0, l);
      }
    }
  }
  /**
   * Process the given file as configured on the processor.
   *
   * An error is thrown if asynchronous transforms are configured.
   *
   * > **Note**: `processSync` freezes the processor if not already *frozen*.
   *
   * > **Note**: `processSync` performs the parse, run, and stringify phases.
   *
   * @param {Compatible | undefined} [file]
   *   File (optional); typically `string` or `VFile`; any value accepted as
   *   `x` in `new VFile(x)`.
   * @returns {VFileWithOutput<CompileResult>}
   *   The processed file.
   *
   *   The parsed, transformed, and compiled value is available at
   *   `file.value` (see note).
   *
   *   > **Note**: unified typically compiles by serializing: most
   *   > compilers return `string` (or `Uint8Array`).
   *   > Some compilers, such as the one configured with
   *   > [`rehype-react`][rehype-react], return other values (in this case, a
   *   > React tree).
   *   > If you’re using a compiler that doesn’t serialize, expect different
   *   > result values.
   *   >
   *   > To register custom results in TypeScript, add them to
   *   > {@linkcode CompileResultMap}.
   *
   *   [rehype-react]: https://github.com/rehypejs/rehype-react
   */
  processSync(e) {
    let t = !1, r;
    return this.freeze(), g("processSync", this.parser || this.Parser), b("processSync", this.compiler || this.Compiler), this.process(e, s), D("processSync", "process", t), r;
    function s(a, c) {
      t = !0, z(a), r = c;
    }
  }
  /**
   * Run *transformers* on a syntax tree.
   *
   * > **Note**: `run` freezes the processor if not already *frozen*.
   *
   * > **Note**: `run` performs the run phase, not other phases.
   *
   * @overload
   * @param {HeadTree extends undefined ? Node : HeadTree} tree
   * @param {RunCallback<TailTree extends undefined ? Node : TailTree>} done
   * @returns {undefined}
   *
   * @overload
   * @param {HeadTree extends undefined ? Node : HeadTree} tree
   * @param {Compatible | undefined} file
   * @param {RunCallback<TailTree extends undefined ? Node : TailTree>} done
   * @returns {undefined}
   *
   * @overload
   * @param {HeadTree extends undefined ? Node : HeadTree} tree
   * @param {Compatible | undefined} [file]
   * @returns {Promise<TailTree extends undefined ? Node : TailTree>}
   *
   * @param {HeadTree extends undefined ? Node : HeadTree} tree
   *   Tree to transform and inspect.
   * @param {(
   *   RunCallback<TailTree extends undefined ? Node : TailTree> |
   *   Compatible
   * )} [file]
   *   File associated with `node` (optional); any value accepted as `x` in
   *   `new VFile(x)`.
   * @param {RunCallback<TailTree extends undefined ? Node : TailTree>} [done]
   *   Callback (optional).
   * @returns {Promise<TailTree extends undefined ? Node : TailTree> | undefined}
   *   Nothing if `done` is given.
   *   Otherwise, a promise rejected with a fatal error or resolved with the
   *   transformed tree.
   */
  run(e, t, r) {
    V(e), this.freeze();
    const s = this.transformers;
    return !r && typeof t == "function" && (r = t, t = void 0), r ? a(void 0, r) : new Promise(a);
    function a(c, o) {
      const u = d(t);
      s.run(e, u, i);
      function i(f, l, p) {
        const h = (
          /** @type {TailTree extends undefined ? Node : TailTree} */
          l || e
        );
        f ? o(f) : c ? c(h) : r(void 0, h, p);
      }
    }
  }
  /**
   * Run *transformers* on a syntax tree.
   *
   * An error is thrown if asynchronous transforms are configured.
   *
   * > **Note**: `runSync` freezes the processor if not already *frozen*.
   *
   * > **Note**: `runSync` performs the run phase, not other phases.
   *
   * @param {HeadTree extends undefined ? Node : HeadTree} tree
   *   Tree to transform and inspect.
   * @param {Compatible | undefined} [file]
   *   File associated with `node` (optional); any value accepted as `x` in
   *   `new VFile(x)`.
   * @returns {TailTree extends undefined ? Node : TailTree}
   *   Transformed tree.
   */
  runSync(e, t) {
    let r = !1, s;
    return this.run(e, t, a), D("runSync", "run", r), s;
    function a(c, o) {
      z(c), s = o, r = !0;
    }
  }
  /**
   * Compile a syntax tree.
   *
   * > **Note**: `stringify` freezes the processor if not already *frozen*.
   *
   * > **Note**: `stringify` performs the stringify phase, not the run phase
   * > or other phases.
   *
   * @param {CompileTree extends undefined ? Node : CompileTree} tree
   *   Tree to compile.
   * @param {Compatible | undefined} [file]
   *   File associated with `node` (optional); any value accepted as `x` in
   *   `new VFile(x)`.
   * @returns {CompileResult extends undefined ? Value : CompileResult}
   *   Textual representation of the tree (see note).
   *
   *   > **Note**: unified typically compiles by serializing: most compilers
   *   > return `string` (or `Uint8Array`).
   *   > Some compilers, such as the one configured with
   *   > [`rehype-react`][rehype-react], return other values (in this case, a
   *   > React tree).
   *   > If you’re using a compiler that doesn’t serialize, expect different
   *   > result values.
   *   >
   *   > To register custom results in TypeScript, add them to
   *   > {@linkcode CompileResultMap}.
   *
   *   [rehype-react]: https://github.com/rehypejs/rehype-react
   */
  stringify(e, t) {
    this.freeze();
    const r = d(t), s = this.compiler || this.Compiler;
    return b("stringify", s), V(e), s(e, r);
  }
  /**
   * Configure the processor to use a plugin, a list of usable values, or a
   * preset.
   *
   * If the processor is already using a plugin, the previous plugin
   * configuration is changed based on the options that are passed in.
   * In other words, the plugin is not added a second time.
   *
   * > **Note**: `use` cannot be called on *frozen* processors.
   * > Call the processor first to create a new unfrozen processor.
   *
   * @example
   *   There are many ways to pass plugins to `.use()`.
   *   This example gives an overview:
   *
   *   ```js
   *   import {unified} from 'unified'
   *
   *   unified()
   *     // Plugin with options:
   *     .use(pluginA, {x: true, y: true})
   *     // Passing the same plugin again merges configuration (to `{x: true, y: false, z: true}`):
   *     .use(pluginA, {y: false, z: true})
   *     // Plugins:
   *     .use([pluginB, pluginC])
   *     // Two plugins, the second with options:
   *     .use([pluginD, [pluginE, {}]])
   *     // Preset with plugins and settings:
   *     .use({plugins: [pluginF, [pluginG, {}]], settings: {position: false}})
   *     // Settings only:
   *     .use({settings: {position: false}})
   *   ```
   *
   * @template {Array<unknown>} [Parameters=[]]
   * @template {Node | string | undefined} [Input=undefined]
   * @template [Output=Input]
   *
   * @overload
   * @param {Preset | null | undefined} [preset]
   * @returns {Processor<ParseTree, HeadTree, TailTree, CompileTree, CompileResult>}
   *
   * @overload
   * @param {PluggableList} list
   * @returns {Processor<ParseTree, HeadTree, TailTree, CompileTree, CompileResult>}
   *
   * @overload
   * @param {Plugin<Parameters, Input, Output>} plugin
   * @param {...(Parameters | [boolean])} parameters
   * @returns {UsePlugin<ParseTree, HeadTree, TailTree, CompileTree, CompileResult, Input, Output>}
   *
   * @param {PluggableList | Plugin | Preset | null | undefined} value
   *   Usable value.
   * @param {...unknown} parameters
   *   Parameters, when a plugin is given as a usable value.
   * @returns {Processor<ParseTree, HeadTree, TailTree, CompileTree, CompileResult>}
   *   Current processor.
   */
  use(e, ...t) {
    const r = this.attachers, s = this.namespace;
    if (P("use", this.frozen), e != null) if (typeof e == "function")
      u(e, t);
    else if (typeof e == "object")
      Array.isArray(e) ? o(e) : c(e);
    else
      throw new TypeError("Expected usable value, not `" + e + "`");
    return this;
    function a(i) {
      if (typeof i == "function")
        u(i, []);
      else if (typeof i == "object")
        if (Array.isArray(i)) {
          const [f, ...l] = (
            /** @type {PluginTuple<Array<unknown>>} */
            i
          );
          u(f, l);
        } else
          c(i);
      else
        throw new TypeError("Expected usable value, not `" + i + "`");
    }
    function c(i) {
      if (!("plugins" in i) && !("settings" in i))
        throw new Error(
          "Expected usable value but received an empty preset, which is probably a mistake: presets typically come with `plugins` and sometimes with `settings`, but this has neither"
        );
      o(i.plugins), i.settings && (s.settings = w(!0, s.settings, i.settings));
    }
    function o(i) {
      let f = -1;
      if (i != null) if (Array.isArray(i))
        for (; ++f < i.length; ) {
          const l = i[f];
          a(l);
        }
      else
        throw new TypeError("Expected a list of plugins, not `" + i + "`");
    }
    function u(i, f) {
      let l = -1, p = -1;
      for (; ++l < r.length; )
        if (r[l][0] === i) {
          p = l;
          break;
        }
      if (p === -1)
        r.push([i, ...f]);
      else if (f.length > 0) {
        let [h, ...y] = f;
        const E = r[p][1];
        x(E) && x(h) && (h = w(!0, E, h)), r[p] = [i, h, ...y];
      }
    }
  }
}
const J = new O().freeze();
function g(n, e) {
  if (typeof e != "function")
    throw new TypeError("Cannot `" + n + "` without `parser`");
}
function b(n, e) {
  if (typeof e != "function")
    throw new TypeError("Cannot `" + n + "` without `compiler`");
}
function P(n, e) {
  if (e)
    throw new Error(
      "Cannot call `" + n + "` on a frozen processor.\nCreate a new processor first, by calling it: use `processor()` instead of `processor`."
    );
}
function V(n) {
  if (!x(n) || typeof n.type != "string")
    throw new TypeError("Expected node, got `" + n + "`");
}
function D(n, e, t) {
  if (!t)
    throw new Error(
      "`" + n + "` finished async. Use `" + e + "` instead"
    );
}
function d(n) {
  return R(n) ? n : new k(n);
}
function R(n) {
  return !!(n && typeof n == "object" && "message" in n && "messages" in n);
}
function Y(n) {
  return typeof n == "string" || q(n);
}
function q(n) {
  return !!(n && typeof n == "object" && "byteLength" in n && "byteOffset" in n);
}
export {
  J as unified
};
