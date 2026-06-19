const fs = require('fs');
const { execFileSync } = require('child_process');

const readmePath = 'readme/index.html';
let html = fs.readFileSync(readmePath, 'utf8');
const original = html;

const screenshotsLink = '<a href="../screenshots/"><span class="lang-fr">Aperçus</span><span class="lang-en">Screenshots</span></a>';
const headerNeedle = '<a href="../index.html#versions"><span class="lang-fr">Versions</span><span class="lang-en">Versions</span></a>';
const footerNeedle = '<nav aria-label="Footer"><a href="../support/"><span class="lang-fr">Assistance</span><span class="lang-en">Support</span></a>';

if (!html.includes(`${headerNeedle}${screenshotsLink}`)) {
  html = html.replace(headerNeedle, `${headerNeedle}${screenshotsLink}`);
}

if (!html.includes(`${footerNeedle}${screenshotsLink}`)) {
  html = html.replace(footerNeedle, `${footerNeedle}${screenshotsLink}`);
}

if (html !== original) {
  fs.writeFileSync(readmePath, html);
}

execFileSync('git', ['config', 'user.name', 'github-actions[bot]']);
execFileSync('git', ['config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com']);
execFileSync('git', ['rm', '.github/scripts/restore-screenshots-link.js', '.github/workflows/restore-screenshots-link.yml']);
execFileSync('git', ['add', readmePath]);

const status = execFileSync('git', ['status', '--porcelain'], { encoding: 'utf8' });
if (status.trim()) {
  execFileSync('git', ['commit', '-m', 'Restore screenshots link on features page'], { stdio: 'inherit' });
  execFileSync('git', ['push'], { stdio: 'inherit' });
} else {
  console.log('No changes to commit.');
}
