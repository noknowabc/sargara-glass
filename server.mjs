/**
 * SARGARA — zero-dependency static file server.
 *
 * Serves the repository root as the website root. Requires no npm packages,
 * so hosting platforms can install and start it instantly:
 *
 *     npm start          # or: node server.mjs
 *
 * Respects PORT / HOST environment variables (cloud platforms set PORT).
 */

import { createReadStream } from "node:fs";
import { stat } from "node:fs/promises";
import { createServer } from "node:http";
import { extname, join, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";
import { createGzip } from "node:zlib";

const ROOT = resolve(fileURLToPath(new URL(".", import.meta.url)));
const PORT = Number(process.env.PORT) || 3000;
const HOST = process.env.HOST || "0.0.0.0";

/** Paths that must never be served publicly. */
const DENIED_PREFIXES = ["/tools", "/data", "/.git"];

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
  if (DENIED_PREFIXES.some((p) => lower === p || lower.startsWith(p + "/"))) return true;
  // never expose dotfiles (.git, .env, .gitignore …)
  return pathname.split("/").some((seg) => seg.startsWith(".") && seg.length > 1);
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
  if (req.method !== "GET" && req.method !== "HEAD") {
    return send(res, 405, "Method Not Allowed\n", { Allow: "GET, HEAD" });
  }

  let pathname;
  try {
    pathname = decodeURIComponent(new URL(req.url, "http://localhost").pathname);
  } catch {
    return send(res, 400, "Bad Request\n");
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
    "Cache-Control": immutable
      ? "public, max-age=31536000, immutable"
      : "public, max-age=3600",
    "X-Content-Type-Options": "nosniff",
  };

  const acceptsGzip = /\bgzip\b/.test(req.headers["accept-encoding"] || "");
  const canGzip = acceptsGzip && COMPRESSIBLE.test(type) && file.size > 1024;

  if (canGzip) {
    headers["Content-Encoding"] = "gzip";
    delete headers["Content-Length"];
    headers["Vary"] = "Accept-Encoding";
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
});
