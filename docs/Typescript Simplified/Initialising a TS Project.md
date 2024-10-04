# With TSC CLI tool
- Initialise an NPM project - `npm init`
- Install typescript package - `npm i --save-dev typescript`
- Create a tsconfig - `npx tsc --init`
- Use `npx tsc <file>` to transpile typescript to javascript 

# With Vite
- Run `npm create vite@latest .` to initialise a project in the current directory
- Choose a framework, and Typescript as the preferred language
- Use `npm run build` to build for production
- Use `npm run preview` to run a production server
- Use `npm run dev` to run a development server

Get TSConfig files from [here](https://github.com/tsconfig/bases). The config files are tuned to the environment, like Bun, Node, Svelte, etc.
