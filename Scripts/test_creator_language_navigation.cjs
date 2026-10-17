const {readFileSync} = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const code = readFileSync('apps/locale.js', 'utf8');
function run(path, browserLanguage) {
  const elements=[]; const navigations=[];
  const document={readyState:'complete',createElement(tag){const el={tag,children:[],append(child){this.children.push(child)},setAttribute(){},addEventListener(name,fn){this[name]=fn}};elements.push(el);return el},querySelector(){return {append(){}}}};
  vm.runInNewContext(code,{document,Intl,navigator:{languages:[browserLanguage],language:browserLanguage},location:{pathname:path,search:'?utm_source=test',hash:'#record-picker',assign(url){navigations.push(url)},replace(){throw Error('Unexpected automatic redirect')}}});
  return {elements,navigations};
}
for (const [path,lang,current] of [['/de-de/apps/','fr-FR','de-DE'],['/apps/','fr-FR','en-US'],['/fr/apps/','en-US','fr-FR'],['/en-gb/apps/dulpi/','de-DE','en-GB']]) {
 const {elements,navigations}=run(path,lang);
 assert.deepEqual(navigations,[]);
 assert.equal(elements.find(x=>x.tag==='option'&&x.selected).value,current);
 const select=elements.find(x=>x.tag==='select'); select.value='fr-FR';select.change();
 assert.equal(navigations[0],'/fr/apps/'+(path.includes('dulpi')?'dulpi/':'')+'?utm_source=test#record-picker');
}
for (const path of ['/record-picker/guides/choose/','/fr/snory-teller-guide/','/unknown/apps/']) assert.equal(run(path,'fr-FR').elements.length,0);
console.log('OK: explicit locales remain stable, only user choice navigates, query and fragment retained.');
