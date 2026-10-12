// 한 판을 끝낸 수만 세는 작은 카운터예요. 누가 했는지는 저장하지 않아요.
// GET  /count → {today, total}
// POST /done  → 숫자를 1 올리고 {today, total}을 돌려줘요.
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

export default {
  async fetch(req, env) {
    const { pathname } = new URL(req.url);
    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: CORS });
    const stub = env.PLAYS.get(env.PLAYS.idFromName("all"));
    if (pathname === "/count" && req.method === "GET") return json(await stub.read());
    if (pathname === "/done" && req.method === "POST") return json(await stub.add());
    return json({ error: "not found" }, 404);
  },
};
