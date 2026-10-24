import { writeFileSync, existsSync } from "node:fs";
const UA={"User-Agent":"gunpla-catalog/1.0 (personal fan site build)"};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const cm=await (await fetch("https://gundam.fandom.com/api.php?action=query&list=categorymembers&cmtitle=Category:Gunpla&cmlimit=500&format=json",{headers:UA})).json();
const titles=cm.query.categorymembers.map(m=>m.title).filter(t=>!t.startsWith("Category:"));
for (const t of titles) {
  const f=`fandom/${t.replace(/[\/:*?"<>| .']/g,"_")}.html`; if(existsSync(f)) continue;
  const r=await fetch(`https://gundam.fandom.com/api.php?action=parse&prop=text&format=json&formatversion=2&redirects=1&page=${encodeURIComponent(t)}`,{headers:UA});
  const j=await r.json(); if(j.error){console.log("ERR",t);continue;}
  writeFileSync(f,`<!--TITLE:${t}-->\n`+j.parse.text); console.log(t,j.parse.text.length,(j.parse.text.match(/<table/g)||[]).length);
  await sleep(1500);
}
