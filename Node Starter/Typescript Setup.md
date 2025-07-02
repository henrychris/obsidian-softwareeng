1. Initialise an npm project with `npm init -y`. 
2. Install typescript locally with: `npm install typescript --save-dev`
3. Initialise a tsc config: `npx tsc --init`
4. Replace ts-config content with:
```json
{
  "compilerOptions": {
    "target": "es2016",
    "module": "commonjs",
    "rootDir": ".",
    "outDir": "./dist",
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "strict": true,
    "skipLibCheck": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "allowJs": false,
    "noEmitOnError": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "sourceMap": true
  },
  "include": [
    "src/**/*.ts",
    "tests/**/*.ts"
  ],
  "exclude": [
    "node_modules",
    ".vscode"
  ]
}
```
5. Add the following scripts to package.json:
```json
{
	"scripts": {
        "prestart": "npx tsc",
        "start": "node dist/server.js ",
        "dev": "npx tsx watch src/server.ts",
    }
}
```
6. Install dependencies:
```bash
npm install express
npm install --save-dev @types/express @types/node tsx
```
