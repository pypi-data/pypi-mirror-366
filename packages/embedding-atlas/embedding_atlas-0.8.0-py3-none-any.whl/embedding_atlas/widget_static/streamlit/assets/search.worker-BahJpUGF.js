var w;
function N(t, e, i) {
  const s = typeof i, n = typeof t;
  if (s !== "undefined") {
    if (n !== "undefined") {
      if (i) {
        if (n === "function" && s === n) return function(o) {
          return t(i(o));
        };
        if (e = t.constructor, e === i.constructor) {
          if (e === Array) return i.concat(t);
          if (e === Map) {
            var r = new Map(i);
            for (var h of t) r.set(h[0], h[1]);
            return r;
          }
          if (e === Set) {
            h = new Set(i);
            for (r of t.values()) h.add(r);
            return h;
          }
        }
      }
      return t;
    }
    return i;
  }
  return n === "undefined" ? e : t;
}
function I() {
  return /* @__PURE__ */ Object.create(null);
}
function D(t) {
  return typeof t == "string";
}
function rt(t) {
  return typeof t == "object";
}
function fe(t) {
  const e = [];
  for (const i of t.keys()) e.push(i);
  return e;
}
function ht(t, e) {
  if (D(e)) t = t[e];
  else for (let i = 0; t && i < e.length; i++) t = t[e[i]];
  return t;
}
function ue(t) {
  let e = 0;
  for (let i = 0, s; i < t.length; i++) (s = t[i]) && e < s.length && (e = s.length);
  return e;
}
const ce = /[^\p{L}\p{N}]+/u, ge = /(\d{3})/g, de = /(\D)(\d{3})/g, ae = /(\d{3})(\D)/g, bt = /[\u0300-\u036f]/g;
function lt(t = {}) {
  if (!this || this.constructor !== lt) return new lt(...arguments);
  if (arguments.length) for (t = 0; t < arguments.length; t++) this.assign(arguments[t]);
  else this.assign(t);
}
w = lt.prototype;
w.assign = function(t) {
  this.normalize = N(t.normalize, !0, this.normalize);
  let e = t.include, i = e || t.exclude || t.split, s;
  if (i || i === "") {
    if (typeof i == "object" && i.constructor !== RegExp) {
      let n = "";
      s = !e, e || (n += "\\p{Z}"), i.letter && (n += "\\p{L}"), i.number && (n += "\\p{N}", s = !!e), i.symbol && (n += "\\p{S}"), i.punctuation && (n += "\\p{P}"), i.control && (n += "\\p{C}"), (i = i.char) && (n += typeof i == "object" ? i.join("") : i);
      try {
        this.split = new RegExp("[" + (e ? "^" : "") + n + "]+", "u");
      } catch {
        this.split = /\s+/;
      }
    } else this.split = i, s = i === !1 || 2 > "a1a".split(i).length;
    this.numeric = N(t.numeric, s);
  } else {
    try {
      this.split = N(this.split, ce);
    } catch {
      this.split = /\s+/;
    }
    this.numeric = N(t.numeric, N(this.numeric, !0));
  }
  if (this.prepare = N(t.prepare, null, this.prepare), this.finalize = N(t.finalize, null, this.finalize), i = t.filter, this.filter = typeof i == "function" ? i : N(i && new Set(i), null, this.filter), this.dedupe = N(t.dedupe, !0, this.dedupe), this.matcher = N((i = t.matcher) && new Map(i), null, this.matcher), this.mapper = N((i = t.mapper) && new Map(i), null, this.mapper), this.stemmer = N(
    (i = t.stemmer) && new Map(i),
    null,
    this.stemmer
  ), this.replacer = N(t.replacer, null, this.replacer), this.minlength = N(t.minlength, 1, this.minlength), this.maxlength = N(t.maxlength, 1024, this.maxlength), this.rtl = N(t.rtl, !1, this.rtl), (this.cache = i = N(t.cache, !0, this.cache)) && (this.H = null, this.S = typeof i == "number" ? i : 2e5, this.B = /* @__PURE__ */ new Map(), this.G = /* @__PURE__ */ new Map(), this.L = this.K = 128), this.h = "", this.M = null, this.A = "", this.N = null, this.matcher) for (const n of this.matcher.keys()) this.h += (this.h ? "|" : "") + n;
  if (this.stemmer) for (const n of this.stemmer.keys()) this.A += (this.A ? "|" : "") + n;
  return this;
};
w.addStemmer = function(t, e) {
  return this.stemmer || (this.stemmer = /* @__PURE__ */ new Map()), this.stemmer.set(t, e), this.A += (this.A ? "|" : "") + t, this.N = null, this.cache && Y(this), this;
};
w.addFilter = function(t) {
  return typeof t == "function" ? this.filter = t : (this.filter || (this.filter = /* @__PURE__ */ new Set()), this.filter.add(t)), this.cache && Y(this), this;
};
w.addMapper = function(t, e) {
  return typeof t == "object" ? this.addReplacer(t, e) : 1 < t.length ? this.addMatcher(t, e) : (this.mapper || (this.mapper = /* @__PURE__ */ new Map()), this.mapper.set(t, e), this.cache && Y(this), this);
};
w.addMatcher = function(t, e) {
  return typeof t == "object" ? this.addReplacer(t, e) : 2 > t.length && (this.dedupe || this.mapper) ? this.addMapper(t, e) : (this.matcher || (this.matcher = /* @__PURE__ */ new Map()), this.matcher.set(t, e), this.h += (this.h ? "|" : "") + t, this.M = null, this.cache && Y(this), this);
};
w.addReplacer = function(t, e) {
  return typeof t == "string" ? this.addMatcher(t, e) : (this.replacer || (this.replacer = []), this.replacer.push(t, e), this.cache && Y(this), this);
};
w.encode = function(t, e) {
  if (this.cache && t.length <= this.K) if (this.H) {
    if (this.B.has(t)) return this.B.get(t);
  } else this.H = setTimeout(Y, 50, this);
  this.normalize && (typeof this.normalize == "function" ? t = this.normalize(t) : t = bt ? t.normalize("NFKD").replace(bt, "").toLowerCase() : t.toLowerCase()), this.prepare && (t = this.prepare(t)), this.numeric && 3 < t.length && (t = t.replace(de, "$1 $2").replace(ae, "$1 $2").replace(ge, "$1 "));
  const i = !(this.dedupe || this.mapper || this.filter || this.matcher || this.stemmer || this.replacer);
  let s = [], n = I(), r, h, o = this.split || this.split === "" ? t.split(this.split) : [t];
  for (let f = 0, u, c; f < o.length; f++) if ((u = c = o[f]) && !(u.length < this.minlength || u.length > this.maxlength)) {
    if (e) {
      if (n[u]) continue;
      n[u] = 1;
    } else {
      if (r === u) continue;
      r = u;
    }
    if (i) s.push(u);
    else if (!this.filter || (typeof this.filter == "function" ? this.filter(u) : !this.filter.has(u))) {
      if (this.cache && u.length <= this.L) if (this.H) {
        var l = this.G.get(u);
        if (l || l === "") {
          l && s.push(l);
          continue;
        }
      } else this.H = setTimeout(Y, 50, this);
      if (this.stemmer) {
        this.N || (this.N = new RegExp("(?!^)(" + this.A + ")$"));
        let a;
        for (; a !== u && 2 < u.length; ) a = u, u = u.replace(this.N, (d) => this.stemmer.get(d));
      }
      if (u && (this.mapper || this.dedupe && 1 < u.length)) {
        l = "";
        for (let a = 0, d = "", p, m; a < u.length; a++) p = u.charAt(a), p === d && this.dedupe || ((m = this.mapper && this.mapper.get(p)) || m === "" ? m === d && this.dedupe || !(d = m) || (l += m) : l += d = p);
        u = l;
      }
      if (this.matcher && 1 < u.length && (this.M || (this.M = new RegExp("(" + this.h + ")", "g")), u = u.replace(this.M, (a) => this.matcher.get(a))), u && this.replacer) for (l = 0; u && l < this.replacer.length; l += 2) u = u.replace(
        this.replacer[l],
        this.replacer[l + 1]
      );
      if (this.cache && c.length <= this.L && (this.G.set(c, u), this.G.size > this.S && (this.G.clear(), this.L = this.L / 1.1 | 0)), u) {
        if (u !== c) if (e) {
          if (n[u]) continue;
          n[u] = 1;
        } else {
          if (h === u) continue;
          h = u;
        }
        s.push(u);
      }
    }
  }
  return this.finalize && (s = this.finalize(s) || s), this.cache && t.length <= this.K && (this.B.set(t, s), this.B.size > this.S && (this.B.clear(), this.K = this.K / 1.1 | 0)), s;
};
function Y(t) {
  t.H = null, t.B.clear(), t.G.clear();
}
let V, it;
async function pe(t) {
  t = t.data;
  var e = t.task;
  const i = t.id;
  let s = t.args;
  switch (e) {
    case "init":
      it = t.options || {}, (e = t.factory) ? (Function("return " + e)()(self), V = new self.FlexSearch.Index(it), delete self.FlexSearch) : V = new $(it), postMessage({ id: i });
      break;
    default:
      let n;
      e === "export" && (s[1] ? (s[0] = it.export, s[2] = 0, s[3] = 1) : s = null), e === "import" ? s[0] && (t = await it.import.call(V, s[0]), V.import(s[0], t)) : (n = s && V[e].apply(V, s)) && n.then && (n = await n), postMessage(e === "search" ? { id: i, msg: n } : { id: i });
  }
}
function It(t) {
  nt.call(t, "add"), nt.call(t, "append"), nt.call(t, "search"), nt.call(t, "update"), nt.call(t, "remove");
}
let St, Dt, at;
function me() {
  St = at = 0;
}
function nt(t) {
  this[t + "Async"] = function() {
    const e = arguments;
    var i = e[e.length - 1];
    let s;
    if (typeof i == "function" && (s = i, delete e[e.length - 1]), St ? at || (at = Date.now() - Dt >= this.priority * this.priority * 3) : (St = setTimeout(me, 0), Dt = Date.now()), at) {
      const r = this;
      return new Promise((h) => {
        setTimeout(function() {
          h(r[t + "Async"].apply(r, e));
        }, 0);
      });
    }
    const n = this[t].apply(this, e);
    return i = n.then ? n : new Promise((r) => r(n)), s && i.then(s), i;
  };
}
let Q = 0;
function ot(t = {}) {
  function e(h) {
    function o(l) {
      l = l.data || l;
      const f = l.id, u = f && n.h[f];
      u && (u(l.msg), delete n.h[f]);
    }
    if (this.worker = h, this.h = I(), this.worker)
      return s ? this.worker.on("message", o) : this.worker.onmessage = o, t.config ? new Promise(function(l) {
        n.h[++Q] = function() {
          l(n), 1e9 < Q && (Q = 0);
        }, n.worker.postMessage({ id: Q, task: "init", factory: i, options: t });
      }) : (this.worker.postMessage({ task: "init", factory: i, options: t }), this.priority = t.priority || 4, this);
  }
  if (!this || this.constructor !== ot) return new ot(t);
  let i = typeof self < "u" ? self._factory : typeof window < "u" ? window._factory : null;
  i && (i = i.toString());
  const s = typeof window > "u", n = this, r = we(i, s, t.worker);
  return r.then ? r.then(function(h) {
    return e.call(n, h);
  }) : e.call(this, r);
}
J("add");
J("append");
J("search");
J("update");
J("remove");
J("clear");
J("export");
J("import");
It(ot.prototype);
function J(t) {
  ot.prototype[t] = function() {
    const e = this, i = [].slice.call(arguments);
    var s = i[i.length - 1];
    let n;
    return typeof s == "function" && (n = s, i.pop()), s = new Promise(function(r) {
      t === "export" && typeof i[0] == "function" && (i[0] = null), e.h[++Q] = r, e.worker.postMessage({ task: t, id: Q, args: i });
    }), n ? (s.then(n), this) : s;
  };
}
function we(t, e, i) {
  return e ? typeof module < "u" ? new (require("worker_threads")).Worker(__dirname + "/worker/node.js") : Promise.resolve().then(function() {
    return ze;
  }).then(function(s) {
    return new s.Worker(import.meta.dirname + "/node/node.mjs");
  }) : t ? new window.Worker(URL.createObjectURL(new Blob(["onmessage=" + pe.toString()], { type: "text/javascript" }))) : new window.Worker(typeof i == "string" ? i : import.meta.url.replace("/worker.js", "/worker/worker.js").replace(
    "flexsearch.bundle.module.min.js",
    "module/worker/worker.js"
  ), { type: "module" });
}
function Lt(t, e = 0) {
  let i = [], s = [];
  e && (e = 25e4 / e * 5e3 | 0);
  for (const n of t.entries()) s.push(n), s.length === e && (i.push(s), s = []);
  return s.length && i.push(s), i;
}
function Bt(t, e) {
  e || (e = /* @__PURE__ */ new Map());
  for (let i = 0, s; i < t.length; i++) s = t[i], e.set(s[0], s[1]);
  return e;
}
function Xt(t, e = 0) {
  let i = [], s = [];
  e && (e = 25e4 / e * 1e3 | 0);
  for (const n of t.entries()) s.push([n[0], Lt(n[1])[0]]), s.length === e && (i.push(s), s = []);
  return s.length && i.push(s), i;
}
function Yt(t, e) {
  e || (e = /* @__PURE__ */ new Map());
  for (let i = 0, s, n; i < t.length; i++) s = t[i], n = e.get(s[0]), e.set(s[0], Bt(s[1], n));
  return e;
}
function Ht(t) {
  let e = [], i = [];
  for (const s of t.keys()) i.push(s), i.length === 25e4 && (e.push(i), i = []);
  return i.length && e.push(i), e;
}
function qt(t, e) {
  e || (e = /* @__PURE__ */ new Set());
  for (let i = 0; i < t.length; i++) e.add(t[i]);
  return e;
}
function pt(t, e, i, s, n, r, h = 0) {
  const o = s && s.constructor === Array;
  var l = o ? s.shift() : s;
  if (!l) return this.export(t, e, n, r + 1);
  if ((l = t((e ? e + "." : "") + (h + 1) + "." + i, JSON.stringify(l))) && l.then) {
    const f = this;
    return l.then(function() {
      return pt.call(f, t, e, i, o ? s : null, n, r, h + 1);
    });
  }
  return pt.call(this, t, e, i, o ? s : null, n, r, h + 1);
}
function Ft(t, e) {
  let i = "";
  for (const s of t.entries()) {
    t = s[0];
    const n = s[1];
    let r = "";
    for (let h = 0, o; h < n.length; h++) {
      o = n[h] || [""];
      let l = "";
      for (let f = 0; f < o.length; f++) l += (l ? "," : "") + (e === "string" ? '"' + o[f] + '"' : o[f]);
      l = "[" + l + "]", r += (r ? "," : "") + l;
    }
    r = '["' + t + '",[' + r + "]]", i += (i ? "," : "") + r;
  }
  return i;
}
function $t(t, e, i, s) {
  let n = [];
  for (let r = 0, h; r < t.index.length; r++) if (h = t.index[r], e >= h.length) e -= h.length;
  else {
    e = h[s ? "splice" : "slice"](e, i);
    const o = e.length;
    if (o && (n = n.length ? n.concat(e) : e, i -= o, s && (t.length -= o), !i)) break;
    e = 0;
  }
  return n;
}
function H(t) {
  if (!this || this.constructor !== H) return new H(t);
  this.index = t ? [t] : [], this.length = t ? t.length : 0;
  const e = this;
  return new Proxy([], { get(i, s) {
    if (s === "length") return e.length;
    if (s === "push") return function(n) {
      e.index[e.index.length - 1].push(n), e.length++;
    };
    if (s === "pop") return function() {
      if (e.length) return e.length--, e.index[e.index.length - 1].pop();
    };
    if (s === "indexOf") return function(n) {
      let r = 0;
      for (let h = 0, o, l; h < e.index.length; h++) {
        if (o = e.index[h], l = o.indexOf(n), 0 <= l) return r + l;
        r += o.length;
      }
      return -1;
    };
    if (s === "includes") return function(n) {
      for (let r = 0; r < e.index.length; r++) if (e.index[r].includes(n)) return !0;
      return !1;
    };
    if (s === "slice") return function(n, r) {
      return $t(e, n || 0, r || e.length, !1);
    };
    if (s === "splice") return function(n, r) {
      return $t(e, n || 0, r || e.length, !0);
    };
    if (s === "constructor") return Array;
    if (typeof s != "symbol") return (i = e.index[s / 2 ** 31 | 0]) && i[s];
  }, set(i, s, n) {
    return i = s / 2 ** 31 | 0, (e.index[i] || (e.index[i] = []))[s] = n, e.length++, !0;
  } });
}
H.prototype.clear = function() {
  this.index.length = 0;
};
H.prototype.destroy = function() {
  this.proxy = this.index = null;
};
H.prototype.push = function() {
};
function T(t = 8) {
  if (!this || this.constructor !== T) return new T(t);
  this.index = I(), this.h = [], this.size = 0, 32 < t ? (this.B = Qt, this.A = BigInt(t)) : (this.B = Vt, this.A = t);
}
T.prototype.get = function(t) {
  const e = this.index[this.B(t)];
  return e && e.get(t);
};
T.prototype.set = function(t, e) {
  var i = this.B(t);
  let s = this.index[i];
  s ? (i = s.size, s.set(t, e), (i -= s.size) && this.size++) : (this.index[i] = s = /* @__PURE__ */ new Map([[t, e]]), this.h.push(s), this.size++);
};
function F(t = 8) {
  if (!this || this.constructor !== F) return new F(t);
  this.index = I(), this.h = [], this.size = 0, 32 < t ? (this.B = Qt, this.A = BigInt(t)) : (this.B = Vt, this.A = t);
}
F.prototype.add = function(t) {
  var e = this.B(t);
  let i = this.index[e];
  i ? (e = i.size, i.add(t), (e -= i.size) && this.size++) : (this.index[e] = i = /* @__PURE__ */ new Set([t]), this.h.push(i), this.size++);
};
w = T.prototype;
w.has = F.prototype.has = function(t) {
  const e = this.index[this.B(t)];
  return e && e.has(t);
};
w.delete = F.prototype.delete = function(t) {
  const e = this.index[this.B(t)];
  e && e.delete(t) && this.size--;
};
w.clear = F.prototype.clear = function() {
  this.index = I(), this.h = [], this.size = 0;
};
w.values = F.prototype.values = function* () {
  for (let t = 0; t < this.h.length; t++) for (let e of this.h[t].values()) yield e;
};
w.keys = F.prototype.keys = function* () {
  for (let t = 0; t < this.h.length; t++) for (let e of this.h[t].keys()) yield e;
};
w.entries = F.prototype.entries = function* () {
  for (let t = 0; t < this.h.length; t++) for (let e of this.h[t].entries()) yield e;
};
function Vt(t) {
  let e = 2 ** this.A - 1;
  if (typeof t == "number") return t & e;
  let i = 0, s = this.A + 1;
  for (let n = 0; n < t.length; n++) i = (i * s ^ t.charCodeAt(n)) & e;
  return this.A === 32 ? i + 2 ** 31 : i;
}
function Qt(t) {
  let e = BigInt(2) ** this.A - BigInt(1);
  var i = typeof t;
  if (i === "bigint") return t & e;
  if (i === "number") return BigInt(t) & e;
  i = BigInt(0);
  let s = this.A + BigInt(1);
  for (let n = 0; n < t.length; n++) i = (i * s ^ BigInt(t.charCodeAt(n))) & e;
  return i;
}
K.prototype.add = function(t, e, i) {
  if (rt(t) && (e = t, t = ht(e, this.key)), e && (t || t === 0)) {
    if (!i && this.reg.has(t)) return this.update(t, e);
    for (let o = 0, l; o < this.field.length; o++) {
      l = this.F[o];
      var s = this.index.get(this.field[o]);
      if (typeof l == "function") {
        var n = l(e);
        n && s.add(t, n, !1, !0);
      } else n = l.I, (!n || n(e)) && (l.constructor === String ? l = ["" + l] : D(l) && (l = [l]), Ot(e, l, this.J, 0, s, t, l[0], i));
    }
    if (this.tag) for (s = 0; s < this.D.length; s++) {
      var r = this.D[s];
      n = this.tag.get(this.R[s]);
      let o = I();
      if (typeof r == "function") {
        if (r = r(e), !r) continue;
      } else {
        var h = r.I;
        if (h && !h(e)) continue;
        r.constructor === String && (r = "" + r), r = ht(e, r);
      }
      if (n && r) {
        D(r) && (r = [r]);
        for (let l = 0, f, u; l < r.length; l++) if (f = r[l], !o[f] && (o[f] = 1, (h = n.get(f)) ? u = h : n.set(f, u = []), !i || !u.includes(t))) {
          if (u.length === 2 ** 31 - 1) {
            if (h = new H(u), this.fastupdate) for (let c of this.reg.values()) c.includes(u) && (c[c.indexOf(u)] = h);
            n.set(f, u = h);
          }
          u.push(t), this.fastupdate && ((h = this.reg.get(t)) ? h.push(u) : this.reg.set(t, [u]));
        }
      }
    }
    if (this.store && (!i || !this.store.has(t))) {
      let o;
      if (this.C) {
        o = I();
        for (let l = 0, f; l < this.C.length; l++) {
          if (f = this.C[l], (i = f.I) && !i(e)) continue;
          let u;
          if (typeof f == "function") {
            if (u = f(e), !u) continue;
            f = [f.V];
          } else if (D(f) || f.constructor === String) {
            o[f] = e[f];
            continue;
          }
          zt(e, o, f, 0, f[0], u);
        }
      }
      this.store.set(t, o || e);
    }
    this.worker && (this.fastupdate || this.reg.add(t));
  }
  return this;
};
function zt(t, e, i, s, n, r) {
  if (t = t[n], s === i.length - 1) e[n] = r || t;
  else if (t) if (t.constructor === Array) for (e = e[n] = Array(t.length), n = 0; n < t.length; n++) zt(t, e, i, s, n);
  else e = e[n] || (e[n] = I()), n = i[++s], zt(t, e, i, s, n);
}
function Ot(t, e, i, s, n, r, h, o) {
  if (t = t[h]) if (s === e.length - 1) {
    if (t.constructor === Array) {
      if (i[s]) {
        for (e = 0; e < t.length; e++) n.add(r, t[e], !0, !0);
        return;
      }
      t = t.join(" ");
    }
    n.add(r, t, o, !0);
  } else if (t.constructor === Array) for (h = 0; h < t.length; h++) Ot(t, e, i, s, n, r, h, o);
  else h = e[++s], Ot(t, e, i, s, n, r, h, o);
  else n.db && n.remove(r);
}
function Kt(t, e, i, s, n, r, h) {
  const o = t.length;
  let l = [], f, u;
  f = I();
  for (let c = 0, a, d, p, m; c < e; c++) for (let g = 0; g < o; g++) if (p = t[g], c < p.length && (a = p[c])) for (let x = 0; x < a.length; x++) {
    if (d = a[x], (u = f[d]) ? f[d]++ : (u = 0, f[d] = 1), m = l[u] || (l[u] = []), !h) {
      let y = c + (g || !n ? 0 : r || 0);
      m = m[y] || (m[y] = []);
    }
    if (m.push(d), h && i && u === o - 1 && m.length - s === i) return s ? m.slice(s) : m;
  }
  if (t = l.length) if (n) l = 1 < l.length ? te(l, i, s, h, r) : (l = l[0]).length > i || s ? l.slice(s, i + s) : l;
  else {
    if (t < o) return [];
    if (l = l[t - 1], i || s) if (h)
      (l.length > i || s) && (l = l.slice(s, i + s));
    else {
      n = [];
      for (let c = 0, a; c < l.length; c++) if (a = l[c], a.length > s) s -= a.length;
      else if ((a.length > i || s) && (a = a.slice(s, i + s), i -= a.length, s && (s -= a.length)), n.push(a), !i) break;
      l = 1 < n.length ? [].concat.apply([], n) : n[0];
    }
  }
  return l;
}
function te(t, e, i, s, n) {
  const r = [], h = I();
  let o;
  var l = t.length;
  let f;
  if (s) {
    for (n = l - 1; 0 <= n; n--)
      if (f = (s = t[n]) && s.length) {
        for (l = 0; l < f; l++) if (o = s[l], !h[o]) {
          if (h[o] = 1, i) i--;
          else if (r.push(o), r.length === e) return r;
        }
      }
  } else for (let u = l - 1, c, a = 0; 0 <= u; u--) {
    c = t[u];
    for (let d = 0; d < c.length; d++) if (f = (s = c[d]) && s.length) {
      for (let p = 0; p < f; p++) if (o = s[p], !h[o]) if (h[o] = 1, i) i--;
      else {
        let m = (d + (u < l - 1 && n || 0)) / (u + 1) | 0;
        if ((r[m] || (r[m] = [])).push(o), ++a === e) return r;
      }
    }
  }
  return r;
}
function ye(t, e, i) {
  const s = I(), n = [];
  for (let r = 0, h; r < e.length; r++) {
    h = e[r];
    for (let o = 0; o < h.length; o++) s[h[o]] = 1;
  }
  if (i) for (let r = 0, h; r < t.length; r++) h = t[r], s[h] && (n.push(h), s[h] = 0);
  else for (let r = 0, h, o; r < t.result.length; r++) for (h = t.result[r], e = 0; e < h.length; e++) o = h[e], s[o] && ((n[r] || (n[r] = [])).push(o), s[o] = 0);
  return n;
}
function Nt(t, e, i, s) {
  if (!t.length) return t;
  if (t.length === 1) return t = t[0], t = i || t.length > e ? e ? t.slice(i, i + e) : t.slice(i) : t, s ? G.call(this, t) : t;
  let n = [];
  for (let r = 0, h, o; r < t.length; r++) if ((h = t[r]) && (o = h.length)) {
    if (i) {
      if (i >= o) {
        i -= o;
        continue;
      }
      i < o && (h = e ? h.slice(i, i + e) : h.slice(i), o = h.length, i = 0);
    }
    if (o > e && (h = h.slice(0, e), o = e), !n.length && o >= e) return s ? G.call(this, h) : h;
    if (n.push(h), e -= o, !e) break;
  }
  return n = 1 < n.length ? [].concat.apply([], n) : n[0], s ? G.call(this, n) : n;
}
function yt(t, e, i) {
  var s = i[0];
  if (s.then) return Promise.all(i).then(function(u) {
    return t[e].apply(t, u);
  });
  if (s[0] && s[0].index) return t[e].apply(t, s);
  s = [];
  let n = [], r = 0, h = 0, o, l, f;
  for (let u = 0, c; u < i.length; u++) if (c = i[u]) {
    let a;
    if (c.constructor === O) a = c.result;
    else if (c.constructor === Array) a = c;
    else if (r = c.limit || 0, h = c.offset || 0, f = c.suggest, l = c.resolve, o = c.enrich && l, c.index) c.resolve = !1, a = c.index.search(c).result, c.resolve = l;
    else if (c.and) a = t.and(c.and);
    else if (c.or) a = t.or(c.or);
    else if (c.xor) a = t.xor(c.xor);
    else if (c.not) a = t.not(c.not);
    else continue;
    if (a.then) n.push(a);
    else if (a.length) s[u] = a;
    else if (!f && (e === "and" || e === "xor")) {
      s = [];
      break;
    }
  }
  return { O: s, P: n, limit: r, offset: h, enrich: o, resolve: l, suggest: f };
}
O.prototype.or = function() {
  const { O: t, P: e, limit: i, offset: s, enrich: n, resolve: r } = yt(this, "or", arguments);
  return ee.call(this, t, e, i, s, n, r);
};
function ee(t, e, i, s, n, r) {
  if (e.length) {
    const h = this;
    return Promise.all(e).then(function(o) {
      t = [];
      for (let l = 0, f; l < o.length; l++) (f = o[l]).length && (t[l] = f);
      return ee.call(h, t, [], i, s, n, r);
    });
  }
  return t.length && (this.result.length && t.push(this.result), 2 > t.length ? this.result = t[0] : (this.result = te(t, i, s, !1, this.h), s = 0)), r ? this.resolve(i, s, n) : this;
}
O.prototype.and = function() {
  let t = this.result.length, e, i, s, n;
  if (!t) {
    const r = arguments[0];
    r && (t = !!r.suggest, n = r.resolve, e = r.limit, i = r.offset, s = r.enrich && n);
  }
  if (t) {
    const { O: r, P: h, limit: o, offset: l, enrich: f, resolve: u, suggest: c } = yt(this, "and", arguments);
    return ie.call(this, r, h, o, l, f, u, c);
  }
  return n ? this.resolve(e, i, s) : this;
};
function ie(t, e, i, s, n, r, h) {
  if (e.length) {
    const o = this;
    return Promise.all(e).then(function(l) {
      t = [];
      for (let f = 0, u; f < l.length; f++) (u = l[f]).length && (t[f] = u);
      return ie.call(o, t, [], i, s, n, r, h);
    });
  }
  if (t.length) if (this.result.length && t.unshift(this.result), 2 > t.length) this.result = t[0];
  else {
    if (e = ue(t)) return this.result = Kt(t, e, i, s, h, this.h, r), r ? n ? G.call(this.index, this.result) : this.result : this;
    this.result = [];
  }
  else h || (this.result = t);
  return r ? this.resolve(i, s, n) : this;
}
O.prototype.xor = function() {
  const { O: t, P: e, limit: i, offset: s, enrich: n, resolve: r, suggest: h } = yt(this, "xor", arguments);
  return ne.call(this, t, e, i, s, n, r, h);
};
function ne(t, e, i, s, n, r, h) {
  if (e.length) {
    const o = this;
    return Promise.all(e).then(function(l) {
      t = [];
      for (let f = 0, u; f < l.length; f++) (u = l[f]).length && (t[f] = u);
      return ne.call(o, t, [], i, s, n, r, h);
    });
  }
  if (t.length) if (this.result.length && t.unshift(this.result), 2 > t.length) this.result = t[0];
  else return this.result = xe.call(this, t, i, s, r, this.h), r ? n ? G.call(this.index, this.result) : this.result : this;
  else h || (this.result = t);
  return r ? this.resolve(i, s, n) : this;
}
function xe(t, e, i, s, n) {
  const r = [], h = I();
  let o = 0;
  for (let l = 0, f; l < t.length; l++) if (f = t[l]) {
    o < f.length && (o = f.length);
    for (let u = 0, c; u < f.length; u++) if (c = f[u]) for (let a = 0, d; a < c.length; a++) d = c[a], h[d] = h[d] ? 2 : 1;
  }
  for (let l = 0, f, u = 0; l < o; l++) for (let c = 0, a; c < t.length; c++) if ((a = t[c]) && (f = a[l])) {
    for (let d = 0, p; d < f.length; d++) if (p = f[d], h[p] === 1) if (i) i--;
    else if (s) {
      if (r.push(p), r.length === e) return r;
    } else {
      const m = l + (c ? n : 0);
      if (r[m] || (r[m] = []), r[m].push(p), ++u === e) return r;
    }
  }
  return r;
}
O.prototype.not = function() {
  const { O: t, P: e, limit: i, offset: s, enrich: n, resolve: r, suggest: h } = yt(this, "not", arguments);
  return se.call(this, t, e, i, s, n, r, h);
};
function se(t, e, i, s, n, r, h) {
  if (e.length) {
    const o = this;
    return Promise.all(e).then(function(l) {
      t = [];
      for (let f = 0, u; f < l.length; f++) (u = l[f]).length && (t[f] = u);
      return se.call(o, t, [], i, s, n, r, h);
    });
  }
  if (t.length && this.result.length) this.result = ve.call(this, t, i, s, r);
  else if (r) return this.resolve(i, s, n);
  return r ? n ? G.call(this.index, this.result) : this.result : this;
}
function ve(t, e, i, s) {
  const n = [];
  t = new Set(t.flat().flat());
  for (let r = 0, h, o = 0; r < this.result.length; r++) if (h = this.result[r]) {
    for (let l = 0, f; l < h.length; l++) if (f = h[l], !t.has(f)) {
      if (i) i--;
      else if (s) {
        if (n.push(f), n.length === e) return n;
      } else if (n[r] || (n[r] = []), n[r].push(f), ++o === e) return n;
    }
  }
  return n;
}
function O(t) {
  if (!this || this.constructor !== O) return new O(t);
  if (t && t.index) return t.resolve = !1, this.index = t.index, this.h = t.boost || 0, this.result = t.index.search(t).result, this;
  this.index = null, this.result = t || [], this.h = 0;
}
O.prototype.limit = function(t) {
  if (this.result.length) {
    const e = [];
    for (let i = 0, s; i < this.result.length; i++) if (s = this.result[i]) if (s.length <= t) {
      if (e[i] = s, t -= s.length, !t) break;
    } else {
      e[i] = s.slice(0, t);
      break;
    }
    this.result = e;
  }
  return this;
};
O.prototype.offset = function(t) {
  if (this.result.length) {
    const e = [];
    for (let i = 0, s; i < this.result.length; i++) (s = this.result[i]) && (s.length <= t ? t -= s.length : (e[i] = s.slice(t), t = 0));
    this.result = e;
  }
  return this;
};
O.prototype.boost = function(t) {
  return this.h += t, this;
};
O.prototype.resolve = function(t, e, i) {
  const s = this.result, n = this.index;
  return this.result = this.index = null, s.length ? (typeof t == "object" && (i = t.enrich, e = t.offset, t = t.limit), Nt.call(n, s, t || 100, e, i)) : s;
};
function kt(t, e, i, s, n) {
  let r, h, o;
  typeof n == "string" ? (r = n, n = "") : r = n.template, h = r.indexOf("$1"), o = r.substring(h + 2), h = r.substring(0, h);
  let l = n && n.boundary, f = !n || n.clip !== !1, u = n && n.merge && o && h && new RegExp(o + " " + h, "g");
  n = n && n.ellipsis;
  var c = 0;
  if (typeof n == "object") {
    var a = n.template;
    c = a.length - 2, n = n.pattern;
  }
  typeof n != "string" && (n = n === !1 ? "" : "..."), c && (n = a.replace("$1", n)), a = n.length - c;
  let d, p;
  typeof l == "object" && (d = l.before, d === 0 && (d = -1), p = l.after, p === 0 && (p = -1), l = l.total || 9e5), c = /* @__PURE__ */ new Map();
  for (let xt = 0, Z, Rt, tt; xt < e.length; xt++) {
    let et;
    if (s) et = e, tt = s;
    else {
      var m = e[xt];
      if (tt = m.field, !tt) continue;
      et = m.result;
    }
    Rt = i.get(tt), Z = Rt.encoder, m = c.get(Z), typeof m != "string" && (m = Z.encode(t), c.set(Z, m));
    for (let ut = 0; ut < et.length; ut++) {
      var g = et[ut].doc;
      if (!g || (g = ht(g, tt), !g)) continue;
      var x = g.trim().split(/\s+/);
      if (!x.length) continue;
      g = "";
      var y = [];
      let ct = [];
      for (var L = -1, M = -1, v = 0, j = 0; j < x.length; j++) {
        var _ = x[j], S = Z.encode(_);
        S = 1 < S.length ? S.join(" ") : S[0];
        let k;
        if (S && _) {
          for (var z = _.length, P = (Z.split ? _.replace(Z.split, "") : _).length - S.length, R = "", E = 0, W = 0; W < m.length; W++) {
            var b = m[W];
            if (b) {
              var B = b.length;
              B += P, E && B <= E || (b = S.indexOf(b), -1 < b && (R = (b ? _.substring(0, b) : "") + h + _.substring(b, b + B) + o + (b + B < z ? _.substring(b + B) : ""), E = B, k = !0));
            }
          }
          R && (l && (0 > L && (L = g.length + (g ? 1 : 0)), M = g.length + (g ? 1 : 0) + R.length, v += z, ct.push(y.length), y.push({ match: R })), g += (g ? " " : "") + R);
        }
        if (!k) _ = x[j], g += (g ? " " : "") + _, l && y.push({ text: _ });
        else if (l && v >= l) break;
      }
      if (v = ct.length * (r.length - 2), d || p || l && g.length - v > l) if (v = l + v - 2 * a, j = M - L, 0 < d && (j += d), 0 < p && (j += p), j <= v) x = d ? L - (0 < d ? d : 0) : L - ((v - j) / 2 | 0), y = p ? M + (0 < p ? p : 0) : x + v, f || (0 < x && g.charAt(x) !== " " && g.charAt(x - 1) !== " " && (x = g.indexOf(" ", x), 0 > x && (x = 0)), y < g.length && g.charAt(y - 1) !== " " && g.charAt(y) !== " " && (y = g.lastIndexOf(" ", y), y < M ? y = M : ++y)), g = (x ? n : "") + g.substring(x, y) + (y < g.length ? n : "");
      else {
        for (M = [], L = {}, v = {}, j = {}, _ = {}, S = {}, R = P = z = 0, W = E = 1; ; ) {
          var C = void 0;
          for (let k = 0, A; k < ct.length; k++) {
            if (A = ct[k], R) if (P !== R) {
              if (j[k + 1]) continue;
              if (A += R, L[A]) {
                z -= a, v[k + 1] = 1, j[k + 1] = 1;
                continue;
              }
              if (A >= y.length - 1) {
                if (A >= y.length) {
                  j[k + 1] = 1, A >= x.length && (v[k + 1] = 1);
                  continue;
                }
                z -= a;
              }
              if (g = y[A].text, B = p && S[k]) if (0 < B) {
                if (g.length > B) if (j[k + 1] = 1, f) g = g.substring(0, B);
                else continue;
                (B -= g.length) || (B = -1), S[k] = B;
              } else {
                j[k + 1] = 1;
                continue;
              }
              if (z + g.length + 1 <= l) g = " " + g, M[k] += g;
              else if (f) C = l - z - 1, 0 < C && (g = " " + g.substring(0, C), M[k] += g), j[k + 1] = 1;
              else {
                j[k + 1] = 1;
                continue;
              }
            } else {
              if (j[k]) continue;
              if (A -= P, L[A]) {
                z -= a, j[k] = 1, v[k] = 1;
                continue;
              }
              if (0 >= A) {
                if (0 > A) {
                  j[k] = 1, v[k] = 1;
                  continue;
                }
                z -= a;
              }
              if (g = y[A].text, B = d && _[k]) if (0 < B) {
                if (g.length > B) if (j[k] = 1, f) g = g.substring(g.length - B);
                else continue;
                (B -= g.length) || (B = -1), _[k] = B;
              } else {
                j[k] = 1;
                continue;
              }
              if (z + g.length + 1 <= l) g += " ", M[k] = g + M[k];
              else if (f) C = g.length + 1 - (l - z), 0 <= C && C < g.length && (g = g.substring(C) + " ", M[k] = g + M[k]), j[k] = 1;
              else {
                j[k] = 1;
                continue;
              }
            }
            else {
              g = y[A].match, d && (_[k] = d), p && (S[k] = p), k && z++;
              let vt;
              if (A ? !k && a && (z += a) : (v[k] = 1, j[k] = 1), A >= x.length - 1 || A < y.length - 1 && y[A + 1].match ? vt = 1 : a && (z += a), z -= r.length - 2, !k || z + g.length <= l) M[k] = g;
              else {
                C = E = W = v[k] = 0;
                break;
              }
              vt && (v[k + 1] = 1, j[k + 1] = 1);
            }
            z += g.length, C = L[A] = 1;
          }
          if (C) P === R ? R++ : P++;
          else {
            if (P === R ? E = 0 : W = 0, !E && !W) break;
            E ? (P++, R = P) : R++;
          }
        }
        g = "";
        for (let k = 0, A; k < M.length; k++) A = (k && v[k] ? " " : (k && !n ? " " : "") + n) + M[k], g += A;
        n && !v[M.length] && (g += n);
      }
      u && (g = g.replace(u, " ")), et[ut].highlight = g;
    }
    if (s) break;
  }
  return e;
}
K.prototype.search = function(t, e, i, s) {
  i || (!e && rt(t) ? (i = t, t = "") : rt(e) && (i = e, e = 0));
  let n = [];
  var r = [];
  let h, o, l, f, u = 0;
  var c = !0;
  let a;
  if (i) {
    i.constructor === Array && (i = { index: i }), t = i.query || t, h = i.pluck, o = i.merge, l = h || i.field || (l = i.index) && (l.index ? null : l), f = this.tag && i.tag;
    var d = i.suggest;
    c = i.resolve !== !1, c || h || !(l = l || this.field) || (D(l) ? h = l : (l.constructor === Array && l.length === 1 && (l = l[0]), h = l.field || l.index));
    var p = (a = c && this.store && i.highlight) || c && this.store && i.enrich;
    e = i.limit || e;
    var m = i.offset || 0;
    if (e || (e = 100), f && (!this.db || !s)) {
      f.constructor !== Array && (f = [f]);
      var g = [];
      for (let M = 0, v; M < f.length; M++) if (v = f[M], v.field && v.tag) {
        var x = v.tag;
        if (x.constructor === Array) for (var y = 0; y < x.length; y++) g.push(v.field, x[y]);
        else g.push(v.field, x);
      } else {
        x = Object.keys(v);
        for (let j = 0, _, S; j < x.length; j++) if (_ = x[j], S = v[_], S.constructor === Array) for (y = 0; y < S.length; y++) g.push(_, S[y]);
        else g.push(_, S);
      }
      if (f = g, !t) {
        if (c = [], g.length) for (r = 0; r < g.length; r += 2) {
          if (this.db) {
            if (d = this.index.get(g[r]), !d) continue;
            c.push(d = d.db.tag(g[r + 1], e, m, p));
          } else d = ke.call(this, g[r], g[r + 1], e, m, p);
          n.push({ field: g[r], tag: g[r + 1], result: d });
        }
        return c.length ? Promise.all(c).then(function(M) {
          for (let v = 0; v < M.length; v++) n[v].result = M[v];
          return n;
        }) : n;
      }
    }
    l && l.constructor !== Array && (l = [l]);
  }
  l || (l = this.field), g = !s && (this.worker || this.db) && [];
  let L;
  for (let M = 0, v, j, _; M < l.length; M++) {
    if (j = l[M], this.db && this.tag && !this.F[M]) continue;
    let S;
    if (D(j) || (S = j, j = S.field, t = S.query || t, e = S.limit || e, m = S.offset || m, d = S.suggest || d, a = (p = this.store && (S.enrich || p)) && (i.highlight || a)), s) v = s[M];
    else if (x = S || i, y = this.index.get(j), f && (this.db && (x.tag = f, L = y.db.support_tag_search, x.field = l), L || (x.enrich = !1)), g) {
      g[M] = y.search(t, e, x), x && p && (x.enrich = p);
      continue;
    } else v = y.search(t, e, x), x && p && (x.enrich = p);
    if (_ = v && (c ? v.length : v.result.length), f && _) {
      if (x = [], y = 0, this.db && s) {
        if (!L) for (let z = l.length; z < s.length; z++) {
          let P = s[z];
          if (P && P.length) y++, x.push(P);
          else if (!d) return c ? n : new O(n);
        }
      } else for (let z = 0, P, R; z < f.length; z += 2) {
        if (P = this.tag.get(f[z]), !P) {
          if (d) continue;
          return c ? n : new O(n);
        }
        if (R = (P = P && P.get(f[z + 1])) && P.length) y++, x.push(P);
        else if (!d) return c ? n : new O(n);
      }
      if (y) {
        if (v = ye(v, x, c), _ = v.length, !_ && !d) return c ? v : new O(v);
        y--;
      }
    }
    if (_) r[u] = j, n.push(v), u++;
    else if (l.length === 1) return c ? n : new O(n);
  }
  if (g) {
    if (this.db && f && f.length && !L) for (p = 0; p < f.length; p += 2) {
      if (r = this.index.get(f[p]), !r) {
        if (d) continue;
        return c ? n : new O(n);
      }
      g.push(r.db.tag(f[p + 1], e, m, !1));
    }
    const M = this;
    return Promise.all(g).then(function(v) {
      return v.length ? M.search(t, e, i, v) : v;
    });
  }
  if (!u) return c ? n : new O(n);
  if (h && (!p || !this.store)) return n[0];
  for (g = [], m = 0; m < r.length; m++) {
    if (d = n[m], p && d.length && typeof d[0].doc > "u" && (this.db ? g.push(d = this.index.get(this.field[0]).db.enrich(d)) : d = G.call(this, d)), h) return c ? a ? kt(t, d, this.index, h, a) : d : new O(d);
    n[m] = { field: r[m], result: d };
  }
  if (p && this.db && g.length) {
    const M = this;
    return Promise.all(g).then(function(v) {
      for (let j = 0; j < v.length; j++) n[j].result = v[j];
      return o ? Ct(n) : a ? kt(t, n, M.index, h, a) : n;
    });
  }
  return o ? Ct(n) : a ? kt(t, n, this.index, h, a) : n;
};
function Ct(t) {
  const e = [], i = I();
  for (let s = 0, n, r; s < t.length; s++) {
    n = t[s], r = n.result;
    for (let h = 0, o, l, f; h < r.length; h++) l = r[h], typeof l != "object" && (l = { id: l }), o = l.id, (f = i[o]) ? f.push(n.field) : (l.field = i[o] = [n.field], e.push(l));
  }
  return e;
}
function ke(t, e, i, s, n) {
  if (t = this.tag.get(t), !t) return [];
  if ((e = (t = t && t.get(e)) && t.length - s) && 0 < e)
    return (e > i || s) && (t = t.slice(s, s + i)), n && (t = G.call(this, t)), t;
}
function G(t) {
  if (!this || !this.store) return t;
  const e = Array(t.length);
  for (let i = 0, s; i < t.length; i++) s = t[i], e[i] = { id: s, doc: this.store.get(s) };
  return e;
}
function K(t) {
  if (!this || this.constructor !== K) return new K(t);
  const e = t.document || t.doc || t;
  let i, s;
  if (this.F = [], this.field = [], this.J = [], this.key = (i = e.key || e.id) && mt(i, this.J) || "id", (s = t.keystore || 0) && (this.keystore = s), this.fastupdate = !!t.fastupdate, this.reg = !this.fastupdate || t.worker || t.db ? s ? new F(s) : /* @__PURE__ */ new Set() : s ? new T(s) : /* @__PURE__ */ new Map(), this.C = (i = e.store || null) && i && i !== !0 && [], this.store = i && (s ? new T(s) : /* @__PURE__ */ new Map()), this.cache = (i = t.cache || null) && new q(i), t.cache = !1, this.worker = t.worker || !1, this.priority = t.priority || 4, this.index = je.call(this, t, e), this.tag = null, (i = e.tag) && (typeof i == "string" && (i = [i]), i.length)) {
    this.tag = /* @__PURE__ */ new Map(), this.D = [], this.R = [];
    for (let n = 0, r, h; n < i.length; n++) {
      if (r = i[n], h = r.field || r, !h) throw Error("The tag field from the document descriptor is undefined.");
      r.custom ? this.D[n] = r.custom : (this.D[n] = mt(h, this.J), r.filter && (typeof this.D[n] == "string" && (this.D[n] = new String(this.D[n])), this.D[n].I = r.filter)), this.R[n] = h, this.tag.set(h, /* @__PURE__ */ new Map());
    }
  }
  if (this.worker) {
    this.fastupdate = !1;
    const n = [];
    for (const r of this.index.values()) r.then && n.push(r);
    if (n.length) {
      const r = this;
      return Promise.all(n).then(function(h) {
        const o = /* @__PURE__ */ new Map();
        let l = 0;
        for (const u of r.index.entries()) {
          const c = u[0];
          var f = u[1];
          if (f.then) {
            f = n[l].encoder || {};
            let a = o.get(f);
            a || (a = f.encode ? f : new lt(f), o.set(f, a)), f = h[l], f.encoder = a, r.index.set(c, f), l++;
          }
        }
        return r;
      });
    }
  } else t.db && (this.fastupdate = !1, this.mount(t.db));
}
w = K.prototype;
w.mount = function(t) {
  let e = this.field;
  if (this.tag) for (let r = 0, h; r < this.R.length; r++) {
    h = this.R[r];
    var i = void 0;
    this.index.set(h, i = new $({}, this.reg)), e === this.field && (e = e.slice(0)), e.push(h), i.tag = this.tag.get(h);
  }
  i = [];
  const s = { db: t.db, type: t.type, fastupdate: t.fastupdate };
  for (let r = 0, h, o; r < e.length; r++) {
    s.field = o = e[r], h = this.index.get(o);
    const l = new t.constructor(t.id, s);
    l.id = t.id, i[r] = l.mount(h), h.document = !0, r ? h.bypass = !0 : h.store = this.store;
  }
  const n = this;
  return this.db = Promise.all(i).then(function() {
    n.db = !0;
  });
};
w.commit = async function(t, e) {
  const i = [];
  for (const s of this.index.values()) i.push(s.commit(t, e));
  await Promise.all(i), this.reg.clear();
};
w.destroy = function() {
  const t = [];
  for (const e of this.index.values()) t.push(e.destroy());
  return Promise.all(t);
};
function je(t, e) {
  const i = /* @__PURE__ */ new Map();
  let s = e.index || e.field || e;
  D(s) && (s = [s]);
  for (let n = 0, r, h; n < s.length; n++) {
    if (r = s[n], D(r) || (h = r, r = r.field), h = rt(h) ? Object.assign({}, t, h) : t, this.worker) {
      const o = new ot(h);
      o.encoder = h.encoder, i.set(r, o);
    }
    this.worker || i.set(r, new $(h, this.reg)), h.custom ? this.F[n] = h.custom : (this.F[n] = mt(r, this.J), h.filter && (typeof this.F[n] == "string" && (this.F[n] = new String(this.F[n])), this.F[n].I = h.filter)), this.field[n] = r;
  }
  if (this.C) {
    t = e.store, D(t) && (t = [t]);
    for (let n = 0, r, h; n < t.length; n++) r = t[n], h = r.field || r, r.custom ? (this.C[n] = r.custom, r.custom.V = h) : (this.C[n] = mt(h, this.J), r.filter && (typeof this.C[n] == "string" && (this.C[n] = new String(this.C[n])), this.C[n].I = r.filter));
  }
  return i;
}
function mt(t, e) {
  const i = t.split(":");
  let s = 0;
  for (let n = 0; n < i.length; n++) t = i[n], t[t.length - 1] === "]" && (t = t.substring(0, t.length - 2)) && (e[s] = !0), t && (i[s++] = t);
  return s < i.length && (i.length = s), 1 < s ? i : i[0];
}
w.append = function(t, e) {
  return this.add(t, e, !0);
};
w.update = function(t, e) {
  return this.remove(t).add(t, e);
};
w.remove = function(t) {
  rt(t) && (t = ht(t, this.key));
  for (var e of this.index.values()) e.remove(t, !0);
  if (this.reg.has(t)) {
    if (this.tag && !this.fastupdate) for (let i of this.tag.values()) for (let s of i) {
      e = s[0];
      const n = s[1], r = n.indexOf(t);
      -1 < r && (1 < n.length ? n.splice(r, 1) : i.delete(e));
    }
    this.store && this.store.delete(t), this.reg.delete(t);
  }
  return this.cache && this.cache.remove(t), this;
};
w.clear = function() {
  const t = [];
  for (const e of this.index.values()) {
    const i = e.clear();
    i.then && t.push(i);
  }
  if (this.tag) for (const e of this.tag.values()) e.clear();
  return this.store && this.store.clear(), this.cache && this.cache.clear(), t.length ? Promise.all(t) : this;
};
w.contain = function(t) {
  return this.db ? this.index.get(this.field[0]).db.has(t) : this.reg.has(t);
};
w.cleanup = function() {
  for (const t of this.index.values()) t.cleanup();
  return this;
};
w.get = function(t) {
  return this.db ? this.index.get(this.field[0]).db.enrich(t).then(function(e) {
    return e[0] && e[0].doc || null;
  }) : this.store.get(t) || null;
};
w.set = function(t, e) {
  return typeof t == "object" && (e = t, t = ht(e, this.key)), this.store.set(t, e), this;
};
w.searchCache = re;
w.export = function(t, e, i = 0, s = 0) {
  if (i < this.field.length) {
    const h = this.field[i];
    if ((e = this.index.get(h).export(t, h, i, s = 1)) && e.then) {
      const o = this;
      return e.then(function() {
        return o.export(t, h, i + 1);
      });
    }
    return this.export(t, h, i + 1);
  }
  let n, r;
  switch (s) {
    case 0:
      n = "reg", r = Ht(this.reg), e = null;
      break;
    case 1:
      n = "tag", r = this.tag && Xt(this.tag, this.reg.size), e = null;
      break;
    case 2:
      n = "doc", r = this.store && Lt(this.store), e = null;
      break;
    default:
      return;
  }
  return pt.call(this, t, e, n, r, i, s);
};
w.import = function(t, e) {
  var i = t.split(".");
  i[i.length - 1] === "json" && i.pop();
  const s = 2 < i.length ? i[0] : "";
  if (i = 2 < i.length ? i[2] : i[1], this.worker && s) return this.index.get(s).import(t);
  if (e) {
    if (typeof e == "string" && (e = JSON.parse(e)), s) return this.index.get(s).import(i, e);
    switch (i) {
      case "reg":
        this.fastupdate = !1, this.reg = qt(e, this.reg);
        for (let n = 0, r; n < this.field.length; n++) r = this.index.get(this.field[n]), r.fastupdate = !1, r.reg = this.reg;
        if (this.worker) {
          e = [];
          for (const n of this.index.values()) e.push(n.import(t));
          return Promise.all(e);
        }
        break;
      case "tag":
        this.tag = Yt(e, this.tag);
        break;
      case "doc":
        this.store = Bt(e, this.store);
    }
  }
};
It(K.prototype);
function re(t, e, i) {
  const s = (typeof t == "object" ? "" + t.query : t).toLowerCase();
  this.cache || (this.cache = new q());
  let n = this.cache.get(s);
  if (!n) {
    if (n = this.search(t, e, i), n.then) {
      const r = this;
      n.then(function(h) {
        return r.cache.set(s, h), h;
      });
    }
    this.cache.set(s, n);
  }
  return n;
}
function q(t) {
  this.limit = t && t !== !0 ? t : 1e3, this.cache = /* @__PURE__ */ new Map(), this.h = "";
}
q.prototype.set = function(t, e) {
  this.cache.set(this.h = t, e), this.cache.size > this.limit && this.cache.delete(this.cache.keys().next().value);
};
q.prototype.get = function(t) {
  const e = this.cache.get(t);
  return e && this.h !== t && (this.cache.delete(t), this.cache.set(this.h = t, e)), e;
};
q.prototype.remove = function(t) {
  for (const e of this.cache) {
    const i = e[0];
    e[1].includes(t) && this.cache.delete(i);
  }
};
q.prototype.clear = function() {
  this.cache.clear(), this.h = "";
};
const Tt = { normalize: !1, numeric: !1, dedupe: !1 }, gt = {}, jt = /* @__PURE__ */ new Map([["b", "p"], ["v", "f"], ["w", "f"], ["z", "s"], ["x", "s"], ["d", "t"], ["n", "m"], ["c", "k"], ["g", "k"], ["j", "k"], ["q", "k"], ["i", "e"], ["y", "e"], ["u", "o"]]), Et = /* @__PURE__ */ new Map([["ae", "a"], ["oe", "o"], ["sh", "s"], ["kh", "k"], ["th", "t"], ["ph", "f"], ["pf", "f"]]), Gt = [/([^aeo])h(.)/g, "$1$2", /([aeo])h([^aeo]|$)/g, "$1$2", /(.)\1+/g, "$1"], Jt = { a: "", e: "", i: "", o: "", u: "", y: "", b: 1, f: 1, p: 1, v: 1, c: 2, g: 2, j: 2, k: 2, q: 2, s: 2, x: 2, z: 2, ß: 2, d: 3, t: 3, l: 4, m: 5, n: 5, r: 6 };
var Me = { Exact: Tt, Default: gt, Normalize: gt, LatinBalance: { mapper: jt }, LatinAdvanced: { mapper: jt, matcher: Et, replacer: Gt }, LatinExtra: { mapper: jt, replacer: Gt.concat([/(?!^)[aeo]/g, ""]), matcher: Et }, LatinSoundex: { dedupe: !1, include: { letter: !0 }, finalize: function(t) {
  for (let i = 0; i < t.length; i++) {
    var e = t[i];
    let s = e.charAt(0), n = Jt[s];
    for (let r = 1, h; r < e.length && (h = e.charAt(r), h === "h" || h === "w" || !(h = Jt[h]) || h === n || (s += h, n = h, s.length !== 4)); r++) ;
    t[i] = s;
  }
} }, CJK: { split: "" }, LatinExact: Tt, LatinDefault: gt, LatinSimple: gt };
$.prototype.remove = function(t, e) {
  const i = this.reg.size && (this.fastupdate ? this.reg.get(t) : this.reg.has(t));
  if (i) {
    if (this.fastupdate) {
      for (let s = 0, n; s < i.length; s++)
        if (n = i[s]) if (2 > n.length) n.pop();
        else {
          const r = n.indexOf(t);
          r === i.length - 1 ? n.pop() : n.splice(r, 1);
        }
    } else ft(this.map, t), this.depth && ft(this.ctx, t);
    e || this.reg.delete(t);
  }
  return this.db && (this.commit_task.push({ del: t }), this.T && he(this)), this.cache && this.cache.remove(t), this;
};
function ft(t, e) {
  let i = 0;
  var s = typeof e > "u";
  if (t.constructor === Array) {
    for (let n = 0, r, h; n < t.length; n++)
      if ((r = t[n]) && r.length) if (s) i++;
      else if (h = r.indexOf(e), 0 <= h) {
        1 < r.length ? (r.splice(h, 1), i++) : delete t[n];
        break;
      } else i++;
  } else for (let n of t.entries()) {
    s = n[0];
    const r = ft(n[1], e);
    r ? i += r : t.delete(s);
  }
  return i;
}
const _e = { memory: { resolution: 1 }, performance: { resolution: 3, fastupdate: !0, context: { depth: 1, resolution: 1 } }, match: { tokenize: "forward" }, score: { resolution: 9, context: { depth: 2, resolution: 3 } } };
$.prototype.add = function(t, e, i, s) {
  if (e && (t || t === 0)) {
    if (!s && !i && this.reg.has(t)) return this.update(t, e);
    s = this.depth, e = this.encoder.encode(e, !s);
    const f = e.length;
    if (f) {
      const u = I(), c = I(), a = this.resolution;
      for (let d = 0; d < f; d++) {
        let p = e[this.rtl ? f - 1 - d : d];
        var n = p.length;
        if (n && (s || !c[p])) {
          var r = this.score ? this.score(e, p, d, null, 0) : dt(a, f, d), h = "";
          switch (this.tokenize) {
            case "full":
              if (2 < n) {
                for (let m = 0, g; m < n; m++) for (r = n; r > m; r--) {
                  h = p.substring(m, r), g = this.rtl ? n - 1 - m : m;
                  var o = this.score ? this.score(e, p, d, h, g) : dt(
                    a,
                    f,
                    d,
                    n,
                    g
                  );
                  st(this, c, h, o, t, i);
                }
                break;
              }
            case "bidirectional":
            case "reverse":
              if (1 < n) {
                for (o = n - 1; 0 < o; o--) {
                  h = p[this.rtl ? n - 1 - o : o] + h;
                  var l = this.score ? this.score(e, p, d, h, o) : dt(a, f, d, n, o);
                  st(this, c, h, l, t, i);
                }
                h = "";
              }
            case "forward":
              if (1 < n) {
                for (o = 0; o < n; o++) h += p[this.rtl ? n - 1 - o : o], st(this, c, h, r, t, i);
                break;
              }
            default:
              if (st(this, c, p, r, t, i), s && 1 < f && d < f - 1) {
                for (n = I(), h = this.U, r = p, o = Math.min(s + 1, this.rtl ? d + 1 : f - d), n[r] = 1, l = 1; l < o; l++) if ((p = e[this.rtl ? f - 1 - d - l : d + l]) && !n[p]) {
                  n[p] = 1;
                  const m = this.score ? this.score(e, r, d, p, l - 1) : dt(h + (f / 2 > h ? 0 : 1), f, d, o - 1, l - 1), g = this.bidirectional && p > r;
                  st(this, u, g ? r : p, m, t, i, g ? p : r);
                }
              }
          }
        }
      }
      this.fastupdate || this.reg.add(t);
    } else e = "";
  }
  return this.db && (e || this.commit_task.push({ del: t }), this.T && he(this)), this;
};
function st(t, e, i, s, n, r, h) {
  let o = h ? t.ctx : t.map, l;
  if ((!e[i] || h && !(l = e[i])[h]) && (h ? (e = l || (e[i] = I()), e[h] = 1, (l = o.get(h)) ? o = l : o.set(h, o = /* @__PURE__ */ new Map())) : e[i] = 1, (l = o.get(i)) ? o = l : o.set(i, o = l = []), o = o[s] || (o[s] = []), !r || !o.includes(n))) {
    if (o.length === 2 ** 31 - 1) {
      if (e = new H(o), t.fastupdate) for (let f of t.reg.values()) f.includes(o) && (f[f.indexOf(o)] = e);
      l[s] = o = e;
    }
    o.push(n), t.fastupdate && ((s = t.reg.get(n)) ? s.push(o) : t.reg.set(n, [o]));
  }
}
function dt(t, e, i, s, n) {
  return i && 1 < t ? e + (s || 0) <= t ? i + (n || 0) : (t - 1) / (e + (s || 0)) * (i + (n || 0)) + 1 | 0 : 0;
}
$.prototype.search = function(t, e, i) {
  i || (e || typeof t != "object" ? typeof e == "object" && (i = e, e = 0) : (i = t, t = ""));
  let s = [], n, r, h, o = 0, l, f, u, c, a;
  i ? (t = i.query || t, e = i.limit || e, o = i.offset || 0, r = i.context, h = i.suggest, a = (l = i.resolve !== !1) && i.enrich, u = i.boost, c = i.resolution, f = this.db && i.tag) : l = this.resolve, r = this.depth && r !== !1;
  let d = this.encoder.encode(t, !r);
  if (n = d.length, e = e || (l ? 100 : 0), n === 1) return Wt.call(this, d[0], "", e, o, l, a, f);
  if (n === 2 && r && !h) return Wt.call(this, d[1], d[0], e, o, l, a, f);
  let p = I(), m = 0, g;
  if (r && (g = d[0], m = 1), c || c === 0 || (c = g ? this.U : this.resolution), this.db) {
    if (this.db.search && (t = this.db.search(this, d, e, o, h, l, a, f), t !== !1)) return t;
    const x = this;
    return async function() {
      for (let y, L; m < n; m++) {
        if ((L = d[m]) && !p[L]) {
          if (p[L] = 1, y = await Pt(x, L, g, 0, 0, !1, !1), y = Zt(y, s, h, c)) {
            s = y;
            break;
          }
          g && (h && y && s.length || (g = L));
        }
        h && g && m === n - 1 && !s.length && (c = x.resolution, g = "", m = -1, p = I());
      }
      return Ut(s, c, e, o, h, u, l);
    }();
  }
  for (let x, y; m < n; m++) {
    if ((y = d[m]) && !p[y]) {
      if (p[y] = 1, x = Pt(this, y, g, 0, 0, !1, !1), x = Zt(x, s, h, c)) {
        s = x;
        break;
      }
      g && (h && x && s.length || (g = y));
    }
    h && g && m === n - 1 && !s.length && (c = this.resolution, g = "", m = -1, p = I());
  }
  return Ut(s, c, e, o, h, u, l);
};
function Ut(t, e, i, s, n, r, h) {
  let o = t.length, l = t;
  if (1 < o) l = Kt(t, e, i, s, n, r, h);
  else if (o === 1) return h ? Nt.call(null, t[0], i, s) : new O(t[0]);
  return h ? l : new O(l);
}
function Wt(t, e, i, s, n, r, h) {
  return t = Pt(this, t, e, i, s, n, r, h), this.db ? t.then(function(o) {
    return n ? o || [] : new O(o);
  }) : t && t.length ? n ? Nt.call(this, t, i, s) : new O(t) : n ? [] : new O();
}
function Zt(t, e, i, s) {
  let n = [];
  if (t && t.length) {
    if (t.length <= s) {
      e.push(t);
      return;
    }
    for (let r = 0, h; r < s; r++) (h = t[r]) && (n[r] = h);
    if (n.length) {
      e.push(n);
      return;
    }
  }
  if (!i) return n;
}
function Pt(t, e, i, s, n, r, h, o) {
  let l;
  return i && (l = t.bidirectional && e > i) && (l = i, i = e, e = l), t.db ? t.db.get(e, i, s, n, r, h, o) : (t = i ? (t = t.ctx.get(i)) && t.get(e) : t.map.get(e), t);
}
function $(t, e) {
  if (!this || this.constructor !== $) return new $(t);
  if (t) {
    var i = D(t) ? t : t.preset;
    i && (t = Object.assign({}, _e[i], t));
  } else t = {};
  i = t.context;
  const s = i === !0 ? { depth: 1 } : i || {}, n = D(t.encoder) ? Me[t.encoder] : t.encode || t.encoder || {};
  this.encoder = n.encode ? n : typeof n == "object" ? new lt(n) : { encode: n }, this.resolution = t.resolution || 9, this.tokenize = i = (i = t.tokenize) && i !== "default" && i !== "exact" && i || "strict", this.depth = i === "strict" && s.depth || 0, this.bidirectional = s.bidirectional !== !1, this.fastupdate = !!t.fastupdate, this.score = t.score || null, (i = t.keystore || 0) && (this.keystore = i), this.map = i ? new T(i) : /* @__PURE__ */ new Map(), this.ctx = i ? new T(i) : /* @__PURE__ */ new Map(), this.reg = e || (this.fastupdate ? i ? new T(i) : /* @__PURE__ */ new Map() : i ? new F(i) : /* @__PURE__ */ new Set()), this.U = s.resolution || 3, this.rtl = n.rtl || t.rtl || !1, this.cache = (i = t.cache || null) && new q(i), this.resolve = t.resolve !== !1, (i = t.db) && (this.db = this.mount(i)), this.T = t.commit !== !1, this.commit_task = [], this.commit_timer = null, this.priority = t.priority || 4;
}
w = $.prototype;
w.mount = function(t) {
  return this.commit_timer && (clearTimeout(this.commit_timer), this.commit_timer = null), t.mount(this);
};
w.commit = function(t, e) {
  return this.commit_timer && (clearTimeout(this.commit_timer), this.commit_timer = null), this.db.commit(this, t, e);
};
w.destroy = function() {
  return this.commit_timer && (clearTimeout(this.commit_timer), this.commit_timer = null), this.db.destroy();
};
function he(t) {
  t.commit_timer || (t.commit_timer = setTimeout(function() {
    t.commit_timer = null, t.db.commit(t, void 0, void 0);
  }, 1));
}
w.clear = function() {
  return this.map.clear(), this.ctx.clear(), this.reg.clear(), this.cache && this.cache.clear(), this.db && (this.commit_timer && clearTimeout(this.commit_timer), this.commit_timer = null, this.commit_task = [{ clear: !0 }]), this;
};
w.append = function(t, e) {
  return this.add(t, e, !0);
};
w.contain = function(t) {
  return this.db ? this.db.has(t) : this.reg.has(t);
};
w.update = function(t, e) {
  const i = this, s = this.remove(t);
  return s && s.then ? s.then(() => i.add(t, e)) : this.add(t, e);
};
w.cleanup = function() {
  return this.fastupdate ? (ft(this.map), this.depth && ft(this.ctx), this) : this;
};
w.searchCache = re;
w.export = function(t, e, i = 0, s = 0) {
  let n, r;
  switch (s) {
    case 0:
      n = "reg", r = Ht(this.reg);
      break;
    case 1:
      n = "cfg", r = null;
      break;
    case 2:
      n = "map", r = Lt(this.map, this.reg.size);
      break;
    case 3:
      n = "ctx", r = Xt(this.ctx, this.reg.size);
      break;
    default:
      return;
  }
  return pt.call(this, t, e, n, r, i, s);
};
w.import = function(t, e) {
  if (e) switch (typeof e == "string" && (e = JSON.parse(e)), t = t.split("."), t[t.length - 1] === "json" && t.pop(), t.length === 3 && t.shift(), t = 1 < t.length ? t[1] : t[0], t) {
    case "reg":
      this.fastupdate = !1, this.reg = qt(e, this.reg);
      break;
    case "map":
      this.map = Bt(e, this.map);
      break;
    case "ctx":
      this.ctx = Yt(e, this.ctx);
  }
};
w.serialize = function(t = !0) {
  let e = "", i = "", s = "";
  if (this.reg.size) {
    let r;
    for (var n of this.reg.keys()) r || (r = typeof n), e += (e ? "," : "") + (r === "string" ? '"' + n + '"' : n);
    e = "index.reg=new Set([" + e + "]);", i = Ft(this.map, r), i = "index.map=new Map([" + i + "]);";
    for (const h of this.ctx.entries()) {
      n = h[0];
      let o = Ft(h[1], r);
      o = "new Map([" + o + "])", o = '["' + n + '",' + o + "]", s += (s ? "," : "") + o;
    }
    s = "index.ctx=new Map([" + s + "]);";
  }
  return t ? "function inject(index){" + e + i + s + "}" : e + i + s;
};
It($.prototype);
const le = typeof window < "u" && (window.indexedDB || window.mozIndexedDB || window.webkitIndexedDB || window.msIndexedDB), wt = ["map", "ctx", "tag", "reg", "cfg"], X = I();
function At(t, e = {}) {
  if (!this || this.constructor !== At) return new At(t, e);
  typeof t == "object" && (e = t, t = t.name), t || console.info("Default storage space was used, because a name was not passed."), this.id = "flexsearch" + (t ? ":" + t.toLowerCase().replace(/[^a-z0-9_\-]/g, "") : ""), this.field = e.field ? e.field.toLowerCase().replace(/[^a-z0-9_\-]/g, "") : "", this.type = e.type, this.fastupdate = this.support_tag_search = !1, this.db = null, this.h = {};
}
w = At.prototype;
w.mount = function(t) {
  return t.index ? t.mount(this) : (t.db = this, this.open());
};
w.open = function() {
  if (this.db) return this.db;
  let t = this;
  navigator.storage && navigator.storage.persist(), X[t.id] || (X[t.id] = []), X[t.id].push(t.field);
  const e = le.open(t.id, 1);
  return e.onupgradeneeded = function() {
    const i = t.db = this.result;
    for (let s = 0, n; s < wt.length; s++) {
      n = wt[s];
      for (let r = 0, h; r < X[t.id].length; r++) h = X[t.id][r], i.objectStoreNames.contains(n + (n !== "reg" && h ? ":" + h : "")) || i.createObjectStore(n + (n !== "reg" && h ? ":" + h : ""));
    }
  }, t.db = U(e, function(i) {
    t.db = i, t.db.onversionchange = function() {
      t.close();
    };
  });
};
w.close = function() {
  this.db && this.db.close(), this.db = null;
};
w.destroy = function() {
  const t = le.deleteDatabase(this.id);
  return U(t);
};
w.clear = function() {
  const t = [];
  for (let i = 0, s; i < wt.length; i++) {
    s = wt[i];
    for (let n = 0, r; n < X[this.id].length; n++) r = X[this.id][n], t.push(s + (s !== "reg" && r ? ":" + r : ""));
  }
  const e = this.db.transaction(t, "readwrite");
  for (let i = 0; i < t.length; i++) e.objectStore(t[i]).clear();
  return U(e);
};
w.get = function(t, e, i = 0, s = 0, n = !0, r = !1) {
  t = this.db.transaction((e ? "ctx" : "map") + (this.field ? ":" + this.field : ""), "readonly").objectStore((e ? "ctx" : "map") + (this.field ? ":" + this.field : "")).get(e ? e + ":" + t : t);
  const h = this;
  return U(t).then(function(o) {
    let l = [];
    if (!o || !o.length) return l;
    if (n) {
      if (!i && !s && o.length === 1) return o[0];
      for (let f = 0, u; f < o.length; f++) if ((u = o[f]) && u.length) {
        if (s >= u.length) {
          s -= u.length;
          continue;
        }
        const c = i ? s + Math.min(u.length - s, i) : u.length;
        for (let a = s; a < c; a++) l.push(u[a]);
        if (s = 0, l.length === i) break;
      }
      return r ? h.enrich(l) : l;
    }
    return o;
  });
};
w.tag = function(t, e = 0, i = 0, s = !1) {
  t = this.db.transaction("tag" + (this.field ? ":" + this.field : ""), "readonly").objectStore("tag" + (this.field ? ":" + this.field : "")).get(t);
  const n = this;
  return U(t).then(function(r) {
    return !r || !r.length || i >= r.length ? [] : !e && !i ? r : (r = r.slice(i, i + e), s ? n.enrich(r) : r);
  });
};
w.enrich = function(t) {
  typeof t != "object" && (t = [t]);
  const e = this.db.transaction("reg", "readonly").objectStore("reg"), i = [];
  for (let s = 0; s < t.length; s++) i[s] = U(e.get(t[s]));
  return Promise.all(i).then(function(s) {
    for (let n = 0; n < s.length; n++) s[n] = { id: t[n], doc: s[n] ? JSON.parse(s[n]) : null };
    return s;
  });
};
w.has = function(t) {
  return t = this.db.transaction("reg", "readonly").objectStore("reg").getKey(t), U(t).then(function(e) {
    return !!e;
  });
};
w.search = null;
w.info = function() {
};
w.transaction = function(t, e, i) {
  t += t !== "reg" && this.field ? ":" + this.field : "";
  let s = this.h[t + ":" + e];
  if (s) return i.call(this, s);
  let n = this.db.transaction(t, e);
  this.h[t + ":" + e] = s = n.objectStore(t);
  const r = i.call(this, s);
  return this.h[t + ":" + e] = null, U(n).finally(function() {
    return n = s = null, r;
  });
};
w.commit = async function(t, e, i) {
  if (e) await this.clear(), t.commit_task = [];
  else {
    let s = t.commit_task;
    t.commit_task = [];
    for (let n = 0, r; n < s.length; n++) if (r = s[n], r.clear) {
      await this.clear(), e = !0;
      break;
    } else s[n] = r.del;
    e || (i || (s = s.concat(fe(t.reg))), s.length && await this.remove(s));
  }
  t.reg.size && (await this.transaction("map", "readwrite", function(s) {
    for (const n of t.map) {
      const r = n[0], h = n[1];
      h.length && (e ? s.put(h, r) : s.get(r).onsuccess = function() {
        let o = this.result;
        var l;
        if (o && o.length) {
          const f = Math.max(o.length, h.length);
          for (let u = 0, c, a; u < f; u++) if ((a = h[u]) && a.length) {
            if ((c = o[u]) && c.length) for (l = 0; l < a.length; l++) c.push(a[l]);
            else o[u] = a;
            l = 1;
          }
        } else o = h, l = 1;
        l && s.put(o, r);
      });
    }
  }), await this.transaction("ctx", "readwrite", function(s) {
    for (const n of t.ctx) {
      const r = n[0], h = n[1];
      for (const o of h) {
        const l = o[0], f = o[1];
        f.length && (e ? s.put(f, r + ":" + l) : s.get(r + ":" + l).onsuccess = function() {
          let u = this.result;
          var c;
          if (u && u.length) {
            const a = Math.max(u.length, f.length);
            for (let d = 0, p, m; d < a; d++) if ((m = f[d]) && m.length) {
              if ((p = u[d]) && p.length) for (c = 0; c < m.length; c++) p.push(m[c]);
              else u[d] = m;
              c = 1;
            }
          } else u = f, c = 1;
          c && s.put(u, r + ":" + l);
        });
      }
    }
  }), t.store ? await this.transaction("reg", "readwrite", function(s) {
    for (const n of t.store) {
      const r = n[0], h = n[1];
      s.put(typeof h == "object" ? JSON.stringify(h) : 1, r);
    }
  }) : t.bypass || await this.transaction("reg", "readwrite", function(s) {
    for (const n of t.reg.keys()) s.put(1, n);
  }), t.tag && await this.transaction("tag", "readwrite", function(s) {
    for (const n of t.tag) {
      const r = n[0], h = n[1];
      h.length && (s.get(r).onsuccess = function() {
        let o = this.result;
        o = o && o.length ? o.concat(h) : h, s.put(o, r);
      });
    }
  }), t.map.clear(), t.ctx.clear(), t.tag && t.tag.clear(), t.store && t.store.clear(), t.document || t.reg.clear());
};
function Mt(t, e, i) {
  const s = t.value;
  let n, r = 0;
  for (let h = 0, o; h < s.length; h++) {
    if (o = i ? s : s[h]) {
      for (let l = 0, f, u; l < e.length; l++) if (u = e[l], f = o.indexOf(u), 0 <= f) if (n = 1, 1 < o.length) o.splice(f, 1);
      else {
        s[h] = [];
        break;
      }
      r += o.length;
    }
    if (i) break;
  }
  r ? n && t.update(s) : t.delete(), t.continue();
}
w.remove = function(t) {
  return typeof t != "object" && (t = [t]), Promise.all([this.transaction("map", "readwrite", function(e) {
    e.openCursor().onsuccess = function() {
      const i = this.result;
      i && Mt(i, t);
    };
  }), this.transaction("ctx", "readwrite", function(e) {
    e.openCursor().onsuccess = function() {
      const i = this.result;
      i && Mt(i, t);
    };
  }), this.transaction("tag", "readwrite", function(e) {
    e.openCursor().onsuccess = function() {
      const i = this.result;
      i && Mt(i, t, !0);
    };
  }), this.transaction("reg", "readwrite", function(e) {
    for (let i = 0; i < t.length; i++) e.delete(t[i]);
  })]);
};
function U(t, e) {
  return new Promise((i, s) => {
    t.onsuccess = t.oncomplete = function() {
      e && e(this.result), e = null, i(this.result);
    }, t.onerror = t.onblocked = s, t = null;
  });
}
const oe = $;
let _t = new oe();
self.onmessage = (t) => {
  switch (t.data.type) {
    case "clear":
      _t = new oe(), postMessage({ identifier: t.data.identifier });
      break;
    case "points":
      for (let i of t.data.points)
        _t.add(i.id, i.text);
      postMessage({ identifier: t.data.identifier });
      break;
    case "query":
      let e = _t.search(t.data.query, { limit: t.data.limit });
      postMessage({ identifier: t.data.identifier, result: e });
      break;
  }
};
var Se = {}, ze = /* @__PURE__ */ Object.freeze({
  __proto__: null,
  default: Se
});
