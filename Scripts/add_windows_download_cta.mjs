import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { resolve } from 'node:path';

const root = resolve(import.meta.dirname, '..');
const files = ['index.html', ...readdirSync(root, { withFileTypes: true })
  .filter(entry => entry.isDirectory() && !entry.name.startsWith('.'))
  .map(entry => `${entry.name}/index.html`)];
let count = 0;
for (const file of files) {
  let html;
  try { html = readFileSync(resolve(root, file), 'utf8'); } catch { continue; }
  if (!html.includes('v20-hero-showcase')) continue;
  if (html.includes('data-windows-download-cta')) continue;
  const pattern = /(<div class="cta-row"><a class="button primary" href="https:\/\/apps\.apple\.com\/[^>]+>[^<]+<\/a>)/;
  if (!pattern.test(html)) throw new Error(`Missing homepage download row: ${file}`);
  html = html.replace(pattern, '$1<a class="button primary" href="https://apps.microsoft.com/detail/9N2ZWRL4M3JC" data-windows-download-cta>Windows · Microsoft Store</a>');
  writeFileSync(resolve(root, file), html);
  count++;
}
console.log(`Added Windows download button to ${count} homepages.`);
