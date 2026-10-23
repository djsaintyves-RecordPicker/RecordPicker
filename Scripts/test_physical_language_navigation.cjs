const {readFileSync}=require('node:fs');
const vm=require('node:vm'),assert=require('node:assert/strict');
const code=readFileSync('physical/locale.js','utf8');
function run(path,languages){
 const navigations=[];const listeners={};
 const location={pathname:path,search:'?utm_source=app&ref=help',hash:'#version-1-0-3',replace(url){navigations.push(url)}};
 const navigator={languages,language:languages[0]};
 vm.runInNewContext(code,{location,navigator,addEventListener:(event,fn)=>{listeners[event]=fn}});
 return {navigations,listeners,navigator,location};
}
const cases=[
 ['/physical/about/',['fr-FR'],'/physical/fr/about/'],
 ['/fr/physical-routine-guide/',['ko-KR'],'/ko/physical-routine-guide/'],
 ['/physical-routine-guide/',['fr-CA'],'/fr-ca/physical-routine-guide/'],
 ['/physical/fr/about/',['de-CH'],'/physical/de-de/about/'],
 ['/physical/fr/support/',['ja-JP'],'/physical/ja/support/'],
 ['/physical/privacy/',['ar-EG'],'/physical/ar-sa/privacy/'],
 ['/physical/fr/privacy/',['zh-HK'],'/physical/zh-hant/privacy/'],
 ['/physical/fr/about/',['zh-SG'],'/physical/zh-hans/about/'],
 ['/physical/about/',['pt-BR'],'/physical/pt-br/about/'],
 ['/physical/fr/about/',['nb-NO'],'/physical/no/about/'],
 ['/physical/about/',['iw-IL'],'/physical/he/about/'],
 ['/physical/fr/about/',['xx-ZZ','it-IT'],'/physical/it/about/'],
 ['/physical/fr/about/',['xx-ZZ'],'/physical/about/'],
 ['/physical/fr/support/index.html',['en-GB'],'/physical/en-gb/support/']
];
for(const [path,preferences,target] of cases){const out=run(path,preferences);assert.deepEqual(out.navigations,[target+'?utm_source=app&ref=help#version-1-0-3']);}
const manifest=JSON.parse(readFileSync('data/physical-localization/manifest.json'));
for(const locale of manifest.locales){
 const prefix=locale==='en-US'?'':locale==='fr-FR'?'fr/':locale.toLowerCase()+'/';
 const guidePrefix=locale==='en-US'?'':locale==='fr-FR'?'fr/':locale.toLowerCase()+'/';
 assert.deepEqual(run('/'+guidePrefix+'physical-routine-guide/',[locale]).navigations,[]);
 for(const kind of ['about','support','privacy'])assert.deepEqual(run('/physical/'+prefix+kind+'/',[locale]).navigations,[],'No loop: '+locale+' '+kind);
}
assert.deepEqual(run('/physical/about/',['xx-ZZ']).navigations,[]);
assert.deepEqual(run('/snory-teller/fr-FR/',['de']).navigations,[]);
const live=run('/physical/fr/about/',['fr-FR']);live.navigator.languages=['ko-KR'];live.listeners.languagechange();assert.equal(live.navigations[0],'/physical/ko/about/?utm_source=app&ref=help#version-1-0-3');
console.log('MPR: all 50 locales, 150 stable routes, ordered preferences, aliases, RTL destinations, fallback, language changes, query/fragment retention passed');
