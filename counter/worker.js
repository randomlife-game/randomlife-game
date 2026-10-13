// 한 판을 끝낸 수와 방문 통계를 세는 작은 카운터예요. 누가 했는지는 저장하지 않아요.
// GET  /count → {today, total}
// POST /done  → 숫자를 1 올리고 {today, total}을 돌려줘요.
// POST /hit   → {k:"visit", ref, lang} 또는 {k:"start"}. 날짜별 숫자만 올려요.
// GET  /stats → 최근 30일 방문·시작·완료 수와 어디서 왔는지(사이트 이름), 나라, 언어 합계.
import { DurableObject } from "cloudflare:workers";

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Max-Age": "86400",
};
const json = (body, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { ...CORS, "Content-Type": "application/json", "Cache-Control": "no-store" },
  });

// 날짜는 한국 시간 기준으로 바뀌어요.
const today = () => new Date(Date.now() + 9 * 3600e3).toISOString().slice(0, 10);

export class Plays extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    this.sql = ctx.storage.sql;
    this.sql.exec("CREATE TABLE IF NOT EXISTS days (day TEXT PRIMARY KEY, n INTEGER NOT NULL)");
    this.sql.exec(
      "CREATE TABLE IF NOT EXISTS hits (day TEXT NOT NULL, kind TEXT NOT NULL, key TEXT NOT NULL, n INTEGER NOT NULL, PRIMARY KEY (day, kind, key))"
    );
  }
  bump(kind, key) {
    this.sql.exec(
      "INSERT INTO hits (day, kind, key, n) VALUES (?, ?, ?, 1) ON CONFLICT(day, kind, key) DO UPDATE SET n = n + 1",
      today(), kind, key
    );
  }
  hit(h) {
    if (h.k === "start") this.bump("start", "");
    if (h.k === "visit") {
      this.bump("visit", "");
      this.bump("ref", h.ref);
      this.bump("lang", h.lang);
      this.bump("country", h.country);
    }
  }
  stats(n) {
    const from = new Date(Date.now() + 9 * 3600e3 - (n - 1) * 86400e3).toISOString().slice(0, 10);
    const days = {};
    const day = (d) => (days[d] ||= { day: d, visit: 0, start: 0, done: 0 });
    for (const r of this.sql.exec("SELECT day, n FROM days WHERE day >= ?", from)) day(r.day).done = r.n;
    for (const r of this.sql.exec("SELECT day, kind, n FROM hits WHERE day >= ? AND kind IN ('visit','start')", from))
      day(r.day)[r.kind] = r.n;
    const top = (kind) =>
      this.sql
        .exec("SELECT key, SUM(n) AS n FROM hits WHERE day >= ? AND kind = ? GROUP BY key ORDER BY n DESC LIMIT 30", from, kind)
        .toArray();
    return {
      from,
      days: Object.values(days).sort((a, b) => (a.day < b.day ? 1 : -1)),
      ref: top("ref"),
      country: top("country"),
      lang: top("lang"),
    };
  }
  read() {
    const d = today();
    const t = this.sql.exec("SELECT n FROM days WHERE day = ?", d).toArray()[0];
    const all = this.sql.exec("SELECT COALESCE(SUM(n), 0) AS s FROM days").one();
    return { today: t ? t.n : 0, total: all.s, day: d };
  }
  add() {
    this.sql.exec(
      "INSERT INTO days (day, n) VALUES (?, 1) ON CONFLICT(day) DO UPDATE SET n = n + 1",
      today()
    );
    return this.read();
  }
}

const LANGS = ["ko", "en", "ja", "zh"];
// 들어온 값은 짧은 이름으로만 받아요. 주소 전체나 검색어는 저장하지 않아요.
function cleanHit(body, req) {
  if (!body || (body.k !== "visit" && body.k !== "start")) return null;
  const ref = String(body.ref || "direct").toLowerCase().replace(/^www\./, "");
  const country = String(req.cf?.country || "??").toUpperCase();
  return {
    k: body.k,
    ref: /^[a-z0-9.-]{1,60}$/.test(ref) ? ref : "other",
    lang: LANGS.includes(body.lang) ? body.lang : "other",
    country: /^[A-Z0-9]{2}$/.test(country) ? country : "??",
  };
}

export default {
  async fetch(req, env) {
    const { pathname } = new URL(req.url);
    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: CORS });
    const stub = env.PLAYS.get(env.PLAYS.idFromName("all"));
    if (pathname === "/count" && req.method === "GET") return json(await stub.read());
    if (pathname === "/done" && req.method === "POST") return json(await stub.add());
    if (pathname === "/hit" && req.method === "POST") {
      const text = await req.text();
      let body = null;
      try { body = text.length <= 500 ? JSON.parse(text) : null; } catch {}
      const h = cleanHit(body, req);
      if (!h) return json({ error: "bad hit" }, 400);
      await stub.hit(h);
      return json({ ok: true });
    }
    if (pathname === "/stats" && req.method === "GET") return json(await stub.stats(30));
    return json({ error: "not found" }, 404);
  },
};
