// 공유 링크 미리보기 만들기
// 카카오톡·X·페이스북은 링크를 붙이면 그 주소의 og:title·og:image를 읽어 미리보기를 보여 줘요.
// GitHub Pages는 판마다 다른 페이지를 만들 수 없어서, 나라×성별×언어별 작은 페이지와 나라별 그림을 미리 만들어 둬요.
// 각 페이지는 열리자마자 첫 화면(?c=..&a=..)으로 넘어가요.
//
// 사용법 (저장소 맨 위에서):
//   python3 -m http.server 8765 &
//   node tools/make-share-pages.js          # s/ 폴더를 다시 만들어요
// Playwright가 필요해요 (npm i -g playwright).
const fs=require("fs"), path=require("path");
let chromium; try{({chromium}=require("playwright"))}catch(e){({chromium}=require(require("child_process").execSync("npm root -g").toString().trim()+"/playwright"))}
const ROOT=path.resolve(__dirname,".."), OUT=path.join(ROOT,"s");
const SITE="https://randomlife-game.github.io/randomlife-game/";
const SRC=process.env.SRC||"http://localhost:8765/index.html";
const T={
  ko:{t:(p,x)=>`친구가 ${p}에서 ${x}로 태어나 한평생을 살아 봤어요`,sx:["남자아이","여자아이"],
      d:"같은 날 정반대 형편에서 태어난 두 아이의 일생을 나란히 살아 보세요. 무료 · 가입 없음",go:"이 인생 보러 가기",site:"랜덤인생게임"},
  en:{t:(p,x)=>`A friend lived a whole life as a ${x} born in ${p}`,sx:["boy","girl"],
      d:"Live two lives side by side: you, and a child born the same day at the opposite end. Free, no sign-up.",go:"See this life",site:"Random Life"},
  ja:{t:(p,x)=>`友だちが${p}で${x}として生まれ、一生を生きてみました`,sx:["男の子","女の子"],
      d:"同じ日に正反対の境遇で生まれた二人の一生を、並べて生きてみよう。無料・登録不要",go:"この人生を見る",site:"ランダム人生"},
  zh:{t:(p,x)=>`朋友作为出生在${p}的${x}，过完了一生`,sx:["男孩","女孩"],
      d:"和同一天出生在截然相反境遇中的孩子，并肩过完两段人生。免费，无需注册。",go:"去看这段人生",site:"随机人生"}
};
const LANGS=["ko","en","ja","zh"];
const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"})[c]);
function page(lang,iso,sex,name){
  const t=T[lang], title=t.t(name,t.sx[sex==="m"?0:1]), url=`${SITE}s/${lang}/${iso}-${sex}.html`, home=`../../?c=${iso}&s=${sex}&l=${lang}`;
  return `<!doctype html><html lang="${lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(title)}</title>
<meta name="description" content="${esc(t.d)}"><meta name="robots" content="noindex">
<meta property="og:type" content="website"><meta property="og:site_name" content="${esc(t.site)}">
<meta property="og:title" content="${esc(title)}"><meta property="og:description" content="${esc(t.d)}">
<meta property="og:url" content="${url}"><meta property="og:image" content="${SITE}s/img/${iso}.jpg">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="${esc(title)}"><meta name="twitter:image" content="${SITE}s/img/${iso}.jpg">
<script>location.replace("../../"+(location.search||"?c=${iso}&s=${sex}&l=${lang}"));</script>
</head><body style="font-family:system-ui,sans-serif;background:#f3eee4;color:#1f1a14;padding:32px"><p>${esc(title)}</p><p><a href="${home}">${esc(t.go)} →</a></p></body></html>
`;
}
(async()=>{
  const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1200,height:630},deviceScaleFactor:1,locale:"ko-KR",colorScheme:"light"});
  await p.goto(SRC,{waitUntil:"networkidle"});
  const list=await p.evaluate(()=>COUNTRIES.map(c=>({iso:c[0],names:NAMES[c[0]],inc:c[4]})));
  fs.rmSync(OUT,{recursive:true,force:true});
  for(const l of LANGS) fs.mkdirSync(path.join(OUT,l),{recursive:true});
  fs.mkdirSync(path.join(OUT,"img"),{recursive:true});
  for(const c of list){
    LANGS.forEach((l,i)=>{ for(const s of ["m","f"]) fs.writeFileSync(path.join(OUT,l,`${c.iso}-${s}.html`),page(l,c.iso,s,c.names[i])); });
    await p.evaluate(({iso,ko,en})=>{
      const c=COUNTRIES.find(x=>x[0]===iso);
      clearInterval(window.babyT); document.getElementById("top").innerHTML="";
      const g=newLife(Math.abs(hashStr(iso))+1,{c,fam:[14,30,50,72][c[4]]}); g.urban=c[4]>=2;
      document.getElementById("app").innerHTML=`<div id="og" style="position:fixed;inset:0;width:1200px;height:630px;overflow:hidden;font-family:var(--ff);color:#1f1a14;background:#f3eee4">
        <div style="position:absolute;inset:0">${sceneSVG(g,4,{t:.06,ar:1200/630}).replace("<svg ",'<svg style="display:block;width:100%;height:100%" ')}</div>
        <div style="position:absolute;left:56px;top:48px;display:flex;align-items:center;gap:14px;font-weight:800;font-size:28px">${LOGO}<span>랜덤인생게임 · Random Life</span></div>
        <div style="position:absolute;left:56px;top:150px;max-width:560px">
          <div style="font-weight:900;font-size:${ko.length>8?64:92}px;line-height:1.02;letter-spacing:-.035em;color:#1f1a14">${ko}</div>
          <div style="font-size:32px;font-weight:700;color:#4d4539;margin-top:12px">${en}</div></div>
        <div style="position:absolute;right:48px;top:48px;width:520px;padding:18px 20px;border-radius:24px;background:rgba(255,253,248,.82);box-shadow:0 18px 40px -24px rgba(60,40,15,.45)">${mapSVG("pin",iso)}</div>
      </div>`;
      const m=document.querySelector("#og svg.mark"); if(m){m.style.width="48px";m.style.height="48px"}
      document.querySelectorAll("#og .ring,#og .clouds").forEach(e=>e.remove());
      const pin=document.querySelector("#og .pin"); if(pin){pin.setAttribute("r","13");pin.setAttribute("stroke-width","4");
        const r=pin.cloneNode(); r.setAttribute("r","26"); r.setAttribute("fill","none"); r.setAttribute("stroke","#c4572a"); r.setAttribute("stroke-width","3"); r.removeAttribute("class"); pin.parentNode.insertBefore(r,pin);}
    },{iso:c.iso,ko:c.names[0],en:c.names[1]});
    await p.screenshot({path:path.join(OUT,"img",`${c.iso}.jpg`),type:"jpeg",quality:80,clip:{x:0,y:0,width:1200,height:630}});
  }
  await b.close();
  console.log("countries",list.length);
})();
