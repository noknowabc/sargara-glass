/**
 * SARGARA — zero-dependency static file server with a private access gate.
 *
 * Serves the repository root as the website root. Requires no npm packages,
 * so hosting platforms can install and start it instantly:
 *
 *     npm start          # or: node server.mjs
 *
 * Respects PORT / HOST environment variables (cloud platforms set PORT).
 *
 * ---------------------------------------------------------------------------
 * Private access gate
 * ---------------------------------------------------------------------------
 * While `access.on` exists (or ACCESS=true is set) every visitor is shown
 * gate.html and must enter the access phrase before any real page is served.
 * The unlock is remembered in a signed, HttpOnly cookie (default 30 days).
 *
 *   ACCESS_PASSWORD   one access phrase            (default: sargara2026)
 *   ACCESS_PASSWORDS  several, comma separated     (optional)
 *   ACCESS_DAYS       cookie lifetime in days      (default: 30)
 *   ACCESS_SECRET     cookie signing secret        (default: derived)
 *   PUBLIC=true       force the gate open          (emergency bypass)
 *
 * Visitors can sign out again at any time:  /?signout=1
 * Delete `access.on` (or set PUBLIC=true) and redeploy to reopen the site.
 */

import { createHash, createHmac, timingSafeEqual } from "node:crypto";
import { createReadStream, existsSync } from "node:fs";
import { readFile, stat } from "node:fs/promises";
import { createServer } from "node:http";
import { extname, join, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";
import { createGzip } from "node:zlib";

const ROOT = resolve(fileURLToPath(new URL(".", import.meta.url)));
const PORT = Number(process.env.PORT) || 3000;
const HOST = process.env.HOST || "0.0.0.0";

/** Directories that must never be served publicly. */
const DENIED_PREFIXES = ["/tools", "/data", "/.git"];

/** Individual files that must never be served publicly. */
const DENIED_FILES = [
  "/server.mjs",
  "/package.json",
  "/package-lock.json",
  "/readme.md",
  "/access.on",
  "/maintenance.on",
];

/**
 * Maintenance mode. While the flag file exists (or MAINTENANCE=true is set on
 * the platform) every request answers with maintenance.html and HTTP 503, which
 * keeps search engines from dropping the site. It outranks the access gate and
 * is meant as an emergency switch: delete the file and redeploy to reopen.
 */
const MAINTENANCE_FLAG = join(ROOT, "maintenance.on");
const MAINTENANCE_PAGE = join(ROOT, "maintenance.html");
const maintenanceEnabled = () => process.env.MAINTENANCE === "true" || existsSync(MAINTENANCE_FLAG);

/* ------------------------------------------------------------ access gate */

const GATE_FLAG = join(ROOT, "access.on");
const GATE_PAGE = join(ROOT, "gate.html");
const GATE_COOKIE = "sg_access";
const GATE_DEFAULT_PASSWORD = "sargara2026";
const GATE_ATTEMPT_WINDOW = 10 * 60 * 1000;
const GATE_ATTEMPT_MAX = 6;
const GATE_ATTEMPT_BLOCK = 10 * 60 * 1000;

const GATE_SESSION_DAYS = Math.min(365, Math.max(1, Number(process.env.ACCESS_DAYS) || 30));

const GATE_PASSWORDS = (() => {
  const configured = [process.env.ACCESS_PASSWORD, process.env.ACCESS_PASSWORDS]
    .filter(Boolean)
    .join(",")
    .split(",")
    .map((value) => value.trim())
    .filter(Boolean);
  return (configured.length ? configured : [GATE_DEFAULT_PASSWORD]).map((value) => value.toLowerCase());
})();

const GATE_FROM_ENV = Boolean(process.env.ACCESS_PASSWORD || process.env.ACCESS_PASSWORDS);

const GATE_SECRET =
  process.env.ACCESS_SECRET ||
  createHash("sha256").update(`sargara-gate:${GATE_PASSWORDS.join("|")}`).digest("hex");

const gateEnabled = () =>
  process.env.PUBLIC !== "true" && (process.env.ACCESS === "true" || existsSync(GATE_FLAG));

/** Files the gate page itself needs while every other path stays closed. */
const GATE_PUBLIC_PATHS = new Set([
  "/gate.html",
  "/assets/img/logo-mark.svg",
  "/assets/img/favicon-32.png",
  "/assets/img/apple-touch-icon.png",
]);

/** ?e=… code → state rendered inside gate.html */
const GATE_STATES = { bad: "bad", slow: "throttled", out: "signedout" };

const attempts = new Map();

function clientKey(req) {
  const forwarded = String(req.headers["x-forwarded-for"] || "").split(",")[0].trim();
  return forwarded || req.socket.remoteAddress || "unknown";
}

function throttledFor(req) {
  const entry = attempts.get(clientKey(req));
  const now = Date.now();
  if (entry && entry.blockedUntil > now) return Math.ceil((entry.blockedUntil - now) / 1000);
  return 0;
}

function noteFailure(req) {
  const key = clientKey(req);
  const now = Date.now();
  const entry = attempts.get(key) || { count: 0, first: now, blockedUntil: 0 };
  if (now - entry.first > GATE_ATTEMPT_WINDOW) {
    entry.count = 0;
    entry.first = now;
  }
  entry.count += 1;
  if (entry.count >= GATE_ATTEMPT_MAX) {
    entry.blockedUntil = now + GATE_ATTEMPT_BLOCK;
    entry.count = 0;
    entry.first = now;
  }
  attempts.set(key, entry);
}

const clearFailures = (req) => attempts.delete(clientKey(req));

const sweep = setInterval(() => {
  const now = Date.now();
  for (const [key, entry] of attempts) {
    if (entry.blockedUntil < now && now - entry.first > GATE_ATTEMPT_WINDOW) attempts.delete(key);
  }
}, 5 * 60 * 1000);
sweep.unref();

function cookieValue(req, name) {
  const header = req.headers.cookie;
  if (!header) return "";
  for (const part of header.split(";")) {
    const index = part.indexOf("=");
    if (index < 0) continue;
    if (part.slice(0, index).trim() === name) return decodeURIComponent(part.slice(index + 1).trim());
  }
  return "";
}

const signature = (expiry) =>
  createHmac("sha256", GATE_SECRET).update(String(expiry)).digest("base64url");

function unlocked(req) {
  const raw = cookieValue(req, GATE_COOKIE);
  const dot = raw.lastIndexOf(".");
  if (dot < 1) return false;
  const expiry = raw.slice(0, dot);
  if (!/^\d{1,12}$/.test(expiry) || Number(expiry) * 1000 < Date.now()) return false;
  const given = Buffer.from(raw.slice(dot + 1));
  const expected = Buffer.from(signature(expiry));
  return given.length === expected.length && timingSafeEqual(given, expected);
}

const isSecureRequest = (req) =>
  String(req.headers["x-forwarded-proto"] || "").split(",")[0].trim() === "https";

function sessionCookie(req) {
  const maxAge = GATE_SESSION_DAYS * 24 * 60 * 60;
  const expiry = Math.floor(Date.now() / 1000) + maxAge;
  const secure = isSecureRequest(req) ? "; Secure" : "";
  return `${GATE_COOKIE}=${expiry}.${signature(expiry)}; Path=/; Max-Age=${maxAge}; HttpOnly; SameSite=Lax${secure}`;
}

function expiredCookie(req) {
  const secure = isSecureRequest(req) ? "; Secure" : "";
  return `${GATE_COOKIE}=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax${secure}`;
}

/** Only same-site paths may be used as a post-unlock destination. */
function safePath(raw) {
  const value = String(raw || "");
  if (!value.startsWith("/") || value.startsWith("//")) return "/";
  if (value.includes("\\") || value.includes("\n") || value.includes("\r")) return "/";
  return value;
}

function withState(path, code) {
  const [base, query] = String(path).split("?");
  const params = new URLSearchParams(query || "");
  params.set("e", code);
  const search = params.toString();
  return search ? `${base || "/"}?${search}` : base || "/";
}

const GATE_FALLBACK =
  '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">' +
  '<meta name="viewport" content="width=device-width,initial-scale=1">' +
  '<meta name="robots" content="noindex,nofollow"><title>SARGARA&reg; &mdash; Private Access</title>' +
  "</head><body style=\"margin:0;display:grid;place-items:center;min-height:100vh;background:#04101f;" +
  'color:#eef5ff;font:400 15px/1.6 system-ui,sans-serif;text-align:center">' +
  '<form method="post" action="/__access" style="display:grid;gap:14px;justify-items:center">' +
  '<strong style="letter-spacing:.3em;font-weight:500">SARGARA&reg;</strong>' +
  '<span style="color:#93aaca">Private access &mdash; enter your access phrase</span>' +
  '<input name="password" type="password" autocomplete="current-password" autofocus ' +
  'style="height:46px;width:260px;border-radius:999px;border:1px solid rgba(150,182,216,.3);' +
  'background:rgba(255,255,255,.05);color:#fff;padding:0 18px;font:inherit;outline:none">' +
  '<button style="height:42px;padding:0 26px;border-radius:999px;border:0;cursor:pointer;' +
  'background:#e2600f;color:#fff;font:inherit">Enter</button></form></body></html>';

async function sendGate(req, res, state = "") {
  let html = GATE_FALLBACK;
  try {
    html = await readFile(GATE_PAGE, "utf8");
  } catch {
    /* fall back to the minimal form above */
  }
  if (html.includes("__BODY_STATE__")) html = html.split("__BODY_STATE__").join(state);

  res.writeHead(200, {
    "Content-Type": "text/html; charset=utf-8",
    "Cache-Control": "no-store, no-cache, must-revalidate",
    "X-Robots-Tag": "noindex, nofollow, noarchive",
    "X-Content-Type-Options": "nosniff",
    Vary: "Cookie",
  });
  res.end(req.method === "HEAD" ? undefined : html);
}

function readBody(req, limit = 4096) {
  return new Promise((resolveBody) => {
    let data = "";
    let overflow = false;
    req.on("data", (chunk) => {
      if (overflow) return;
      data += chunk;
      if (data.length > limit) {
        overflow = true;
        data = "";
      }
    });
    req.on("end", () => resolveBody(overflow ? "" : data));
    req.on("error", () => resolveBody(""));
  });
}

async function handleAccess(req, res) {
  const body = await readBody(req);
  const type = String(req.headers["content-type"] || "");
  const wantsJson = String(req.headers.accept || "").includes("application/json");

  let password = "";
  let destination = "";

  if (type.includes("application/json")) {
    try {
      const data = JSON.parse(body || "{}");
      password = String(data.password || "");
      destination = String(data.next || "");
    } catch {
      /* treated as a wrong phrase below */
    }
  } else {
    const params = new URLSearchParams(body);
    password = params.get("password") || "";
    destination = params.get("next") || "";
  }

  const next = safePath(destination);

  const json = (status, payload) => {
    res.writeHead(status, {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
      "X-Robots-Tag": "noindex, nofollow",
    });
    res.end(JSON.stringify(payload));
  };

  const redirect = (location, cookie) => {
    const headers = { Location: location, "Cache-Control": "no-store" };
    if (cookie) headers["Set-Cookie"] = cookie;
    res.writeHead(303, headers);
    res.end();
  };

  const wait = throttledFor(req);
  if (wait) {
    if (wantsJson) return json(429, { ok: false, reason: "throttled", retry: wait });
    return redirect(withState(next, "slow"), null);
  }

  const phrase = password.trim().toLowerCase();

  if (phrase && GATE_PASSWORDS.includes(phrase)) {
    clearFailures(req);
    console.log(`[gate] access granted to ${clientKey(req)} → ${next}`);
    if (wantsJson) {
      res.setHeader("Set-Cookie", sessionCookie(req));
      return json(200, { ok: true, next });
    }
    return redirect(next, sessionCookie(req));
  }

  noteFailure(req);
  console.warn(`[gate] access rejected from ${clientKey(req)}`);
  if (wantsJson) return json(401, { ok: false, reason: "bad" });
  return redirect(withState(next, "bad"), null);
}

function sendRobotsDisallow(req, res) {
  const body = "User-agent: *\nDisallow: /\n";
  res.writeHead(200, {
    "Content-Type": "text/plain; charset=utf-8",
    "Content-Length": Buffer.byteLength(body),
    "Cache-Control": "no-store",
    "X-Robots-Tag": "noindex, nofollow",
  });
  res.end(req.method === "HEAD" ? undefined : body);
}

/* ------------------------------------------------------------------ static */

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".xml": "application/xml; charset=utf-8",
  ".txt": "text/plain; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".webp": "image/webp",
  ".avif": "image/avif",
  ".ico": "image/x-icon",
  ".woff": "font/woff",
  ".woff2": "font/woff2",
  ".pdf": "application/pdf",
};

const COMPRESSIBLE = /^(text\/|application\/(json|xml|javascript)|image\/svg)/;

function isDenied(pathname) {
  const lower = pathname.toLowerCase();
  if (DENIED_PREFIXES.some((prefix) => lower === prefix || lower.startsWith(prefix + "/"))) return true;
  if (DENIED_FILES.includes(lower)) return true;
  // never expose dotfiles (.git, .env, .gitignore …)
  return pathname.split("/").some((segment) => segment.startsWith(".") && segment.length > 1);
}

async function resolveFile(pathname) {
  const candidates = [];
  if (pathname.endsWith("/")) {
    candidates.push(join(pathname, "index.html"));
  } else {
    candidates.push(pathname, `${pathname}.html`, join(pathname, "index.html"));
  }

  for (const candidate of candidates) {
    const abs = resolve(join(ROOT, candidate));
    if (abs !== ROOT && !abs.startsWith(ROOT + sep)) continue; // path traversal guard
    try {
      const info = await stat(abs);
      if (info.isFile()) return { abs, size: info.size, mtime: info.mtime };
    } catch {
      /* try next candidate */
    }
  }
  return null;
}

function send(res, status, body, headers = {}) {
  res.writeHead(status, {
    "Content-Type": "text/plain; charset=utf-8",
    "Cache-Control": "no-store",
    ...headers,
  });
  res.end(body);
}

const server = createServer(async (req, res) => {
  if (maintenanceEnabled()) {
    if (req.method !== "GET" && req.method !== "HEAD") {
      return send(res, 503, "Service Unavailable\n", { "Retry-After": "3600" });
    }
    let html = "<!DOCTYPE html><title>SARGARA®</title><h1>We'll be back soon</h1>";
    try {
      html = await readFile(MAINTENANCE_PAGE, "utf8");
    } catch {
      /* fall back to the minimal notice above */
    }
    res.writeHead(503, {
      "Content-Type": "text/html; charset=utf-8",
      "Cache-Control": "no-store",
      "Retry-After": "3600",
      "X-Content-Type-Options": "nosniff",
    });
    return res.end(req.method === "HEAD" ? undefined : html);
  }

  let url;
  try {
    url = new URL(req.url, "http://localhost");
  } catch {
    return send(res, 400, "Bad Request\n");
  }

  let pathname;
  try {
    pathname = decodeURIComponent(url.pathname);
  } catch {
    return send(res, 400, "Bad Request\n");
  }

  const gated = gateEnabled();

  if (gated) {
    if (pathname === "/__access") {
      if (req.method !== "POST") {
        return send(res, 405, "Method Not Allowed\n", { Allow: "POST" });
      }
      return handleAccess(req, res);
    }

    if (url.searchParams.has("signout")) {
      res.writeHead(303, {
        Location: withState(pathname, "out"),
        "Set-Cookie": expiredCookie(req),
        "Cache-Control": "no-store",
      });
      return res.end();
    }

    if (!unlocked(req)) {
      if (req.method !== "GET" && req.method !== "HEAD") {
        return send(res, 405, "Method Not Allowed\n", { Allow: "GET, HEAD" });
      }
      if (pathname === "/robots.txt") return sendRobotsDisallow(req, res);
      if (!GATE_PUBLIC_PATHS.has(pathname)) {
        return sendGate(req, res, GATE_STATES[url.searchParams.get("e")] || "");
      }
    }
  }

  if (req.method !== "GET" && req.method !== "HEAD") {
    return send(res, 405, "Method Not Allowed\n", { Allow: "GET, HEAD" });
  }

  if (pathname.includes("\0") || isDenied(pathname)) {
    return send(res, 404, "Not Found\n");
  }

  let file = await resolveFile(pathname);
  let status = 200;

  if (!file) {
    file = await resolveFile("/404.html");
    status = 404;
  }
  if (!file) {
    return send(res, 404, "Not Found\n");
  }

  const ext = extname(file.abs).toLowerCase();
  const type = MIME[ext] || "application/octet-stream";
  const immutable = /\.(png|jpe?g|webp|avif|svg|ico|woff2?)$/i.test(file.abs);

  const headers = {
    "Content-Type": type,
    "Content-Length": file.size,
    "Last-Modified": file.mtime.toUTCString(),
    "Cache-Control": gated
      ? type.startsWith("text/html")
        ? "no-store"
        : "private, max-age=3600"
      : immutable
        ? "public, max-age=31536000, immutable"
        : "public, max-age=3600",
    "X-Content-Type-Options": "nosniff",
  };

  if (gated) headers.Vary = "Cookie";

  const acceptsGzip = /\bgzip\b/.test(req.headers["accept-encoding"] || "");
  const canGzip = acceptsGzip && COMPRESSIBLE.test(type) && file.size > 1024;

  if (canGzip) {
    headers["Content-Encoding"] = "gzip";
    delete headers["Content-Length"];
    headers["Vary"] = headers.Vary ? `${headers.Vary}, Accept-Encoding` : "Accept-Encoding";
  }

  res.writeHead(status, headers);
  if (req.method === "HEAD") return res.end();

  const stream = createReadStream(file.abs);
  if (canGzip) {
    stream.pipe(createGzip()).pipe(res);
  } else {
    stream.pipe(res);
  }
  stream.on("error", () => res.destroy());
});

server.listen(PORT, HOST, () => {
  console.log(`SARGARA site listening on http://${HOST}:${PORT}  (root: ${ROOT})`);
  if (maintenanceEnabled()) {
    console.log("Maintenance mode: ON — every request returns maintenance.html (503).");
  }
  if (gateEnabled()) {
    const source = GATE_FROM_ENV
      ? "access phrase from environment"
      : `default access phrase "${GATE_DEFAULT_PASSWORD}" — set ACCESS_PASSWORD to change it`;
    console.log(`Access gate: ON — ${GATE_PASSWORDS.length} phrase(s) accepted, ${source}.`);
  }
});
