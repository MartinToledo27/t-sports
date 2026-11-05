const C='tsports-v2';
const PRE=['./','index.html','tema.css','logo.svg','icono.png','nba/','f1/'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(C).then(c=>Promise.all(PRE.map(u=>c.add(u).catch(()=>{})))).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==C).map(x=>caches.delete(x)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{
  const r=e.request;
  if(r.method!=='GET')return;
  const u=new URL(r.url);
  const fuente=/(googleapis|gstatic)\.com$/.test(u.hostname);
  if(u.origin!==location.origin&&!fuente)return;
  const key=fuente?r:new Request(u.origin+u.pathname);
  if(fuente){
    e.respondWith(caches.open(C).then(c=>c.match(key).then(hit=>{
      const red=fetch(r).then(res=>{if(res.ok||res.type==='opaque')c.put(key,res.clone());return res}).catch(()=>hit);
      return hit||red;
    })));
    return;
  }
  e.respondWith(fetch(r).then(res=>{
    if(res.ok){const cp=res.clone();caches.open(C).then(c=>c.put(key,cp))}
    return res;
  }).catch(()=>caches.match(key)));
});
