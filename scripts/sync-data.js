import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const projectRoot = path.resolve(__dirname, '..');
const backendDir = path.join(projectRoot, 'backend', 'data');
const publicDir = path.join(projectRoot, 'public');

const files = [
  { src: 'sp500_erp_data.json', dest: 'sp500_erp_data.json' },
  { src: 'hs300_erp_data.json', dest: 'erp_data.json' },
  { src: 'zzall_erp_data.json', dest: 'zzall_erp_data.json' },
  { src: 'zz500_erp_data.json', dest: 'zz500_erp_data.json' },
];

if (!fs.existsSync(backendDir)) {
  console.log('Backend data directory not found, skipping sync');
  process.exit(0);
}

for (const { src, dest } of files) {
  const srcPath = path.join(backendDir, src);
  const destPath = path.join(publicDir, dest);
  if (fs.existsSync(srcPath)) {
    fs.copyFileSync(srcPath, destPath);
    console.log(`Synced: ${src} -> ${dest}`);
  } else {
    console.log(`Source not found: ${src}`);
  }
}

console.log('Data sync complete');