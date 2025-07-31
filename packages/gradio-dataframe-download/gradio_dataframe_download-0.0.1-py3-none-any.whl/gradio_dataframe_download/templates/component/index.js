var It = Object.defineProperty;
var Ne = (r) => {
  throw TypeError(r);
};
var zt = (r, e, t) => e in r ? It(r, e, { enumerable: !0, configurable: !0, writable: !0, value: t }) : r[e] = t;
var E = (r, e, t) => zt(r, typeof e != "symbol" ? e + "" : e, t), Fe = (r, e, t) => e.has(r) || Ne("Cannot " + t);
var W = (r, e, t) => (Fe(r, e, "read from private field"), t ? t.call(r) : e.get(r)), ye = (r, e, t) => e.has(r) ? Ne("Cannot add the same private member more than once") : e instanceof WeakSet ? e.add(r) : e.set(r, t), Me = (r, e, t, n) => (Fe(r, e, "write to private field"), n ? n.call(r, t) : e.set(r, t), t), ce = (r, e, t) => (Fe(r, e, "access private method"), t);
new Intl.Collator(0, { numeric: 1 }).compare;
typeof process < "u" && process.versions && process.versions.node;
var j;
class Pi extends TransformStream {
  /** Constructs a new instance. */
  constructor(t = { allowCR: !1 }) {
    super({
      transform: (n, i) => {
        for (n = W(this, j) + n; ; ) {
          const a = n.indexOf(`
`), o = t.allowCR ? n.indexOf("\r") : -1;
          if (o !== -1 && o !== n.length - 1 && (a === -1 || a - 1 > o)) {
            i.enqueue(n.slice(0, o)), n = n.slice(o + 1);
            continue;
          }
          if (a === -1)
            break;
          const l = n[a - 1] === "\r" ? a - 1 : a;
          i.enqueue(n.slice(0, l)), n = n.slice(a + 1);
        }
        Me(this, j, n);
      },
      flush: (n) => {
        if (W(this, j) === "")
          return;
        const i = t.allowCR && W(this, j).endsWith("\r") ? W(this, j).slice(0, -1) : W(this, j);
        n.enqueue(i);
      }
    });
    ye(this, j, "");
  }
}
j = new WeakMap();
const { setContext: Ni, getContext: Lt } = window.__gradio__svelte__internal, Ot = "WORKER_PROXY_CONTEXT_KEY";
function Pt() {
  return Lt(Ot);
}
const Nt = "lite.local";
function Mt(r) {
  return r.host === window.location.host || r.host === "localhost:7860" || r.host === "127.0.0.1:7860" || // Ref: https://github.com/gradio-app/gradio/blob/v3.32.0/js/app/src/Index.svelte#L194
  r.host === Nt;
}
function jt(r, e) {
  const t = e.toLowerCase();
  for (const [n, i] of Object.entries(r))
    if (n.toLowerCase() === t)
      return i;
}
function Ht(r) {
  const e = typeof window < "u";
  if (r == null || !e)
    return !1;
  const t = new URL(r, window.location.href);
  return !(!Mt(t) || t.protocol !== "http:" && t.protocol !== "https:");
}
let _e;
async function Ut(r) {
  const e = typeof window < "u";
  if (r == null || !e || !Ht(r))
    return r;
  if (_e == null)
    try {
      _e = Pt();
    } catch {
      return r;
    }
  if (_e == null)
    return r;
  const n = new URL(r, window.location.href).pathname;
  return _e.httpRequest({
    method: "GET",
    path: n,
    headers: {},
    query_string: ""
  }).then((i) => {
    if (i.status !== 200)
      throw new Error(`Failed to get file ${n} from the Wasm worker.`);
    const a = new Blob([i.body], {
      type: jt(i.headers, "content-type")
    });
    return URL.createObjectURL(a);
  });
}
const {
  SvelteComponent: Mi,
  assign: ji,
  check_outros: Hi,
  children: Ui,
  claim_element: Gi,
  compute_rest_props: Zi,
  create_slot: Xi,
  detach: Wi,
  element: Yi,
  empty: Ki,
  exclude_internal_props: Qi,
  get_all_dirty_from_scope: Vi,
  get_slot_changes: Ji,
  get_spread_update: ea,
  group_outros: ta,
  init: na,
  insert_hydration: ia,
  listen: aa,
  prevent_default: oa,
  safe_not_equal: ra,
  set_attributes: la,
  set_style: sa,
  toggle_class: ua,
  transition_in: ca,
  transition_out: _a,
  update_slot_base: da
} = window.__gradio__svelte__internal, { createEventDispatcher: pa, onMount: ha } = window.__gradio__svelte__internal, {
  SvelteComponent: Gt,
  assign: be,
  bubble: Zt,
  claim_element: Xt,
  compute_rest_props: je,
  detach: Wt,
  element: Yt,
  exclude_internal_props: Kt,
  get_spread_update: Qt,
  init: Vt,
  insert_hydration: Jt,
  listen: en,
  noop: He,
  safe_not_equal: tn,
  set_attributes: Ue,
  src_url_equal: nn,
  toggle_class: Ge
} = window.__gradio__svelte__internal;
function an(r) {
  let e, t, n, i, a = [
    {
      src: t = /*resolved_src*/
      r[0]
    },
    /*$$restProps*/
    r[1]
  ], o = {};
  for (let l = 0; l < a.length; l += 1)
    o = be(o, a[l]);
  return {
    c() {
      e = Yt("img"), this.h();
    },
    l(l) {
      e = Xt(l, "IMG", { src: !0 }), this.h();
    },
    h() {
      Ue(e, o), Ge(e, "svelte-kxeri3", !0);
    },
    m(l, s) {
      Jt(l, e, s), n || (i = en(
        e,
        "load",
        /*load_handler*/
        r[4]
      ), n = !0);
    },
    p(l, [s]) {
      Ue(e, o = Qt(a, [
        s & /*resolved_src*/
        1 && !nn(e.src, t = /*resolved_src*/
        l[0]) && { src: t },
        s & /*$$restProps*/
        2 && /*$$restProps*/
        l[1]
      ])), Ge(e, "svelte-kxeri3", !0);
    },
    i: He,
    o: He,
    d(l) {
      l && Wt(e), n = !1, i();
    }
  };
}
function on(r, e, t) {
  const n = ["src"];
  let i = je(e, n), { src: a = void 0 } = e, o, l;
  function s(_) {
    Zt.call(this, r, _);
  }
  return r.$$set = (_) => {
    e = be(be({}, e), Kt(_)), t(1, i = je(e, n)), "src" in _ && t(2, a = _.src);
  }, r.$$.update = () => {
    if (r.$$.dirty & /*src, latest_src*/
    12) {
      t(0, o = a), t(3, l = a);
      const _ = a;
      Ut(_).then((d) => {
        l === _ && t(0, o = d);
      });
    }
  }, [o, i, a, l, s];
}
class at extends Gt {
  constructor(e) {
    super(), Vt(this, e, on, an, tn, { src: 2 });
  }
}
const rn = [
  { color: "red", primary: 600, secondary: 100 },
  { color: "green", primary: 600, secondary: 100 },
  { color: "blue", primary: 600, secondary: 100 },
  { color: "yellow", primary: 500, secondary: 100 },
  { color: "purple", primary: 600, secondary: 100 },
  { color: "teal", primary: 600, secondary: 100 },
  { color: "orange", primary: 600, secondary: 100 },
  { color: "cyan", primary: 600, secondary: 100 },
  { color: "lime", primary: 500, secondary: 100 },
  { color: "pink", primary: 600, secondary: 100 }
], Ze = {
  inherit: "inherit",
  current: "currentColor",
  transparent: "transparent",
  black: "#000",
  white: "#fff",
  slate: {
    50: "#f8fafc",
    100: "#f1f5f9",
    200: "#e2e8f0",
    300: "#cbd5e1",
    400: "#94a3b8",
    500: "#64748b",
    600: "#475569",
    700: "#334155",
    800: "#1e293b",
    900: "#0f172a",
    950: "#020617"
  },
  gray: {
    50: "#f9fafb",
    100: "#f3f4f6",
    200: "#e5e7eb",
    300: "#d1d5db",
    400: "#9ca3af",
    500: "#6b7280",
    600: "#4b5563",
    700: "#374151",
    800: "#1f2937",
    900: "#111827",
    950: "#030712"
  },
  zinc: {
    50: "#fafafa",
    100: "#f4f4f5",
    200: "#e4e4e7",
    300: "#d4d4d8",
    400: "#a1a1aa",
    500: "#71717a",
    600: "#52525b",
    700: "#3f3f46",
    800: "#27272a",
    900: "#18181b",
    950: "#09090b"
  },
  neutral: {
    50: "#fafafa",
    100: "#f5f5f5",
    200: "#e5e5e5",
    300: "#d4d4d4",
    400: "#a3a3a3",
    500: "#737373",
    600: "#525252",
    700: "#404040",
    800: "#262626",
    900: "#171717",
    950: "#0a0a0a"
  },
  stone: {
    50: "#fafaf9",
    100: "#f5f5f4",
    200: "#e7e5e4",
    300: "#d6d3d1",
    400: "#a8a29e",
    500: "#78716c",
    600: "#57534e",
    700: "#44403c",
    800: "#292524",
    900: "#1c1917",
    950: "#0c0a09"
  },
  red: {
    50: "#fef2f2",
    100: "#fee2e2",
    200: "#fecaca",
    300: "#fca5a5",
    400: "#f87171",
    500: "#ef4444",
    600: "#dc2626",
    700: "#b91c1c",
    800: "#991b1b",
    900: "#7f1d1d",
    950: "#450a0a"
  },
  orange: {
    50: "#fff7ed",
    100: "#ffedd5",
    200: "#fed7aa",
    300: "#fdba74",
    400: "#fb923c",
    500: "#f97316",
    600: "#ea580c",
    700: "#c2410c",
    800: "#9a3412",
    900: "#7c2d12",
    950: "#431407"
  },
  amber: {
    50: "#fffbeb",
    100: "#fef3c7",
    200: "#fde68a",
    300: "#fcd34d",
    400: "#fbbf24",
    500: "#f59e0b",
    600: "#d97706",
    700: "#b45309",
    800: "#92400e",
    900: "#78350f",
    950: "#451a03"
  },
  yellow: {
    50: "#fefce8",
    100: "#fef9c3",
    200: "#fef08a",
    300: "#fde047",
    400: "#facc15",
    500: "#eab308",
    600: "#ca8a04",
    700: "#a16207",
    800: "#854d0e",
    900: "#713f12",
    950: "#422006"
  },
  lime: {
    50: "#f7fee7",
    100: "#ecfccb",
    200: "#d9f99d",
    300: "#bef264",
    400: "#a3e635",
    500: "#84cc16",
    600: "#65a30d",
    700: "#4d7c0f",
    800: "#3f6212",
    900: "#365314",
    950: "#1a2e05"
  },
  green: {
    50: "#f0fdf4",
    100: "#dcfce7",
    200: "#bbf7d0",
    300: "#86efac",
    400: "#4ade80",
    500: "#22c55e",
    600: "#16a34a",
    700: "#15803d",
    800: "#166534",
    900: "#14532d",
    950: "#052e16"
  },
  emerald: {
    50: "#ecfdf5",
    100: "#d1fae5",
    200: "#a7f3d0",
    300: "#6ee7b7",
    400: "#34d399",
    500: "#10b981",
    600: "#059669",
    700: "#047857",
    800: "#065f46",
    900: "#064e3b",
    950: "#022c22"
  },
  teal: {
    50: "#f0fdfa",
    100: "#ccfbf1",
    200: "#99f6e4",
    300: "#5eead4",
    400: "#2dd4bf",
    500: "#14b8a6",
    600: "#0d9488",
    700: "#0f766e",
    800: "#115e59",
    900: "#134e4a",
    950: "#042f2e"
  },
  cyan: {
    50: "#ecfeff",
    100: "#cffafe",
    200: "#a5f3fc",
    300: "#67e8f9",
    400: "#22d3ee",
    500: "#06b6d4",
    600: "#0891b2",
    700: "#0e7490",
    800: "#155e75",
    900: "#164e63",
    950: "#083344"
  },
  sky: {
    50: "#f0f9ff",
    100: "#e0f2fe",
    200: "#bae6fd",
    300: "#7dd3fc",
    400: "#38bdf8",
    500: "#0ea5e9",
    600: "#0284c7",
    700: "#0369a1",
    800: "#075985",
    900: "#0c4a6e",
    950: "#082f49"
  },
  blue: {
    50: "#eff6ff",
    100: "#dbeafe",
    200: "#bfdbfe",
    300: "#93c5fd",
    400: "#60a5fa",
    500: "#3b82f6",
    600: "#2563eb",
    700: "#1d4ed8",
    800: "#1e40af",
    900: "#1e3a8a",
    950: "#172554"
  },
  indigo: {
    50: "#eef2ff",
    100: "#e0e7ff",
    200: "#c7d2fe",
    300: "#a5b4fc",
    400: "#818cf8",
    500: "#6366f1",
    600: "#4f46e5",
    700: "#4338ca",
    800: "#3730a3",
    900: "#312e81",
    950: "#1e1b4b"
  },
  violet: {
    50: "#f5f3ff",
    100: "#ede9fe",
    200: "#ddd6fe",
    300: "#c4b5fd",
    400: "#a78bfa",
    500: "#8b5cf6",
    600: "#7c3aed",
    700: "#6d28d9",
    800: "#5b21b6",
    900: "#4c1d95",
    950: "#2e1065"
  },
  purple: {
    50: "#faf5ff",
    100: "#f3e8ff",
    200: "#e9d5ff",
    300: "#d8b4fe",
    400: "#c084fc",
    500: "#a855f7",
    600: "#9333ea",
    700: "#7e22ce",
    800: "#6b21a8",
    900: "#581c87",
    950: "#3b0764"
  },
  fuchsia: {
    50: "#fdf4ff",
    100: "#fae8ff",
    200: "#f5d0fe",
    300: "#f0abfc",
    400: "#e879f9",
    500: "#d946ef",
    600: "#c026d3",
    700: "#a21caf",
    800: "#86198f",
    900: "#701a75",
    950: "#4a044e"
  },
  pink: {
    50: "#fdf2f8",
    100: "#fce7f3",
    200: "#fbcfe8",
    300: "#f9a8d4",
    400: "#f472b6",
    500: "#ec4899",
    600: "#db2777",
    700: "#be185d",
    800: "#9d174d",
    900: "#831843",
    950: "#500724"
  },
  rose: {
    50: "#fff1f2",
    100: "#ffe4e6",
    200: "#fecdd3",
    300: "#fda4af",
    400: "#fb7185",
    500: "#f43f5e",
    600: "#e11d48",
    700: "#be123c",
    800: "#9f1239",
    900: "#881337",
    950: "#4c0519"
  }
};
rn.reduce(
  (r, { color: e, primary: t, secondary: n }) => ({
    ...r,
    [e]: {
      primary: Ze[e][t],
      secondary: Ze[e][n]
    }
  }),
  {}
);
const {
  SvelteComponent: ma,
  append_hydration: ga,
  assign: fa,
  attr: $a,
  binding_callbacks: Da,
  children: va,
  claim_element: Fa,
  claim_space: ya,
  claim_svg_element: ba,
  create_slot: wa,
  detach: ka,
  element: Ca,
  empty: Aa,
  get_all_dirty_from_scope: Ea,
  get_slot_changes: Sa,
  get_spread_update: xa,
  init: Ba,
  insert_hydration: qa,
  listen: Ta,
  noop: Ra,
  safe_not_equal: Ia,
  set_dynamic_element_data: za,
  set_style: La,
  space: Oa,
  svg_element: Pa,
  toggle_class: Na,
  transition_in: Ma,
  transition_out: ja,
  update_slot_base: Ha
} = window.__gradio__svelte__internal;
function Ce() {
  return {
    async: !1,
    breaks: !1,
    extensions: null,
    gfm: !0,
    hooks: null,
    pedantic: !1,
    renderer: null,
    silent: !1,
    tokenizer: null,
    walkTokens: null
  };
}
let Z = Ce();
function ot(r) {
  Z = r;
}
const rt = /[&<>"']/, ln = new RegExp(rt.source, "g"), lt = /[<>"']|&(?!(#\d{1,7}|#[Xx][a-fA-F0-9]{1,6}|\w+);)/, sn = new RegExp(lt.source, "g"), un = {
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;",
  "'": "&#39;"
}, Xe = (r) => un[r];
function R(r, e) {
  if (e) {
    if (rt.test(r))
      return r.replace(ln, Xe);
  } else if (lt.test(r))
    return r.replace(sn, Xe);
  return r;
}
const cn = /&(#(?:\d+)|(?:#x[0-9A-Fa-f]+)|(?:\w+));?/ig;
function _n(r) {
  return r.replace(cn, (e, t) => (t = t.toLowerCase(), t === "colon" ? ":" : t.charAt(0) === "#" ? t.charAt(1) === "x" ? String.fromCharCode(parseInt(t.substring(2), 16)) : String.fromCharCode(+t.substring(1)) : ""));
}
const dn = /(^|[^\[])\^/g;
function A(r, e) {
  let t = typeof r == "string" ? r : r.source;
  e = e || "";
  const n = {
    replace: (i, a) => {
      let o = typeof a == "string" ? a : a.source;
      return o = o.replace(dn, "$1"), t = t.replace(i, o), n;
    },
    getRegex: () => new RegExp(t, e)
  };
  return n;
}
function We(r) {
  try {
    r = encodeURI(r).replace(/%25/g, "%");
  } catch {
    return null;
  }
  return r;
}
const J = { exec: () => null };
function Ye(r, e) {
  const t = r.replace(/\|/g, (a, o, l) => {
    let s = !1, _ = o;
    for (; --_ >= 0 && l[_] === "\\"; )
      s = !s;
    return s ? "|" : " |";
  }), n = t.split(/ \|/);
  let i = 0;
  if (n[0].trim() || n.shift(), n.length > 0 && !n[n.length - 1].trim() && n.pop(), e)
    if (n.length > e)
      n.splice(e);
    else
      for (; n.length < e; )
        n.push("");
  for (; i < n.length; i++)
    n[i] = n[i].trim().replace(/\\\|/g, "|");
  return n;
}
function de(r, e, t) {
  const n = r.length;
  if (n === 0)
    return "";
  let i = 0;
  for (; i < n && r.charAt(n - i - 1) === e; )
    i++;
  return r.slice(0, n - i);
}
function pn(r, e) {
  if (r.indexOf(e[1]) === -1)
    return -1;
  let t = 0;
  for (let n = 0; n < r.length; n++)
    if (r[n] === "\\")
      n++;
    else if (r[n] === e[0])
      t++;
    else if (r[n] === e[1] && (t--, t < 0))
      return n;
  return -1;
}
function Ke(r, e, t, n) {
  const i = e.href, a = e.title ? R(e.title) : null, o = r[1].replace(/\\([\[\]])/g, "$1");
  if (r[0].charAt(0) !== "!") {
    n.state.inLink = !0;
    const l = {
      type: "link",
      raw: t,
      href: i,
      title: a,
      text: o,
      tokens: n.inlineTokens(o)
    };
    return n.state.inLink = !1, l;
  }
  return {
    type: "image",
    raw: t,
    href: i,
    title: a,
    text: R(o)
  };
}
function hn(r, e) {
  const t = r.match(/^(\s+)(?:```)/);
  if (t === null)
    return e;
  const n = t[1];
  return e.split(`
`).map((i) => {
    const a = i.match(/^\s+/);
    if (a === null)
      return i;
    const [o] = a;
    return o.length >= n.length ? i.slice(n.length) : i;
  }).join(`
`);
}
class he {
  // set by the lexer
  constructor(e) {
    E(this, "options");
    E(this, "rules");
    // set by the lexer
    E(this, "lexer");
    this.options = e || Z;
  }
  space(e) {
    const t = this.rules.block.newline.exec(e);
    if (t && t[0].length > 0)
      return {
        type: "space",
        raw: t[0]
      };
  }
  code(e) {
    const t = this.rules.block.code.exec(e);
    if (t) {
      const n = t[0].replace(/^ {1,4}/gm, "");
      return {
        type: "code",
        raw: t[0],
        codeBlockStyle: "indented",
        text: this.options.pedantic ? n : de(n, `
`)
      };
    }
  }
  fences(e) {
    const t = this.rules.block.fences.exec(e);
    if (t) {
      const n = t[0], i = hn(n, t[3] || "");
      return {
        type: "code",
        raw: n,
        lang: t[2] ? t[2].trim().replace(this.rules.inline.anyPunctuation, "$1") : t[2],
        text: i
      };
    }
  }
  heading(e) {
    const t = this.rules.block.heading.exec(e);
    if (t) {
      let n = t[2].trim();
      if (/#$/.test(n)) {
        const i = de(n, "#");
        (this.options.pedantic || !i || / $/.test(i)) && (n = i.trim());
      }
      return {
        type: "heading",
        raw: t[0],
        depth: t[1].length,
        text: n,
        tokens: this.lexer.inline(n)
      };
    }
  }
  hr(e) {
    const t = this.rules.block.hr.exec(e);
    if (t)
      return {
        type: "hr",
        raw: t[0]
      };
  }
  blockquote(e) {
    const t = this.rules.block.blockquote.exec(e);
    if (t) {
      let n = t[0].replace(/\n {0,3}((?:=+|-+) *)(?=\n|$)/g, `
    $1`);
      n = de(n.replace(/^ *>[ \t]?/gm, ""), `
`);
      const i = this.lexer.state.top;
      this.lexer.state.top = !0;
      const a = this.lexer.blockTokens(n);
      return this.lexer.state.top = i, {
        type: "blockquote",
        raw: t[0],
        tokens: a,
        text: n
      };
    }
  }
  list(e) {
    let t = this.rules.block.list.exec(e);
    if (t) {
      let n = t[1].trim();
      const i = n.length > 1, a = {
        type: "list",
        raw: "",
        ordered: i,
        start: i ? +n.slice(0, -1) : "",
        loose: !1,
        items: []
      };
      n = i ? `\\d{1,9}\\${n.slice(-1)}` : `\\${n}`, this.options.pedantic && (n = i ? n : "[*+-]");
      const o = new RegExp(`^( {0,3}${n})((?:[	 ][^\\n]*)?(?:\\n|$))`);
      let l = "", s = "", _ = !1;
      for (; e; ) {
        let d = !1;
        if (!(t = o.exec(e)) || this.rules.block.hr.test(e))
          break;
        l = t[0], e = e.substring(l.length);
        let f = t[2].split(`
`, 1)[0].replace(/^\t+/, (m) => " ".repeat(3 * m.length)), $ = e.split(`
`, 1)[0], y = 0;
        this.options.pedantic ? (y = 2, s = f.trimStart()) : (y = t[2].search(/[^ ]/), y = y > 4 ? 1 : y, s = f.slice(y), y += t[1].length);
        let S = !1;
        if (!f && /^ *$/.test($) && (l += $ + `
`, e = e.substring($.length + 1), d = !0), !d) {
          const m = new RegExp(`^ {0,${Math.min(3, y - 1)}}(?:[*+-]|\\d{1,9}[.)])((?:[ 	][^\\n]*)?(?:\\n|$))`), u = new RegExp(`^ {0,${Math.min(3, y - 1)}}((?:- *){3,}|(?:_ *){3,}|(?:\\* *){3,})(?:\\n+|$)`), c = new RegExp(`^ {0,${Math.min(3, y - 1)}}(?:\`\`\`|~~~)`), p = new RegExp(`^ {0,${Math.min(3, y - 1)}}#`);
          for (; e; ) {
            const h = e.split(`
`, 1)[0];
            if ($ = h, this.options.pedantic && ($ = $.replace(/^ {1,4}(?=( {4})*[^ ])/g, "  ")), c.test($) || p.test($) || m.test($) || u.test(e))
              break;
            if ($.search(/[^ ]/) >= y || !$.trim())
              s += `
` + $.slice(y);
            else {
              if (S || f.search(/[^ ]/) >= 4 || c.test(f) || p.test(f) || u.test(f))
                break;
              s += `
` + $;
            }
            !S && !$.trim() && (S = !0), l += h + `
`, e = e.substring(h.length + 1), f = $.slice(y);
          }
        }
        a.loose || (_ ? a.loose = !0 : /\n *\n *$/.test(l) && (_ = !0));
        let b = null, D;
        this.options.gfm && (b = /^\[[ xX]\] /.exec(s), b && (D = b[0] !== "[ ] ", s = s.replace(/^\[[ xX]\] +/, ""))), a.items.push({
          type: "list_item",
          raw: l,
          task: !!b,
          checked: D,
          loose: !1,
          text: s,
          tokens: []
        }), a.raw += l;
      }
      a.items[a.items.length - 1].raw = l.trimEnd(), a.items[a.items.length - 1].text = s.trimEnd(), a.raw = a.raw.trimEnd();
      for (let d = 0; d < a.items.length; d++)
        if (this.lexer.state.top = !1, a.items[d].tokens = this.lexer.blockTokens(a.items[d].text, []), !a.loose) {
          const f = a.items[d].tokens.filter((y) => y.type === "space"), $ = f.length > 0 && f.some((y) => /\n.*\n/.test(y.raw));
          a.loose = $;
        }
      if (a.loose)
        for (let d = 0; d < a.items.length; d++)
          a.items[d].loose = !0;
      return a;
    }
  }
  html(e) {
    const t = this.rules.block.html.exec(e);
    if (t)
      return {
        type: "html",
        block: !0,
        raw: t[0],
        pre: t[1] === "pre" || t[1] === "script" || t[1] === "style",
        text: t[0]
      };
  }
  def(e) {
    const t = this.rules.block.def.exec(e);
    if (t) {
      const n = t[1].toLowerCase().replace(/\s+/g, " "), i = t[2] ? t[2].replace(/^<(.*)>$/, "$1").replace(this.rules.inline.anyPunctuation, "$1") : "", a = t[3] ? t[3].substring(1, t[3].length - 1).replace(this.rules.inline.anyPunctuation, "$1") : t[3];
      return {
        type: "def",
        tag: n,
        raw: t[0],
        href: i,
        title: a
      };
    }
  }
  table(e) {
    const t = this.rules.block.table.exec(e);
    if (!t || !/[:|]/.test(t[2]))
      return;
    const n = Ye(t[1]), i = t[2].replace(/^\||\| *$/g, "").split("|"), a = t[3] && t[3].trim() ? t[3].replace(/\n[ \t]*$/, "").split(`
`) : [], o = {
      type: "table",
      raw: t[0],
      header: [],
      align: [],
      rows: []
    };
    if (n.length === i.length) {
      for (const l of i)
        /^ *-+: *$/.test(l) ? o.align.push("right") : /^ *:-+: *$/.test(l) ? o.align.push("center") : /^ *:-+ *$/.test(l) ? o.align.push("left") : o.align.push(null);
      for (const l of n)
        o.header.push({
          text: l,
          tokens: this.lexer.inline(l)
        });
      for (const l of a)
        o.rows.push(Ye(l, o.header.length).map((s) => ({
          text: s,
          tokens: this.lexer.inline(s)
        })));
      return o;
    }
  }
  lheading(e) {
    const t = this.rules.block.lheading.exec(e);
    if (t)
      return {
        type: "heading",
        raw: t[0],
        depth: t[2].charAt(0) === "=" ? 1 : 2,
        text: t[1],
        tokens: this.lexer.inline(t[1])
      };
  }
  paragraph(e) {
    const t = this.rules.block.paragraph.exec(e);
    if (t) {
      const n = t[1].charAt(t[1].length - 1) === `
` ? t[1].slice(0, -1) : t[1];
      return {
        type: "paragraph",
        raw: t[0],
        text: n,
        tokens: this.lexer.inline(n)
      };
    }
  }
  text(e) {
    const t = this.rules.block.text.exec(e);
    if (t)
      return {
        type: "text",
        raw: t[0],
        text: t[0],
        tokens: this.lexer.inline(t[0])
      };
  }
  escape(e) {
    const t = this.rules.inline.escape.exec(e);
    if (t)
      return {
        type: "escape",
        raw: t[0],
        text: R(t[1])
      };
  }
  tag(e) {
    const t = this.rules.inline.tag.exec(e);
    if (t)
      return !this.lexer.state.inLink && /^<a /i.test(t[0]) ? this.lexer.state.inLink = !0 : this.lexer.state.inLink && /^<\/a>/i.test(t[0]) && (this.lexer.state.inLink = !1), !this.lexer.state.inRawBlock && /^<(pre|code|kbd|script)(\s|>)/i.test(t[0]) ? this.lexer.state.inRawBlock = !0 : this.lexer.state.inRawBlock && /^<\/(pre|code|kbd|script)(\s|>)/i.test(t[0]) && (this.lexer.state.inRawBlock = !1), {
        type: "html",
        raw: t[0],
        inLink: this.lexer.state.inLink,
        inRawBlock: this.lexer.state.inRawBlock,
        block: !1,
        text: t[0]
      };
  }
  link(e) {
    const t = this.rules.inline.link.exec(e);
    if (t) {
      const n = t[2].trim();
      if (!this.options.pedantic && /^</.test(n)) {
        if (!/>$/.test(n))
          return;
        const o = de(n.slice(0, -1), "\\");
        if ((n.length - o.length) % 2 === 0)
          return;
      } else {
        const o = pn(t[2], "()");
        if (o > -1) {
          const s = (t[0].indexOf("!") === 0 ? 5 : 4) + t[1].length + o;
          t[2] = t[2].substring(0, o), t[0] = t[0].substring(0, s).trim(), t[3] = "";
        }
      }
      let i = t[2], a = "";
      if (this.options.pedantic) {
        const o = /^([^'"]*[^\s])\s+(['"])(.*)\2/.exec(i);
        o && (i = o[1], a = o[3]);
      } else
        a = t[3] ? t[3].slice(1, -1) : "";
      return i = i.trim(), /^</.test(i) && (this.options.pedantic && !/>$/.test(n) ? i = i.slice(1) : i = i.slice(1, -1)), Ke(t, {
        href: i && i.replace(this.rules.inline.anyPunctuation, "$1"),
        title: a && a.replace(this.rules.inline.anyPunctuation, "$1")
      }, t[0], this.lexer);
    }
  }
  reflink(e, t) {
    let n;
    if ((n = this.rules.inline.reflink.exec(e)) || (n = this.rules.inline.nolink.exec(e))) {
      const i = (n[2] || n[1]).replace(/\s+/g, " "), a = t[i.toLowerCase()];
      if (!a) {
        const o = n[0].charAt(0);
        return {
          type: "text",
          raw: o,
          text: o
        };
      }
      return Ke(n, a, n[0], this.lexer);
    }
  }
  emStrong(e, t, n = "") {
    let i = this.rules.inline.emStrongLDelim.exec(e);
    if (!i || i[3] && n.match(/[\p{L}\p{N}]/u))
      return;
    if (!(i[1] || i[2] || "") || !n || this.rules.inline.punctuation.exec(n)) {
      const o = [...i[0]].length - 1;
      let l, s, _ = o, d = 0;
      const f = i[0][0] === "*" ? this.rules.inline.emStrongRDelimAst : this.rules.inline.emStrongRDelimUnd;
      for (f.lastIndex = 0, t = t.slice(-1 * e.length + o); (i = f.exec(t)) != null; ) {
        if (l = i[1] || i[2] || i[3] || i[4] || i[5] || i[6], !l)
          continue;
        if (s = [...l].length, i[3] || i[4]) {
          _ += s;
          continue;
        } else if ((i[5] || i[6]) && o % 3 && !((o + s) % 3)) {
          d += s;
          continue;
        }
        if (_ -= s, _ > 0)
          continue;
        s = Math.min(s, s + _ + d);
        const $ = [...i[0]][0].length, y = e.slice(0, o + i.index + $ + s);
        if (Math.min(o, s) % 2) {
          const b = y.slice(1, -1);
          return {
            type: "em",
            raw: y,
            text: b,
            tokens: this.lexer.inlineTokens(b)
          };
        }
        const S = y.slice(2, -2);
        return {
          type: "strong",
          raw: y,
          text: S,
          tokens: this.lexer.inlineTokens(S)
        };
      }
    }
  }
  codespan(e) {
    const t = this.rules.inline.code.exec(e);
    if (t) {
      let n = t[2].replace(/\n/g, " ");
      const i = /[^ ]/.test(n), a = /^ /.test(n) && / $/.test(n);
      return i && a && (n = n.substring(1, n.length - 1)), n = R(n, !0), {
        type: "codespan",
        raw: t[0],
        text: n
      };
    }
  }
  br(e) {
    const t = this.rules.inline.br.exec(e);
    if (t)
      return {
        type: "br",
        raw: t[0]
      };
  }
  del(e) {
    const t = this.rules.inline.del.exec(e);
    if (t)
      return {
        type: "del",
        raw: t[0],
        text: t[2],
        tokens: this.lexer.inlineTokens(t[2])
      };
  }
  autolink(e) {
    const t = this.rules.inline.autolink.exec(e);
    if (t) {
      let n, i;
      return t[2] === "@" ? (n = R(t[1]), i = "mailto:" + n) : (n = R(t[1]), i = n), {
        type: "link",
        raw: t[0],
        text: n,
        href: i,
        tokens: [
          {
            type: "text",
            raw: n,
            text: n
          }
        ]
      };
    }
  }
  url(e) {
    var n;
    let t;
    if (t = this.rules.inline.url.exec(e)) {
      let i, a;
      if (t[2] === "@")
        i = R(t[0]), a = "mailto:" + i;
      else {
        let o;
        do
          o = t[0], t[0] = ((n = this.rules.inline._backpedal.exec(t[0])) == null ? void 0 : n[0]) ?? "";
        while (o !== t[0]);
        i = R(t[0]), t[1] === "www." ? a = "http://" + t[0] : a = t[0];
      }
      return {
        type: "link",
        raw: t[0],
        text: i,
        href: a,
        tokens: [
          {
            type: "text",
            raw: i,
            text: i
          }
        ]
      };
    }
  }
  inlineText(e) {
    const t = this.rules.inline.text.exec(e);
    if (t) {
      let n;
      return this.lexer.state.inRawBlock ? n = t[0] : n = R(t[0]), {
        type: "text",
        raw: t[0],
        text: n
      };
    }
  }
}
const mn = /^(?: *(?:\n|$))+/, gn = /^( {4}[^\n]+(?:\n(?: *(?:\n|$))*)?)+/, fn = /^ {0,3}(`{3,}(?=[^`\n]*(?:\n|$))|~{3,})([^\n]*)(?:\n|$)(?:|([\s\S]*?)(?:\n|$))(?: {0,3}\1[~`]* *(?=\n|$)|$)/, ne = /^ {0,3}((?:-[\t ]*){3,}|(?:_[ \t]*){3,}|(?:\*[ \t]*){3,})(?:\n+|$)/, $n = /^ {0,3}(#{1,6})(?=\s|$)(.*)(?:\n+|$)/, st = /(?:[*+-]|\d{1,9}[.)])/, ut = A(/^(?!bull |blockCode|fences|blockquote|heading|html)((?:.|\n(?!\s*?\n|bull |blockCode|fences|blockquote|heading|html))+?)\n {0,3}(=+|-+) *(?:\n+|$)/).replace(/bull/g, st).replace(/blockCode/g, / {4}/).replace(/fences/g, / {0,3}(?:`{3,}|~{3,})/).replace(/blockquote/g, / {0,3}>/).replace(/heading/g, / {0,3}#{1,6}/).replace(/html/g, / {0,3}<[^\n>]+>\n/).getRegex(), Ae = /^([^\n]+(?:\n(?!hr|heading|lheading|blockquote|fences|list|html|table| +\n)[^\n]+)*)/, Dn = /^[^\n]+/, Ee = /(?!\s*\])(?:\\.|[^\[\]\\])+/, vn = A(/^ {0,3}\[(label)\]: *(?:\n *)?([^<\s][^\s]*|<.*?>)(?:(?: +(?:\n *)?| *\n *)(title))? *(?:\n+|$)/).replace("label", Ee).replace("title", /(?:"(?:\\"?|[^"\\])*"|'[^'\n]*(?:\n[^'\n]+)*\n?'|\([^()]*\))/).getRegex(), Fn = A(/^( {0,3}bull)([ \t][^\n]+?)?(?:\n|$)/).replace(/bull/g, st).getRegex(), fe = "address|article|aside|base|basefont|blockquote|body|caption|center|col|colgroup|dd|details|dialog|dir|div|dl|dt|fieldset|figcaption|figure|footer|form|frame|frameset|h[1-6]|head|header|hr|html|iframe|legend|li|link|main|menu|menuitem|meta|nav|noframes|ol|optgroup|option|p|param|search|section|summary|table|tbody|td|tfoot|th|thead|title|tr|track|ul", Se = /<!--(?:-?>|[\s\S]*?(?:-->|$))/, yn = A("^ {0,3}(?:<(script|pre|style|textarea)[\\s>][\\s\\S]*?(?:</\\1>[^\\n]*\\n+|$)|comment[^\\n]*(\\n+|$)|<\\?[\\s\\S]*?(?:\\?>\\n*|$)|<![A-Z][\\s\\S]*?(?:>\\n*|$)|<!\\[CDATA\\[[\\s\\S]*?(?:\\]\\]>\\n*|$)|</?(tag)(?: +|\\n|/?>)[\\s\\S]*?(?:(?:\\n *)+\\n|$)|<(?!script|pre|style|textarea)([a-z][\\w-]*)(?:attribute)*? */?>(?=[ \\t]*(?:\\n|$))[\\s\\S]*?(?:(?:\\n *)+\\n|$)|</(?!script|pre|style|textarea)[a-z][\\w-]*\\s*>(?=[ \\t]*(?:\\n|$))[\\s\\S]*?(?:(?:\\n *)+\\n|$))", "i").replace("comment", Se).replace("tag", fe).replace("attribute", / +[a-zA-Z:_][\w.:-]*(?: *= *"[^"\n]*"| *= *'[^'\n]*'| *= *[^\s"'=<>`]+)?/).getRegex(), ct = A(Ae).replace("hr", ne).replace("heading", " {0,3}#{1,6}(?:\\s|$)").replace("|lheading", "").replace("|table", "").replace("blockquote", " {0,3}>").replace("fences", " {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n").replace("list", " {0,3}(?:[*+-]|1[.)]) ").replace("html", "</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)").replace("tag", fe).getRegex(), bn = A(/^( {0,3}> ?(paragraph|[^\n]*)(?:\n|$))+/).replace("paragraph", ct).getRegex(), xe = {
  blockquote: bn,
  code: gn,
  def: vn,
  fences: fn,
  heading: $n,
  hr: ne,
  html: yn,
  lheading: ut,
  list: Fn,
  newline: mn,
  paragraph: ct,
  table: J,
  text: Dn
}, Qe = A("^ *([^\\n ].*)\\n {0,3}((?:\\| *)?:?-+:? *(?:\\| *:?-+:? *)*(?:\\| *)?)(?:\\n((?:(?! *\\n|hr|heading|blockquote|code|fences|list|html).*(?:\\n|$))*)\\n*|$)").replace("hr", ne).replace("heading", " {0,3}#{1,6}(?:\\s|$)").replace("blockquote", " {0,3}>").replace("code", " {4}[^\\n]").replace("fences", " {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n").replace("list", " {0,3}(?:[*+-]|1[.)]) ").replace("html", "</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)").replace("tag", fe).getRegex(), wn = {
  ...xe,
  table: Qe,
  paragraph: A(Ae).replace("hr", ne).replace("heading", " {0,3}#{1,6}(?:\\s|$)").replace("|lheading", "").replace("table", Qe).replace("blockquote", " {0,3}>").replace("fences", " {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n").replace("list", " {0,3}(?:[*+-]|1[.)]) ").replace("html", "</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)").replace("tag", fe).getRegex()
}, kn = {
  ...xe,
  html: A(`^ *(?:comment *(?:\\n|\\s*$)|<(tag)[\\s\\S]+?</\\1> *(?:\\n{2,}|\\s*$)|<tag(?:"[^"]*"|'[^']*'|\\s[^'"/>\\s]*)*?/?> *(?:\\n{2,}|\\s*$))`).replace("comment", Se).replace(/tag/g, "(?!(?:a|em|strong|small|s|cite|q|dfn|abbr|data|time|code|var|samp|kbd|sub|sup|i|b|u|mark|ruby|rt|rp|bdi|bdo|span|br|wbr|ins|del|img)\\b)\\w+(?!:|[^\\w\\s@]*@)\\b").getRegex(),
  def: /^ *\[([^\]]+)\]: *<?([^\s>]+)>?(?: +(["(][^\n]+[")]))? *(?:\n+|$)/,
  heading: /^(#{1,6})(.*)(?:\n+|$)/,
  fences: J,
  // fences not supported
  lheading: /^(.+?)\n {0,3}(=+|-+) *(?:\n+|$)/,
  paragraph: A(Ae).replace("hr", ne).replace("heading", ` *#{1,6} *[^
]`).replace("lheading", ut).replace("|table", "").replace("blockquote", " {0,3}>").replace("|fences", "").replace("|list", "").replace("|html", "").replace("|tag", "").getRegex()
}, _t = /^\\([!"#$%&'()*+,\-./:;<=>?@\[\]\\^_`{|}~])/, Cn = /^(`+)([^`]|[^`][\s\S]*?[^`])\1(?!`)/, dt = /^( {2,}|\\)\n(?!\s*$)/, An = /^(`+|[^`])(?:(?= {2,}\n)|[\s\S]*?(?:(?=[\\<!\[`*_]|\b_|$)|[^ ](?= {2,}\n)))/, ie = "\\p{P}\\p{S}", En = A(/^((?![*_])[\spunctuation])/, "u").replace(/punctuation/g, ie).getRegex(), Sn = /\[[^[\]]*?\]\([^\(\)]*?\)|`[^`]*?`|<[^<>]*?>/g, xn = A(/^(?:\*+(?:((?!\*)[punct])|[^\s*]))|^_+(?:((?!_)[punct])|([^\s_]))/, "u").replace(/punct/g, ie).getRegex(), Bn = A("^[^_*]*?__[^_*]*?\\*[^_*]*?(?=__)|[^*]+(?=[^*])|(?!\\*)[punct](\\*+)(?=[\\s]|$)|[^punct\\s](\\*+)(?!\\*)(?=[punct\\s]|$)|(?!\\*)[punct\\s](\\*+)(?=[^punct\\s])|[\\s](\\*+)(?!\\*)(?=[punct])|(?!\\*)[punct](\\*+)(?!\\*)(?=[punct])|[^punct\\s](\\*+)(?=[^punct\\s])", "gu").replace(/punct/g, ie).getRegex(), qn = A("^[^_*]*?\\*\\*[^_*]*?_[^_*]*?(?=\\*\\*)|[^_]+(?=[^_])|(?!_)[punct](_+)(?=[\\s]|$)|[^punct\\s](_+)(?!_)(?=[punct\\s]|$)|(?!_)[punct\\s](_+)(?=[^punct\\s])|[\\s](_+)(?!_)(?=[punct])|(?!_)[punct](_+)(?!_)(?=[punct])", "gu").replace(/punct/g, ie).getRegex(), Tn = A(/\\([punct])/, "gu").replace(/punct/g, ie).getRegex(), Rn = A(/^<(scheme:[^\s\x00-\x1f<>]*|email)>/).replace("scheme", /[a-zA-Z][a-zA-Z0-9+.-]{1,31}/).replace("email", /[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+(@)[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+(?![-_])/).getRegex(), In = A(Se).replace("(?:-->|$)", "-->").getRegex(), zn = A("^comment|^</[a-zA-Z][\\w:-]*\\s*>|^<[a-zA-Z][\\w-]*(?:attribute)*?\\s*/?>|^<\\?[\\s\\S]*?\\?>|^<![a-zA-Z]+\\s[\\s\\S]*?>|^<!\\[CDATA\\[[\\s\\S]*?\\]\\]>").replace("comment", In).replace("attribute", /\s+[a-zA-Z:_][\w.:-]*(?:\s*=\s*"[^"]*"|\s*=\s*'[^']*'|\s*=\s*[^\s"'=<>`]+)?/).getRegex(), me = /(?:\[(?:\\.|[^\[\]\\])*\]|\\.|`[^`]*`|[^\[\]\\`])*?/, Ln = A(/^!?\[(label)\]\(\s*(href)(?:\s+(title))?\s*\)/).replace("label", me).replace("href", /<(?:\\.|[^\n<>\\])+>|[^\s\x00-\x1f]*/).replace("title", /"(?:\\"?|[^"\\])*"|'(?:\\'?|[^'\\])*'|\((?:\\\)?|[^)\\])*\)/).getRegex(), pt = A(/^!?\[(label)\]\[(ref)\]/).replace("label", me).replace("ref", Ee).getRegex(), ht = A(/^!?\[(ref)\](?:\[\])?/).replace("ref", Ee).getRegex(), On = A("reflink|nolink(?!\\()", "g").replace("reflink", pt).replace("nolink", ht).getRegex(), Be = {
  _backpedal: J,
  // only used for GFM url
  anyPunctuation: Tn,
  autolink: Rn,
  blockSkip: Sn,
  br: dt,
  code: Cn,
  del: J,
  emStrongLDelim: xn,
  emStrongRDelimAst: Bn,
  emStrongRDelimUnd: qn,
  escape: _t,
  link: Ln,
  nolink: ht,
  punctuation: En,
  reflink: pt,
  reflinkSearch: On,
  tag: zn,
  text: An,
  url: J
}, Pn = {
  ...Be,
  link: A(/^!?\[(label)\]\((.*?)\)/).replace("label", me).getRegex(),
  reflink: A(/^!?\[(label)\]\s*\[([^\]]*)\]/).replace("label", me).getRegex()
}, we = {
  ...Be,
  escape: A(_t).replace("])", "~|])").getRegex(),
  url: A(/^((?:ftp|https?):\/\/|www\.)(?:[a-zA-Z0-9\-]+\.?)+[^\s<]*|^email/, "i").replace("email", /[A-Za-z0-9._+-]+(@)[a-zA-Z0-9-_]+(?:\.[a-zA-Z0-9-_]*[a-zA-Z0-9])+(?![-_])/).getRegex(),
  _backpedal: /(?:[^?!.,:;*_'"~()&]+|\([^)]*\)|&(?![a-zA-Z0-9]+;$)|[?!.,:;*_'"~)]+(?!$))+/,
  del: /^(~~?)(?=[^\s~])([\s\S]*?[^\s~])\1(?=[^~]|$)/,
  text: /^([`~]+|[^`~])(?:(?= {2,}\n)|(?=[a-zA-Z0-9.!#$%&'*+\/=?_`{\|}~-]+@)|[\s\S]*?(?:(?=[\\<!\[`*~_]|\b_|https?:\/\/|ftp:\/\/|www\.|$)|[^ ](?= {2,}\n)|[^a-zA-Z0-9.!#$%&'*+\/=?_`{\|}~-](?=[a-zA-Z0-9.!#$%&'*+\/=?_`{\|}~-]+@)))/
}, Nn = {
  ...we,
  br: A(dt).replace("{2,}", "*").getRegex(),
  text: A(we.text).replace("\\b_", "\\b_| {2,}\\n").replace(/\{2,\}/g, "*").getRegex()
}, pe = {
  normal: xe,
  gfm: wn,
  pedantic: kn
}, Q = {
  normal: Be,
  gfm: we,
  breaks: Nn,
  pedantic: Pn
};
class P {
  constructor(e) {
    E(this, "tokens");
    E(this, "options");
    E(this, "state");
    E(this, "tokenizer");
    E(this, "inlineQueue");
    this.tokens = [], this.tokens.links = /* @__PURE__ */ Object.create(null), this.options = e || Z, this.options.tokenizer = this.options.tokenizer || new he(), this.tokenizer = this.options.tokenizer, this.tokenizer.options = this.options, this.tokenizer.lexer = this, this.inlineQueue = [], this.state = {
      inLink: !1,
      inRawBlock: !1,
      top: !0
    };
    const t = {
      block: pe.normal,
      inline: Q.normal
    };
    this.options.pedantic ? (t.block = pe.pedantic, t.inline = Q.pedantic) : this.options.gfm && (t.block = pe.gfm, this.options.breaks ? t.inline = Q.breaks : t.inline = Q.gfm), this.tokenizer.rules = t;
  }
  /**
   * Expose Rules
   */
  static get rules() {
    return {
      block: pe,
      inline: Q
    };
  }
  /**
   * Static Lex Method
   */
  static lex(e, t) {
    return new P(t).lex(e);
  }
  /**
   * Static Lex Inline Method
   */
  static lexInline(e, t) {
    return new P(t).inlineTokens(e);
  }
  /**
   * Preprocessing
   */
  lex(e) {
    e = e.replace(/\r\n|\r/g, `
`), this.blockTokens(e, this.tokens);
    for (let t = 0; t < this.inlineQueue.length; t++) {
      const n = this.inlineQueue[t];
      this.inlineTokens(n.src, n.tokens);
    }
    return this.inlineQueue = [], this.tokens;
  }
  blockTokens(e, t = []) {
    this.options.pedantic ? e = e.replace(/\t/g, "    ").replace(/^ +$/gm, "") : e = e.replace(/^( *)(\t+)/gm, (l, s, _) => s + "    ".repeat(_.length));
    let n, i, a, o;
    for (; e; )
      if (!(this.options.extensions && this.options.extensions.block && this.options.extensions.block.some((l) => (n = l.call({ lexer: this }, e, t)) ? (e = e.substring(n.raw.length), t.push(n), !0) : !1))) {
        if (n = this.tokenizer.space(e)) {
          e = e.substring(n.raw.length), n.raw.length === 1 && t.length > 0 ? t[t.length - 1].raw += `
` : t.push(n);
          continue;
        }
        if (n = this.tokenizer.code(e)) {
          e = e.substring(n.raw.length), i = t[t.length - 1], i && (i.type === "paragraph" || i.type === "text") ? (i.raw += `
` + n.raw, i.text += `
` + n.text, this.inlineQueue[this.inlineQueue.length - 1].src = i.text) : t.push(n);
          continue;
        }
        if (n = this.tokenizer.fences(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.heading(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.hr(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.blockquote(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.list(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.html(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.def(e)) {
          e = e.substring(n.raw.length), i = t[t.length - 1], i && (i.type === "paragraph" || i.type === "text") ? (i.raw += `
` + n.raw, i.text += `
` + n.raw, this.inlineQueue[this.inlineQueue.length - 1].src = i.text) : this.tokens.links[n.tag] || (this.tokens.links[n.tag] = {
            href: n.href,
            title: n.title
          });
          continue;
        }
        if (n = this.tokenizer.table(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.lheading(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (a = e, this.options.extensions && this.options.extensions.startBlock) {
          let l = 1 / 0;
          const s = e.slice(1);
          let _;
          this.options.extensions.startBlock.forEach((d) => {
            _ = d.call({ lexer: this }, s), typeof _ == "number" && _ >= 0 && (l = Math.min(l, _));
          }), l < 1 / 0 && l >= 0 && (a = e.substring(0, l + 1));
        }
        if (this.state.top && (n = this.tokenizer.paragraph(a))) {
          i = t[t.length - 1], o && i.type === "paragraph" ? (i.raw += `
` + n.raw, i.text += `
` + n.text, this.inlineQueue.pop(), this.inlineQueue[this.inlineQueue.length - 1].src = i.text) : t.push(n), o = a.length !== e.length, e = e.substring(n.raw.length);
          continue;
        }
        if (n = this.tokenizer.text(e)) {
          e = e.substring(n.raw.length), i = t[t.length - 1], i && i.type === "text" ? (i.raw += `
` + n.raw, i.text += `
` + n.text, this.inlineQueue.pop(), this.inlineQueue[this.inlineQueue.length - 1].src = i.text) : t.push(n);
          continue;
        }
        if (e) {
          const l = "Infinite loop on byte: " + e.charCodeAt(0);
          if (this.options.silent) {
            console.error(l);
            break;
          } else
            throw new Error(l);
        }
      }
    return this.state.top = !0, t;
  }
  inline(e, t = []) {
    return this.inlineQueue.push({ src: e, tokens: t }), t;
  }
  /**
   * Lexing/Compiling
   */
  inlineTokens(e, t = []) {
    let n, i, a, o = e, l, s, _;
    if (this.tokens.links) {
      const d = Object.keys(this.tokens.links);
      if (d.length > 0)
        for (; (l = this.tokenizer.rules.inline.reflinkSearch.exec(o)) != null; )
          d.includes(l[0].slice(l[0].lastIndexOf("[") + 1, -1)) && (o = o.slice(0, l.index) + "[" + "a".repeat(l[0].length - 2) + "]" + o.slice(this.tokenizer.rules.inline.reflinkSearch.lastIndex));
    }
    for (; (l = this.tokenizer.rules.inline.blockSkip.exec(o)) != null; )
      o = o.slice(0, l.index) + "[" + "a".repeat(l[0].length - 2) + "]" + o.slice(this.tokenizer.rules.inline.blockSkip.lastIndex);
    for (; (l = this.tokenizer.rules.inline.anyPunctuation.exec(o)) != null; )
      o = o.slice(0, l.index) + "++" + o.slice(this.tokenizer.rules.inline.anyPunctuation.lastIndex);
    for (; e; )
      if (s || (_ = ""), s = !1, !(this.options.extensions && this.options.extensions.inline && this.options.extensions.inline.some((d) => (n = d.call({ lexer: this }, e, t)) ? (e = e.substring(n.raw.length), t.push(n), !0) : !1))) {
        if (n = this.tokenizer.escape(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.tag(e)) {
          e = e.substring(n.raw.length), i = t[t.length - 1], i && n.type === "text" && i.type === "text" ? (i.raw += n.raw, i.text += n.text) : t.push(n);
          continue;
        }
        if (n = this.tokenizer.link(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.reflink(e, this.tokens.links)) {
          e = e.substring(n.raw.length), i = t[t.length - 1], i && n.type === "text" && i.type === "text" ? (i.raw += n.raw, i.text += n.text) : t.push(n);
          continue;
        }
        if (n = this.tokenizer.emStrong(e, o, _)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.codespan(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.br(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.del(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.autolink(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (!this.state.inLink && (n = this.tokenizer.url(e))) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (a = e, this.options.extensions && this.options.extensions.startInline) {
          let d = 1 / 0;
          const f = e.slice(1);
          let $;
          this.options.extensions.startInline.forEach((y) => {
            $ = y.call({ lexer: this }, f), typeof $ == "number" && $ >= 0 && (d = Math.min(d, $));
          }), d < 1 / 0 && d >= 0 && (a = e.substring(0, d + 1));
        }
        if (n = this.tokenizer.inlineText(a)) {
          e = e.substring(n.raw.length), n.raw.slice(-1) !== "_" && (_ = n.raw.slice(-1)), s = !0, i = t[t.length - 1], i && i.type === "text" ? (i.raw += n.raw, i.text += n.text) : t.push(n);
          continue;
        }
        if (e) {
          const d = "Infinite loop on byte: " + e.charCodeAt(0);
          if (this.options.silent) {
            console.error(d);
            break;
          } else
            throw new Error(d);
        }
      }
    return t;
  }
}
class ge {
  constructor(e) {
    E(this, "options");
    this.options = e || Z;
  }
  code(e, t, n) {
    var a;
    const i = (a = (t || "").match(/^\S*/)) == null ? void 0 : a[0];
    return e = e.replace(/\n$/, "") + `
`, i ? '<pre><code class="language-' + R(i) + '">' + (n ? e : R(e, !0)) + `</code></pre>
` : "<pre><code>" + (n ? e : R(e, !0)) + `</code></pre>
`;
  }
  blockquote(e) {
    return `<blockquote>
${e}</blockquote>
`;
  }
  html(e, t) {
    return e;
  }
  heading(e, t, n) {
    return `<h${t}>${e}</h${t}>
`;
  }
  hr() {
    return `<hr>
`;
  }
  list(e, t, n) {
    const i = t ? "ol" : "ul", a = t && n !== 1 ? ' start="' + n + '"' : "";
    return "<" + i + a + `>
` + e + "</" + i + `>
`;
  }
  listitem(e, t, n) {
    return `<li>${e}</li>
`;
  }
  checkbox(e) {
    return "<input " + (e ? 'checked="" ' : "") + 'disabled="" type="checkbox">';
  }
  paragraph(e) {
    return `<p>${e}</p>
`;
  }
  table(e, t) {
    return t && (t = `<tbody>${t}</tbody>`), `<table>
<thead>
` + e + `</thead>
` + t + `</table>
`;
  }
  tablerow(e) {
    return `<tr>
${e}</tr>
`;
  }
  tablecell(e, t) {
    const n = t.header ? "th" : "td";
    return (t.align ? `<${n} align="${t.align}">` : `<${n}>`) + e + `</${n}>
`;
  }
  /**
   * span level renderer
   */
  strong(e) {
    return `<strong>${e}</strong>`;
  }
  em(e) {
    return `<em>${e}</em>`;
  }
  codespan(e) {
    return `<code>${e}</code>`;
  }
  br() {
    return "<br>";
  }
  del(e) {
    return `<del>${e}</del>`;
  }
  link(e, t, n) {
    const i = We(e);
    if (i === null)
      return n;
    e = i;
    let a = '<a href="' + e + '"';
    return t && (a += ' title="' + t + '"'), a += ">" + n + "</a>", a;
  }
  image(e, t, n) {
    const i = We(e);
    if (i === null)
      return n;
    e = i;
    let a = `<img src="${e}" alt="${n}"`;
    return t && (a += ` title="${t}"`), a += ">", a;
  }
  text(e) {
    return e;
  }
}
class qe {
  // no need for block level renderers
  strong(e) {
    return e;
  }
  em(e) {
    return e;
  }
  codespan(e) {
    return e;
  }
  del(e) {
    return e;
  }
  html(e) {
    return e;
  }
  text(e) {
    return e;
  }
  link(e, t, n) {
    return "" + n;
  }
  image(e, t, n) {
    return "" + n;
  }
  br() {
    return "";
  }
}
class N {
  constructor(e) {
    E(this, "options");
    E(this, "renderer");
    E(this, "textRenderer");
    this.options = e || Z, this.options.renderer = this.options.renderer || new ge(), this.renderer = this.options.renderer, this.renderer.options = this.options, this.textRenderer = new qe();
  }
  /**
   * Static Parse Method
   */
  static parse(e, t) {
    return new N(t).parse(e);
  }
  /**
   * Static Parse Inline Method
   */
  static parseInline(e, t) {
    return new N(t).parseInline(e);
  }
  /**
   * Parse Loop
   */
  parse(e, t = !0) {
    let n = "";
    for (let i = 0; i < e.length; i++) {
      const a = e[i];
      if (this.options.extensions && this.options.extensions.renderers && this.options.extensions.renderers[a.type]) {
        const o = a, l = this.options.extensions.renderers[o.type].call({ parser: this }, o);
        if (l !== !1 || !["space", "hr", "heading", "code", "table", "blockquote", "list", "html", "paragraph", "text"].includes(o.type)) {
          n += l || "";
          continue;
        }
      }
      switch (a.type) {
        case "space":
          continue;
        case "hr": {
          n += this.renderer.hr();
          continue;
        }
        case "heading": {
          const o = a;
          n += this.renderer.heading(this.parseInline(o.tokens), o.depth, _n(this.parseInline(o.tokens, this.textRenderer)));
          continue;
        }
        case "code": {
          const o = a;
          n += this.renderer.code(o.text, o.lang, !!o.escaped);
          continue;
        }
        case "table": {
          const o = a;
          let l = "", s = "";
          for (let d = 0; d < o.header.length; d++)
            s += this.renderer.tablecell(this.parseInline(o.header[d].tokens), { header: !0, align: o.align[d] });
          l += this.renderer.tablerow(s);
          let _ = "";
          for (let d = 0; d < o.rows.length; d++) {
            const f = o.rows[d];
            s = "";
            for (let $ = 0; $ < f.length; $++)
              s += this.renderer.tablecell(this.parseInline(f[$].tokens), { header: !1, align: o.align[$] });
            _ += this.renderer.tablerow(s);
          }
          n += this.renderer.table(l, _);
          continue;
        }
        case "blockquote": {
          const o = a, l = this.parse(o.tokens);
          n += this.renderer.blockquote(l);
          continue;
        }
        case "list": {
          const o = a, l = o.ordered, s = o.start, _ = o.loose;
          let d = "";
          for (let f = 0; f < o.items.length; f++) {
            const $ = o.items[f], y = $.checked, S = $.task;
            let b = "";
            if ($.task) {
              const D = this.renderer.checkbox(!!y);
              _ ? $.tokens.length > 0 && $.tokens[0].type === "paragraph" ? ($.tokens[0].text = D + " " + $.tokens[0].text, $.tokens[0].tokens && $.tokens[0].tokens.length > 0 && $.tokens[0].tokens[0].type === "text" && ($.tokens[0].tokens[0].text = D + " " + $.tokens[0].tokens[0].text)) : $.tokens.unshift({
                type: "text",
                text: D + " "
              }) : b += D + " ";
            }
            b += this.parse($.tokens, _), d += this.renderer.listitem(b, S, !!y);
          }
          n += this.renderer.list(d, l, s);
          continue;
        }
        case "html": {
          const o = a;
          n += this.renderer.html(o.text, o.block);
          continue;
        }
        case "paragraph": {
          const o = a;
          n += this.renderer.paragraph(this.parseInline(o.tokens));
          continue;
        }
        case "text": {
          let o = a, l = o.tokens ? this.parseInline(o.tokens) : o.text;
          for (; i + 1 < e.length && e[i + 1].type === "text"; )
            o = e[++i], l += `
` + (o.tokens ? this.parseInline(o.tokens) : o.text);
          n += t ? this.renderer.paragraph(l) : l;
          continue;
        }
        default: {
          const o = 'Token with "' + a.type + '" type was not found.';
          if (this.options.silent)
            return console.error(o), "";
          throw new Error(o);
        }
      }
    }
    return n;
  }
  /**
   * Parse Inline Tokens
   */
  parseInline(e, t) {
    t = t || this.renderer;
    let n = "";
    for (let i = 0; i < e.length; i++) {
      const a = e[i];
      if (this.options.extensions && this.options.extensions.renderers && this.options.extensions.renderers[a.type]) {
        const o = this.options.extensions.renderers[a.type].call({ parser: this }, a);
        if (o !== !1 || !["escape", "html", "link", "image", "strong", "em", "codespan", "br", "del", "text"].includes(a.type)) {
          n += o || "";
          continue;
        }
      }
      switch (a.type) {
        case "escape": {
          const o = a;
          n += t.text(o.text);
          break;
        }
        case "html": {
          const o = a;
          n += t.html(o.text);
          break;
        }
        case "link": {
          const o = a;
          n += t.link(o.href, o.title, this.parseInline(o.tokens, t));
          break;
        }
        case "image": {
          const o = a;
          n += t.image(o.href, o.title, o.text);
          break;
        }
        case "strong": {
          const o = a;
          n += t.strong(this.parseInline(o.tokens, t));
          break;
        }
        case "em": {
          const o = a;
          n += t.em(this.parseInline(o.tokens, t));
          break;
        }
        case "codespan": {
          const o = a;
          n += t.codespan(o.text);
          break;
        }
        case "br": {
          n += t.br();
          break;
        }
        case "del": {
          const o = a;
          n += t.del(this.parseInline(o.tokens, t));
          break;
        }
        case "text": {
          const o = a;
          n += t.text(o.text);
          break;
        }
        default: {
          const o = 'Token with "' + a.type + '" type was not found.';
          if (this.options.silent)
            return console.error(o), "";
          throw new Error(o);
        }
      }
    }
    return n;
  }
}
class ee {
  constructor(e) {
    E(this, "options");
    this.options = e || Z;
  }
  /**
   * Process markdown before marked
   */
  preprocess(e) {
    return e;
  }
  /**
   * Process HTML after marked is finished
   */
  postprocess(e) {
    return e;
  }
  /**
   * Process all tokens before walk tokens
   */
  processAllTokens(e) {
    return e;
  }
}
E(ee, "passThroughHooks", /* @__PURE__ */ new Set([
  "preprocess",
  "postprocess",
  "processAllTokens"
]));
var G, ke, mt;
class Mn {
  constructor(...e) {
    ye(this, G);
    E(this, "defaults", Ce());
    E(this, "options", this.setOptions);
    E(this, "parse", ce(this, G, ke).call(this, P.lex, N.parse));
    E(this, "parseInline", ce(this, G, ke).call(this, P.lexInline, N.parseInline));
    E(this, "Parser", N);
    E(this, "Renderer", ge);
    E(this, "TextRenderer", qe);
    E(this, "Lexer", P);
    E(this, "Tokenizer", he);
    E(this, "Hooks", ee);
    this.use(...e);
  }
  /**
   * Run callback for every token
   */
  walkTokens(e, t) {
    var i, a;
    let n = [];
    for (const o of e)
      switch (n = n.concat(t.call(this, o)), o.type) {
        case "table": {
          const l = o;
          for (const s of l.header)
            n = n.concat(this.walkTokens(s.tokens, t));
          for (const s of l.rows)
            for (const _ of s)
              n = n.concat(this.walkTokens(_.tokens, t));
          break;
        }
        case "list": {
          const l = o;
          n = n.concat(this.walkTokens(l.items, t));
          break;
        }
        default: {
          const l = o;
          (a = (i = this.defaults.extensions) == null ? void 0 : i.childTokens) != null && a[l.type] ? this.defaults.extensions.childTokens[l.type].forEach((s) => {
            const _ = l[s].flat(1 / 0);
            n = n.concat(this.walkTokens(_, t));
          }) : l.tokens && (n = n.concat(this.walkTokens(l.tokens, t)));
        }
      }
    return n;
  }
  use(...e) {
    const t = this.defaults.extensions || { renderers: {}, childTokens: {} };
    return e.forEach((n) => {
      const i = { ...n };
      if (i.async = this.defaults.async || i.async || !1, n.extensions && (n.extensions.forEach((a) => {
        if (!a.name)
          throw new Error("extension name required");
        if ("renderer" in a) {
          const o = t.renderers[a.name];
          o ? t.renderers[a.name] = function(...l) {
            let s = a.renderer.apply(this, l);
            return s === !1 && (s = o.apply(this, l)), s;
          } : t.renderers[a.name] = a.renderer;
        }
        if ("tokenizer" in a) {
          if (!a.level || a.level !== "block" && a.level !== "inline")
            throw new Error("extension level must be 'block' or 'inline'");
          const o = t[a.level];
          o ? o.unshift(a.tokenizer) : t[a.level] = [a.tokenizer], a.start && (a.level === "block" ? t.startBlock ? t.startBlock.push(a.start) : t.startBlock = [a.start] : a.level === "inline" && (t.startInline ? t.startInline.push(a.start) : t.startInline = [a.start]));
        }
        "childTokens" in a && a.childTokens && (t.childTokens[a.name] = a.childTokens);
      }), i.extensions = t), n.renderer) {
        const a = this.defaults.renderer || new ge(this.defaults);
        for (const o in n.renderer) {
          if (!(o in a))
            throw new Error(`renderer '${o}' does not exist`);
          if (o === "options")
            continue;
          const l = o, s = n.renderer[l], _ = a[l];
          a[l] = (...d) => {
            let f = s.apply(a, d);
            return f === !1 && (f = _.apply(a, d)), f || "";
          };
        }
        i.renderer = a;
      }
      if (n.tokenizer) {
        const a = this.defaults.tokenizer || new he(this.defaults);
        for (const o in n.tokenizer) {
          if (!(o in a))
            throw new Error(`tokenizer '${o}' does not exist`);
          if (["options", "rules", "lexer"].includes(o))
            continue;
          const l = o, s = n.tokenizer[l], _ = a[l];
          a[l] = (...d) => {
            let f = s.apply(a, d);
            return f === !1 && (f = _.apply(a, d)), f;
          };
        }
        i.tokenizer = a;
      }
      if (n.hooks) {
        const a = this.defaults.hooks || new ee();
        for (const o in n.hooks) {
          if (!(o in a))
            throw new Error(`hook '${o}' does not exist`);
          if (o === "options")
            continue;
          const l = o, s = n.hooks[l], _ = a[l];
          ee.passThroughHooks.has(o) ? a[l] = (d) => {
            if (this.defaults.async)
              return Promise.resolve(s.call(a, d)).then(($) => _.call(a, $));
            const f = s.call(a, d);
            return _.call(a, f);
          } : a[l] = (...d) => {
            let f = s.apply(a, d);
            return f === !1 && (f = _.apply(a, d)), f;
          };
        }
        i.hooks = a;
      }
      if (n.walkTokens) {
        const a = this.defaults.walkTokens, o = n.walkTokens;
        i.walkTokens = function(l) {
          let s = [];
          return s.push(o.call(this, l)), a && (s = s.concat(a.call(this, l))), s;
        };
      }
      this.defaults = { ...this.defaults, ...i };
    }), this;
  }
  setOptions(e) {
    return this.defaults = { ...this.defaults, ...e }, this;
  }
  lexer(e, t) {
    return P.lex(e, t ?? this.defaults);
  }
  parser(e, t) {
    return N.parse(e, t ?? this.defaults);
  }
}
G = new WeakSet(), ke = function(e, t) {
  return (n, i) => {
    const a = { ...i }, o = { ...this.defaults, ...a };
    this.defaults.async === !0 && a.async === !1 && (o.silent || console.warn("marked(): The async option was set to true by an extension. The async: false option sent to parse will be ignored."), o.async = !0);
    const l = ce(this, G, mt).call(this, !!o.silent, !!o.async);
    if (typeof n > "u" || n === null)
      return l(new Error("marked(): input parameter is undefined or null"));
    if (typeof n != "string")
      return l(new Error("marked(): input parameter is of type " + Object.prototype.toString.call(n) + ", string expected"));
    if (o.hooks && (o.hooks.options = o), o.async)
      return Promise.resolve(o.hooks ? o.hooks.preprocess(n) : n).then((s) => e(s, o)).then((s) => o.hooks ? o.hooks.processAllTokens(s) : s).then((s) => o.walkTokens ? Promise.all(this.walkTokens(s, o.walkTokens)).then(() => s) : s).then((s) => t(s, o)).then((s) => o.hooks ? o.hooks.postprocess(s) : s).catch(l);
    try {
      o.hooks && (n = o.hooks.preprocess(n));
      let s = e(n, o);
      o.hooks && (s = o.hooks.processAllTokens(s)), o.walkTokens && this.walkTokens(s, o.walkTokens);
      let _ = t(s, o);
      return o.hooks && (_ = o.hooks.postprocess(_)), _;
    } catch (s) {
      return l(s);
    }
  };
}, mt = function(e, t) {
  return (n) => {
    if (n.message += `
Please report this to https://github.com/markedjs/marked.`, e) {
      const i = "<p>An error occurred:</p><pre>" + R(n.message + "", !0) + "</pre>";
      return t ? Promise.resolve(i) : i;
    }
    if (t)
      return Promise.reject(n);
    throw n;
  };
};
const U = new Mn();
function C(r, e) {
  return U.parse(r, e);
}
C.options = C.setOptions = function(r) {
  return U.setOptions(r), C.defaults = U.defaults, ot(C.defaults), C;
};
C.getDefaults = Ce;
C.defaults = Z;
C.use = function(...r) {
  return U.use(...r), C.defaults = U.defaults, ot(C.defaults), C;
};
C.walkTokens = function(r, e) {
  return U.walkTokens(r, e);
};
C.parseInline = U.parseInline;
C.Parser = N;
C.parser = N.parse;
C.Renderer = ge;
C.TextRenderer = qe;
C.Lexer = P;
C.lexer = P.lex;
C.Tokenizer = he;
C.Hooks = ee;
C.parse = C;
C.options;
C.setOptions;
C.use;
C.walkTokens;
C.parseInline;
N.parse;
P.lex;
const jn = /[\0-\x1F!-,\.\/:-@\[-\^`\{-\xA9\xAB-\xB4\xB6-\xB9\xBB-\xBF\xD7\xF7\u02C2-\u02C5\u02D2-\u02DF\u02E5-\u02EB\u02ED\u02EF-\u02FF\u0375\u0378\u0379\u037E\u0380-\u0385\u0387\u038B\u038D\u03A2\u03F6\u0482\u0530\u0557\u0558\u055A-\u055F\u0589-\u0590\u05BE\u05C0\u05C3\u05C6\u05C8-\u05CF\u05EB-\u05EE\u05F3-\u060F\u061B-\u061F\u066A-\u066D\u06D4\u06DD\u06DE\u06E9\u06FD\u06FE\u0700-\u070F\u074B\u074C\u07B2-\u07BF\u07F6-\u07F9\u07FB\u07FC\u07FE\u07FF\u082E-\u083F\u085C-\u085F\u086B-\u089F\u08B5\u08C8-\u08D2\u08E2\u0964\u0965\u0970\u0984\u098D\u098E\u0991\u0992\u09A9\u09B1\u09B3-\u09B5\u09BA\u09BB\u09C5\u09C6\u09C9\u09CA\u09CF-\u09D6\u09D8-\u09DB\u09DE\u09E4\u09E5\u09F2-\u09FB\u09FD\u09FF\u0A00\u0A04\u0A0B-\u0A0E\u0A11\u0A12\u0A29\u0A31\u0A34\u0A37\u0A3A\u0A3B\u0A3D\u0A43-\u0A46\u0A49\u0A4A\u0A4E-\u0A50\u0A52-\u0A58\u0A5D\u0A5F-\u0A65\u0A76-\u0A80\u0A84\u0A8E\u0A92\u0AA9\u0AB1\u0AB4\u0ABA\u0ABB\u0AC6\u0ACA\u0ACE\u0ACF\u0AD1-\u0ADF\u0AE4\u0AE5\u0AF0-\u0AF8\u0B00\u0B04\u0B0D\u0B0E\u0B11\u0B12\u0B29\u0B31\u0B34\u0B3A\u0B3B\u0B45\u0B46\u0B49\u0B4A\u0B4E-\u0B54\u0B58-\u0B5B\u0B5E\u0B64\u0B65\u0B70\u0B72-\u0B81\u0B84\u0B8B-\u0B8D\u0B91\u0B96-\u0B98\u0B9B\u0B9D\u0BA0-\u0BA2\u0BA5-\u0BA7\u0BAB-\u0BAD\u0BBA-\u0BBD\u0BC3-\u0BC5\u0BC9\u0BCE\u0BCF\u0BD1-\u0BD6\u0BD8-\u0BE5\u0BF0-\u0BFF\u0C0D\u0C11\u0C29\u0C3A-\u0C3C\u0C45\u0C49\u0C4E-\u0C54\u0C57\u0C5B-\u0C5F\u0C64\u0C65\u0C70-\u0C7F\u0C84\u0C8D\u0C91\u0CA9\u0CB4\u0CBA\u0CBB\u0CC5\u0CC9\u0CCE-\u0CD4\u0CD7-\u0CDD\u0CDF\u0CE4\u0CE5\u0CF0\u0CF3-\u0CFF\u0D0D\u0D11\u0D45\u0D49\u0D4F-\u0D53\u0D58-\u0D5E\u0D64\u0D65\u0D70-\u0D79\u0D80\u0D84\u0D97-\u0D99\u0DB2\u0DBC\u0DBE\u0DBF\u0DC7-\u0DC9\u0DCB-\u0DCE\u0DD5\u0DD7\u0DE0-\u0DE5\u0DF0\u0DF1\u0DF4-\u0E00\u0E3B-\u0E3F\u0E4F\u0E5A-\u0E80\u0E83\u0E85\u0E8B\u0EA4\u0EA6\u0EBE\u0EBF\u0EC5\u0EC7\u0ECE\u0ECF\u0EDA\u0EDB\u0EE0-\u0EFF\u0F01-\u0F17\u0F1A-\u0F1F\u0F2A-\u0F34\u0F36\u0F38\u0F3A-\u0F3D\u0F48\u0F6D-\u0F70\u0F85\u0F98\u0FBD-\u0FC5\u0FC7-\u0FFF\u104A-\u104F\u109E\u109F\u10C6\u10C8-\u10CC\u10CE\u10CF\u10FB\u1249\u124E\u124F\u1257\u1259\u125E\u125F\u1289\u128E\u128F\u12B1\u12B6\u12B7\u12BF\u12C1\u12C6\u12C7\u12D7\u1311\u1316\u1317\u135B\u135C\u1360-\u137F\u1390-\u139F\u13F6\u13F7\u13FE-\u1400\u166D\u166E\u1680\u169B-\u169F\u16EB-\u16ED\u16F9-\u16FF\u170D\u1715-\u171F\u1735-\u173F\u1754-\u175F\u176D\u1771\u1774-\u177F\u17D4-\u17D6\u17D8-\u17DB\u17DE\u17DF\u17EA-\u180A\u180E\u180F\u181A-\u181F\u1879-\u187F\u18AB-\u18AF\u18F6-\u18FF\u191F\u192C-\u192F\u193C-\u1945\u196E\u196F\u1975-\u197F\u19AC-\u19AF\u19CA-\u19CF\u19DA-\u19FF\u1A1C-\u1A1F\u1A5F\u1A7D\u1A7E\u1A8A-\u1A8F\u1A9A-\u1AA6\u1AA8-\u1AAF\u1AC1-\u1AFF\u1B4C-\u1B4F\u1B5A-\u1B6A\u1B74-\u1B7F\u1BF4-\u1BFF\u1C38-\u1C3F\u1C4A-\u1C4C\u1C7E\u1C7F\u1C89-\u1C8F\u1CBB\u1CBC\u1CC0-\u1CCF\u1CD3\u1CFB-\u1CFF\u1DFA\u1F16\u1F17\u1F1E\u1F1F\u1F46\u1F47\u1F4E\u1F4F\u1F58\u1F5A\u1F5C\u1F5E\u1F7E\u1F7F\u1FB5\u1FBD\u1FBF-\u1FC1\u1FC5\u1FCD-\u1FCF\u1FD4\u1FD5\u1FDC-\u1FDF\u1FED-\u1FF1\u1FF5\u1FFD-\u203E\u2041-\u2053\u2055-\u2070\u2072-\u207E\u2080-\u208F\u209D-\u20CF\u20F1-\u2101\u2103-\u2106\u2108\u2109\u2114\u2116-\u2118\u211E-\u2123\u2125\u2127\u2129\u212E\u213A\u213B\u2140-\u2144\u214A-\u214D\u214F-\u215F\u2189-\u24B5\u24EA-\u2BFF\u2C2F\u2C5F\u2CE5-\u2CEA\u2CF4-\u2CFF\u2D26\u2D28-\u2D2C\u2D2E\u2D2F\u2D68-\u2D6E\u2D70-\u2D7E\u2D97-\u2D9F\u2DA7\u2DAF\u2DB7\u2DBF\u2DC7\u2DCF\u2DD7\u2DDF\u2E00-\u2E2E\u2E30-\u3004\u3008-\u3020\u3030\u3036\u3037\u303D-\u3040\u3097\u3098\u309B\u309C\u30A0\u30FB\u3100-\u3104\u3130\u318F-\u319F\u31C0-\u31EF\u3200-\u33FF\u4DC0-\u4DFF\u9FFD-\u9FFF\uA48D-\uA4CF\uA4FE\uA4FF\uA60D-\uA60F\uA62C-\uA63F\uA673\uA67E\uA6F2-\uA716\uA720\uA721\uA789\uA78A\uA7C0\uA7C1\uA7CB-\uA7F4\uA828-\uA82B\uA82D-\uA83F\uA874-\uA87F\uA8C6-\uA8CF\uA8DA-\uA8DF\uA8F8-\uA8FA\uA8FC\uA92E\uA92F\uA954-\uA95F\uA97D-\uA97F\uA9C1-\uA9CE\uA9DA-\uA9DF\uA9FF\uAA37-\uAA3F\uAA4E\uAA4F\uAA5A-\uAA5F\uAA77-\uAA79\uAAC3-\uAADA\uAADE\uAADF\uAAF0\uAAF1\uAAF7-\uAB00\uAB07\uAB08\uAB0F\uAB10\uAB17-\uAB1F\uAB27\uAB2F\uAB5B\uAB6A-\uAB6F\uABEB\uABEE\uABEF\uABFA-\uABFF\uD7A4-\uD7AF\uD7C7-\uD7CA\uD7FC-\uD7FF\uE000-\uF8FF\uFA6E\uFA6F\uFADA-\uFAFF\uFB07-\uFB12\uFB18-\uFB1C\uFB29\uFB37\uFB3D\uFB3F\uFB42\uFB45\uFBB2-\uFBD2\uFD3E-\uFD4F\uFD90\uFD91\uFDC8-\uFDEF\uFDFC-\uFDFF\uFE10-\uFE1F\uFE30-\uFE32\uFE35-\uFE4C\uFE50-\uFE6F\uFE75\uFEFD-\uFF0F\uFF1A-\uFF20\uFF3B-\uFF3E\uFF40\uFF5B-\uFF65\uFFBF-\uFFC1\uFFC8\uFFC9\uFFD0\uFFD1\uFFD8\uFFD9\uFFDD-\uFFFF]|\uD800[\uDC0C\uDC27\uDC3B\uDC3E\uDC4E\uDC4F\uDC5E-\uDC7F\uDCFB-\uDD3F\uDD75-\uDDFC\uDDFE-\uDE7F\uDE9D-\uDE9F\uDED1-\uDEDF\uDEE1-\uDEFF\uDF20-\uDF2C\uDF4B-\uDF4F\uDF7B-\uDF7F\uDF9E\uDF9F\uDFC4-\uDFC7\uDFD0\uDFD6-\uDFFF]|\uD801[\uDC9E\uDC9F\uDCAA-\uDCAF\uDCD4-\uDCD7\uDCFC-\uDCFF\uDD28-\uDD2F\uDD64-\uDDFF\uDF37-\uDF3F\uDF56-\uDF5F\uDF68-\uDFFF]|\uD802[\uDC06\uDC07\uDC09\uDC36\uDC39-\uDC3B\uDC3D\uDC3E\uDC56-\uDC5F\uDC77-\uDC7F\uDC9F-\uDCDF\uDCF3\uDCF6-\uDCFF\uDD16-\uDD1F\uDD3A-\uDD7F\uDDB8-\uDDBD\uDDC0-\uDDFF\uDE04\uDE07-\uDE0B\uDE14\uDE18\uDE36\uDE37\uDE3B-\uDE3E\uDE40-\uDE5F\uDE7D-\uDE7F\uDE9D-\uDEBF\uDEC8\uDEE7-\uDEFF\uDF36-\uDF3F\uDF56-\uDF5F\uDF73-\uDF7F\uDF92-\uDFFF]|\uD803[\uDC49-\uDC7F\uDCB3-\uDCBF\uDCF3-\uDCFF\uDD28-\uDD2F\uDD3A-\uDE7F\uDEAA\uDEAD-\uDEAF\uDEB2-\uDEFF\uDF1D-\uDF26\uDF28-\uDF2F\uDF51-\uDFAF\uDFC5-\uDFDF\uDFF7-\uDFFF]|\uD804[\uDC47-\uDC65\uDC70-\uDC7E\uDCBB-\uDCCF\uDCE9-\uDCEF\uDCFA-\uDCFF\uDD35\uDD40-\uDD43\uDD48-\uDD4F\uDD74\uDD75\uDD77-\uDD7F\uDDC5-\uDDC8\uDDCD\uDDDB\uDDDD-\uDDFF\uDE12\uDE38-\uDE3D\uDE3F-\uDE7F\uDE87\uDE89\uDE8E\uDE9E\uDEA9-\uDEAF\uDEEB-\uDEEF\uDEFA-\uDEFF\uDF04\uDF0D\uDF0E\uDF11\uDF12\uDF29\uDF31\uDF34\uDF3A\uDF45\uDF46\uDF49\uDF4A\uDF4E\uDF4F\uDF51-\uDF56\uDF58-\uDF5C\uDF64\uDF65\uDF6D-\uDF6F\uDF75-\uDFFF]|\uD805[\uDC4B-\uDC4F\uDC5A-\uDC5D\uDC62-\uDC7F\uDCC6\uDCC8-\uDCCF\uDCDA-\uDD7F\uDDB6\uDDB7\uDDC1-\uDDD7\uDDDE-\uDDFF\uDE41-\uDE43\uDE45-\uDE4F\uDE5A-\uDE7F\uDEB9-\uDEBF\uDECA-\uDEFF\uDF1B\uDF1C\uDF2C-\uDF2F\uDF3A-\uDFFF]|\uD806[\uDC3B-\uDC9F\uDCEA-\uDCFE\uDD07\uDD08\uDD0A\uDD0B\uDD14\uDD17\uDD36\uDD39\uDD3A\uDD44-\uDD4F\uDD5A-\uDD9F\uDDA8\uDDA9\uDDD8\uDDD9\uDDE2\uDDE5-\uDDFF\uDE3F-\uDE46\uDE48-\uDE4F\uDE9A-\uDE9C\uDE9E-\uDEBF\uDEF9-\uDFFF]|\uD807[\uDC09\uDC37\uDC41-\uDC4F\uDC5A-\uDC71\uDC90\uDC91\uDCA8\uDCB7-\uDCFF\uDD07\uDD0A\uDD37-\uDD39\uDD3B\uDD3E\uDD48-\uDD4F\uDD5A-\uDD5F\uDD66\uDD69\uDD8F\uDD92\uDD99-\uDD9F\uDDAA-\uDEDF\uDEF7-\uDFAF\uDFB1-\uDFFF]|\uD808[\uDF9A-\uDFFF]|\uD809[\uDC6F-\uDC7F\uDD44-\uDFFF]|[\uD80A\uD80B\uD80E-\uD810\uD812-\uD819\uD824-\uD82B\uD82D\uD82E\uD830-\uD833\uD837\uD839\uD83D\uD83F\uD87B-\uD87D\uD87F\uD885-\uDB3F\uDB41-\uDBFF][\uDC00-\uDFFF]|\uD80D[\uDC2F-\uDFFF]|\uD811[\uDE47-\uDFFF]|\uD81A[\uDE39-\uDE3F\uDE5F\uDE6A-\uDECF\uDEEE\uDEEF\uDEF5-\uDEFF\uDF37-\uDF3F\uDF44-\uDF4F\uDF5A-\uDF62\uDF78-\uDF7C\uDF90-\uDFFF]|\uD81B[\uDC00-\uDE3F\uDE80-\uDEFF\uDF4B-\uDF4E\uDF88-\uDF8E\uDFA0-\uDFDF\uDFE2\uDFE5-\uDFEF\uDFF2-\uDFFF]|\uD821[\uDFF8-\uDFFF]|\uD823[\uDCD6-\uDCFF\uDD09-\uDFFF]|\uD82C[\uDD1F-\uDD4F\uDD53-\uDD63\uDD68-\uDD6F\uDEFC-\uDFFF]|\uD82F[\uDC6B-\uDC6F\uDC7D-\uDC7F\uDC89-\uDC8F\uDC9A-\uDC9C\uDC9F-\uDFFF]|\uD834[\uDC00-\uDD64\uDD6A-\uDD6C\uDD73-\uDD7A\uDD83\uDD84\uDD8C-\uDDA9\uDDAE-\uDE41\uDE45-\uDFFF]|\uD835[\uDC55\uDC9D\uDCA0\uDCA1\uDCA3\uDCA4\uDCA7\uDCA8\uDCAD\uDCBA\uDCBC\uDCC4\uDD06\uDD0B\uDD0C\uDD15\uDD1D\uDD3A\uDD3F\uDD45\uDD47-\uDD49\uDD51\uDEA6\uDEA7\uDEC1\uDEDB\uDEFB\uDF15\uDF35\uDF4F\uDF6F\uDF89\uDFA9\uDFC3\uDFCC\uDFCD]|\uD836[\uDC00-\uDDFF\uDE37-\uDE3A\uDE6D-\uDE74\uDE76-\uDE83\uDE85-\uDE9A\uDEA0\uDEB0-\uDFFF]|\uD838[\uDC07\uDC19\uDC1A\uDC22\uDC25\uDC2B-\uDCFF\uDD2D-\uDD2F\uDD3E\uDD3F\uDD4A-\uDD4D\uDD4F-\uDEBF\uDEFA-\uDFFF]|\uD83A[\uDCC5-\uDCCF\uDCD7-\uDCFF\uDD4C-\uDD4F\uDD5A-\uDFFF]|\uD83B[\uDC00-\uDDFF\uDE04\uDE20\uDE23\uDE25\uDE26\uDE28\uDE33\uDE38\uDE3A\uDE3C-\uDE41\uDE43-\uDE46\uDE48\uDE4A\uDE4C\uDE50\uDE53\uDE55\uDE56\uDE58\uDE5A\uDE5C\uDE5E\uDE60\uDE63\uDE65\uDE66\uDE6B\uDE73\uDE78\uDE7D\uDE7F\uDE8A\uDE9C-\uDEA0\uDEA4\uDEAA\uDEBC-\uDFFF]|\uD83C[\uDC00-\uDD2F\uDD4A-\uDD4F\uDD6A-\uDD6F\uDD8A-\uDFFF]|\uD83E[\uDC00-\uDFEF\uDFFA-\uDFFF]|\uD869[\uDEDE-\uDEFF]|\uD86D[\uDF35-\uDF3F]|\uD86E[\uDC1E\uDC1F]|\uD873[\uDEA2-\uDEAF]|\uD87A[\uDFE1-\uDFFF]|\uD87E[\uDE1E-\uDFFF]|\uD884[\uDF4B-\uDFFF]|\uDB40[\uDC00-\uDCFF\uDDF0-\uDFFF]/g, Hn = Object.hasOwnProperty;
class gt {
  /**
   * Create a new slug class.
   */
  constructor() {
    this.occurrences, this.reset();
  }
  /**
   * Generate a unique slug.
  *
  * Tracks previously generated slugs: repeated calls with the same value
  * will result in different slugs.
  * Use the `slug` function to get same slugs.
   *
   * @param  {string} value
   *   String of text to slugify
   * @param  {boolean} [maintainCase=false]
   *   Keep the current case, otherwise make all lowercase
   * @return {string}
   *   A unique slug string
   */
  slug(e, t) {
    const n = this;
    let i = Un(e, t === !0);
    const a = i;
    for (; Hn.call(n.occurrences, i); )
      n.occurrences[a]++, i = a + "-" + n.occurrences[a];
    return n.occurrences[i] = 0, i;
  }
  /**
   * Reset - Forget all previous slugs
   *
   * @return void
   */
  reset() {
    this.occurrences = /* @__PURE__ */ Object.create(null);
  }
}
function Un(r, e) {
  return typeof r != "string" ? "" : (e || (r = r.toLowerCase()), r.replace(jn, "").replace(/ /g, "-"));
}
new gt();
var Ve = typeof globalThis < "u" ? globalThis : typeof window < "u" ? window : typeof global < "u" ? global : typeof self < "u" ? self : {}, Gn = { exports: {} };
(function(r) {
  var e = typeof window < "u" ? window : typeof WorkerGlobalScope < "u" && self instanceof WorkerGlobalScope ? self : {};
  /**
   * Prism: Lightweight, robust, elegant syntax highlighting
   *
   * @license MIT <https://opensource.org/licenses/MIT>
   * @author Lea Verou <https://lea.verou.me>
   * @namespace
   * @public
   */
  var t = function(n) {
    var i = /(?:^|\s)lang(?:uage)?-([\w-]+)(?=\s|$)/i, a = 0, o = {}, l = {
      /**
       * By default, Prism will attempt to highlight all code elements (by calling {@link Prism.highlightAll}) on the
       * current page after the page finished loading. This might be a problem if e.g. you wanted to asynchronously load
       * additional languages or plugins yourself.
       *
       * By setting this value to `true`, Prism will not automatically highlight all code elements on the page.
       *
       * You obviously have to change this value before the automatic highlighting started. To do this, you can add an
       * empty Prism object into the global scope before loading the Prism script like this:
       *
       * ```js
       * window.Prism = window.Prism || {};
       * Prism.manual = true;
       * // add a new <script> to load Prism's script
       * ```
       *
       * @default false
       * @type {boolean}
       * @memberof Prism
       * @public
       */
      manual: n.Prism && n.Prism.manual,
      /**
       * By default, if Prism is in a web worker, it assumes that it is in a worker it created itself, so it uses
       * `addEventListener` to communicate with its parent instance. However, if you're using Prism manually in your
       * own worker, you don't want it to do this.
       *
       * By setting this value to `true`, Prism will not add its own listeners to the worker.
       *
       * You obviously have to change this value before Prism executes. To do this, you can add an
       * empty Prism object into the global scope before loading the Prism script like this:
       *
       * ```js
       * window.Prism = window.Prism || {};
       * Prism.disableWorkerMessageHandler = true;
       * // Load Prism's script
       * ```
       *
       * @default false
       * @type {boolean}
       * @memberof Prism
       * @public
       */
      disableWorkerMessageHandler: n.Prism && n.Prism.disableWorkerMessageHandler,
      /**
       * A namespace for utility methods.
       *
       * All function in this namespace that are not explicitly marked as _public_ are for __internal use only__ and may
       * change or disappear at any time.
       *
       * @namespace
       * @memberof Prism
       */
      util: {
        encode: function u(c) {
          return c instanceof s ? new s(c.type, u(c.content), c.alias) : Array.isArray(c) ? c.map(u) : c.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/\u00a0/g, " ");
        },
        /**
         * Returns the name of the type of the given value.
         *
         * @param {any} o
         * @returns {string}
         * @example
         * type(null)      === 'Null'
         * type(undefined) === 'Undefined'
         * type(123)       === 'Number'
         * type('foo')     === 'String'
         * type(true)      === 'Boolean'
         * type([1, 2])    === 'Array'
         * type({})        === 'Object'
         * type(String)    === 'Function'
         * type(/abc+/)    === 'RegExp'
         */
        type: function(u) {
          return Object.prototype.toString.call(u).slice(8, -1);
        },
        /**
         * Returns a unique number for the given object. Later calls will still return the same number.
         *
         * @param {Object} obj
         * @returns {number}
         */
        objId: function(u) {
          return u.__id || Object.defineProperty(u, "__id", { value: ++a }), u.__id;
        },
        /**
         * Creates a deep clone of the given object.
         *
         * The main intended use of this function is to clone language definitions.
         *
         * @param {T} o
         * @param {Record<number, any>} [visited]
         * @returns {T}
         * @template T
         */
        clone: function u(c, p) {
          p = p || {};
          var h, g;
          switch (l.util.type(c)) {
            case "Object":
              if (g = l.util.objId(c), p[g])
                return p[g];
              h = /** @type {Record<string, any>} */
              {}, p[g] = h;
              for (var F in c)
                c.hasOwnProperty(F) && (h[F] = u(c[F], p));
              return (
                /** @type {any} */
                h
              );
            case "Array":
              return g = l.util.objId(c), p[g] ? p[g] : (h = [], p[g] = h, /** @type {Array} */
              /** @type {any} */
              c.forEach(function(w, v) {
                h[v] = u(w, p);
              }), /** @type {any} */
              h);
            default:
              return c;
          }
        },
        /**
         * Returns the Prism language of the given element set by a `language-xxxx` or `lang-xxxx` class.
         *
         * If no language is set for the element or the element is `null` or `undefined`, `none` will be returned.
         *
         * @param {Element} element
         * @returns {string}
         */
        getLanguage: function(u) {
          for (; u; ) {
            var c = i.exec(u.className);
            if (c)
              return c[1].toLowerCase();
            u = u.parentElement;
          }
          return "none";
        },
        /**
         * Sets the Prism `language-xxxx` class of the given element.
         *
         * @param {Element} element
         * @param {string} language
         * @returns {void}
         */
        setLanguage: function(u, c) {
          u.className = u.className.replace(RegExp(i, "gi"), ""), u.classList.add("language-" + c);
        },
        /**
         * Returns the script element that is currently executing.
         *
         * This does __not__ work for line script element.
         *
         * @returns {HTMLScriptElement | null}
         */
        currentScript: function() {
          if (typeof document > "u")
            return null;
          if ("currentScript" in document)
            return (
              /** @type {any} */
              document.currentScript
            );
          try {
            throw new Error();
          } catch (h) {
            var u = (/at [^(\r\n]*\((.*):[^:]+:[^:]+\)$/i.exec(h.stack) || [])[1];
            if (u) {
              var c = document.getElementsByTagName("script");
              for (var p in c)
                if (c[p].src == u)
                  return c[p];
            }
            return null;
          }
        },
        /**
         * Returns whether a given class is active for `element`.
         *
         * The class can be activated if `element` or one of its ancestors has the given class and it can be deactivated
         * if `element` or one of its ancestors has the negated version of the given class. The _negated version_ of the
         * given class is just the given class with a `no-` prefix.
         *
         * Whether the class is active is determined by the closest ancestor of `element` (where `element` itself is
         * closest ancestor) that has the given class or the negated version of it. If neither `element` nor any of its
         * ancestors have the given class or the negated version of it, then the default activation will be returned.
         *
         * In the paradoxical situation where the closest ancestor contains __both__ the given class and the negated
         * version of it, the class is considered active.
         *
         * @param {Element} element
         * @param {string} className
         * @param {boolean} [defaultActivation=false]
         * @returns {boolean}
         */
        isActive: function(u, c, p) {
          for (var h = "no-" + c; u; ) {
            var g = u.classList;
            if (g.contains(c))
              return !0;
            if (g.contains(h))
              return !1;
            u = u.parentElement;
          }
          return !!p;
        }
      },
      /**
       * This namespace contains all currently loaded languages and the some helper functions to create and modify languages.
       *
       * @namespace
       * @memberof Prism
       * @public
       */
      languages: {
        /**
         * The grammar for plain, unformatted text.
         */
        plain: o,
        plaintext: o,
        text: o,
        txt: o,
        /**
         * Creates a deep copy of the language with the given id and appends the given tokens.
         *
         * If a token in `redef` also appears in the copied language, then the existing token in the copied language
         * will be overwritten at its original position.
         *
         * ## Best practices
         *
         * Since the position of overwriting tokens (token in `redef` that overwrite tokens in the copied language)
         * doesn't matter, they can technically be in any order. However, this can be confusing to others that trying to
         * understand the language definition because, normally, the order of tokens matters in Prism grammars.
         *
         * Therefore, it is encouraged to order overwriting tokens according to the positions of the overwritten tokens.
         * Furthermore, all non-overwriting tokens should be placed after the overwriting ones.
         *
         * @param {string} id The id of the language to extend. This has to be a key in `Prism.languages`.
         * @param {Grammar} redef The new tokens to append.
         * @returns {Grammar} The new language created.
         * @public
         * @example
         * Prism.languages['css-with-colors'] = Prism.languages.extend('css', {
         *     // Prism.languages.css already has a 'comment' token, so this token will overwrite CSS' 'comment' token
         *     // at its original position
         *     'comment': { ... },
         *     // CSS doesn't have a 'color' token, so this token will be appended
         *     'color': /\b(?:red|green|blue)\b/
         * });
         */
        extend: function(u, c) {
          var p = l.util.clone(l.languages[u]);
          for (var h in c)
            p[h] = c[h];
          return p;
        },
        /**
         * Inserts tokens _before_ another token in a language definition or any other grammar.
         *
         * ## Usage
         *
         * This helper method makes it easy to modify existing languages. For example, the CSS language definition
         * not only defines CSS highlighting for CSS documents, but also needs to define highlighting for CSS embedded
         * in HTML through `<style>` elements. To do this, it needs to modify `Prism.languages.markup` and add the
         * appropriate tokens. However, `Prism.languages.markup` is a regular JavaScript object literal, so if you do
         * this:
         *
         * ```js
         * Prism.languages.markup.style = {
         *     // token
         * };
         * ```
         *
         * then the `style` token will be added (and processed) at the end. `insertBefore` allows you to insert tokens
         * before existing tokens. For the CSS example above, you would use it like this:
         *
         * ```js
         * Prism.languages.insertBefore('markup', 'cdata', {
         *     'style': {
         *         // token
         *     }
         * });
         * ```
         *
         * ## Special cases
         *
         * If the grammars of `inside` and `insert` have tokens with the same name, the tokens in `inside`'s grammar
         * will be ignored.
         *
         * This behavior can be used to insert tokens after `before`:
         *
         * ```js
         * Prism.languages.insertBefore('markup', 'comment', {
         *     'comment': Prism.languages.markup.comment,
         *     // tokens after 'comment'
         * });
         * ```
         *
         * ## Limitations
         *
         * The main problem `insertBefore` has to solve is iteration order. Since ES2015, the iteration order for object
         * properties is guaranteed to be the insertion order (except for integer keys) but some browsers behave
         * differently when keys are deleted and re-inserted. So `insertBefore` can't be implemented by temporarily
         * deleting properties which is necessary to insert at arbitrary positions.
         *
         * To solve this problem, `insertBefore` doesn't actually insert the given tokens into the target object.
         * Instead, it will create a new object and replace all references to the target object with the new one. This
         * can be done without temporarily deleting properties, so the iteration order is well-defined.
         *
         * However, only references that can be reached from `Prism.languages` or `insert` will be replaced. I.e. if
         * you hold the target object in a variable, then the value of the variable will not change.
         *
         * ```js
         * var oldMarkup = Prism.languages.markup;
         * var newMarkup = Prism.languages.insertBefore('markup', 'comment', { ... });
         *
         * assert(oldMarkup !== Prism.languages.markup);
         * assert(newMarkup === Prism.languages.markup);
         * ```
         *
         * @param {string} inside The property of `root` (e.g. a language id in `Prism.languages`) that contains the
         * object to be modified.
         * @param {string} before The key to insert before.
         * @param {Grammar} insert An object containing the key-value pairs to be inserted.
         * @param {Object<string, any>} [root] The object containing `inside`, i.e. the object that contains the
         * object to be modified.
         *
         * Defaults to `Prism.languages`.
         * @returns {Grammar} The new grammar object.
         * @public
         */
        insertBefore: function(u, c, p, h) {
          h = h || /** @type {any} */
          l.languages;
          var g = h[u], F = {};
          for (var w in g)
            if (g.hasOwnProperty(w)) {
              if (w == c)
                for (var v in p)
                  p.hasOwnProperty(v) && (F[v] = p[v]);
              p.hasOwnProperty(w) || (F[w] = g[w]);
            }
          var k = h[u];
          return h[u] = F, l.languages.DFS(l.languages, function(x, L) {
            L === k && x != u && (this[x] = F);
          }), F;
        },
        // Traverse a language definition with Depth First Search
        DFS: function u(c, p, h, g) {
          g = g || {};
          var F = l.util.objId;
          for (var w in c)
            if (c.hasOwnProperty(w)) {
              p.call(c, w, c[w], h || w);
              var v = c[w], k = l.util.type(v);
              k === "Object" && !g[F(v)] ? (g[F(v)] = !0, u(v, p, null, g)) : k === "Array" && !g[F(v)] && (g[F(v)] = !0, u(v, p, w, g));
            }
        }
      },
      plugins: {},
      /**
       * This is the most high-level function in Prism’s API.
       * It fetches all the elements that have a `.language-xxxx` class and then calls {@link Prism.highlightElement} on
       * each one of them.
       *
       * This is equivalent to `Prism.highlightAllUnder(document, async, callback)`.
       *
       * @param {boolean} [async=false] Same as in {@link Prism.highlightAllUnder}.
       * @param {HighlightCallback} [callback] Same as in {@link Prism.highlightAllUnder}.
       * @memberof Prism
       * @public
       */
      highlightAll: function(u, c) {
        l.highlightAllUnder(document, u, c);
      },
      /**
       * Fetches all the descendants of `container` that have a `.language-xxxx` class and then calls
       * {@link Prism.highlightElement} on each one of them.
       *
       * The following hooks will be run:
       * 1. `before-highlightall`
       * 2. `before-all-elements-highlight`
       * 3. All hooks of {@link Prism.highlightElement} for each element.
       *
       * @param {ParentNode} container The root element, whose descendants that have a `.language-xxxx` class will be highlighted.
       * @param {boolean} [async=false] Whether each element is to be highlighted asynchronously using Web Workers.
       * @param {HighlightCallback} [callback] An optional callback to be invoked on each element after its highlighting is done.
       * @memberof Prism
       * @public
       */
      highlightAllUnder: function(u, c, p) {
        var h = {
          callback: p,
          container: u,
          selector: 'code[class*="language-"], [class*="language-"] code, code[class*="lang-"], [class*="lang-"] code'
        };
        l.hooks.run("before-highlightall", h), h.elements = Array.prototype.slice.apply(h.container.querySelectorAll(h.selector)), l.hooks.run("before-all-elements-highlight", h);
        for (var g = 0, F; F = h.elements[g++]; )
          l.highlightElement(F, c === !0, h.callback);
      },
      /**
       * Highlights the code inside a single element.
       *
       * The following hooks will be run:
       * 1. `before-sanity-check`
       * 2. `before-highlight`
       * 3. All hooks of {@link Prism.highlight}. These hooks will be run by an asynchronous worker if `async` is `true`.
       * 4. `before-insert`
       * 5. `after-highlight`
       * 6. `complete`
       *
       * Some the above hooks will be skipped if the element doesn't contain any text or there is no grammar loaded for
       * the element's language.
       *
       * @param {Element} element The element containing the code.
       * It must have a class of `language-xxxx` to be processed, where `xxxx` is a valid language identifier.
       * @param {boolean} [async=false] Whether the element is to be highlighted asynchronously using Web Workers
       * to improve performance and avoid blocking the UI when highlighting very large chunks of code. This option is
       * [disabled by default](https://prismjs.com/faq.html#why-is-asynchronous-highlighting-disabled-by-default).
       *
       * Note: All language definitions required to highlight the code must be included in the main `prism.js` file for
       * asynchronous highlighting to work. You can build your own bundle on the
       * [Download page](https://prismjs.com/download.html).
       * @param {HighlightCallback} [callback] An optional callback to be invoked after the highlighting is done.
       * Mostly useful when `async` is `true`, since in that case, the highlighting is done asynchronously.
       * @memberof Prism
       * @public
       */
      highlightElement: function(u, c, p) {
        var h = l.util.getLanguage(u), g = l.languages[h];
        l.util.setLanguage(u, h);
        var F = u.parentElement;
        F && F.nodeName.toLowerCase() === "pre" && l.util.setLanguage(F, h);
        var w = u.textContent, v = {
          element: u,
          language: h,
          grammar: g,
          code: w
        };
        function k(L) {
          v.highlightedCode = L, l.hooks.run("before-insert", v), v.element.innerHTML = v.highlightedCode, l.hooks.run("after-highlight", v), l.hooks.run("complete", v), p && p.call(v.element);
        }
        if (l.hooks.run("before-sanity-check", v), F = v.element.parentElement, F && F.nodeName.toLowerCase() === "pre" && !F.hasAttribute("tabindex") && F.setAttribute("tabindex", "0"), !v.code) {
          l.hooks.run("complete", v), p && p.call(v.element);
          return;
        }
        if (l.hooks.run("before-highlight", v), !v.grammar) {
          k(l.util.encode(v.code));
          return;
        }
        if (c && n.Worker) {
          var x = new Worker(l.filename);
          x.onmessage = function(L) {
            k(L.data);
          }, x.postMessage(JSON.stringify({
            language: v.language,
            code: v.code,
            immediateClose: !0
          }));
        } else
          k(l.highlight(v.code, v.grammar, v.language));
      },
      /**
       * Low-level function, only use if you know what you’re doing. It accepts a string of text as input
       * and the language definitions to use, and returns a string with the HTML produced.
       *
       * The following hooks will be run:
       * 1. `before-tokenize`
       * 2. `after-tokenize`
       * 3. `wrap`: On each {@link Token}.
       *
       * @param {string} text A string with the code to be highlighted.
       * @param {Grammar} grammar An object containing the tokens to use.
       *
       * Usually a language definition like `Prism.languages.markup`.
       * @param {string} language The name of the language definition passed to `grammar`.
       * @returns {string} The highlighted HTML.
       * @memberof Prism
       * @public
       * @example
       * Prism.highlight('var foo = true;', Prism.languages.javascript, 'javascript');
       */
      highlight: function(u, c, p) {
        var h = {
          code: u,
          grammar: c,
          language: p
        };
        if (l.hooks.run("before-tokenize", h), !h.grammar)
          throw new Error('The language "' + h.language + '" has no grammar.');
        return h.tokens = l.tokenize(h.code, h.grammar), l.hooks.run("after-tokenize", h), s.stringify(l.util.encode(h.tokens), h.language);
      },
      /**
       * This is the heart of Prism, and the most low-level function you can use. It accepts a string of text as input
       * and the language definitions to use, and returns an array with the tokenized code.
       *
       * When the language definition includes nested tokens, the function is called recursively on each of these tokens.
       *
       * This method could be useful in other contexts as well, as a very crude parser.
       *
       * @param {string} text A string with the code to be highlighted.
       * @param {Grammar} grammar An object containing the tokens to use.
       *
       * Usually a language definition like `Prism.languages.markup`.
       * @returns {TokenStream} An array of strings and tokens, a token stream.
       * @memberof Prism
       * @public
       * @example
       * let code = `var foo = 0;`;
       * let tokens = Prism.tokenize(code, Prism.languages.javascript);
       * tokens.forEach(token => {
       *     if (token instanceof Prism.Token && token.type === 'number') {
       *         console.log(`Found numeric literal: ${token.content}`);
       *     }
       * });
       */
      tokenize: function(u, c) {
        var p = c.rest;
        if (p) {
          for (var h in p)
            c[h] = p[h];
          delete c.rest;
        }
        var g = new f();
        return $(g, g.head, u), d(u, g, c, g.head, 0), S(g);
      },
      /**
       * @namespace
       * @memberof Prism
       * @public
       */
      hooks: {
        all: {},
        /**
         * Adds the given callback to the list of callbacks for the given hook.
         *
         * The callback will be invoked when the hook it is registered for is run.
         * Hooks are usually directly run by a highlight function but you can also run hooks yourself.
         *
         * One callback function can be registered to multiple hooks and the same hook multiple times.
         *
         * @param {string} name The name of the hook.
         * @param {HookCallback} callback The callback function which is given environment variables.
         * @public
         */
        add: function(u, c) {
          var p = l.hooks.all;
          p[u] = p[u] || [], p[u].push(c);
        },
        /**
         * Runs a hook invoking all registered callbacks with the given environment variables.
         *
         * Callbacks will be invoked synchronously and in the order in which they were registered.
         *
         * @param {string} name The name of the hook.
         * @param {Object<string, any>} env The environment variables of the hook passed to all callbacks registered.
         * @public
         */
        run: function(u, c) {
          var p = l.hooks.all[u];
          if (!(!p || !p.length))
            for (var h = 0, g; g = p[h++]; )
              g(c);
        }
      },
      Token: s
    };
    n.Prism = l;
    function s(u, c, p, h) {
      this.type = u, this.content = c, this.alias = p, this.length = (h || "").length | 0;
    }
    s.stringify = function u(c, p) {
      if (typeof c == "string")
        return c;
      if (Array.isArray(c)) {
        var h = "";
        return c.forEach(function(k) {
          h += u(k, p);
        }), h;
      }
      var g = {
        type: c.type,
        content: u(c.content, p),
        tag: "span",
        classes: ["token", c.type],
        attributes: {},
        language: p
      }, F = c.alias;
      F && (Array.isArray(F) ? Array.prototype.push.apply(g.classes, F) : g.classes.push(F)), l.hooks.run("wrap", g);
      var w = "";
      for (var v in g.attributes)
        w += " " + v + '="' + (g.attributes[v] || "").replace(/"/g, "&quot;") + '"';
      return "<" + g.tag + ' class="' + g.classes.join(" ") + '"' + w + ">" + g.content + "</" + g.tag + ">";
    };
    function _(u, c, p, h) {
      u.lastIndex = c;
      var g = u.exec(p);
      if (g && h && g[1]) {
        var F = g[1].length;
        g.index += F, g[0] = g[0].slice(F);
      }
      return g;
    }
    function d(u, c, p, h, g, F) {
      for (var w in p)
        if (!(!p.hasOwnProperty(w) || !p[w])) {
          var v = p[w];
          v = Array.isArray(v) ? v : [v];
          for (var k = 0; k < v.length; ++k) {
            if (F && F.cause == w + "," + k)
              return;
            var x = v[k], L = x.inside, ae = !!x.lookbehind, oe = !!x.greedy, Bt = x.alias;
            if (oe && !x.pattern.global) {
              var qt = x.pattern.toString().match(/[imsuy]*$/)[0];
              x.pattern = RegExp(x.pattern.source, qt + "g");
            }
            for (var Oe = x.pattern || x, B = h.next, O = g; B !== c.tail && !(F && O >= F.reach); O += B.value.length, B = B.next) {
              var X = B.value;
              if (c.length > u.length)
                return;
              if (!(X instanceof s)) {
                var re = 1, z;
                if (oe) {
                  if (z = _(Oe, O, u, ae), !z || z.index >= u.length)
                    break;
                  var le = z.index, Tt = z.index + z[0].length, H = O;
                  for (H += B.value.length; le >= H; )
                    B = B.next, H += B.value.length;
                  if (H -= B.value.length, O = H, B.value instanceof s)
                    continue;
                  for (var K = B; K !== c.tail && (H < Tt || typeof K.value == "string"); K = K.next)
                    re++, H += K.value.length;
                  re--, X = u.slice(O, H), z.index -= O;
                } else if (z = _(Oe, 0, X, ae), !z)
                  continue;
                var le = z.index, se = z[0], $e = X.slice(0, le), Pe = X.slice(le + se.length), De = O + X.length;
                F && De > F.reach && (F.reach = De);
                var ue = B.prev;
                $e && (ue = $(c, ue, $e), O += $e.length), y(c, ue, re);
                var Rt = new s(w, L ? l.tokenize(se, L) : se, Bt, se);
                if (B = $(c, ue, Rt), Pe && $(c, B, Pe), re > 1) {
                  var ve = {
                    cause: w + "," + k,
                    reach: De
                  };
                  d(u, c, p, B.prev, O, ve), F && ve.reach > F.reach && (F.reach = ve.reach);
                }
              }
            }
          }
        }
    }
    function f() {
      var u = { value: null, prev: null, next: null }, c = { value: null, prev: u, next: null };
      u.next = c, this.head = u, this.tail = c, this.length = 0;
    }
    function $(u, c, p) {
      var h = c.next, g = { value: p, prev: c, next: h };
      return c.next = g, h.prev = g, u.length++, g;
    }
    function y(u, c, p) {
      for (var h = c.next, g = 0; g < p && h !== u.tail; g++)
        h = h.next;
      c.next = h, h.prev = c, u.length -= g;
    }
    function S(u) {
      for (var c = [], p = u.head.next; p !== u.tail; )
        c.push(p.value), p = p.next;
      return c;
    }
    if (!n.document)
      return n.addEventListener && (l.disableWorkerMessageHandler || n.addEventListener("message", function(u) {
        var c = JSON.parse(u.data), p = c.language, h = c.code, g = c.immediateClose;
        n.postMessage(l.highlight(h, l.languages[p], p)), g && n.close();
      }, !1)), l;
    var b = l.util.currentScript();
    b && (l.filename = b.src, b.hasAttribute("data-manual") && (l.manual = !0));
    function D() {
      l.manual || l.highlightAll();
    }
    if (!l.manual) {
      var m = document.readyState;
      m === "loading" || m === "interactive" && b && b.defer ? document.addEventListener("DOMContentLoaded", D) : window.requestAnimationFrame ? window.requestAnimationFrame(D) : window.setTimeout(D, 16);
    }
    return l;
  }(e);
  r.exports && (r.exports = t), typeof Ve < "u" && (Ve.Prism = t), t.languages.markup = {
    comment: {
      pattern: /<!--(?:(?!<!--)[\s\S])*?-->/,
      greedy: !0
    },
    prolog: {
      pattern: /<\?[\s\S]+?\?>/,
      greedy: !0
    },
    doctype: {
      // https://www.w3.org/TR/xml/#NT-doctypedecl
      pattern: /<!DOCTYPE(?:[^>"'[\]]|"[^"]*"|'[^']*')+(?:\[(?:[^<"'\]]|"[^"]*"|'[^']*'|<(?!!--)|<!--(?:[^-]|-(?!->))*-->)*\]\s*)?>/i,
      greedy: !0,
      inside: {
        "internal-subset": {
          pattern: /(^[^\[]*\[)[\s\S]+(?=\]>$)/,
          lookbehind: !0,
          greedy: !0,
          inside: null
          // see below
        },
        string: {
          pattern: /"[^"]*"|'[^']*'/,
          greedy: !0
        },
        punctuation: /^<!|>$|[[\]]/,
        "doctype-tag": /^DOCTYPE/i,
        name: /[^\s<>'"]+/
      }
    },
    cdata: {
      pattern: /<!\[CDATA\[[\s\S]*?\]\]>/i,
      greedy: !0
    },
    tag: {
      pattern: /<\/?(?!\d)[^\s>\/=$<%]+(?:\s(?:\s*[^\s>\/=]+(?:\s*=\s*(?:"[^"]*"|'[^']*'|[^\s'">=]+(?=[\s>]))|(?=[\s/>])))+)?\s*\/?>/,
      greedy: !0,
      inside: {
        tag: {
          pattern: /^<\/?[^\s>\/]+/,
          inside: {
            punctuation: /^<\/?/,
            namespace: /^[^\s>\/:]+:/
          }
        },
        "special-attr": [],
        "attr-value": {
          pattern: /=\s*(?:"[^"]*"|'[^']*'|[^\s'">=]+)/,
          inside: {
            punctuation: [
              {
                pattern: /^=/,
                alias: "attr-equals"
              },
              {
                pattern: /^(\s*)["']|["']$/,
                lookbehind: !0
              }
            ]
          }
        },
        punctuation: /\/?>/,
        "attr-name": {
          pattern: /[^\s>\/]+/,
          inside: {
            namespace: /^[^\s>\/:]+:/
          }
        }
      }
    },
    entity: [
      {
        pattern: /&[\da-z]{1,8};/i,
        alias: "named-entity"
      },
      /&#x?[\da-f]{1,8};/i
    ]
  }, t.languages.markup.tag.inside["attr-value"].inside.entity = t.languages.markup.entity, t.languages.markup.doctype.inside["internal-subset"].inside = t.languages.markup, t.hooks.add("wrap", function(n) {
    n.type === "entity" && (n.attributes.title = n.content.replace(/&amp;/, "&"));
  }), Object.defineProperty(t.languages.markup.tag, "addInlined", {
    /**
     * Adds an inlined language to markup.
     *
     * An example of an inlined language is CSS with `<style>` tags.
     *
     * @param {string} tagName The name of the tag that contains the inlined language. This name will be treated as
     * case insensitive.
     * @param {string} lang The language key.
     * @example
     * addInlined('style', 'css');
     */
    value: function(i, a) {
      var o = {};
      o["language-" + a] = {
        pattern: /(^<!\[CDATA\[)[\s\S]+?(?=\]\]>$)/i,
        lookbehind: !0,
        inside: t.languages[a]
      }, o.cdata = /^<!\[CDATA\[|\]\]>$/i;
      var l = {
        "included-cdata": {
          pattern: /<!\[CDATA\[[\s\S]*?\]\]>/i,
          inside: o
        }
      };
      l["language-" + a] = {
        pattern: /[\s\S]+/,
        inside: t.languages[a]
      };
      var s = {};
      s[i] = {
        pattern: RegExp(/(<__[^>]*>)(?:<!\[CDATA\[(?:[^\]]|\](?!\]>))*\]\]>|(?!<!\[CDATA\[)[\s\S])*?(?=<\/__>)/.source.replace(/__/g, function() {
          return i;
        }), "i"),
        lookbehind: !0,
        greedy: !0,
        inside: l
      }, t.languages.insertBefore("markup", "cdata", s);
    }
  }), Object.defineProperty(t.languages.markup.tag, "addAttribute", {
    /**
     * Adds an pattern to highlight languages embedded in HTML attributes.
     *
     * An example of an inlined language is CSS with `style` attributes.
     *
     * @param {string} attrName The name of the tag that contains the inlined language. This name will be treated as
     * case insensitive.
     * @param {string} lang The language key.
     * @example
     * addAttribute('style', 'css');
     */
    value: function(n, i) {
      t.languages.markup.tag.inside["special-attr"].push({
        pattern: RegExp(
          /(^|["'\s])/.source + "(?:" + n + ")" + /\s*=\s*(?:"[^"]*"|'[^']*'|[^\s'">=]+(?=[\s>]))/.source,
          "i"
        ),
        lookbehind: !0,
        inside: {
          "attr-name": /^[^\s=]+/,
          "attr-value": {
            pattern: /=[\s\S]+/,
            inside: {
              value: {
                pattern: /(^=\s*(["']|(?!["'])))\S[\s\S]*(?=\2$)/,
                lookbehind: !0,
                alias: [i, "language-" + i],
                inside: t.languages[i]
              },
              punctuation: [
                {
                  pattern: /^=/,
                  alias: "attr-equals"
                },
                /"|'/
              ]
            }
          }
        }
      });
    }
  }), t.languages.html = t.languages.markup, t.languages.mathml = t.languages.markup, t.languages.svg = t.languages.markup, t.languages.xml = t.languages.extend("markup", {}), t.languages.ssml = t.languages.xml, t.languages.atom = t.languages.xml, t.languages.rss = t.languages.xml, function(n) {
    var i = /(?:"(?:\\(?:\r\n|[\s\S])|[^"\\\r\n])*"|'(?:\\(?:\r\n|[\s\S])|[^'\\\r\n])*')/;
    n.languages.css = {
      comment: /\/\*[\s\S]*?\*\//,
      atrule: {
        pattern: RegExp("@[\\w-](?:" + /[^;{\s"']|\s+(?!\s)/.source + "|" + i.source + ")*?" + /(?:;|(?=\s*\{))/.source),
        inside: {
          rule: /^@[\w-]+/,
          "selector-function-argument": {
            pattern: /(\bselector\s*\(\s*(?![\s)]))(?:[^()\s]|\s+(?![\s)])|\((?:[^()]|\([^()]*\))*\))+(?=\s*\))/,
            lookbehind: !0,
            alias: "selector"
          },
          keyword: {
            pattern: /(^|[^\w-])(?:and|not|only|or)(?![\w-])/,
            lookbehind: !0
          }
          // See rest below
        }
      },
      url: {
        // https://drafts.csswg.org/css-values-3/#urls
        pattern: RegExp("\\burl\\((?:" + i.source + "|" + /(?:[^\\\r\n()"']|\\[\s\S])*/.source + ")\\)", "i"),
        greedy: !0,
        inside: {
          function: /^url/i,
          punctuation: /^\(|\)$/,
          string: {
            pattern: RegExp("^" + i.source + "$"),
            alias: "url"
          }
        }
      },
      selector: {
        pattern: RegExp(`(^|[{}\\s])[^{}\\s](?:[^{};"'\\s]|\\s+(?![\\s{])|` + i.source + ")*(?=\\s*\\{)"),
        lookbehind: !0
      },
      string: {
        pattern: i,
        greedy: !0
      },
      property: {
        pattern: /(^|[^-\w\xA0-\uFFFF])(?!\s)[-_a-z\xA0-\uFFFF](?:(?!\s)[-\w\xA0-\uFFFF])*(?=\s*:)/i,
        lookbehind: !0
      },
      important: /!important\b/i,
      function: {
        pattern: /(^|[^-a-z0-9])[-a-z0-9]+(?=\()/i,
        lookbehind: !0
      },
      punctuation: /[(){};:,]/
    }, n.languages.css.atrule.inside.rest = n.languages.css;
    var a = n.languages.markup;
    a && (a.tag.addInlined("style", "css"), a.tag.addAttribute("style", "css"));
  }(t), t.languages.clike = {
    comment: [
      {
        pattern: /(^|[^\\])\/\*[\s\S]*?(?:\*\/|$)/,
        lookbehind: !0,
        greedy: !0
      },
      {
        pattern: /(^|[^\\:])\/\/.*/,
        lookbehind: !0,
        greedy: !0
      }
    ],
    string: {
      pattern: /(["'])(?:\\(?:\r\n|[\s\S])|(?!\1)[^\\\r\n])*\1/,
      greedy: !0
    },
    "class-name": {
      pattern: /(\b(?:class|extends|implements|instanceof|interface|new|trait)\s+|\bcatch\s+\()[\w.\\]+/i,
      lookbehind: !0,
      inside: {
        punctuation: /[.\\]/
      }
    },
    keyword: /\b(?:break|catch|continue|do|else|finally|for|function|if|in|instanceof|new|null|return|throw|try|while)\b/,
    boolean: /\b(?:false|true)\b/,
    function: /\b\w+(?=\()/,
    number: /\b0x[\da-f]+\b|(?:\b\d+(?:\.\d*)?|\B\.\d+)(?:e[+-]?\d+)?/i,
    operator: /[<>]=?|[!=]=?=?|--?|\+\+?|&&?|\|\|?|[?*/~^%]/,
    punctuation: /[{}[\];(),.:]/
  }, t.languages.javascript = t.languages.extend("clike", {
    "class-name": [
      t.languages.clike["class-name"],
      {
        pattern: /(^|[^$\w\xA0-\uFFFF])(?!\s)[_$A-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\.(?:constructor|prototype))/,
        lookbehind: !0
      }
    ],
    keyword: [
      {
        pattern: /((?:^|\})\s*)catch\b/,
        lookbehind: !0
      },
      {
        pattern: /(^|[^.]|\.\.\.\s*)\b(?:as|assert(?=\s*\{)|async(?=\s*(?:function\b|\(|[$\w\xA0-\uFFFF]|$))|await|break|case|class|const|continue|debugger|default|delete|do|else|enum|export|extends|finally(?=\s*(?:\{|$))|for|from(?=\s*(?:['"]|$))|function|(?:get|set)(?=\s*(?:[#\[$\w\xA0-\uFFFF]|$))|if|implements|import|in|instanceof|interface|let|new|null|of|package|private|protected|public|return|static|super|switch|this|throw|try|typeof|undefined|var|void|while|with|yield)\b/,
        lookbehind: !0
      }
    ],
    // Allow for all non-ASCII characters (See http://stackoverflow.com/a/2008444)
    function: /#?(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\s*(?:\.\s*(?:apply|bind|call)\s*)?\()/,
    number: {
      pattern: RegExp(
        /(^|[^\w$])/.source + "(?:" + // constant
        (/NaN|Infinity/.source + "|" + // binary integer
        /0[bB][01]+(?:_[01]+)*n?/.source + "|" + // octal integer
        /0[oO][0-7]+(?:_[0-7]+)*n?/.source + "|" + // hexadecimal integer
        /0[xX][\dA-Fa-f]+(?:_[\dA-Fa-f]+)*n?/.source + "|" + // decimal bigint
        /\d+(?:_\d+)*n/.source + "|" + // decimal number (integer or float) but no bigint
        /(?:\d+(?:_\d+)*(?:\.(?:\d+(?:_\d+)*)?)?|\.\d+(?:_\d+)*)(?:[Ee][+-]?\d+(?:_\d+)*)?/.source) + ")" + /(?![\w$])/.source
      ),
      lookbehind: !0
    },
    operator: /--|\+\+|\*\*=?|=>|&&=?|\|\|=?|[!=]==|<<=?|>>>?=?|[-+*/%&|^!=<>]=?|\.{3}|\?\?=?|\?\.?|[~:]/
  }), t.languages.javascript["class-name"][0].pattern = /(\b(?:class|extends|implements|instanceof|interface|new)\s+)[\w.\\]+/, t.languages.insertBefore("javascript", "keyword", {
    regex: {
      pattern: RegExp(
        // lookbehind
        // eslint-disable-next-line regexp/no-dupe-characters-character-class
        /((?:^|[^$\w\xA0-\uFFFF."'\])\s]|\b(?:return|yield))\s*)/.source + // Regex pattern:
        // There are 2 regex patterns here. The RegExp set notation proposal added support for nested character
        // classes if the `v` flag is present. Unfortunately, nested CCs are both context-free and incompatible
        // with the only syntax, so we have to define 2 different regex patterns.
        /\//.source + "(?:" + /(?:\[(?:[^\]\\\r\n]|\\.)*\]|\\.|[^/\\\[\r\n])+\/[dgimyus]{0,7}/.source + "|" + // `v` flag syntax. This supports 3 levels of nested character classes.
        /(?:\[(?:[^[\]\\\r\n]|\\.|\[(?:[^[\]\\\r\n]|\\.|\[(?:[^[\]\\\r\n]|\\.)*\])*\])*\]|\\.|[^/\\\[\r\n])+\/[dgimyus]{0,7}v[dgimyus]{0,7}/.source + ")" + // lookahead
        /(?=(?:\s|\/\*(?:[^*]|\*(?!\/))*\*\/)*(?:$|[\r\n,.;:})\]]|\/\/))/.source
      ),
      lookbehind: !0,
      greedy: !0,
      inside: {
        "regex-source": {
          pattern: /^(\/)[\s\S]+(?=\/[a-z]*$)/,
          lookbehind: !0,
          alias: "language-regex",
          inside: t.languages.regex
        },
        "regex-delimiter": /^\/|\/$/,
        "regex-flags": /^[a-z]+$/
      }
    },
    // This must be declared before keyword because we use "function" inside the look-forward
    "function-variable": {
      pattern: /#?(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\s*[=:]\s*(?:async\s*)?(?:\bfunction\b|(?:\((?:[^()]|\([^()]*\))*\)|(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*)\s*=>))/,
      alias: "function"
    },
    parameter: [
      {
        pattern: /(function(?:\s+(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*)?\s*\(\s*)(?!\s)(?:[^()\s]|\s+(?![\s)])|\([^()]*\))+(?=\s*\))/,
        lookbehind: !0,
        inside: t.languages.javascript
      },
      {
        pattern: /(^|[^$\w\xA0-\uFFFF])(?!\s)[_$a-z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\s*=>)/i,
        lookbehind: !0,
        inside: t.languages.javascript
      },
      {
        pattern: /(\(\s*)(?!\s)(?:[^()\s]|\s+(?![\s)])|\([^()]*\))+(?=\s*\)\s*=>)/,
        lookbehind: !0,
        inside: t.languages.javascript
      },
      {
        pattern: /((?:\b|\s|^)(?!(?:as|async|await|break|case|catch|class|const|continue|debugger|default|delete|do|else|enum|export|extends|finally|for|from|function|get|if|implements|import|in|instanceof|interface|let|new|null|of|package|private|protected|public|return|set|static|super|switch|this|throw|try|typeof|undefined|var|void|while|with|yield)(?![$\w\xA0-\uFFFF]))(?:(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*\s*)\(\s*|\]\s*\(\s*)(?!\s)(?:[^()\s]|\s+(?![\s)])|\([^()]*\))+(?=\s*\)\s*\{)/,
        lookbehind: !0,
        inside: t.languages.javascript
      }
    ],
    constant: /\b[A-Z](?:[A-Z_]|\dx?)*\b/
  }), t.languages.insertBefore("javascript", "string", {
    hashbang: {
      pattern: /^#!.*/,
      greedy: !0,
      alias: "comment"
    },
    "template-string": {
      pattern: /`(?:\\[\s\S]|\$\{(?:[^{}]|\{(?:[^{}]|\{[^}]*\})*\})+\}|(?!\$\{)[^\\`])*`/,
      greedy: !0,
      inside: {
        "template-punctuation": {
          pattern: /^`|`$/,
          alias: "string"
        },
        interpolation: {
          pattern: /((?:^|[^\\])(?:\\{2})*)\$\{(?:[^{}]|\{(?:[^{}]|\{[^}]*\})*\})+\}/,
          lookbehind: !0,
          inside: {
            "interpolation-punctuation": {
              pattern: /^\$\{|\}$/,
              alias: "punctuation"
            },
            rest: t.languages.javascript
          }
        },
        string: /[\s\S]+/
      }
    },
    "string-property": {
      pattern: /((?:^|[,{])[ \t]*)(["'])(?:\\(?:\r\n|[\s\S])|(?!\2)[^\\\r\n])*\2(?=\s*:)/m,
      lookbehind: !0,
      greedy: !0,
      alias: "property"
    }
  }), t.languages.insertBefore("javascript", "operator", {
    "literal-property": {
      pattern: /((?:^|[,{])[ \t]*)(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\s*:)/m,
      lookbehind: !0,
      alias: "property"
    }
  }), t.languages.markup && (t.languages.markup.tag.addInlined("script", "javascript"), t.languages.markup.tag.addAttribute(
    /on(?:abort|blur|change|click|composition(?:end|start|update)|dblclick|error|focus(?:in|out)?|key(?:down|up)|load|mouse(?:down|enter|leave|move|out|over|up)|reset|resize|scroll|select|slotchange|submit|unload|wheel)/.source,
    "javascript"
  )), t.languages.js = t.languages.javascript, function() {
    if (typeof t > "u" || typeof document > "u")
      return;
    Element.prototype.matches || (Element.prototype.matches = Element.prototype.msMatchesSelector || Element.prototype.webkitMatchesSelector);
    var n = "Loading…", i = function(b, D) {
      return "✖ Error " + b + " while fetching file: " + D;
    }, a = "✖ Error: File does not exist or is empty", o = {
      js: "javascript",
      py: "python",
      rb: "ruby",
      ps1: "powershell",
      psm1: "powershell",
      sh: "bash",
      bat: "batch",
      h: "c",
      tex: "latex"
    }, l = "data-src-status", s = "loading", _ = "loaded", d = "failed", f = "pre[data-src]:not([" + l + '="' + _ + '"]):not([' + l + '="' + s + '"])';
    function $(b, D, m) {
      var u = new XMLHttpRequest();
      u.open("GET", b, !0), u.onreadystatechange = function() {
        u.readyState == 4 && (u.status < 400 && u.responseText ? D(u.responseText) : u.status >= 400 ? m(i(u.status, u.statusText)) : m(a));
      }, u.send(null);
    }
    function y(b) {
      var D = /^\s*(\d+)\s*(?:(,)\s*(?:(\d+)\s*)?)?$/.exec(b || "");
      if (D) {
        var m = Number(D[1]), u = D[2], c = D[3];
        return u ? c ? [m, Number(c)] : [m, void 0] : [m, m];
      }
    }
    t.hooks.add("before-highlightall", function(b) {
      b.selector += ", " + f;
    }), t.hooks.add("before-sanity-check", function(b) {
      var D = (
        /** @type {HTMLPreElement} */
        b.element
      );
      if (D.matches(f)) {
        b.code = "", D.setAttribute(l, s);
        var m = D.appendChild(document.createElement("CODE"));
        m.textContent = n;
        var u = D.getAttribute("data-src"), c = b.language;
        if (c === "none") {
          var p = (/\.(\w+)$/.exec(u) || [, "none"])[1];
          c = o[p] || p;
        }
        t.util.setLanguage(m, c), t.util.setLanguage(D, c);
        var h = t.plugins.autoloader;
        h && h.loadLanguages(c), $(
          u,
          function(g) {
            D.setAttribute(l, _);
            var F = y(D.getAttribute("data-range"));
            if (F) {
              var w = g.split(/\r\n?|\n/g), v = F[0], k = F[1] == null ? w.length : F[1];
              v < 0 && (v += w.length), v = Math.max(0, Math.min(v - 1, w.length)), k < 0 && (k += w.length), k = Math.max(0, Math.min(k, w.length)), g = w.slice(v, k).join(`
`), D.hasAttribute("data-start") || D.setAttribute("data-start", String(v + 1));
            }
            m.textContent = g, t.highlightElement(m);
          },
          function(g) {
            D.setAttribute(l, d), m.textContent = g;
          }
        );
      }
    }), t.plugins.fileHighlight = {
      /**
       * Executes the File Highlight plugin for all matching `pre` elements under the given container.
       *
       * Note: Elements which are already loaded or currently loading will not be touched by this method.
       *
       * @param {ParentNode} [container=document]
       */
      highlight: function(D) {
        for (var m = (D || document).querySelectorAll(f), u = 0, c; c = m[u++]; )
          t.highlightElement(c);
      }
    };
    var S = !1;
    t.fileHighlight = function() {
      S || (console.warn("Prism.fileHighlight is deprecated. Use `Prism.plugins.fileHighlight.highlight` instead."), S = !0), t.plugins.fileHighlight.highlight.apply(this, arguments);
    };
  }();
})(Gn);
Prism.languages.python = {
  comment: {
    pattern: /(^|[^\\])#.*/,
    lookbehind: !0,
    greedy: !0
  },
  "string-interpolation": {
    pattern: /(?:f|fr|rf)(?:("""|''')[\s\S]*?\1|("|')(?:\\.|(?!\2)[^\\\r\n])*\2)/i,
    greedy: !0,
    inside: {
      interpolation: {
        // "{" <expression> <optional "!s", "!r", or "!a"> <optional ":" format specifier> "}"
        pattern: /((?:^|[^{])(?:\{\{)*)\{(?!\{)(?:[^{}]|\{(?!\{)(?:[^{}]|\{(?!\{)(?:[^{}])+\})+\})+\}/,
        lookbehind: !0,
        inside: {
          "format-spec": {
            pattern: /(:)[^:(){}]+(?=\}$)/,
            lookbehind: !0
          },
          "conversion-option": {
            pattern: /![sra](?=[:}]$)/,
            alias: "punctuation"
          },
          rest: null
        }
      },
      string: /[\s\S]+/
    }
  },
  "triple-quoted-string": {
    pattern: /(?:[rub]|br|rb)?("""|''')[\s\S]*?\1/i,
    greedy: !0,
    alias: "string"
  },
  string: {
    pattern: /(?:[rub]|br|rb)?("|')(?:\\.|(?!\1)[^\\\r\n])*\1/i,
    greedy: !0
  },
  function: {
    pattern: /((?:^|\s)def[ \t]+)[a-zA-Z_]\w*(?=\s*\()/g,
    lookbehind: !0
  },
  "class-name": {
    pattern: /(\bclass\s+)\w+/i,
    lookbehind: !0
  },
  decorator: {
    pattern: /(^[\t ]*)@\w+(?:\.\w+)*/m,
    lookbehind: !0,
    alias: ["annotation", "punctuation"],
    inside: {
      punctuation: /\./
    }
  },
  keyword: /\b(?:_(?=\s*:)|and|as|assert|async|await|break|case|class|continue|def|del|elif|else|except|exec|finally|for|from|global|if|import|in|is|lambda|match|nonlocal|not|or|pass|print|raise|return|try|while|with|yield)\b/,
  builtin: /\b(?:__import__|abs|all|any|apply|ascii|basestring|bin|bool|buffer|bytearray|bytes|callable|chr|classmethod|cmp|coerce|compile|complex|delattr|dict|dir|divmod|enumerate|eval|execfile|file|filter|float|format|frozenset|getattr|globals|hasattr|hash|help|hex|id|input|int|intern|isinstance|issubclass|iter|len|list|locals|long|map|max|memoryview|min|next|object|oct|open|ord|pow|property|range|raw_input|reduce|reload|repr|reversed|round|set|setattr|slice|sorted|staticmethod|str|sum|super|tuple|type|unichr|unicode|vars|xrange|zip)\b/,
  boolean: /\b(?:False|None|True)\b/,
  number: /\b0(?:b(?:_?[01])+|o(?:_?[0-7])+|x(?:_?[a-f0-9])+)\b|(?:\b\d+(?:_\d+)*(?:\.(?:\d+(?:_\d+)*)?)?|\B\.\d+(?:_\d+)*)(?:e[+-]?\d+(?:_\d+)*)?j?(?!\w)/i,
  operator: /[-+%=]=?|!=|:=|\*\*?=?|\/\/?=?|<[<=>]?|>[=>]?|[&|^~]/,
  punctuation: /[{}[\];(),.:]/
};
Prism.languages.python["string-interpolation"].inside.interpolation.inside.rest = Prism.languages.python;
Prism.languages.py = Prism.languages.python;
(function(r) {
  var e = /\\(?:[^a-z()[\]]|[a-z*]+)/i, t = {
    "equation-command": {
      pattern: e,
      alias: "regex"
    }
  };
  r.languages.latex = {
    comment: /%.*/,
    // the verbatim environment prints whitespace to the document
    cdata: {
      pattern: /(\\begin\{((?:lstlisting|verbatim)\*?)\})[\s\S]*?(?=\\end\{\2\})/,
      lookbehind: !0
    },
    /*
     * equations can be between $$ $$ or $ $ or \( \) or \[ \]
     * (all are multiline)
     */
    equation: [
      {
        pattern: /\$\$(?:\\[\s\S]|[^\\$])+\$\$|\$(?:\\[\s\S]|[^\\$])+\$|\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\]/,
        inside: t,
        alias: "string"
      },
      {
        pattern: /(\\begin\{((?:align|eqnarray|equation|gather|math|multline)\*?)\})[\s\S]*?(?=\\end\{\2\})/,
        lookbehind: !0,
        inside: t,
        alias: "string"
      }
    ],
    /*
     * arguments which are keywords or references are highlighted
     * as keywords
     */
    keyword: {
      pattern: /(\\(?:begin|cite|documentclass|end|label|ref|usepackage)(?:\[[^\]]+\])?\{)[^}]+(?=\})/,
      lookbehind: !0
    },
    url: {
      pattern: /(\\url\{)[^}]+(?=\})/,
      lookbehind: !0
    },
    /*
     * section or chapter headlines are highlighted as bold so that
     * they stand out more
     */
    headline: {
      pattern: /(\\(?:chapter|frametitle|paragraph|part|section|subparagraph|subsection|subsubparagraph|subsubsection|subsubsubparagraph)\*?(?:\[[^\]]+\])?\{)[^}]+(?=\})/,
      lookbehind: !0,
      alias: "class-name"
    },
    function: {
      pattern: e,
      alias: "selector"
    },
    punctuation: /[[\]{}&]/
  }, r.languages.tex = r.languages.latex, r.languages.context = r.languages.latex;
})(Prism);
(function(r) {
  var e = "\\b(?:BASH|BASHOPTS|BASH_ALIASES|BASH_ARGC|BASH_ARGV|BASH_CMDS|BASH_COMPLETION_COMPAT_DIR|BASH_LINENO|BASH_REMATCH|BASH_SOURCE|BASH_VERSINFO|BASH_VERSION|COLORTERM|COLUMNS|COMP_WORDBREAKS|DBUS_SESSION_BUS_ADDRESS|DEFAULTS_PATH|DESKTOP_SESSION|DIRSTACK|DISPLAY|EUID|GDMSESSION|GDM_LANG|GNOME_KEYRING_CONTROL|GNOME_KEYRING_PID|GPG_AGENT_INFO|GROUPS|HISTCONTROL|HISTFILE|HISTFILESIZE|HISTSIZE|HOME|HOSTNAME|HOSTTYPE|IFS|INSTANCE|JOB|LANG|LANGUAGE|LC_ADDRESS|LC_ALL|LC_IDENTIFICATION|LC_MEASUREMENT|LC_MONETARY|LC_NAME|LC_NUMERIC|LC_PAPER|LC_TELEPHONE|LC_TIME|LESSCLOSE|LESSOPEN|LINES|LOGNAME|LS_COLORS|MACHTYPE|MAILCHECK|MANDATORY_PATH|NO_AT_BRIDGE|OLDPWD|OPTERR|OPTIND|ORBIT_SOCKETDIR|OSTYPE|PAPERSIZE|PATH|PIPESTATUS|PPID|PS1|PS2|PS3|PS4|PWD|RANDOM|REPLY|SECONDS|SELINUX_INIT|SESSION|SESSIONTYPE|SESSION_MANAGER|SHELL|SHELLOPTS|SHLVL|SSH_AUTH_SOCK|TERM|UID|UPSTART_EVENTS|UPSTART_INSTANCE|UPSTART_JOB|UPSTART_SESSION|USER|WINDOWID|XAUTHORITY|XDG_CONFIG_DIRS|XDG_CURRENT_DESKTOP|XDG_DATA_DIRS|XDG_GREETER_DATA_DIR|XDG_MENU_PREFIX|XDG_RUNTIME_DIR|XDG_SEAT|XDG_SEAT_PATH|XDG_SESSION_DESKTOP|XDG_SESSION_ID|XDG_SESSION_PATH|XDG_SESSION_TYPE|XDG_VTNR|XMODIFIERS)\\b", t = {
    pattern: /(^(["']?)\w+\2)[ \t]+\S.*/,
    lookbehind: !0,
    alias: "punctuation",
    // this looks reasonably well in all themes
    inside: null
    // see below
  }, n = {
    bash: t,
    environment: {
      pattern: RegExp("\\$" + e),
      alias: "constant"
    },
    variable: [
      // [0]: Arithmetic Environment
      {
        pattern: /\$?\(\([\s\S]+?\)\)/,
        greedy: !0,
        inside: {
          // If there is a $ sign at the beginning highlight $(( and )) as variable
          variable: [
            {
              pattern: /(^\$\(\([\s\S]+)\)\)/,
              lookbehind: !0
            },
            /^\$\(\(/
          ],
          number: /\b0x[\dA-Fa-f]+\b|(?:\b\d+(?:\.\d*)?|\B\.\d+)(?:[Ee]-?\d+)?/,
          // Operators according to https://www.gnu.org/software/bash/manual/bashref.html#Shell-Arithmetic
          operator: /--|\+\+|\*\*=?|<<=?|>>=?|&&|\|\||[=!+\-*/%<>^&|]=?|[?~:]/,
          // If there is no $ sign at the beginning highlight (( and )) as punctuation
          punctuation: /\(\(?|\)\)?|,|;/
        }
      },
      // [1]: Command Substitution
      {
        pattern: /\$\((?:\([^)]+\)|[^()])+\)|`[^`]+`/,
        greedy: !0,
        inside: {
          variable: /^\$\(|^`|\)$|`$/
        }
      },
      // [2]: Brace expansion
      {
        pattern: /\$\{[^}]+\}/,
        greedy: !0,
        inside: {
          operator: /:[-=?+]?|[!\/]|##?|%%?|\^\^?|,,?/,
          punctuation: /[\[\]]/,
          environment: {
            pattern: RegExp("(\\{)" + e),
            lookbehind: !0,
            alias: "constant"
          }
        }
      },
      /\$(?:\w+|[#?*!@$])/
    ],
    // Escape sequences from echo and printf's manuals, and escaped quotes.
    entity: /\\(?:[abceEfnrtv\\"]|O?[0-7]{1,3}|U[0-9a-fA-F]{8}|u[0-9a-fA-F]{4}|x[0-9a-fA-F]{1,2})/
  };
  r.languages.bash = {
    shebang: {
      pattern: /^#!\s*\/.*/,
      alias: "important"
    },
    comment: {
      pattern: /(^|[^"{\\$])#.*/,
      lookbehind: !0
    },
    "function-name": [
      // a) function foo {
      // b) foo() {
      // c) function foo() {
      // but not “foo {”
      {
        // a) and c)
        pattern: /(\bfunction\s+)[\w-]+(?=(?:\s*\(?:\s*\))?\s*\{)/,
        lookbehind: !0,
        alias: "function"
      },
      {
        // b)
        pattern: /\b[\w-]+(?=\s*\(\s*\)\s*\{)/,
        alias: "function"
      }
    ],
    // Highlight variable names as variables in for and select beginnings.
    "for-or-select": {
      pattern: /(\b(?:for|select)\s+)\w+(?=\s+in\s)/,
      alias: "variable",
      lookbehind: !0
    },
    // Highlight variable names as variables in the left-hand part
    // of assignments (“=” and “+=”).
    "assign-left": {
      pattern: /(^|[\s;|&]|[<>]\()\w+(?:\.\w+)*(?=\+?=)/,
      inside: {
        environment: {
          pattern: RegExp("(^|[\\s;|&]|[<>]\\()" + e),
          lookbehind: !0,
          alias: "constant"
        }
      },
      alias: "variable",
      lookbehind: !0
    },
    // Highlight parameter names as variables
    parameter: {
      pattern: /(^|\s)-{1,2}(?:\w+:[+-]?)?\w+(?:\.\w+)*(?=[=\s]|$)/,
      alias: "variable",
      lookbehind: !0
    },
    string: [
      // Support for Here-documents https://en.wikipedia.org/wiki/Here_document
      {
        pattern: /((?:^|[^<])<<-?\s*)(\w+)\s[\s\S]*?(?:\r?\n|\r)\2/,
        lookbehind: !0,
        greedy: !0,
        inside: n
      },
      // Here-document with quotes around the tag
      // → No expansion (so no “inside”).
      {
        pattern: /((?:^|[^<])<<-?\s*)(["'])(\w+)\2\s[\s\S]*?(?:\r?\n|\r)\3/,
        lookbehind: !0,
        greedy: !0,
        inside: {
          bash: t
        }
      },
      // “Normal” string
      {
        // https://www.gnu.org/software/bash/manual/html_node/Double-Quotes.html
        pattern: /(^|[^\\](?:\\\\)*)"(?:\\[\s\S]|\$\([^)]+\)|\$(?!\()|`[^`]+`|[^"\\`$])*"/,
        lookbehind: !0,
        greedy: !0,
        inside: n
      },
      {
        // https://www.gnu.org/software/bash/manual/html_node/Single-Quotes.html
        pattern: /(^|[^$\\])'[^']*'/,
        lookbehind: !0,
        greedy: !0
      },
      {
        // https://www.gnu.org/software/bash/manual/html_node/ANSI_002dC-Quoting.html
        pattern: /\$'(?:[^'\\]|\\[\s\S])*'/,
        greedy: !0,
        inside: {
          entity: n.entity
        }
      }
    ],
    environment: {
      pattern: RegExp("\\$?" + e),
      alias: "constant"
    },
    variable: n.variable,
    function: {
      pattern: /(^|[\s;|&]|[<>]\()(?:add|apropos|apt|apt-cache|apt-get|aptitude|aspell|automysqlbackup|awk|basename|bash|bc|bconsole|bg|bzip2|cal|cargo|cat|cfdisk|chgrp|chkconfig|chmod|chown|chroot|cksum|clear|cmp|column|comm|composer|cp|cron|crontab|csplit|curl|cut|date|dc|dd|ddrescue|debootstrap|df|diff|diff3|dig|dir|dircolors|dirname|dirs|dmesg|docker|docker-compose|du|egrep|eject|env|ethtool|expand|expect|expr|fdformat|fdisk|fg|fgrep|file|find|fmt|fold|format|free|fsck|ftp|fuser|gawk|git|gparted|grep|groupadd|groupdel|groupmod|groups|grub-mkconfig|gzip|halt|head|hg|history|host|hostname|htop|iconv|id|ifconfig|ifdown|ifup|import|install|ip|java|jobs|join|kill|killall|less|link|ln|locate|logname|logrotate|look|lpc|lpr|lprint|lprintd|lprintq|lprm|ls|lsof|lynx|make|man|mc|mdadm|mkconfig|mkdir|mke2fs|mkfifo|mkfs|mkisofs|mknod|mkswap|mmv|more|most|mount|mtools|mtr|mutt|mv|nano|nc|netstat|nice|nl|node|nohup|notify-send|npm|nslookup|op|open|parted|passwd|paste|pathchk|ping|pkill|pnpm|podman|podman-compose|popd|pr|printcap|printenv|ps|pushd|pv|quota|quotacheck|quotactl|ram|rar|rcp|reboot|remsync|rename|renice|rev|rm|rmdir|rpm|rsync|scp|screen|sdiff|sed|sendmail|seq|service|sftp|sh|shellcheck|shuf|shutdown|sleep|slocate|sort|split|ssh|stat|strace|su|sudo|sum|suspend|swapon|sync|sysctl|tac|tail|tar|tee|time|timeout|top|touch|tr|traceroute|tsort|tty|umount|uname|unexpand|uniq|units|unrar|unshar|unzip|update-grub|uptime|useradd|userdel|usermod|users|uudecode|uuencode|v|vcpkg|vdir|vi|vim|virsh|vmstat|wait|watch|wc|wget|whereis|which|who|whoami|write|xargs|xdg-open|yarn|yes|zenity|zip|zsh|zypper)(?=$|[)\s;|&])/,
      lookbehind: !0
    },
    keyword: {
      pattern: /(^|[\s;|&]|[<>]\()(?:case|do|done|elif|else|esac|fi|for|function|if|in|select|then|until|while)(?=$|[)\s;|&])/,
      lookbehind: !0
    },
    // https://www.gnu.org/software/bash/manual/html_node/Shell-Builtin-Commands.html
    builtin: {
      pattern: /(^|[\s;|&]|[<>]\()(?:\.|:|alias|bind|break|builtin|caller|cd|command|continue|declare|echo|enable|eval|exec|exit|export|getopts|hash|help|let|local|logout|mapfile|printf|pwd|read|readarray|readonly|return|set|shift|shopt|source|test|times|trap|type|typeset|ulimit|umask|unalias|unset)(?=$|[)\s;|&])/,
      lookbehind: !0,
      // Alias added to make those easier to distinguish from strings.
      alias: "class-name"
    },
    boolean: {
      pattern: /(^|[\s;|&]|[<>]\()(?:false|true)(?=$|[)\s;|&])/,
      lookbehind: !0
    },
    "file-descriptor": {
      pattern: /\B&\d\b/,
      alias: "important"
    },
    operator: {
      // Lots of redirections here, but not just that.
      pattern: /\d?<>|>\||\+=|=[=~]?|!=?|<<[<-]?|[&\d]?>>|\d[<>]&?|[<>][&=]?|&[>&]?|\|[&|]?/,
      inside: {
        "file-descriptor": {
          pattern: /^\d/,
          alias: "important"
        }
      }
    },
    punctuation: /\$?\(\(?|\)\)?|\.\.|[{}[\];\\]/,
    number: {
      pattern: /(^|\s)(?:[1-9]\d*|0)(?:[.,]\d+)?\b/,
      lookbehind: !0
    }
  }, t.inside = r.languages.bash;
  for (var i = [
    "comment",
    "function-name",
    "for-or-select",
    "assign-left",
    "parameter",
    "string",
    "environment",
    "function",
    "keyword",
    "builtin",
    "boolean",
    "file-descriptor",
    "operator",
    "punctuation",
    "number"
  ], a = n.variable[1].inside, o = 0; o < i.length; o++)
    a[i[o]] = r.languages.bash[i[o]];
  r.languages.sh = r.languages.bash, r.languages.shell = r.languages.bash;
})(Prism);
new gt();
const Zn = (r) => {
  const e = {};
  for (let t = 0, n = r.length; t < n; t++) {
    const i = r[t];
    for (const a in i)
      e[a] ? e[a] = e[a].concat(i[a]) : e[a] = i[a];
  }
  return e;
}, Xn = [
  "abbr",
  "accept",
  "accept-charset",
  "accesskey",
  "action",
  "align",
  "alink",
  "allow",
  "allowfullscreen",
  "alt",
  "anchor",
  "archive",
  "as",
  "async",
  "autocapitalize",
  "autocomplete",
  "autocorrect",
  "autofocus",
  "autopictureinpicture",
  "autoplay",
  "axis",
  "background",
  "behavior",
  "bgcolor",
  "border",
  "bordercolor",
  "capture",
  "cellpadding",
  "cellspacing",
  "challenge",
  "char",
  "charoff",
  "charset",
  "checked",
  "cite",
  "class",
  "classid",
  "clear",
  "code",
  "codebase",
  "codetype",
  "color",
  "cols",
  "colspan",
  "compact",
  "content",
  "contenteditable",
  "controls",
  "controlslist",
  "conversiondestination",
  "coords",
  "crossorigin",
  "csp",
  "data",
  "datetime",
  "declare",
  "decoding",
  "default",
  "defer",
  "dir",
  "direction",
  "dirname",
  "disabled",
  "disablepictureinpicture",
  "disableremoteplayback",
  "disallowdocumentaccess",
  "download",
  "draggable",
  "elementtiming",
  "enctype",
  "end",
  "enterkeyhint",
  "event",
  "exportparts",
  "face",
  "for",
  "form",
  "formaction",
  "formenctype",
  "formmethod",
  "formnovalidate",
  "formtarget",
  "frame",
  "frameborder",
  "headers",
  "height",
  "hidden",
  "high",
  "href",
  "hreflang",
  "hreftranslate",
  "hspace",
  "http-equiv",
  "id",
  "imagesizes",
  "imagesrcset",
  "importance",
  "impressiondata",
  "impressionexpiry",
  "incremental",
  "inert",
  "inputmode",
  "integrity",
  "invisible",
  "ismap",
  "keytype",
  "kind",
  "label",
  "lang",
  "language",
  "latencyhint",
  "leftmargin",
  "link",
  "list",
  "loading",
  "longdesc",
  "loop",
  "low",
  "lowsrc",
  "manifest",
  "marginheight",
  "marginwidth",
  "max",
  "maxlength",
  "mayscript",
  "media",
  "method",
  "min",
  "minlength",
  "multiple",
  "muted",
  "name",
  "nohref",
  "nomodule",
  "nonce",
  "noresize",
  "noshade",
  "novalidate",
  "nowrap",
  "object",
  "open",
  "optimum",
  "part",
  "pattern",
  "ping",
  "placeholder",
  "playsinline",
  "policy",
  "poster",
  "preload",
  "pseudo",
  "readonly",
  "referrerpolicy",
  "rel",
  "reportingorigin",
  "required",
  "resources",
  "rev",
  "reversed",
  "role",
  "rows",
  "rowspan",
  "rules",
  "sandbox",
  "scheme",
  "scope",
  "scopes",
  "scrollamount",
  "scrolldelay",
  "scrolling",
  "select",
  "selected",
  "shadowroot",
  "shadowrootdelegatesfocus",
  "shape",
  "size",
  "sizes",
  "slot",
  "span",
  "spellcheck",
  "src",
  "srclang",
  "srcset",
  "standby",
  "start",
  "step",
  "style",
  "summary",
  "tabindex",
  "target",
  "text",
  "title",
  "topmargin",
  "translate",
  "truespeed",
  "trusttoken",
  "type",
  "usemap",
  "valign",
  "value",
  "valuetype",
  "version",
  "virtualkeyboardpolicy",
  "vlink",
  "vspace",
  "webkitdirectory",
  "width",
  "wrap"
], Wn = [
  "accent-height",
  "accumulate",
  "additive",
  "alignment-baseline",
  "ascent",
  "attributename",
  "attributetype",
  "azimuth",
  "basefrequency",
  "baseline-shift",
  "begin",
  "bias",
  "by",
  "class",
  "clip",
  "clippathunits",
  "clip-path",
  "clip-rule",
  "color",
  "color-interpolation",
  "color-interpolation-filters",
  "color-profile",
  "color-rendering",
  "cx",
  "cy",
  "d",
  "dx",
  "dy",
  "diffuseconstant",
  "direction",
  "display",
  "divisor",
  "dominant-baseline",
  "dur",
  "edgemode",
  "elevation",
  "end",
  "fill",
  "fill-opacity",
  "fill-rule",
  "filter",
  "filterunits",
  "flood-color",
  "flood-opacity",
  "font-family",
  "font-size",
  "font-size-adjust",
  "font-stretch",
  "font-style",
  "font-variant",
  "font-weight",
  "fx",
  "fy",
  "g1",
  "g2",
  "glyph-name",
  "glyphref",
  "gradientunits",
  "gradienttransform",
  "height",
  "href",
  "id",
  "image-rendering",
  "in",
  "in2",
  "k",
  "k1",
  "k2",
  "k3",
  "k4",
  "kerning",
  "keypoints",
  "keysplines",
  "keytimes",
  "lang",
  "lengthadjust",
  "letter-spacing",
  "kernelmatrix",
  "kernelunitlength",
  "lighting-color",
  "local",
  "marker-end",
  "marker-mid",
  "marker-start",
  "markerheight",
  "markerunits",
  "markerwidth",
  "maskcontentunits",
  "maskunits",
  "max",
  "mask",
  "media",
  "method",
  "mode",
  "min",
  "name",
  "numoctaves",
  "offset",
  "operator",
  "opacity",
  "order",
  "orient",
  "orientation",
  "origin",
  "overflow",
  "paint-order",
  "path",
  "pathlength",
  "patterncontentunits",
  "patterntransform",
  "patternunits",
  "points",
  "preservealpha",
  "preserveaspectratio",
  "primitiveunits",
  "r",
  "rx",
  "ry",
  "radius",
  "refx",
  "refy",
  "repeatcount",
  "repeatdur",
  "restart",
  "result",
  "rotate",
  "scale",
  "seed",
  "shape-rendering",
  "specularconstant",
  "specularexponent",
  "spreadmethod",
  "startoffset",
  "stddeviation",
  "stitchtiles",
  "stop-color",
  "stop-opacity",
  "stroke-dasharray",
  "stroke-dashoffset",
  "stroke-linecap",
  "stroke-linejoin",
  "stroke-miterlimit",
  "stroke-opacity",
  "stroke",
  "stroke-width",
  "style",
  "surfacescale",
  "systemlanguage",
  "tabindex",
  "targetx",
  "targety",
  "transform",
  "transform-origin",
  "text-anchor",
  "text-decoration",
  "text-rendering",
  "textlength",
  "type",
  "u1",
  "u2",
  "unicode",
  "values",
  "viewbox",
  "visibility",
  "version",
  "vert-adv-y",
  "vert-origin-x",
  "vert-origin-y",
  "width",
  "word-spacing",
  "wrap",
  "writing-mode",
  "xchannelselector",
  "ychannelselector",
  "x",
  "x1",
  "x2",
  "xmlns",
  "y",
  "y1",
  "y2",
  "z",
  "zoomandpan"
], Yn = [
  "accent",
  "accentunder",
  "align",
  "bevelled",
  "close",
  "columnsalign",
  "columnlines",
  "columnspan",
  "denomalign",
  "depth",
  "dir",
  "display",
  "displaystyle",
  "encoding",
  "fence",
  "frame",
  "height",
  "href",
  "id",
  "largeop",
  "length",
  "linethickness",
  "lspace",
  "lquote",
  "mathbackground",
  "mathcolor",
  "mathsize",
  "mathvariant",
  "maxsize",
  "minsize",
  "movablelimits",
  "notation",
  "numalign",
  "open",
  "rowalign",
  "rowlines",
  "rowspacing",
  "rowspan",
  "rspace",
  "rquote",
  "scriptlevel",
  "scriptminsize",
  "scriptsizemultiplier",
  "selection",
  "separator",
  "separators",
  "stretchy",
  "subscriptshift",
  "supscriptshift",
  "symmetric",
  "voffset",
  "width",
  "xmlns"
];
Zn([
  Object.fromEntries(Xn.map((r) => [r, ["*"]])),
  Object.fromEntries(Wn.map((r) => [r, ["svg:*"]])),
  Object.fromEntries(Yn.map((r) => [r, ["math:*"]]))
]);
const {
  HtmlTagHydration: Ua,
  SvelteComponent: Ga,
  attr: Za,
  binding_callbacks: Xa,
  children: Wa,
  claim_element: Ya,
  claim_html_tag: Ka,
  detach: Qa,
  element: Va,
  init: Ja,
  insert_hydration: eo,
  noop: to,
  safe_not_equal: no,
  toggle_class: io
} = window.__gradio__svelte__internal, { afterUpdate: ao, tick: oo, onMount: ro } = window.__gradio__svelte__internal, {
  SvelteComponent: lo,
  attr: so,
  children: uo,
  claim_component: co,
  claim_element: _o,
  create_component: po,
  destroy_component: ho,
  detach: mo,
  element: go,
  init: fo,
  insert_hydration: $o,
  mount_component: Do,
  safe_not_equal: vo,
  transition_in: Fo,
  transition_out: yo
} = window.__gradio__svelte__internal, {
  SvelteComponent: bo,
  attr: wo,
  check_outros: ko,
  children: Co,
  claim_component: Ao,
  claim_element: Eo,
  claim_space: So,
  create_component: xo,
  create_slot: Bo,
  destroy_component: qo,
  detach: To,
  element: Ro,
  empty: Io,
  get_all_dirty_from_scope: zo,
  get_slot_changes: Lo,
  group_outros: Oo,
  init: Po,
  insert_hydration: No,
  mount_component: Mo,
  safe_not_equal: jo,
  space: Ho,
  toggle_class: Uo,
  transition_in: Go,
  transition_out: Zo,
  update_slot_base: Xo
} = window.__gradio__svelte__internal, {
  SvelteComponent: Wo,
  append_hydration: Yo,
  attr: Ko,
  children: Qo,
  claim_component: Vo,
  claim_element: Jo,
  claim_space: er,
  claim_text: tr,
  create_component: nr,
  destroy_component: ir,
  detach: ar,
  element: or,
  init: rr,
  insert_hydration: lr,
  mount_component: sr,
  safe_not_equal: ur,
  set_data: cr,
  space: _r,
  text: dr,
  toggle_class: pr,
  transition_in: hr,
  transition_out: mr
} = window.__gradio__svelte__internal, {
  SvelteComponent: gr,
  append_hydration: fr,
  attr: $r,
  bubble: Dr,
  check_outros: vr,
  children: Fr,
  claim_component: yr,
  claim_element: br,
  claim_space: wr,
  claim_text: kr,
  construct_svelte_component: Cr,
  create_component: Ar,
  create_slot: Er,
  destroy_component: Sr,
  detach: xr,
  element: Br,
  get_all_dirty_from_scope: qr,
  get_slot_changes: Tr,
  group_outros: Rr,
  init: Ir,
  insert_hydration: zr,
  listen: Lr,
  mount_component: Or,
  safe_not_equal: Pr,
  set_data: Nr,
  set_style: Mr,
  space: jr,
  text: Hr,
  toggle_class: Ur,
  transition_in: Gr,
  transition_out: Zr,
  update_slot_base: Xr
} = window.__gradio__svelte__internal, {
  SvelteComponent: Wr,
  append_hydration: Yr,
  attr: Kr,
  binding_callbacks: Qr,
  children: Vr,
  claim_element: Jr,
  create_slot: el,
  detach: tl,
  element: nl,
  get_all_dirty_from_scope: il,
  get_slot_changes: al,
  init: ol,
  insert_hydration: rl,
  safe_not_equal: ll,
  toggle_class: sl,
  transition_in: ul,
  transition_out: cl,
  update_slot_base: _l
} = window.__gradio__svelte__internal, {
  SvelteComponent: dl,
  append_hydration: pl,
  attr: hl,
  children: ml,
  claim_svg_element: gl,
  detach: fl,
  init: $l,
  insert_hydration: Dl,
  noop: vl,
  safe_not_equal: Fl,
  svg_element: yl
} = window.__gradio__svelte__internal, {
  SvelteComponent: bl,
  append_hydration: wl,
  attr: kl,
  children: Cl,
  claim_svg_element: Al,
  detach: El,
  init: Sl,
  insert_hydration: xl,
  noop: Bl,
  safe_not_equal: ql,
  svg_element: Tl
} = window.__gradio__svelte__internal, {
  SvelteComponent: Rl,
  append_hydration: Il,
  attr: zl,
  children: Ll,
  claim_svg_element: Ol,
  detach: Pl,
  init: Nl,
  insert_hydration: Ml,
  noop: jl,
  safe_not_equal: Hl,
  svg_element: Ul
} = window.__gradio__svelte__internal, {
  SvelteComponent: Gl,
  append_hydration: Zl,
  attr: Xl,
  children: Wl,
  claim_svg_element: Yl,
  detach: Kl,
  init: Ql,
  insert_hydration: Vl,
  noop: Jl,
  safe_not_equal: es,
  svg_element: ts
} = window.__gradio__svelte__internal, {
  SvelteComponent: ns,
  append_hydration: is,
  attr: as,
  children: os,
  claim_svg_element: rs,
  detach: ls,
  init: ss,
  insert_hydration: us,
  noop: cs,
  safe_not_equal: _s,
  svg_element: ds
} = window.__gradio__svelte__internal, {
  SvelteComponent: ps,
  append_hydration: hs,
  attr: ms,
  children: gs,
  claim_svg_element: fs,
  detach: $s,
  init: Ds,
  insert_hydration: vs,
  noop: Fs,
  safe_not_equal: ys,
  svg_element: bs
} = window.__gradio__svelte__internal, {
  SvelteComponent: ws,
  append_hydration: ks,
  attr: Cs,
  children: As,
  claim_svg_element: Es,
  detach: Ss,
  init: xs,
  insert_hydration: Bs,
  noop: qs,
  safe_not_equal: Ts,
  svg_element: Rs
} = window.__gradio__svelte__internal, {
  SvelteComponent: Is,
  append_hydration: zs,
  attr: Ls,
  children: Os,
  claim_svg_element: Ps,
  detach: Ns,
  init: Ms,
  insert_hydration: js,
  noop: Hs,
  safe_not_equal: Us,
  svg_element: Gs
} = window.__gradio__svelte__internal, {
  SvelteComponent: Zs,
  append_hydration: Xs,
  attr: Ws,
  children: Ys,
  claim_svg_element: Ks,
  detach: Qs,
  init: Vs,
  insert_hydration: Js,
  noop: eu,
  safe_not_equal: tu,
  svg_element: nu
} = window.__gradio__svelte__internal, {
  SvelteComponent: iu,
  append_hydration: au,
  attr: ou,
  children: ru,
  claim_svg_element: lu,
  detach: su,
  init: uu,
  insert_hydration: cu,
  noop: _u,
  safe_not_equal: du,
  svg_element: pu
} = window.__gradio__svelte__internal, {
  SvelteComponent: hu,
  append_hydration: mu,
  attr: gu,
  children: fu,
  claim_svg_element: $u,
  detach: Du,
  init: vu,
  insert_hydration: Fu,
  noop: yu,
  safe_not_equal: bu,
  svg_element: wu
} = window.__gradio__svelte__internal, {
  SvelteComponent: ku,
  append_hydration: Cu,
  attr: Au,
  children: Eu,
  claim_svg_element: Su,
  detach: xu,
  init: Bu,
  insert_hydration: qu,
  noop: Tu,
  safe_not_equal: Ru,
  svg_element: Iu
} = window.__gradio__svelte__internal, {
  SvelteComponent: zu,
  append_hydration: Lu,
  attr: Ou,
  children: Pu,
  claim_svg_element: Nu,
  detach: Mu,
  init: ju,
  insert_hydration: Hu,
  noop: Uu,
  safe_not_equal: Gu,
  set_style: Zu,
  svg_element: Xu
} = window.__gradio__svelte__internal, {
  SvelteComponent: Wu,
  append_hydration: Yu,
  attr: Ku,
  children: Qu,
  claim_svg_element: Vu,
  detach: Ju,
  init: ec,
  insert_hydration: tc,
  noop: nc,
  safe_not_equal: ic,
  svg_element: ac
} = window.__gradio__svelte__internal, {
  SvelteComponent: oc,
  append_hydration: rc,
  attr: lc,
  children: sc,
  claim_svg_element: uc,
  detach: cc,
  init: _c,
  insert_hydration: dc,
  noop: pc,
  safe_not_equal: hc,
  svg_element: mc
} = window.__gradio__svelte__internal, {
  SvelteComponent: gc,
  append_hydration: fc,
  attr: $c,
  children: Dc,
  claim_svg_element: vc,
  detach: Fc,
  init: yc,
  insert_hydration: bc,
  noop: wc,
  safe_not_equal: kc,
  svg_element: Cc
} = window.__gradio__svelte__internal, {
  SvelteComponent: Ac,
  append_hydration: Ec,
  attr: Sc,
  children: xc,
  claim_svg_element: Bc,
  detach: qc,
  init: Tc,
  insert_hydration: Rc,
  noop: Ic,
  safe_not_equal: zc,
  svg_element: Lc
} = window.__gradio__svelte__internal, {
  SvelteComponent: Oc,
  append_hydration: Pc,
  attr: Nc,
  children: Mc,
  claim_svg_element: jc,
  detach: Hc,
  init: Uc,
  insert_hydration: Gc,
  noop: Zc,
  safe_not_equal: Xc,
  svg_element: Wc
} = window.__gradio__svelte__internal, {
  SvelteComponent: Yc,
  append_hydration: Kc,
  attr: Qc,
  children: Vc,
  claim_svg_element: Jc,
  detach: e_,
  init: t_,
  insert_hydration: n_,
  noop: i_,
  safe_not_equal: a_,
  svg_element: o_
} = window.__gradio__svelte__internal, {
  SvelteComponent: r_,
  append_hydration: l_,
  attr: s_,
  children: u_,
  claim_svg_element: c_,
  detach: __,
  init: d_,
  insert_hydration: p_,
  noop: h_,
  safe_not_equal: m_,
  svg_element: g_
} = window.__gradio__svelte__internal, {
  SvelteComponent: f_,
  append_hydration: $_,
  attr: D_,
  children: v_,
  claim_svg_element: F_,
  detach: y_,
  init: b_,
  insert_hydration: w_,
  noop: k_,
  safe_not_equal: C_,
  svg_element: A_
} = window.__gradio__svelte__internal, {
  SvelteComponent: E_,
  append_hydration: S_,
  attr: x_,
  children: B_,
  claim_svg_element: q_,
  detach: T_,
  init: R_,
  insert_hydration: I_,
  noop: z_,
  safe_not_equal: L_,
  svg_element: O_
} = window.__gradio__svelte__internal, {
  SvelteComponent: P_,
  append_hydration: N_,
  attr: M_,
  children: j_,
  claim_svg_element: H_,
  detach: U_,
  init: G_,
  insert_hydration: Z_,
  noop: X_,
  safe_not_equal: W_,
  svg_element: Y_
} = window.__gradio__svelte__internal, {
  SvelteComponent: K_,
  append_hydration: Q_,
  attr: V_,
  children: J_,
  claim_svg_element: ed,
  detach: td,
  init: nd,
  insert_hydration: id,
  noop: ad,
  safe_not_equal: od,
  svg_element: rd
} = window.__gradio__svelte__internal, {
  SvelteComponent: ld,
  append_hydration: sd,
  attr: ud,
  children: cd,
  claim_svg_element: _d,
  detach: dd,
  init: pd,
  insert_hydration: hd,
  noop: md,
  safe_not_equal: gd,
  svg_element: fd
} = window.__gradio__svelte__internal, {
  SvelteComponent: $d,
  append_hydration: Dd,
  attr: vd,
  children: Fd,
  claim_svg_element: yd,
  detach: bd,
  init: wd,
  insert_hydration: kd,
  noop: Cd,
  safe_not_equal: Ad,
  svg_element: Ed
} = window.__gradio__svelte__internal, {
  SvelteComponent: Sd,
  append_hydration: xd,
  attr: Bd,
  children: qd,
  claim_svg_element: Td,
  detach: Rd,
  init: Id,
  insert_hydration: zd,
  noop: Ld,
  safe_not_equal: Od,
  svg_element: Pd
} = window.__gradio__svelte__internal, {
  SvelteComponent: Nd,
  append_hydration: Md,
  attr: jd,
  children: Hd,
  claim_svg_element: Ud,
  detach: Gd,
  init: Zd,
  insert_hydration: Xd,
  noop: Wd,
  safe_not_equal: Yd,
  svg_element: Kd
} = window.__gradio__svelte__internal, {
  SvelteComponent: Qd,
  append_hydration: Vd,
  attr: Jd,
  children: ep,
  claim_svg_element: tp,
  detach: np,
  init: ip,
  insert_hydration: ap,
  noop: op,
  safe_not_equal: rp,
  svg_element: lp
} = window.__gradio__svelte__internal, {
  SvelteComponent: sp,
  append_hydration: up,
  attr: cp,
  children: _p,
  claim_svg_element: dp,
  detach: pp,
  init: hp,
  insert_hydration: mp,
  noop: gp,
  safe_not_equal: fp,
  svg_element: $p
} = window.__gradio__svelte__internal, {
  SvelteComponent: Dp,
  append_hydration: vp,
  attr: Fp,
  children: yp,
  claim_svg_element: bp,
  detach: wp,
  init: kp,
  insert_hydration: Cp,
  noop: Ap,
  safe_not_equal: Ep,
  svg_element: Sp
} = window.__gradio__svelte__internal, {
  SvelteComponent: xp,
  append_hydration: Bp,
  attr: qp,
  children: Tp,
  claim_svg_element: Rp,
  detach: Ip,
  init: zp,
  insert_hydration: Lp,
  noop: Op,
  safe_not_equal: Pp,
  svg_element: Np
} = window.__gradio__svelte__internal, {
  SvelteComponent: Mp,
  append_hydration: jp,
  attr: Hp,
  children: Up,
  claim_svg_element: Gp,
  detach: Zp,
  init: Xp,
  insert_hydration: Wp,
  noop: Yp,
  safe_not_equal: Kp,
  svg_element: Qp
} = window.__gradio__svelte__internal, {
  SvelteComponent: Vp,
  append_hydration: Jp,
  attr: eh,
  children: th,
  claim_svg_element: nh,
  detach: ih,
  init: ah,
  insert_hydration: oh,
  noop: rh,
  safe_not_equal: lh,
  svg_element: sh
} = window.__gradio__svelte__internal, {
  SvelteComponent: uh,
  append_hydration: ch,
  attr: _h,
  children: dh,
  claim_svg_element: ph,
  detach: hh,
  init: mh,
  insert_hydration: gh,
  noop: fh,
  safe_not_equal: $h,
  svg_element: Dh
} = window.__gradio__svelte__internal, {
  SvelteComponent: vh,
  append_hydration: Fh,
  attr: yh,
  children: bh,
  claim_svg_element: wh,
  detach: kh,
  init: Ch,
  insert_hydration: Ah,
  noop: Eh,
  safe_not_equal: Sh,
  svg_element: xh
} = window.__gradio__svelte__internal, {
  SvelteComponent: Bh,
  append_hydration: qh,
  attr: Th,
  children: Rh,
  claim_svg_element: Ih,
  detach: zh,
  init: Lh,
  insert_hydration: Oh,
  noop: Ph,
  safe_not_equal: Nh,
  svg_element: Mh
} = window.__gradio__svelte__internal, {
  SvelteComponent: jh,
  append_hydration: Hh,
  attr: Uh,
  children: Gh,
  claim_svg_element: Zh,
  detach: Xh,
  init: Wh,
  insert_hydration: Yh,
  noop: Kh,
  safe_not_equal: Qh,
  svg_element: Vh
} = window.__gradio__svelte__internal, {
  SvelteComponent: Jh,
  append_hydration: em,
  attr: tm,
  children: nm,
  claim_svg_element: im,
  detach: am,
  init: om,
  insert_hydration: rm,
  noop: lm,
  safe_not_equal: sm,
  svg_element: um
} = window.__gradio__svelte__internal, {
  SvelteComponent: cm,
  append_hydration: _m,
  attr: dm,
  children: pm,
  claim_svg_element: hm,
  detach: mm,
  init: gm,
  insert_hydration: fm,
  noop: $m,
  safe_not_equal: Dm,
  svg_element: vm
} = window.__gradio__svelte__internal, {
  SvelteComponent: Fm,
  append_hydration: ym,
  attr: bm,
  children: wm,
  claim_svg_element: km,
  detach: Cm,
  init: Am,
  insert_hydration: Em,
  noop: Sm,
  safe_not_equal: xm,
  svg_element: Bm
} = window.__gradio__svelte__internal, {
  SvelteComponent: qm,
  append_hydration: Tm,
  attr: Rm,
  children: Im,
  claim_svg_element: zm,
  detach: Lm,
  init: Om,
  insert_hydration: Pm,
  noop: Nm,
  safe_not_equal: Mm,
  svg_element: jm
} = window.__gradio__svelte__internal, {
  SvelteComponent: Hm,
  append_hydration: Um,
  attr: Gm,
  children: Zm,
  claim_svg_element: Xm,
  detach: Wm,
  init: Ym,
  insert_hydration: Km,
  noop: Qm,
  safe_not_equal: Vm,
  svg_element: Jm
} = window.__gradio__svelte__internal, {
  SvelteComponent: eg,
  append_hydration: tg,
  attr: ng,
  children: ig,
  claim_svg_element: ag,
  detach: og,
  init: rg,
  insert_hydration: lg,
  noop: sg,
  safe_not_equal: ug,
  svg_element: cg
} = window.__gradio__svelte__internal, {
  SvelteComponent: _g,
  append_hydration: dg,
  attr: pg,
  children: hg,
  claim_svg_element: mg,
  detach: gg,
  init: fg,
  insert_hydration: $g,
  noop: Dg,
  safe_not_equal: vg,
  svg_element: Fg
} = window.__gradio__svelte__internal, {
  SvelteComponent: yg,
  append_hydration: bg,
  attr: wg,
  children: kg,
  claim_svg_element: Cg,
  detach: Ag,
  init: Eg,
  insert_hydration: Sg,
  noop: xg,
  safe_not_equal: Bg,
  svg_element: qg
} = window.__gradio__svelte__internal, {
  SvelteComponent: Tg,
  append_hydration: Rg,
  attr: Ig,
  children: zg,
  claim_svg_element: Lg,
  detach: Og,
  init: Pg,
  insert_hydration: Ng,
  noop: Mg,
  safe_not_equal: jg,
  svg_element: Hg
} = window.__gradio__svelte__internal, {
  SvelteComponent: Ug,
  append_hydration: Gg,
  attr: Zg,
  children: Xg,
  claim_svg_element: Wg,
  detach: Yg,
  init: Kg,
  insert_hydration: Qg,
  noop: Vg,
  safe_not_equal: Jg,
  set_style: ef,
  svg_element: tf
} = window.__gradio__svelte__internal, {
  SvelteComponent: nf,
  append_hydration: af,
  attr: of,
  children: rf,
  claim_svg_element: lf,
  detach: sf,
  init: uf,
  insert_hydration: cf,
  noop: _f,
  safe_not_equal: df,
  svg_element: pf
} = window.__gradio__svelte__internal, {
  SvelteComponent: hf,
  append_hydration: mf,
  attr: gf,
  children: ff,
  claim_svg_element: $f,
  detach: Df,
  init: vf,
  insert_hydration: Ff,
  noop: yf,
  safe_not_equal: bf,
  svg_element: wf
} = window.__gradio__svelte__internal, {
  SvelteComponent: kf,
  append_hydration: Cf,
  attr: Af,
  children: Ef,
  claim_svg_element: Sf,
  detach: xf,
  init: Bf,
  insert_hydration: qf,
  noop: Tf,
  safe_not_equal: Rf,
  svg_element: If
} = window.__gradio__svelte__internal, {
  SvelteComponent: zf,
  append_hydration: Lf,
  attr: Of,
  children: Pf,
  claim_svg_element: Nf,
  detach: Mf,
  init: jf,
  insert_hydration: Hf,
  noop: Uf,
  safe_not_equal: Gf,
  svg_element: Zf
} = window.__gradio__svelte__internal, {
  SvelteComponent: Xf,
  append_hydration: Wf,
  attr: Yf,
  children: Kf,
  claim_svg_element: Qf,
  detach: Vf,
  init: Jf,
  insert_hydration: e0,
  noop: t0,
  safe_not_equal: n0,
  svg_element: i0
} = window.__gradio__svelte__internal, {
  SvelteComponent: a0,
  append_hydration: o0,
  attr: r0,
  children: l0,
  claim_svg_element: s0,
  detach: u0,
  init: c0,
  insert_hydration: _0,
  noop: d0,
  safe_not_equal: p0,
  svg_element: h0
} = window.__gradio__svelte__internal, {
  SvelteComponent: m0,
  append_hydration: g0,
  attr: f0,
  children: $0,
  claim_svg_element: D0,
  detach: v0,
  init: F0,
  insert_hydration: y0,
  noop: b0,
  safe_not_equal: w0,
  svg_element: k0
} = window.__gradio__svelte__internal, {
  SvelteComponent: C0,
  append_hydration: A0,
  attr: E0,
  children: S0,
  claim_svg_element: x0,
  detach: B0,
  init: q0,
  insert_hydration: T0,
  noop: R0,
  safe_not_equal: I0,
  svg_element: z0
} = window.__gradio__svelte__internal, {
  SvelteComponent: L0,
  append_hydration: O0,
  attr: P0,
  children: N0,
  claim_svg_element: M0,
  claim_text: j0,
  detach: H0,
  init: U0,
  insert_hydration: G0,
  noop: Z0,
  safe_not_equal: X0,
  svg_element: W0,
  text: Y0
} = window.__gradio__svelte__internal, {
  SvelteComponent: K0,
  append_hydration: Q0,
  attr: V0,
  children: J0,
  claim_svg_element: e$,
  detach: t$,
  init: n$,
  insert_hydration: i$,
  noop: a$,
  safe_not_equal: o$,
  svg_element: r$
} = window.__gradio__svelte__internal, {
  SvelteComponent: l$,
  append_hydration: s$,
  attr: u$,
  children: c$,
  claim_svg_element: _$,
  detach: d$,
  init: p$,
  insert_hydration: h$,
  noop: m$,
  safe_not_equal: g$,
  svg_element: f$
} = window.__gradio__svelte__internal, {
  SvelteComponent: $$,
  append_hydration: D$,
  attr: v$,
  children: F$,
  claim_svg_element: y$,
  detach: b$,
  init: w$,
  insert_hydration: k$,
  noop: C$,
  safe_not_equal: A$,
  svg_element: E$
} = window.__gradio__svelte__internal, {
  SvelteComponent: S$,
  append_hydration: x$,
  attr: B$,
  children: q$,
  claim_svg_element: T$,
  detach: R$,
  init: I$,
  insert_hydration: z$,
  noop: L$,
  safe_not_equal: O$,
  svg_element: P$
} = window.__gradio__svelte__internal, {
  SvelteComponent: N$,
  append_hydration: M$,
  attr: j$,
  children: H$,
  claim_svg_element: U$,
  detach: G$,
  init: Z$,
  insert_hydration: X$,
  noop: W$,
  safe_not_equal: Y$,
  svg_element: K$
} = window.__gradio__svelte__internal, {
  SvelteComponent: Q$,
  append_hydration: V$,
  attr: J$,
  children: e1,
  claim_svg_element: t1,
  detach: n1,
  init: i1,
  insert_hydration: a1,
  noop: o1,
  safe_not_equal: r1,
  svg_element: l1
} = window.__gradio__svelte__internal, {
  SvelteComponent: s1,
  append_hydration: u1,
  attr: c1,
  children: _1,
  claim_svg_element: d1,
  detach: p1,
  init: h1,
  insert_hydration: m1,
  noop: g1,
  safe_not_equal: f1,
  svg_element: $1
} = window.__gradio__svelte__internal, {
  SvelteComponent: D1,
  append_hydration: v1,
  attr: F1,
  children: y1,
  claim_svg_element: b1,
  claim_text: w1,
  detach: k1,
  init: C1,
  insert_hydration: A1,
  noop: E1,
  safe_not_equal: S1,
  svg_element: x1,
  text: B1
} = window.__gradio__svelte__internal, {
  SvelteComponent: q1,
  append_hydration: T1,
  attr: R1,
  children: I1,
  claim_svg_element: z1,
  claim_text: L1,
  detach: O1,
  init: P1,
  insert_hydration: N1,
  noop: M1,
  safe_not_equal: j1,
  svg_element: H1,
  text: U1
} = window.__gradio__svelte__internal, {
  SvelteComponent: G1,
  append_hydration: Z1,
  attr: X1,
  children: W1,
  claim_svg_element: Y1,
  claim_text: K1,
  detach: Q1,
  init: V1,
  insert_hydration: J1,
  noop: eD,
  safe_not_equal: tD,
  svg_element: nD,
  text: iD
} = window.__gradio__svelte__internal, {
  SvelteComponent: aD,
  append_hydration: oD,
  attr: rD,
  children: lD,
  claim_svg_element: sD,
  detach: uD,
  init: cD,
  insert_hydration: _D,
  noop: dD,
  safe_not_equal: pD,
  svg_element: hD
} = window.__gradio__svelte__internal, {
  SvelteComponent: mD,
  append_hydration: gD,
  attr: fD,
  children: $D,
  claim_svg_element: DD,
  detach: vD,
  init: FD,
  insert_hydration: yD,
  noop: bD,
  safe_not_equal: wD,
  svg_element: kD
} = window.__gradio__svelte__internal, {
  SvelteComponent: CD,
  append_hydration: AD,
  attr: ED,
  children: SD,
  claim_svg_element: xD,
  detach: BD,
  init: qD,
  insert_hydration: TD,
  noop: RD,
  safe_not_equal: ID,
  svg_element: zD
} = window.__gradio__svelte__internal, {
  SvelteComponent: LD,
  append_hydration: OD,
  attr: PD,
  children: ND,
  claim_svg_element: MD,
  detach: jD,
  init: HD,
  insert_hydration: UD,
  noop: GD,
  safe_not_equal: ZD,
  svg_element: XD
} = window.__gradio__svelte__internal, {
  SvelteComponent: WD,
  append_hydration: YD,
  attr: KD,
  children: QD,
  claim_svg_element: VD,
  detach: JD,
  init: ev,
  insert_hydration: tv,
  noop: nv,
  safe_not_equal: iv,
  svg_element: av
} = window.__gradio__svelte__internal, {
  SvelteComponent: ov,
  append_hydration: rv,
  attr: lv,
  children: sv,
  claim_svg_element: uv,
  detach: cv,
  init: _v,
  insert_hydration: dv,
  noop: pv,
  safe_not_equal: hv,
  svg_element: mv
} = window.__gradio__svelte__internal, {
  SvelteComponent: gv,
  append_hydration: fv,
  attr: $v,
  children: Dv,
  claim_svg_element: vv,
  detach: Fv,
  init: yv,
  insert_hydration: bv,
  noop: wv,
  safe_not_equal: kv,
  svg_element: Cv
} = window.__gradio__svelte__internal, {
  SvelteComponent: Av,
  append_hydration: Ev,
  attr: Sv,
  children: xv,
  claim_svg_element: Bv,
  detach: qv,
  init: Tv,
  insert_hydration: Rv,
  noop: Iv,
  safe_not_equal: zv,
  svg_element: Lv
} = window.__gradio__svelte__internal, {
  SvelteComponent: Ov,
  claim_component: Pv,
  create_component: Nv,
  destroy_component: Mv,
  init: jv,
  mount_component: Hv,
  safe_not_equal: Uv,
  transition_in: Gv,
  transition_out: Zv
} = window.__gradio__svelte__internal, { createEventDispatcher: Xv } = window.__gradio__svelte__internal, {
  SvelteComponent: Wv,
  append_hydration: Yv,
  attr: Kv,
  check_outros: Qv,
  children: Vv,
  claim_component: Jv,
  claim_element: eF,
  claim_space: tF,
  claim_text: nF,
  create_component: iF,
  destroy_component: aF,
  detach: oF,
  element: rF,
  empty: lF,
  group_outros: sF,
  init: uF,
  insert_hydration: cF,
  mount_component: _F,
  safe_not_equal: dF,
  set_data: pF,
  space: hF,
  text: mF,
  toggle_class: gF,
  transition_in: fF,
  transition_out: $F
} = window.__gradio__svelte__internal, {
  SvelteComponent: DF,
  attr: vF,
  children: FF,
  claim_element: yF,
  create_slot: bF,
  detach: wF,
  element: kF,
  get_all_dirty_from_scope: CF,
  get_slot_changes: AF,
  init: EF,
  insert_hydration: SF,
  safe_not_equal: xF,
  toggle_class: BF,
  transition_in: qF,
  transition_out: TF,
  update_slot_base: RF
} = window.__gradio__svelte__internal, {
  SvelteComponent: IF,
  append_hydration: zF,
  attr: LF,
  check_outros: OF,
  children: PF,
  claim_component: NF,
  claim_element: MF,
  claim_space: jF,
  create_component: HF,
  destroy_component: UF,
  detach: GF,
  element: ZF,
  empty: XF,
  group_outros: WF,
  init: YF,
  insert_hydration: KF,
  listen: QF,
  mount_component: VF,
  safe_not_equal: JF,
  space: ey,
  toggle_class: ty,
  transition_in: ny,
  transition_out: iy
} = window.__gradio__svelte__internal, {
  SvelteComponent: ay,
  attr: oy,
  children: ry,
  claim_element: ly,
  create_slot: sy,
  detach: uy,
  element: cy,
  get_all_dirty_from_scope: _y,
  get_slot_changes: dy,
  init: py,
  insert_hydration: hy,
  null_to_empty: my,
  safe_not_equal: gy,
  transition_in: fy,
  transition_out: $y,
  update_slot_base: Dy
} = window.__gradio__svelte__internal, {
  SvelteComponent: vy,
  check_outros: Fy,
  claim_component: yy,
  create_component: by,
  destroy_component: wy,
  detach: ky,
  empty: Cy,
  group_outros: Ay,
  init: Ey,
  insert_hydration: Sy,
  mount_component: xy,
  noop: By,
  safe_not_equal: qy,
  transition_in: Ty,
  transition_out: Ry
} = window.__gradio__svelte__internal, { createEventDispatcher: Iy } = window.__gradio__svelte__internal, {
  SvelteComponent: zy,
  append_hydration: Ly,
  attr: Oy,
  binding_callbacks: Py,
  bubble: Ny,
  check_outros: My,
  children: jy,
  claim_component: Hy,
  claim_element: Uy,
  claim_space: Gy,
  create_component: Zy,
  destroy_component: Xy,
  detach: Wy,
  element: Yy,
  empty: Ky,
  group_outros: Qy,
  init: Vy,
  insert_hydration: Jy,
  listen: eb,
  mount_component: tb,
  safe_not_equal: nb,
  space: ib,
  toggle_class: ab,
  transition_in: ob,
  transition_out: rb
} = window.__gradio__svelte__internal, { createEventDispatcher: lb, onMount: sb } = window.__gradio__svelte__internal, {
  SvelteComponent: Kn,
  append_hydration: ft,
  attr: T,
  bubble: Qn,
  check_outros: Te,
  children: $t,
  claim_component: Dt,
  claim_element: vt,
  claim_space: Ft,
  create_component: yt,
  create_slot: bt,
  destroy_component: wt,
  detach: te,
  element: kt,
  empty: Je,
  get_all_dirty_from_scope: Ct,
  get_slot_changes: At,
  group_outros: Re,
  init: Vn,
  insert_hydration: Ie,
  listen: Jn,
  mount_component: Et,
  safe_not_equal: ei,
  set_style: q,
  space: St,
  toggle_class: Y,
  transition_in: I,
  transition_out: M,
  update_slot_base: xt
} = window.__gradio__svelte__internal;
function ti(r) {
  let e, t, n, i, a, o, l = (
    /*icon*/
    r[7] && et(r)
  );
  const s = (
    /*#slots*/
    r[12].default
  ), _ = bt(
    s,
    r,
    /*$$scope*/
    r[11],
    null
  );
  return {
    c() {
      e = kt("button"), l && l.c(), t = St(), _ && _.c(), this.h();
    },
    l(d) {
      e = vt(d, "BUTTON", { class: !0, id: !0 });
      var f = $t(e);
      l && l.l(f), t = Ft(f), _ && _.l(f), f.forEach(te), this.h();
    },
    h() {
      T(e, "class", n = /*size*/
      r[4] + " " + /*variant*/
      r[3] + " " + /*elem_classes*/
      r[1].join(" ") + " svelte-rvoavt"), T(
        e,
        "id",
        /*elem_id*/
        r[0]
      ), e.disabled = /*disabled*/
      r[8], Y(e, "hidden", !/*visible*/
      r[2]), q(
        e,
        "flex-grow",
        /*scale*/
        r[9]
      ), q(
        e,
        "width",
        /*scale*/
        r[9] === 0 ? "fit-content" : null
      ), q(e, "min-width", typeof /*min_width*/
      r[10] == "number" ? `calc(min(${/*min_width*/
      r[10]}px, 100%))` : null);
    },
    m(d, f) {
      Ie(d, e, f), l && l.m(e, null), ft(e, t), _ && _.m(e, null), i = !0, a || (o = Jn(
        e,
        "click",
        /*click_handler*/
        r[13]
      ), a = !0);
    },
    p(d, f) {
      /*icon*/
      d[7] ? l ? (l.p(d, f), f & /*icon*/
      128 && I(l, 1)) : (l = et(d), l.c(), I(l, 1), l.m(e, t)) : l && (Re(), M(l, 1, 1, () => {
        l = null;
      }), Te()), _ && _.p && (!i || f & /*$$scope*/
      2048) && xt(
        _,
        s,
        d,
        /*$$scope*/
        d[11],
        i ? At(
          s,
          /*$$scope*/
          d[11],
          f,
          null
        ) : Ct(
          /*$$scope*/
          d[11]
        ),
        null
      ), (!i || f & /*size, variant, elem_classes*/
      26 && n !== (n = /*size*/
      d[4] + " " + /*variant*/
      d[3] + " " + /*elem_classes*/
      d[1].join(" ") + " svelte-rvoavt")) && T(e, "class", n), (!i || f & /*elem_id*/
      1) && T(
        e,
        "id",
        /*elem_id*/
        d[0]
      ), (!i || f & /*disabled*/
      256) && (e.disabled = /*disabled*/
      d[8]), (!i || f & /*size, variant, elem_classes, visible*/
      30) && Y(e, "hidden", !/*visible*/
      d[2]), f & /*scale*/
      512 && q(
        e,
        "flex-grow",
        /*scale*/
        d[9]
      ), f & /*scale*/
      512 && q(
        e,
        "width",
        /*scale*/
        d[9] === 0 ? "fit-content" : null
      ), f & /*min_width*/
      1024 && q(e, "min-width", typeof /*min_width*/
      d[10] == "number" ? `calc(min(${/*min_width*/
      d[10]}px, 100%))` : null);
    },
    i(d) {
      i || (I(l), I(_, d), i = !0);
    },
    o(d) {
      M(l), M(_, d), i = !1;
    },
    d(d) {
      d && te(e), l && l.d(), _ && _.d(d), a = !1, o();
    }
  };
}
function ni(r) {
  let e, t, n, i, a = (
    /*icon*/
    r[7] && tt(r)
  );
  const o = (
    /*#slots*/
    r[12].default
  ), l = bt(
    o,
    r,
    /*$$scope*/
    r[11],
    null
  );
  return {
    c() {
      e = kt("a"), a && a.c(), t = St(), l && l.c(), this.h();
    },
    l(s) {
      e = vt(s, "A", {
        href: !0,
        rel: !0,
        "aria-disabled": !0,
        class: !0,
        id: !0
      });
      var _ = $t(e);
      a && a.l(_), t = Ft(_), l && l.l(_), _.forEach(te), this.h();
    },
    h() {
      T(
        e,
        "href",
        /*link*/
        r[6]
      ), T(e, "rel", "noopener noreferrer"), T(
        e,
        "aria-disabled",
        /*disabled*/
        r[8]
      ), T(e, "class", n = /*size*/
      r[4] + " " + /*variant*/
      r[3] + " " + /*elem_classes*/
      r[1].join(" ") + " svelte-rvoavt"), T(
        e,
        "id",
        /*elem_id*/
        r[0]
      ), Y(e, "hidden", !/*visible*/
      r[2]), Y(
        e,
        "disabled",
        /*disabled*/
        r[8]
      ), q(
        e,
        "flex-grow",
        /*scale*/
        r[9]
      ), q(
        e,
        "pointer-events",
        /*disabled*/
        r[8] ? "none" : null
      ), q(
        e,
        "width",
        /*scale*/
        r[9] === 0 ? "fit-content" : null
      ), q(e, "min-width", typeof /*min_width*/
      r[10] == "number" ? `calc(min(${/*min_width*/
      r[10]}px, 100%))` : null);
    },
    m(s, _) {
      Ie(s, e, _), a && a.m(e, null), ft(e, t), l && l.m(e, null), i = !0;
    },
    p(s, _) {
      /*icon*/
      s[7] ? a ? (a.p(s, _), _ & /*icon*/
      128 && I(a, 1)) : (a = tt(s), a.c(), I(a, 1), a.m(e, t)) : a && (Re(), M(a, 1, 1, () => {
        a = null;
      }), Te()), l && l.p && (!i || _ & /*$$scope*/
      2048) && xt(
        l,
        o,
        s,
        /*$$scope*/
        s[11],
        i ? At(
          o,
          /*$$scope*/
          s[11],
          _,
          null
        ) : Ct(
          /*$$scope*/
          s[11]
        ),
        null
      ), (!i || _ & /*link*/
      64) && T(
        e,
        "href",
        /*link*/
        s[6]
      ), (!i || _ & /*disabled*/
      256) && T(
        e,
        "aria-disabled",
        /*disabled*/
        s[8]
      ), (!i || _ & /*size, variant, elem_classes*/
      26 && n !== (n = /*size*/
      s[4] + " " + /*variant*/
      s[3] + " " + /*elem_classes*/
      s[1].join(" ") + " svelte-rvoavt")) && T(e, "class", n), (!i || _ & /*elem_id*/
      1) && T(
        e,
        "id",
        /*elem_id*/
        s[0]
      ), (!i || _ & /*size, variant, elem_classes, visible*/
      30) && Y(e, "hidden", !/*visible*/
      s[2]), (!i || _ & /*size, variant, elem_classes, disabled*/
      282) && Y(
        e,
        "disabled",
        /*disabled*/
        s[8]
      ), _ & /*scale*/
      512 && q(
        e,
        "flex-grow",
        /*scale*/
        s[9]
      ), _ & /*disabled*/
      256 && q(
        e,
        "pointer-events",
        /*disabled*/
        s[8] ? "none" : null
      ), _ & /*scale*/
      512 && q(
        e,
        "width",
        /*scale*/
        s[9] === 0 ? "fit-content" : null
      ), _ & /*min_width*/
      1024 && q(e, "min-width", typeof /*min_width*/
      s[10] == "number" ? `calc(min(${/*min_width*/
      s[10]}px, 100%))` : null);
    },
    i(s) {
      i || (I(a), I(l, s), i = !0);
    },
    o(s) {
      M(a), M(l, s), i = !1;
    },
    d(s) {
      s && te(e), a && a.d(), l && l.d(s);
    }
  };
}
function et(r) {
  let e, t;
  return e = new at({
    props: {
      class: `button-icon ${/*value*/
      r[5] ? "right-padded" : ""}`,
      src: (
        /*icon*/
        r[7].url
      ),
      alt: `${/*value*/
      r[5]} icon`
    }
  }), {
    c() {
      yt(e.$$.fragment);
    },
    l(n) {
      Dt(e.$$.fragment, n);
    },
    m(n, i) {
      Et(e, n, i), t = !0;
    },
    p(n, i) {
      const a = {};
      i & /*value*/
      32 && (a.class = `button-icon ${/*value*/
      n[5] ? "right-padded" : ""}`), i & /*icon*/
      128 && (a.src = /*icon*/
      n[7].url), i & /*value*/
      32 && (a.alt = `${/*value*/
      n[5]} icon`), e.$set(a);
    },
    i(n) {
      t || (I(e.$$.fragment, n), t = !0);
    },
    o(n) {
      M(e.$$.fragment, n), t = !1;
    },
    d(n) {
      wt(e, n);
    }
  };
}
function tt(r) {
  let e, t;
  return e = new at({
    props: {
      class: "button-icon",
      src: (
        /*icon*/
        r[7].url
      ),
      alt: `${/*value*/
      r[5]} icon`
    }
  }), {
    c() {
      yt(e.$$.fragment);
    },
    l(n) {
      Dt(e.$$.fragment, n);
    },
    m(n, i) {
      Et(e, n, i), t = !0;
    },
    p(n, i) {
      const a = {};
      i & /*icon*/
      128 && (a.src = /*icon*/
      n[7].url), i & /*value*/
      32 && (a.alt = `${/*value*/
      n[5]} icon`), e.$set(a);
    },
    i(n) {
      t || (I(e.$$.fragment, n), t = !0);
    },
    o(n) {
      M(e.$$.fragment, n), t = !1;
    },
    d(n) {
      wt(e, n);
    }
  };
}
function ii(r) {
  let e, t, n, i;
  const a = [ni, ti], o = [];
  function l(s, _) {
    return (
      /*link*/
      s[6] && /*link*/
      s[6].length > 0 ? 0 : 1
    );
  }
  return e = l(r), t = o[e] = a[e](r), {
    c() {
      t.c(), n = Je();
    },
    l(s) {
      t.l(s), n = Je();
    },
    m(s, _) {
      o[e].m(s, _), Ie(s, n, _), i = !0;
    },
    p(s, [_]) {
      let d = e;
      e = l(s), e === d ? o[e].p(s, _) : (Re(), M(o[d], 1, 1, () => {
        o[d] = null;
      }), Te(), t = o[e], t ? t.p(s, _) : (t = o[e] = a[e](s), t.c()), I(t, 1), t.m(n.parentNode, n));
    },
    i(s) {
      i || (I(t), i = !0);
    },
    o(s) {
      M(t), i = !1;
    },
    d(s) {
      s && te(n), o[e].d(s);
    }
  };
}
function ai(r, e, t) {
  let { $$slots: n = {}, $$scope: i } = e, { elem_id: a = "" } = e, { elem_classes: o = [] } = e, { visible: l = !0 } = e, { variant: s = "secondary" } = e, { size: _ = "lg" } = e, { value: d = null } = e, { link: f = null } = e, { icon: $ = null } = e, { disabled: y = !1 } = e, { scale: S = null } = e, { min_width: b = void 0 } = e;
  function D(m) {
    Qn.call(this, r, m);
  }
  return r.$$set = (m) => {
    "elem_id" in m && t(0, a = m.elem_id), "elem_classes" in m && t(1, o = m.elem_classes), "visible" in m && t(2, l = m.visible), "variant" in m && t(3, s = m.variant), "size" in m && t(4, _ = m.size), "value" in m && t(5, d = m.value), "link" in m && t(6, f = m.link), "icon" in m && t(7, $ = m.icon), "disabled" in m && t(8, y = m.disabled), "scale" in m && t(9, S = m.scale), "min_width" in m && t(10, b = m.min_width), "$$scope" in m && t(11, i = m.$$scope);
  }, [
    a,
    o,
    l,
    s,
    _,
    d,
    f,
    $,
    y,
    S,
    b,
    i,
    n,
    D
  ];
}
class oi extends Kn {
  constructor(e) {
    super(), Vn(this, e, ai, ii, ei, {
      elem_id: 0,
      elem_classes: 1,
      visible: 2,
      variant: 3,
      size: 4,
      value: 5,
      link: 6,
      icon: 7,
      disabled: 8,
      scale: 9,
      min_width: 10
    });
  }
}
const {
  SvelteComponent: ub,
  claim_component: cb,
  claim_text: _b,
  create_component: db,
  destroy_component: pb,
  detach: hb,
  init: mb,
  insert_hydration: gb,
  mount_component: fb,
  safe_not_equal: $b,
  set_data: Db,
  text: vb,
  transition_in: Fb,
  transition_out: yb
} = window.__gradio__svelte__internal, {
  SvelteComponent: ri,
  attr: V,
  claim_component: li,
  claim_element: si,
  claim_text: ui,
  create_component: ci,
  destroy_component: _i,
  detach: ze,
  element: di,
  empty: nt,
  init: pi,
  insert_hydration: Le,
  mount_component: hi,
  safe_not_equal: mi,
  set_data: gi,
  src_url_equal: it,
  text: fi,
  transition_in: $i,
  transition_out: Di
} = window.__gradio__svelte__internal, { createEventDispatcher: vi } = window.__gradio__svelte__internal;
function Fi(r) {
  let e;
  return {
    c() {
      e = fi(
        /*label*/
        r[10]
      );
    },
    l(t) {
      e = ui(
        t,
        /*label*/
        r[10]
      );
    },
    m(t, n) {
      Le(t, e, n);
    },
    p(t, n) {
      n & /*label*/
      1024 && gi(
        e,
        /*label*/
        t[10]
      );
    },
    d(t) {
      t && ze(e);
    }
  };
}
function yi(r) {
  let e, t, n;
  return {
    c() {
      e = di("img"), this.h();
    },
    l(i) {
      e = si(i, "IMG", { class: !0, src: !0, alt: !0 }), this.h();
    },
    h() {
      V(e, "class", "button-icon svelte-qrkusm"), it(e.src, t = /*icon*/
      r[6].url) || V(e, "src", t), V(e, "alt", n = `${/*label*/
      r[10]} icon`);
    },
    m(i, a) {
      Le(i, e, a);
    },
    p(i, a) {
      a & /*icon*/
      64 && !it(e.src, t = /*icon*/
      i[6].url) && V(e, "src", t), a & /*label*/
      1024 && n !== (n = `${/*label*/
      i[10]} icon`) && V(e, "alt", n);
    },
    d(i) {
      i && ze(e);
    }
  };
}
function bi(r) {
  let e;
  function t(a, o) {
    return (
      /*icon*/
      a[6] ? yi : Fi
    );
  }
  let n = t(r), i = n(r);
  return {
    c() {
      i.c(), e = nt();
    },
    l(a) {
      i.l(a), e = nt();
    },
    m(a, o) {
      i.m(a, o), Le(a, e, o);
    },
    p(a, o) {
      n === (n = t(a)) && i ? i.p(a, o) : (i.d(1), i = n(a), i && (i.c(), i.m(e.parentNode, e)));
    },
    d(a) {
      a && ze(e), i.d(a);
    }
  };
}
function wi(r) {
  let e, t;
  return e = new oi({
    props: {
      size: (
        /*size*/
        r[4]
      ),
      variant: (
        /*variant*/
        r[3]
      ),
      elem_id: (
        /*elem_id*/
        r[0]
      ),
      elem_classes: (
        /*elem_classes*/
        r[1]
      ),
      visible: (
        /*visible*/
        r[2]
      ),
      scale: (
        /*scale*/
        r[8]
      ),
      min_width: (
        /*min_width*/
        r[9]
      ),
      disabled: (
        /*disabled*/
        r[7]
      ),
      $$slots: { default: [bi] },
      $$scope: { ctx: r }
    }
  }), e.$on(
    "click",
    /*click_handler*/
    r[12]
  ), {
    c() {
      ci(e.$$.fragment);
    },
    l(n) {
      li(e.$$.fragment, n);
    },
    m(n, i) {
      hi(e, n, i), t = !0;
    },
    p(n, [i]) {
      const a = {};
      i & /*size*/
      16 && (a.size = /*size*/
      n[4]), i & /*variant*/
      8 && (a.variant = /*variant*/
      n[3]), i & /*elem_id*/
      1 && (a.elem_id = /*elem_id*/
      n[0]), i & /*elem_classes*/
      2 && (a.elem_classes = /*elem_classes*/
      n[1]), i & /*visible*/
      4 && (a.visible = /*visible*/
      n[2]), i & /*scale*/
      256 && (a.scale = /*scale*/
      n[8]), i & /*min_width*/
      512 && (a.min_width = /*min_width*/
      n[9]), i & /*disabled*/
      128 && (a.disabled = /*disabled*/
      n[7]), i & /*$$scope, icon, label*/
      17472 && (a.$$scope = { dirty: i, ctx: n }), e.$set(a);
    },
    i(n) {
      t || ($i(e.$$.fragment, n), t = !0);
    },
    o(n) {
      Di(e.$$.fragment, n), t = !1;
    },
    d(n) {
      _i(e, n);
    }
  };
}
function ki(r, e, t) {
  let { elem_id: n = "" } = e, { elem_classes: i = [] } = e, { visible: a = !0 } = e, { variant: o = "secondary" } = e, { size: l = "lg" } = e, { value: s = null } = e, { icon: _ = null } = e, { disabled: d = !1 } = e, { scale: f = null } = e, { min_width: $ = void 0 } = e, { label: y = "" } = e;
  const S = vi();
  function b(m) {
    if (S("click"), !m) {
      console.warn("`DataFrameDownloadButton` was not sent any data");
      return;
    }
    try {
      const u = JSON.parse(m);
      if (!u || // expecting `columns` & `data` keys
      !Array.isArray(u.columns) || !Array.isArray(u.data))
        throw new Error("Invalid data format received from backend");
      const c = u.columns, p = u.data, h = c.join(","), g = p.map((ae) => (
        // convert values to strings
        ae.map(String).map((oe) => `"${oe.replace(/"/g, '""')}"`).join(",")
      )), F = "\uFEFF" + [h, ...g].join(`
`), w = new Blob([F], { type: "text/csv;charset=utf-8;" }), v = URL.createObjectURL(w), k = document.createElement("a"), L = `dataframe_${(/* @__PURE__ */ new Date()).toISOString().slice(0, 19).replace(/[:T]/g, "-")}.csv`;
      k.setAttribute("href", v), k.setAttribute("download", L), k.style.visibility = "hidden", document.body.appendChild(k), k.click(), document.body.removeChild(k), URL.revokeObjectURL(v);
    } catch (u) {
      console.error("Failed to generate/download CSV:", u);
    }
  }
  const D = () => {
    b(s);
  };
  return r.$$set = (m) => {
    "elem_id" in m && t(0, n = m.elem_id), "elem_classes" in m && t(1, i = m.elem_classes), "visible" in m && t(2, a = m.visible), "variant" in m && t(3, o = m.variant), "size" in m && t(4, l = m.size), "value" in m && t(5, s = m.value), "icon" in m && t(6, _ = m.icon), "disabled" in m && t(7, d = m.disabled), "scale" in m && t(8, f = m.scale), "min_width" in m && t(9, $ = m.min_width), "label" in m && t(10, y = m.label);
  }, [
    n,
    i,
    a,
    o,
    l,
    s,
    _,
    d,
    f,
    $,
    y,
    b,
    D
  ];
}
class Ci extends ri {
  constructor(e) {
    super(), pi(this, e, ki, wi, mi, {
      elem_id: 0,
      elem_classes: 1,
      visible: 2,
      variant: 3,
      size: 4,
      value: 5,
      icon: 6,
      disabled: 7,
      scale: 8,
      min_width: 9,
      label: 10
    });
  }
}
const {
  SvelteComponent: Ai,
  claim_component: Ei,
  create_component: Si,
  destroy_component: xi,
  init: Bi,
  mount_component: qi,
  safe_not_equal: Ti,
  transition_in: Ri,
  transition_out: Ii
} = window.__gradio__svelte__internal;
function zi(r) {
  let e, t;
  return e = new Ci({
    props: {
      value: (
        /*value*/
        r[11]
      ),
      variant: (
        /*variant*/
        r[3]
      ),
      elem_id: (
        /*elem_id*/
        r[0]
      ),
      elem_classes: (
        /*elem_classes*/
        r[1]
      ),
      size: (
        /*size*/
        r[5]
      ),
      scale: (
        /*scale*/
        r[6]
      ),
      icon: (
        /*icon*/
        r[7]
      ),
      min_width: (
        /*min_width*/
        r[8]
      ),
      visible: (
        /*visible*/
        r[2]
      ),
      label: (
        /*label*/
        r[9]
      ),
      disabled: !/*value*/
      r[11] || !/*interactive*/
      r[4]
    }
  }), e.$on(
    "click",
    /*click_handler*/
    r[12]
  ), {
    c() {
      Si(e.$$.fragment);
    },
    l(n) {
      Ei(e.$$.fragment, n);
    },
    m(n, i) {
      qi(e, n, i), t = !0;
    },
    p(n, [i]) {
      const a = {};
      i & /*value*/
      2048 && (a.value = /*value*/
      n[11]), i & /*variant*/
      8 && (a.variant = /*variant*/
      n[3]), i & /*elem_id*/
      1 && (a.elem_id = /*elem_id*/
      n[0]), i & /*elem_classes*/
      2 && (a.elem_classes = /*elem_classes*/
      n[1]), i & /*size*/
      32 && (a.size = /*size*/
      n[5]), i & /*scale*/
      64 && (a.scale = /*scale*/
      n[6]), i & /*icon*/
      128 && (a.icon = /*icon*/
      n[7]), i & /*min_width*/
      256 && (a.min_width = /*min_width*/
      n[8]), i & /*visible*/
      4 && (a.visible = /*visible*/
      n[2]), i & /*label*/
      512 && (a.label = /*label*/
      n[9]), i & /*value, interactive*/
      2064 && (a.disabled = !/*value*/
      n[11] || !/*interactive*/
      n[4]), e.$set(a);
    },
    i(n) {
      t || (Ri(e.$$.fragment, n), t = !0);
    },
    o(n) {
      Ii(e.$$.fragment, n), t = !1;
    },
    d(n) {
      xi(e, n);
    }
  };
}
function Li(r, e, t) {
  let { elem_id: n = "" } = e, { elem_classes: i = [] } = e, { visible: a = !0 } = e, { variant: o = "secondary" } = e, { interactive: l } = e, { size: s = "lg" } = e, { scale: _ = null } = e, { icon: d = null } = e, { min_width: f = void 0 } = e, { label: $ } = e, { gradio: y } = e, { value: S = null } = e;
  const b = () => y.dispatch("click");
  return r.$$set = (D) => {
    "elem_id" in D && t(0, n = D.elem_id), "elem_classes" in D && t(1, i = D.elem_classes), "visible" in D && t(2, a = D.visible), "variant" in D && t(3, o = D.variant), "interactive" in D && t(4, l = D.interactive), "size" in D && t(5, s = D.size), "scale" in D && t(6, _ = D.scale), "icon" in D && t(7, d = D.icon), "min_width" in D && t(8, f = D.min_width), "label" in D && t(9, $ = D.label), "gradio" in D && t(10, y = D.gradio), "value" in D && t(11, S = D.value);
  }, [
    n,
    i,
    a,
    o,
    l,
    s,
    _,
    d,
    f,
    $,
    y,
    S,
    b
  ];
}
class bb extends Ai {
  constructor(e) {
    super(), Bi(this, e, Li, zi, Ti, {
      elem_id: 0,
      elem_classes: 1,
      visible: 2,
      variant: 3,
      interactive: 4,
      size: 5,
      scale: 6,
      icon: 7,
      min_width: 8,
      label: 9,
      gradio: 10,
      value: 11
    });
  }
}
export {
  Ci as BaseButton,
  bb as default
};
