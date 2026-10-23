import { writeFileSync, existsSync } from "node:fs";
const UA={"User-Agent":"gunpla-catalog/1.0 (personal site build)"};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
for (const t of process.argv.slice(2)) {
  const f=`p_${t.replace(/[\/:*?"<>| .]/g,"_")}.html`; if(existsSync(f)) {console.log("skip",t);continue;}
  for(let i=0;i<6;i++){ const r=await fetch(`https://ja.wikipedia.org/w/api.php?action=parse&prop=text|sections&format=json&formatversion=2&redirects=1&page=${encodeURIComponent(t)}`,{headers:UA}); const s=await r.text();
    if(s.startsWith("{")){const j=JSON.parse(s); if(j.error){console.log("ERR",t,j.error.code);break;} writeFileSync(f,j.parse.text); console.log(t,j.parse.text.length,"tables",(j.parse.text.match(/<table/g)||[]).length,"li",(j.parse.text.match(/<li/g)||[]).length); break;}
    await sleep(8000*(i+1)); }
  await sleep(4000);
}
