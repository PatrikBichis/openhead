// OpenHead cockpit: cards on a board, each showing a sensor or a control of one head.
// The page talks only to the local `openhead cockpit` server (bridge described in server.py).

const STORE_KEY = "openhead.cockpit.layout";
const DEFAULT_LAYOUT = [
  { id: "video", wide: true },
  { id: "say" },
  { id: "expression" },
  { id: "listen" },
  { id: "status" },
  { id: "mode" },
  { id: "pose" },
  { id: "imu" },
];
const COLORS = { x: "#e76f51", y: "#2a9d8f", z: "#1f3a5f", gold: "#ffc857", ink: "#1d1b22", line: "rgba(29,27,34,.12)" };

// The joke from the promo film first, then a few more to try the cues with.
const PRESETS = [
  ["Joke", "[happy] Why did the robot go on holiday? [pause] It needed to recharge! [laugh]"],
  ["Hello", "[happy] Hello! I'm OpenHead. [nod] What can I do for you?"],
  ["Meeting", "[serious] You have a meeting in five minutes. [nod] Don't forget your notes."],
  ["Curious", "[curious] Hmm, what are you building today? [tilt]"],
  ["Low battery", "[sad 0.6] Oh no, my battery is getting low. [sigh] Could you plug me in?"],
  ["Surprise", "[surprised] Wow! [pause 0.4] [laugh] I did not see that coming."],
];

// ---------------------------------------------------------------- link to the server

class Link {
  constructor() {
    this.key = new URLSearchParams(location.hash.slice(1)).get("k") || sessionStorage.getItem("openhead.k") || "";
    try { sessionStorage.setItem("openhead.k", this.key); } catch { /* private mode */ }
    this.hello = null;
    this.ids = 0;
    this.pending = new Map();
    this.topics = new Map(); // topic -> {opts, listeners:Set}
    this.onHello = () => {};
    this.connect();
  }

  connect() {
    const ws = new WebSocket(`ws://${location.host}/ws?k=${encodeURIComponent(this.key)}`);
    this.ws = ws;
    ws.onopen = () => {
      for (const [topic, t] of this.topics) this.send({ op: "subscribe", topic, ...t.opts });
    };
    ws.onmessage = (ev) => this.receive(JSON.parse(ev.data));
    ws.onclose = () => {
      for (const p of this.pending.values()) p.reject({ code: "not_connected", message: "cockpit server went away" });
      this.pending.clear();
      this.onHello(null);
      setTimeout(() => this.connect(), 2000);
    };
  }

  send(msg) {
    if (this.ws.readyState === WebSocket.OPEN) this.ws.send(JSON.stringify(msg));
  }

  receive(msg) {
    if (msg.op === "hello" || msg.op === "link") {
      this.hello = msg;
      this.onHello(msg);
    } else if (msg.op === "topic" || msg.op === "topic_error") {
      const t = this.topics.get(msg.topic);
      if (t) for (const fn of t.listeners) fn(msg.op === "topic" ? msg.data : null, msg.op === "topic_error" ? msg : null);
    } else if (msg.op === "result") {
      const p = this.pending.get(msg.id);
      if (!p) return;
      this.pending.delete(msg.id);
      msg.ok ? p.resolve(msg.result ?? {}) : p.reject(msg.error);
    }
  }

  request(msg) {
    const id = `p${++this.ids}`;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.send({ ...msg, id });
    });
  }

  command(type, params = {}) { return this.request({ op: "command", type, params }); }
  say(text) { return this.request({ op: "say", text }); }

  /** Listen to a topic; the first listener's options win. Returns a function that stops listening. */
  subscribe(topic, opts, fn) {
    let t = this.topics.get(topic);
    if (!t) {
      t = { opts, listeners: new Set() };
      this.topics.set(topic, t);
      this.send({ op: "subscribe", topic, ...opts });
    }
    t.listeners.add(fn);
    return () => {
      t.listeners.delete(fn);
      if (!t.listeners.size) {
        this.topics.delete(topic);
        this.send({ op: "unsubscribe", topic });
      }
    };
  }

  /** Change a topic's options (camera size and rate). */
  resubscribe(topic, opts) {
    const t = this.topics.get(topic);
    if (!t) return;
    t.opts = opts;
    this.send({ op: "subscribe", topic, ...opts });
  }

  has(capability) { return !!this.hello?.capabilities?.includes(capability); }
}

// ---------------------------------------------------------------- small helpers

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") node.className = v;
    else if (k === "text") node.textContent = v;
    else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
    else if (v !== false && v != null) node.setAttribute(k, v === true ? "" : v);
  }
  for (const c of children) if (c != null) node.append(c);
  return node;
}

function kv(rows) {
  const dl = el("dl", { class: "kv" });
  const cells = {};
  for (const [key, label] of rows) {
    const dd = el("dd", { text: "–" });
    cells[key] = dd;
    dl.append(el("dt", { text: label }), dd);
  }
  return { dl, set: (key, value) => { if (cells[key]) cells[key].textContent = value ?? "–"; } };
}

function fmt(n, digits = 2) { return typeof n === "number" ? n.toFixed(digits) : "–"; }

function segmented(options, onPick) {
  const box = el("div", { class: "segmented", role: "group" });
  const buttons = options.map(([value, label]) => {
    const b = el("button", { type: "button", "aria-pressed": "false", text: label, onclick: () => onPick(value) });
    box.append(b);
    return [value, b];
  });
  return { box, set: (v) => { for (const [value, b] of buttons) b.setAttribute("aria-pressed", String(value === v)); } };
}

function canvas(cls = "plot") {
  const c = el("canvas", { class: cls });
  const ctx = c.getContext("2d");
  const fit = () => {
    const r = c.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    if (c.width !== Math.round(r.width * dpr) || c.height !== Math.round(r.height * dpr)) {
      c.width = Math.round(r.width * dpr);
      c.height = Math.round(r.height * dpr);
    }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    return { w: r.width, h: r.height };
  };
  return { c, ctx, fit };
}

function errorText(e) { return e?.message ? `${e.code}: ${e.message}` : String(e); }

/** Status line under a control: shows the last error for a few seconds. */
function note() {
  const p = el("p", { class: "muted", role: "status" });
  let timer;
  return {
    p,
    show(text, ms = 4000) {
      p.textContent = text;
      clearTimeout(timer);
      if (ms) timer = setTimeout(() => (p.textContent = ""), ms);
    },
  };
}

function modeHint(link, wanted, what) {
  const p = el("p", { class: "muted" });
  const go = el("button", { type: "button", class: "btn ghost", text: `Switch to ${wanted}`,
    onclick: () => link.command("mode.set", { mode: wanted }).catch((e) => (p.textContent = errorText(e))) });
  const box = el("div", { class: "row" }, p, go);
  return { box, show(on) { box.hidden = !on; p.textContent = `${what} needs mode ${wanted}.`; } };
}

// ---------------------------------------------------------------- cards

const CARDS = {
  video: {
    title: "Camera",
    about: "Low-resolution video from the head's camera",
    needs: "camera.stream",
    mount(body, link) {
      const img = el("img", { alt: "What the head's camera sees" });
      const msg = el("p", { text: "Waiting for frames…" });
      const badge = el("span", { class: "badge", hidden: true });
      const view = el("div", { class: "video" }, msg, img, badge);
      img.hidden = true;
      const size = el("select", { "aria-label": "Frame size" },
        ...[160, 320, 480, 640].map((v) => el("option", { value: v, text: `${v} px`, selected: v === 320 })));
      const rate = el("select", { "aria-label": "Frames per second" },
        ...[1, 2, 4, 8, 10].map((v) => el("option", { value: v, text: `${v} fps`, selected: v === 4 })));
      const opts = () => ({ rate_hz: Number(rate.value), max_px: Number(size.value) });
      size.onchange = rate.onchange = () => link.resubscribe("camera", opts());
      body.append(view, el("div", { class: "row" }, el("label", { text: "Size" }), size, el("label", { text: "Rate" }), rate),
        el("p", { class: "muted", text: "The phone shows “Camera shared” while you watch. Frames are not stored." }));
      let last = 0;
      let mode = "idle";
      const stopStatus = link.subscribe("status", { rate_hz: 1 }, (s) => {
        if (!s) return;
        mode = s.mode;
        if (mode === "idle") {
          img.hidden = true;
          badge.hidden = true;
          msg.hidden = false;
          msg.textContent = "The camera runs in mode capture (front) or sensing (back). Pick one in the Mode card.";
        }
      });
      const stop = link.subscribe("camera", opts(), (f, err) => {
        if (err) { msg.hidden = false; msg.textContent = errorText(err); return; }
        img.src = `data:image/jpeg;base64,${f.jpeg}`;
        img.hidden = false;
        msg.hidden = true;
        const now = performance.now();
        const fps = last ? 1000 / (now - last) : 0;
        last = now;
        badge.hidden = false;
        badge.textContent = `${f.source} · ${f.width}×${f.height}${fps ? ` · ${fps.toFixed(1)} fps` : ""}`;
      });
      return () => { stop(); stopStatus(); };
    },
  },

  mode: {
    title: "Mode",
    about: "Idle, capture (front camera) or sensing (ARKit)",
    mount(body, link) {
      const n = note();
      const seg = segmented([["idle", "Idle"], ["capture", "Capture"], ["sensing", "Sensing"]], (mode) =>
        link.command("mode.set", { mode }).then(() => seg.set(mode)).catch((e) => n.show(errorText(e))));
      body.append(seg.box, el("p", { class: "muted", text: "Capture: front camera, several faces. Sensing: ARKit world tracking (back camera) and one face." }), n.p);
      return link.subscribe("status", { rate_hz: 1 }, (s) => s && seg.set(s.mode));
    },
  },

  status: {
    title: "Status",
    about: "Battery, temperature, view, clients",
    mount(body, link) {
      const t = kv([["device", "Device"], ["battery", "Battery"], ["thermal", "Thermal"], ["view", "On screen"],
        ["theme", "Theme · emotion"], ["clients", "Clients"], ["viewers", "Watching camera"], ["rtt", "Round trip"], ["uptime", "Uptime"]]);
      body.append(t.dl);
      const d = link.hello?.device;
      t.set("device", d ? `${d.name} (${d.model || d.platform})` : link.hello?.head);
      return link.subscribe("status", { rate_hz: 1 }, (s) => {
        if (!s) return;
        t.set("battery", s.battery_level != null ? `${Math.round(s.battery_level * 100)} %${s.charging ? " ⚡" : ""}` : (s.charging ? "charging" : "–"));
        t.set("thermal", s.thermal_state);
        t.set("view", s.overlay && s.overlay !== "none" ? `${s.view} + ${s.overlay}` : s.view);
        t.set("theme", `${s.theme} · ${s.emotion}`);
        t.set("clients", s.clients);
        t.set("viewers", s.camera_viewers ?? "–");
        t.set("rtt", s.rtt_ms != null ? `${s.rtt_ms} ms` : "–");
        t.set("uptime", s.uptime_s != null ? `${Math.floor(s.uptime_s / 60)} min` : "–");
      });
    },
  },

  say: {
    title: "Speak",
    about: "Text the head says, with cues like [happy] or [laugh]",
    needs: "speech",
    mount(body, link) {
      const text = el("textarea", { "aria-label": "What the head should say", placeholder: "[happy] Hello! [laugh]" });
      text.value = PRESETS[0][1];
      const chips = el("div", { class: "chips", "aria-label": "Examples" },
        ...PRESETS.map(([label, line]) => el("button", { type: "button", class: "chip", text: label, title: line,
          onclick: () => { text.value = line; text.focus(); } })));
      const n = note();
      const sayBtn = el("button", { type: "button", class: "btn coral", text: "Say",
        onclick: () => link.say(text.value).then((r) => n.show(`Speaking (${r.utterance_id})`)).catch((e) => n.show(errorText(e))) });
      const stopBtn = el("button", { type: "button", class: "btn ghost", text: "Stop",
        onclick: () => link.command("speech.stop").catch((e) => n.show(errorText(e))) });
      text.addEventListener("keydown", (e) => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) sayBtn.click(); });
      const feed = el("ul", { class: "feed", "aria-live": "polite" });
      body.append(el("p", { class: "muted", text: "Cues: [happy] [sad 0.5] [serious] [laugh] [sigh] [pause 0.5] [nod] [shake] [tilt]. Ctrl+Enter says it." }),
        chips, text, el("div", { class: "row" }, sayBtn, stopBtn), n.p, feed);
      return link.subscribe("speech", {}, (m) => {
        if (!m || !["say_start", "cue", "say_end"].includes(m.event)) return;
        const line = m.event === "cue" ? `[${m.cue}]` : m.event === "say_end" ? (m.interrupted ? "interrupted" : "done") : "speaking…";
        feed.prepend(el("li", { text: `${m.utterance_id}: ${line}` }));
        while (feed.children.length > 30) feed.lastChild.remove();
      });
    },
  },

  listen: {
    title: "Listen",
    about: "Speech to text with the head's microphone",
    needs: "speech",
    mount(body, link) {
      const n = note();
      const locale = el("select", { "aria-label": "Language" },
        ...["en-US", "en-GB", "sv-SE", "de-DE", "fr-FR", "es-ES"].map((v) => el("option", { value: v, text: v })));
      let on = false;
      const btn = el("button", { type: "button", class: "btn", text: "Start listening" });
      const setOn = (v) => { on = v; btn.textContent = v ? "Stop listening" : "Start listening"; btn.classList.toggle("coral", v); };
      btn.onclick = () => link.command("speech.listen", { on: !on, locale: locale.value })
        .then((r) => { setOn(!!r.listening); if (r.listening) n.show(r.on_device ? "On the device" : "With Apple's speech recognition", 0); else n.show(""); })
        .catch((e) => n.show(errorText(e)));
      const partial = el("li", { class: "partial", hidden: true });
      const feed = el("ul", { class: "feed", "aria-live": "polite" }, partial);
      body.append(el("div", { class: "row" }, btn, locale), n.p, feed);
      const stop = link.subscribe("speech", {}, (m) => {
        if (!m) return;
        if (m.event === "partial") { partial.hidden = false; partial.textContent = `… ${m.text}`; }
        if (m.event === "heard") {
          partial.hidden = true;
          const conf = m.confidence != null ? ` (${m.confidence.toFixed(2)})` : "";
          partial.after(el("li", { text: `${m.text}${conf}` }));
          while (feed.children.length > 31) feed.lastChild.remove();
        }
      });
      return () => { stop(); if (on) link.command("speech.listen", { on: false }).catch(() => {}); };
    },
  },

  expression: {
    title: "Expression and theme",
    about: "Change theme and emotion",
    mount(body, link) {
      const n = note();
      const theme = el("select", { "aria-label": "Theme" });
      const chips = el("div", { class: "chips", "aria-label": "Emotions" });
      const intensity = el("input", { type: "range", min: 0.1, max: 1, step: 0.05, value: 1, "aria-label": "Intensity" });
      const iv = el("span", { class: "mono", text: "1.00" });
      intensity.oninput = () => (iv.textContent = Number(intensity.value).toFixed(2));
      let themes = [];
      let current = "";
      const drawChips = () => {
        const t = themes.find((x) => x.name === theme.value);
        chips.replaceChildren(...(t ? [...t.expressions, ...(t.extras || [])] : []).map((name) =>
          el("button", { type: "button", class: "chip", text: name.replaceAll("_", " "), "aria-pressed": String(name === current),
            onclick: () => link.command("face.set_emotion", { name, intensity: Number(intensity.value) })
              .then(() => { current = name; drawChips(); }).catch((e) => n.show(errorText(e))) })));
      };
      theme.onchange = () => link.command("face.set_theme", { name: theme.value }).then(drawChips).catch((e) => n.show(errorText(e)));
      const load = () => link.command("face.list").then((r) => {
        themes = r.themes;
        theme.replaceChildren(...themes.map((t) => el("option", { value: t.name, text: t.title || t.name, selected: t.name === r.active })));
        drawChips();
      }).catch((e) => n.show(errorText(e)));
      load();
      body.append(el("div", { class: "row" }, el("label", { text: "Theme" }), theme),
        chips, el("div", { class: "row" }, el("label", { text: "Intensity" }), intensity, iv),
        el("div", { class: "row" },
          el("button", { type: "button", class: "btn ghost", text: "Blink", onclick: () => link.command("face.blink").catch((e) => n.show(errorText(e))) }),
          el("button", { type: "button", class: "btn ghost", text: "Show face", onclick: () => link.command("display.show", { content: "face" }).catch((e) => n.show(errorText(e))) })),
        n.p);
      return link.subscribe("status", { rate_hz: 1 }, (s) => {
        if (!s) return;
        if (s.emotion !== current) { current = s.emotion; drawChips(); }
        if (s.theme && theme.value !== s.theme && themes.length) { theme.value = s.theme; drawChips(); }
      });
    },
  },

  pose: {
    title: "Position (ARKit)",
    about: "Where the head is and which way it faces",
    needs: "pose",
    mount(body, link) {
      const plot = canvas("plot square");
      const t = kv([["pos", "Position x, y, z"], ["yaw", "Heading (yaw)"], ["state", "Tracking"]]);
      const hint = modeHint(link, "sensing", "Position");
      body.append(hint.box, plot.c, t.dl);
      const trail = [];
      const draw = () => {
        const { w, h } = plot.fit();
        const { ctx } = plot;
        ctx.clearRect(0, 0, w, h);
        const scale = Math.min(w, h) / 4; // 4 m across
        ctx.strokeStyle = COLORS.line;
        ctx.lineWidth = 1;
        for (let m = -4; m <= 4; m += 0.5) {
          ctx.beginPath(); ctx.moveTo(w / 2 + m * scale, 0); ctx.lineTo(w / 2 + m * scale, h); ctx.stroke();
          ctx.beginPath(); ctx.moveTo(0, h / 2 + m * scale); ctx.lineTo(w, h / 2 + m * scale); ctx.stroke();
        }
        if (!trail.length) return;
        ctx.strokeStyle = COLORS.gold;
        ctx.lineWidth = 3;
        ctx.lineJoin = "round";
        ctx.beginPath();
        trail.forEach(([x, z], i) => (i ? ctx.lineTo : ctx.moveTo).call(ctx, w / 2 + x * scale, h / 2 + z * scale));
        ctx.stroke();
        const [x, z, yaw] = trail[trail.length - 1];
        ctx.save();
        ctx.translate(w / 2 + x * scale, h / 2 + z * scale);
        ctx.rotate(-yaw);
        ctx.fillStyle = COLORS.z;
        ctx.beginPath(); ctx.moveTo(0, -12); ctx.lineTo(8, 8); ctx.lineTo(0, 4); ctx.lineTo(-8, 8); ctx.closePath(); ctx.fill();
        ctx.restore();
      };
      draw();
      const stopStatus = link.subscribe("status", { rate_hz: 1 }, (s) => s && hint.show(s.mode !== "sensing"));
      const stop = link.subscribe("pose", { rate_hz: 10 }, (p) => {
        if (!p) return;
        const [qx, qy, qz, qw] = p.q;
        const yaw = Math.atan2(2 * (qw * qy + qx * qz), 1 - 2 * (qy * qy + qx * qx));
        trail.push([p.position[0], p.position[2], yaw]);
        if (trail.length > 600) trail.shift();
        t.set("pos", p.position.map((v) => v.toFixed(2)).join(", ") + " m");
        t.set("yaw", `${Math.round((yaw * 180) / Math.PI)}°`);
        t.set("state", p.tracking_reason ? `${p.tracking_state} (${p.tracking_reason})` : p.tracking_state);
        draw();
      });
      return () => { stop(); stopStatus(); };
    },
  },

  imu: {
    title: "Motion (IMU)",
    about: "Gyroscope and accelerometer, last 10 s",
    needs: "imu",
    mount(body, link) {
      const gyro = canvas();
      const accel = canvas();
      const legend = el("div", { class: "legend" }, ...["x", "y", "z"].map((a) => {
        const i = el("i"); i.style.background = COLORS[a]; return el("span", {}, i, a);
      }));
      body.append(el("label", { text: "Gyroscope (rad/s)" }), gyro.c, el("label", { text: "Accelerometer (g)" }), accel.c, legend);
      const g = [];
      const a = [];
      const plot = ({ fit, ctx }, data, range) => {
        const { w, h } = fit();
        ctx.clearRect(0, 0, w, h);
        ctx.strokeStyle = COLORS.line;
        ctx.beginPath(); ctx.moveTo(0, h / 2); ctx.lineTo(w, h / 2); ctx.stroke();
        ["x", "y", "z"].forEach((axis, k) => {
          ctx.strokeStyle = COLORS[axis];
          ctx.lineWidth = 2;
          ctx.beginPath();
          data.forEach((v, i) => {
            const px = (i / 199) * w;
            const py = h / 2 - (Math.max(-range, Math.min(range, v[k])) / range) * (h / 2 - 4);
            i ? ctx.lineTo(px, py) : ctx.moveTo(px, py);
          });
          ctx.stroke();
        });
      };
      let pending = false;
      return link.subscribe("imu", { rate_hz: 20 }, (s) => {
        if (!s) return;
        g.push(s.gyro); a.push(s.accel);
        if (g.length > 200) { g.shift(); a.shift(); }
        if (!pending) {
          pending = true;
          requestAnimationFrame(() => { pending = false; plot(gyro, g, 3); plot(accel, a, 1.5); });
        }
      });
    },
  },

  env: {
    title: "Compass and air",
    about: "Heading, air pressure, magnetic field",
    needs: "env",
    mount(body, link) {
      const dial = canvas("plot square");
      const t = kv([["heading", "Heading"], ["pressure", "Air pressure"], ["alt", "Relative altitude"], ["mag", "Magnetic field (µT)"]]);
      body.append(dial.c, t.dl);
      const draw = (deg) => {
        const { w, h } = dial.fit();
        const { ctx } = dial;
        const r = Math.min(w, h) / 2 - 18;
        if (r <= 0) return; // not laid out yet
        ctx.clearRect(0, 0, w, h);
        ctx.save();
        ctx.translate(w / 2, h / 2);
        ctx.strokeStyle = COLORS.line; ctx.lineWidth = 2;
        ctx.beginPath(); ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.stroke();
        ctx.fillStyle = "#4a4652"; ctx.font = "600 13px system-ui"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
        ["N", "E", "S", "W"].forEach((c, i) => {
          const a = ((i * 90 - deg) * Math.PI) / 180;
          ctx.fillStyle = c === "N" ? COLORS.x : "#4a4652";
          ctx.fillText(c, Math.sin(a) * (r + 10 - 22), -Math.cos(a) * (r + 10 - 22));
        });
        ctx.fillStyle = COLORS.z;
        ctx.beginPath(); ctx.moveTo(0, -r + 6); ctx.lineTo(7, 0); ctx.lineTo(-7, 0); ctx.closePath(); ctx.fill();
        ctx.restore();
      };
      requestAnimationFrame(() => draw(0));
      return link.subscribe("env", { rate_hz: 2 }, (e) => {
        if (!e) return;
        if (e.heading_deg != null) { draw(e.heading_deg); t.set("heading", `${Math.round(e.heading_deg)}° ${e.heading_ref || ""}`); }
        t.set("pressure", e.pressure_kpa != null ? `${(e.pressure_kpa * 10).toFixed(1)} hPa` : null);
        t.set("alt", e.relative_altitude_m != null ? `${e.relative_altitude_m.toFixed(2)} m` : null);
        t.set("mag", e.magnetic_field_ut ? e.magnetic_field_ut.map((v) => v.toFixed(1)).join(", ") : null);
      });
    },
  },

  gps: {
    title: "Location (GPS)",
    about: "Latitude, longitude, accuracy; the track stays on this page",
    needs: "gps",
    mount(body, link) {
      const t = kv([["pos", "Lat, lon"], ["alt", "Altitude"], ["acc", "Accuracy"], ["speed", "Speed · course"]]);
      const plot = canvas();
      body.append(t.dl, plot.c, el("p", { class: "muted", text: "Track relative to the first fix. Nothing leaves this computer." }));
      const track = [];
      return link.subscribe("gps", { rate_hz: 1 }, (g) => {
        if (!g) return;
        t.set("pos", `${g.lat.toFixed(6)}, ${g.lon.toFixed(6)}`);
        t.set("alt", g.alt_m != null ? `${g.alt_m.toFixed(1)} m` : null);
        t.set("acc", g.h_accuracy_m != null ? `± ${g.h_accuracy_m.toFixed(1)} m` : null);
        t.set("speed", g.speed_m_s != null ? `${g.speed_m_s.toFixed(2)} m/s · ${Math.round(g.course_deg ?? 0)}°` : null);
        track.push([g.lat, g.lon]);
        if (track.length > 900) track.shift();
        const { w, h } = plot.fit();
        const { ctx } = plot;
        const [lat0, lon0] = track[0];
        const pts = track.map(([la, lo]) => [(lo - lon0) * 111320 * Math.cos((lat0 * Math.PI) / 180), (la - lat0) * 111320]);
        const span = Math.max(20, ...pts.flat().map(Math.abs)) * 2.2;
        ctx.clearRect(0, 0, w, h);
        ctx.strokeStyle = COLORS.y; ctx.lineWidth = 3; ctx.lineJoin = "round";
        ctx.beginPath();
        pts.forEach(([x, y], i) => (i ? ctx.lineTo : ctx.moveTo).call(ctx, w / 2 + (x / span) * h, h / 2 - (y / span) * h));
        ctx.stroke();
      });
    },
  },

  faces: {
    title: "Faces",
    about: "People the camera sees (no identification)",
    needs: "faces",
    mount(body, link) {
      const hint = el("p", { class: "muted", text: "Faces are found in mode capture or sensing. They are not recognised, only located." });
      const tbody = el("tbody");
      body.append(hint, el("table", {}, el("thead", {}, el("tr", {}, ...["Id", "Bearing", "Elevation", "Size", "Distance"].map((h) => el("th", { text: h })))), tbody));
      return link.subscribe("faces", { rate_hz: 4 }, (m) => {
        if (!m) return;
        tbody.replaceChildren(...m.faces.map((f) => el("tr", {},
          el("td", { text: `${f.id}${f.locked ? " 🔒" : ""}` }), el("td", { text: `${fmt(f.bearing, 1)}°` }),
          el("td", { text: `${fmt(f.elevation, 1)}°` }), el("td", { text: fmt(f.size, 2) }),
          el("td", { text: f.distance_m != null ? `${f.distance_m.toFixed(2)} m` : "–" }))));
        if (!m.faces.length) tbody.append(el("tr", {}, el("td", { colspan: 5, class: "muted", text: "Nobody in view" })));
      });
    },
  },

  log: {
    title: "Log",
    about: "What the head reports",
    needs: "log",
    mount(body, link) {
      const levels = ["debug", "info", "notice", "warning", "error", "fault"];
      const floor = el("select", { "aria-label": "Lowest level" },
        ...["debug", "info", "warning"].map((v) => el("option", { value: v, text: `${v} and up`, selected: v === "info" })));
      const feed = el("ul", { class: "feed mono" });
      body.append(el("div", { class: "row" }, el("label", { text: "Show" }), floor), feed);
      return link.subscribe("log", {}, (e) => {
        if (!e) return;
        // Every received command is logged at info; that is noise unless you ask for debug.
        const level = e.subsystem === "link" && e.message.startsWith("recv ") ? "debug" : e.level;
        if (levels.indexOf(level) < levels.indexOf(floor.value)) return;
        feed.prepend(el("li", {}, el("span", { class: `lvl ${e.level}`, text: e.level }), ` ${e.subsystem}: ${e.message}`));
        while (feed.children.length > 100) feed.lastChild.remove();
      });
    },
  },

  lidar: {
    title: "LiDAR depth (Pro)",
    about: "Distance and room mesh on Pro models, optional",
    mount(body, link) {
      if (!link.has("lidar")) {
        body.closest(".card").classList.add("disabled-card");
        body.append(el("p", { class: "muted", text: "Pro models only, and optional: this phone has no LiDAR. Everything else works without it." }));
        return () => {};
      }
      const hint = modeHint(link, "sensing", "Depth");
      const big = el("div", { class: "big", text: "–" });
      const plot = canvas("plot square");
      body.append(hint.box, el("label", { text: "Distance at the centre of the back camera" }), big);
      const anchors = new Map();
      let stopMesh = () => {};
      if (link.has("scene_mesh")) {
        body.append(el("label", { text: "Room mesh from above" }), plot.c);
        stopMesh = link.subscribe("mesh", { rate_hz: 1 }, (m) => {
          if (!m) return;
          for (const id of m.removed) anchors.delete(id);
          for (const a of m.anchors) anchors.set(a.id, a);
          drawMesh();
        });
      }
      function drawMesh() {
        const { w, h } = plot.fit();
        const { ctx } = plot;
        ctx.clearRect(0, 0, w, h);
        const scale = Math.min(w, h) / 8;
        ctx.strokeStyle = COLORS.y; ctx.lineWidth = 1;
        for (const a of anchors.values()) {
          const v = new Float32Array(Uint8Array.from(atob(a.vertices), (c) => c.charCodeAt(0)).buffer);
          const f = new Uint32Array(Uint8Array.from(atob(a.faces), (c) => c.charCodeAt(0)).buffer);
          const [qx, qy, qz, qw] = a.q;
          const rot = (x, y, z) => { // v' = v + w t + q × t with t = 2 q × v; then to the anchor; (x, z) from above
            const tx = 2 * (qy * z - qz * y), ty = 2 * (qz * x - qx * z), tz = 2 * (qx * y - qy * x);
            return [x + qw * tx + (qy * tz - qz * ty) + a.position[0], z + qw * tz + (qx * ty - qy * tx) + a.position[2]];
          };
          for (let i = 0; i < f.length; i += 3) {
            ctx.beginPath();
            for (let k = 0; k < 3; k++) {
              const j = f[i + k] * 3;
              const [x, z] = rot(v[j], v[j + 1], v[j + 2]);
              (k ? ctx.lineTo : ctx.moveTo).call(ctx, w / 2 + x * scale, h / 2 + z * scale);
            }
            ctx.closePath(); ctx.stroke();
          }
        }
      }
      let sensing = false;
      const stopStatus = link.subscribe("status", { rate_hz: 1 }, (s) => { if (s) { sensing = s.mode === "sensing"; hint.show(!sensing); } });
      const timer = setInterval(() => {
        if (!sensing) return;
        link.command("depth.sample", { points: [{ x: 0.5, y: 0.5 }] })
          .then((r) => (big.textContent = r.depths_m[0] != null ? `${r.depths_m[0].toFixed(2)} m` : "no reading"))
          .catch((e) => (big.textContent = errorText(e)));
      }, 1000);
      return () => { clearInterval(timer); stopMesh(); stopStatus(); };
    },
  },

  light: {
    title: "Camera light",
    about: "Torch with brightness, coming in a later release",
    mount(body) {
      body.closest(".card").classList.add("disabled-card");
      const slider = el("input", { type: "range", min: 0, max: 1, step: 0.05, value: 0, disabled: true, "aria-label": "Light brightness" });
      body.append(el("div", { class: "row" }, el("button", { type: "button", class: "btn", text: "Light on", disabled: true }), slider),
        el("p", { class: "muted", text: "Coming in a later release: turn on the phone's light and set its brightness." }));
      return () => {};
    },
  },
};

// ---------------------------------------------------------------- board and layout

function loadLayout() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORE_KEY) || "null");
    if (saved?.v === 1 && Array.isArray(saved.cards)) return saved.cards.filter((c) => CARDS[c.id]);
  } catch { /* storage blocked or bad JSON: use the default */ }
  return DEFAULT_LAYOUT.map((c) => ({ ...c }));
}

function saveLayout(cards) {
  try { localStorage.setItem(STORE_KEY, JSON.stringify({ v: 1, cards })); } catch { /* not saved, still works */ }
}

class Board {
  constructor(link) {
    this.link = link;
    this.root = document.querySelector("#board");
    this.layout = loadLayout();
    this.mounted = new Map(); // id -> {node, cleanup}
    this.dragging = null;
  }

  render() {
    for (const { cleanup } of this.mounted.values()) cleanup?.();
    this.mounted.clear();
    this.root.replaceChildren();
    for (const entry of this.layout) this.root.append(this.mount(entry));
    this.menu();
  }

  mount(entry) {
    const def = CARDS[entry.id];
    const node = document.querySelector("#card-template").content.firstElementChild.cloneNode(true);
    node.dataset.id = entry.id;
    node.classList.toggle("wide", !!entry.wide);
    node.querySelector("h2").textContent = def.title;
    node.setAttribute("aria-label", def.title);
    const body = node.querySelector(".card-body");
    const head = node.querySelector(".card-head");
    node.querySelector(".close").onclick = () => this.remove(entry.id);
    node.querySelector(".size").onclick = () => {
      entry.wide = !entry.wide;
      node.classList.toggle("wide", entry.wide);
      saveLayout(this.layout);
    };
    head.addEventListener("dragstart", (e) => {
      this.dragging = entry.id;
      node.classList.add("dragging");
      e.dataTransfer.effectAllowed = "move";
      e.dataTransfer.setData("text/plain", entry.id);
    });
    head.addEventListener("dragend", () => {
      this.dragging = null;
      node.classList.remove("dragging");
      this.root.querySelectorAll(".drop-before, .drop-after").forEach((n) => n.classList.remove("drop-before", "drop-after"));
    });
    node.addEventListener("dragover", (e) => {
      if (!this.dragging || this.dragging === entry.id) return;
      e.preventDefault();
      const after = this.after(node, e);
      node.classList.toggle("drop-after", after);
      node.classList.toggle("drop-before", !after);
    });
    node.addEventListener("dragleave", () => node.classList.remove("drop-before", "drop-after"));
    node.addEventListener("drop", (e) => {
      e.preventDefault();
      if (this.dragging && this.dragging !== entry.id) this.move(this.dragging, entry.id, this.after(node, e));
    });
    head.addEventListener("keydown", (e) => {
      if (!e.altKey || !["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"].includes(e.key)) return;
      e.preventDefault();
      const i = this.layout.indexOf(entry);
      const j = i + (e.key === "ArrowLeft" || e.key === "ArrowUp" ? -1 : 1);
      if (j < 0 || j >= this.layout.length) return;
      this.layout.splice(j, 0, ...this.layout.splice(i, 1));
      saveLayout(this.layout);
      const ref = this.root.children[j < i ? j : j + 1] ?? null;
      this.root.insertBefore(node, ref);
      head.focus();
    });
    let cleanup = () => {};
    if (def.needs && this.link.hello && !this.link.has(def.needs)) {
      node.classList.add("disabled-card");
      body.append(el("p", { class: "muted", text: `This head does not offer “${def.needs}”. Update the OpenHead app on the phone.` }));
    } else {
      try { cleanup = def.mount(body, this.link) || cleanup; } catch (err) { body.append(el("p", { class: "muted", text: String(err) })); }
    }
    this.mounted.set(entry.id, { node, cleanup });
    return node;
  }

  after(node, e) {
    const r = node.getBoundingClientRect();
    return e.clientX > r.left + r.width / 2;
  }

  move(id, targetId, after) {
    const from = this.layout.findIndex((c) => c.id === id);
    const [entry] = this.layout.splice(from, 1);
    let to = this.layout.findIndex((c) => c.id === targetId) + (after ? 1 : 0);
    this.layout.splice(to, 0, entry);
    saveLayout(this.layout);
    const node = this.mounted.get(id).node;
    const target = this.mounted.get(targetId).node;
    target.classList.remove("drop-before", "drop-after");
    this.root.insertBefore(node, after ? target.nextSibling : target);
  }

  remove(id) {
    this.layout = this.layout.filter((c) => c.id !== id);
    saveLayout(this.layout);
    const m = this.mounted.get(id);
    m?.cleanup?.();
    m?.node.remove();
    this.mounted.delete(id);
    this.menu();
  }

  add(id) {
    const entry = { id };
    this.layout.push(entry);
    saveLayout(this.layout);
    const node = this.mount(entry);
    this.root.append(node);
    this.menu();
    node.scrollIntoView({ behavior: "smooth", block: "nearest" });
    node.querySelector(".card-head").focus({ preventScroll: true });
  }

  reset() {
    try { localStorage.removeItem(STORE_KEY); } catch { /* ignore */ }
    this.layout = DEFAULT_LAYOUT.map((c) => ({ ...c }));
    this.render();
  }

  menu() {
    const box = document.querySelector("#add-menu");
    const free = Object.entries(CARDS).filter(([id]) => !this.layout.some((c) => c.id === id));
    box.replaceChildren(...free.map(([id, def]) => el("button", { type: "button", role: "menuitem",
      onclick: () => { closeMenu(); this.add(id); } }, def.title, el("small", { text: def.about }))));
    if (!free.length) box.append(el("p", { class: "empty", text: "Every card is on the board." }));
  }
}

// ---------------------------------------------------------------- start

const link = new Link();
const board = new Board(link);
const addBtn = document.querySelector("#add-card");
const addMenu = document.querySelector("#add-menu");
function closeMenu() { addMenu.hidden = true; addBtn.setAttribute("aria-expanded", "false"); }
addBtn.onclick = () => {
  addMenu.hidden = !addMenu.hidden;
  addBtn.setAttribute("aria-expanded", String(!addMenu.hidden));
  if (!addMenu.hidden) addMenu.querySelector("button")?.focus();
};
document.addEventListener("click", (e) => { if (!e.target.closest(".add")) closeMenu(); });
document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeMenu(); });
document.querySelector("#reset-layout").onclick = () => board.reset();

const banner = document.querySelector("#banner");
let started = false;
let lastCaps = "";
link.onHello = (h) => {
  const chip = document.querySelector("#device");
  const name = document.querySelector("#device-name");
  if (!h) {
    chip.dataset.state = "off";
    name.textContent = "Cockpit server stopped";
    banner.hidden = false;
    banner.textContent = "Lost the cockpit server. Is `openhead cockpit` still running? Retrying…";
    return;
  }
  const d = h.device;
  chip.dataset.state = h.connected ? "on" : "off";
  name.textContent = d ? `${d.name} · ${h.head}${h.connected ? "" : " (reconnecting)"}` : h.head;
  banner.hidden = h.connected;
  banner.textContent = h.connected ? "" : `The head at ${h.head} is not reachable. The cockpit reconnects when it comes back.`;
  const caps = (h.capabilities || []).join(",");
  if (!started || caps !== lastCaps) {
    started = true;
    lastCaps = caps;
    board.render();
  }
};
window.cockpit = { link, board }; // for tests and the console
