const fs = require('fs');
const path = require('path');

const indexDtsPath = path.join(__dirname, 'node_modules/@phosphor-icons/react/dist/index.d.ts');
const csrDir = path.join(__dirname, 'node_modules/@phosphor-icons/react/dist/csr');
const ssrDir = path.join(__dirname, 'node_modules/@phosphor-icons/react/dist/ssr');

if (fs.existsSync(indexDtsPath)) {
  const content = fs.readFileSync(indexDtsPath, 'utf8');
  const regex = /export \* from '\.\/csr\/([a-zA-Z0-9]+)';/g;
  let match;
  let count = 0;

  while ((match = regex.exec(content)) !== null) {
    const iconName = match[1];
    const csrFile = path.join(csrDir, `${iconName}.d.ts`);
    const ssrFile = path.join(ssrDir, `${iconName}.d.ts`);
    const dtsContent = `import { Icon } from '../lib/types';\ndeclare const I: Icon;\nexport declare const ${iconName}: Icon;\nexport { I as ${iconName}Icon };\n`;

    if (!fs.existsSync(csrFile)) {
      fs.writeFileSync(csrFile, dtsContent, 'utf8');
      count++;
    }
    if (fs.existsSync(ssrDir) && !fs.existsSync(ssrFile)) {
      fs.writeFileSync(ssrFile, dtsContent, 'utf8');
    }
  }
  console.log(`Generated ${count} missing .d.ts files in @phosphor-icons/react`);
}
