import fs from 'node:fs';
import path from 'node:path';
const root = path.resolve(import.meta.dirname, '..');
const store = 'https://apps.microsoft.com/detail/9N2ZWRL4M3JC';
const available = {'':'Available now','en-us':'Available now','en-gb':'Available now','en-au':'Available now','en-ca':'Available now',fr:'Disponible maintenant','fr-ca':'Disponible maintenant',de:'Jetzt verfügbar',it:'Disponibile ora','es-es':'Ya disponible','es-mx':'Ya disponible',ar:'متاح الآن',ca:'Disponible ara',da:'Tilgængelig nu',el:'Διαθέσιμο τώρα',fi:'Saatavilla nyt',he:'זמין עכשיו',hi:'अब उपलब्ध है',id:'Tersedia sekarang',ja:'配信開始',ko:'지금 이용 가능',nb:'Tilgjengelig nå',nl:'Nu beschikbaar',pl:'Już dostępna','pt-br':'Disponível agora','pt-pt':'Disponível agora',ru:'Уже доступно',sv:'Tillgänglig nu',th:'พร้อมใช้งานแล้ว',tr:'Şimdi kullanılabilir',vi:'Đã có mặt','zh-hans':'现已推出','zh-hant':'現已推出'};
function walk(dir) { return fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.name.startsWith('.')||['Scripts','assets','data'].includes(e.name)?[]:e.isDirectory()?walk(path.join(dir,e.name)):e.name.endsWith('.html')?[path.join(dir,e.name)]:[]); }
for (const file of walk(root)) {
  const relative=path.relative(root,file).split(path.sep); const locale=Object.hasOwn(available,relative[0])?relative[0]:'';
  const label=available[locale]; const fr=locale.startsWith('fr'); const en=locale===''||locale.startsWith('en-');
  let text=fs.readFileSync(file,'utf8'), before=text;
  text=text.replace(/(windows-app\/">Windows <small>)[^<]*(<\/small>)/g,`$1${label}$2`);
  text=text.replace(/(<b>Windows<\/b><small>)[^<]*(<\/small>)/g,`$1${label}$2`);
  text=text.replace(/(<strong>Windows<\/strong>)<span class="platform-status coming-soon">[^<]*<\/span>/g,`$1<a class="platform-status coming-soon" href="${store}">${label} · Microsoft Store</a>`);
  text=text.replace(/(aria-label="Windows: )[^;]+;/g,`$1${label};`);
  // This block now announces only the still-in-development Android beta.
  text=text.replace(/(<h2 id="platform-expansion-title">)[^<]*(<\/h2>)/g,'$1Record Picker · Android$2');
  text=text.replace(/<p class="platform-expansion-detail">.*?<\/p>/gs,'');
  if (relative.includes('windows-app')) {
    const description=fr?'Record Picker 2.4.3 est disponible sur le Microsoft Store pour Windows 11, sur PC x64 et ARM64.':en?'Record Picker 2.4.3 is available in the Microsoft Store for Windows 11 on x64 and ARM64 PCs.':`Record Picker 2.4.3 · Windows 11 · Microsoft Store · ${label}`;
    const intro=fr?'Votre collection, votre prochaine écoute.':en?'Your collection. Your next listen.':'Random Pick · Mood Pick · Today’s Pick';
    const details=fr?'Importez votre collection en CSV ou ajoutez vos disques, puis retrouvez Random Pick, Mood Pick et Today’s Pick sur votre PC. Interface en français et en anglais.':en?'Import your collection from CSV or add your records, then enjoy Random Pick, Mood Pick and Today’s Pick on your PC. Interface available in English and French.':'Random Pick · Mood Pick · Today’s Pick · CSV';
    const pricing=fr?'Gratuit jusqu’à 100 disques possédés. Achat Pro facultatif dans le Microsoft Store pour supprimer cette limite.':en?'Free for up to 100 owned records. An optional Pro purchase in the Microsoft Store removes this limit.':'';
    const button=fr?'Obtenir sur le Microsoft Store':en?'Get it from Microsoft Store':'Microsoft Store';
    const main=`<section class="hero platform-product-hero"><div class="hero-copy"><p class="kicker">${label}</p><h1>Record Picker</h1><p class="tagline">Windows</p><p class="deck">${description}</p><div class="cta-row"><a class="button primary" href="${store}">${button}</a></div></div><div class="platform-symbol windows-symbol" aria-hidden="true">⊞</div></section><section class="section platform-expansion windows-release" data-windows-version="2.4.3"><div class="section-head"><h2>${intro}</h2><p class="lead">${details}</p>${pricing?`<p>${pricing}</p>`:''}</div></section>`;
    text=text.replace(/<section class="hero platform-product-hero platform-development-hero">.*?<section class="contact-band">/s,main+'<section class="contact-band">');
    const regions={'en-au':'Australia','en-ca':'Canada','en-gb':'United Kingdom','en-us':'United States','fr-ca':'Canada','es-es':'España','es-mx':'México','pt-br':'Brasil','pt-pt':'Portugal'};
    const metadataDescription=description+(regions[locale]?` — ${regions[locale]}`:'');
    text=text.replace(/(<meta (?:name="description"|property="og:description"|name="twitter:description") content=")[^"]*/g,`$1${metadataDescription}`);
    text=text.replace(/(<span id="site-footer-version">)Record Picker · [^<]+/,'$1Record Picker · Windows 2.4.3');
  }
  if(text!==before) fs.writeFileSync(file,text);
}
const readme=path.join(root,'README.md');
fs.writeFileSync(readme,fs.readFileSync(readme,'utf8').replace('Android and Windows versions are in development. Release details will be announced\nwhen both versions are ready.',`Windows 2.4.3 is available in the Microsoft Store: ${store}\nAndroid remains in development.`).replace('- Windows: coming soon.','- Windows: 2.4.3 available on the Microsoft Store (Windows 11, x64 and ARM64).').replace('Localized Windows preview pages','Localized Windows product pages'));
console.log('Published Windows availability across localized pages.');
