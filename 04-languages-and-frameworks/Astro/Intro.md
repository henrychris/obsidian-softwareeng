1. Run `npm create @astro/latest`
2. Add markdown files to `src/pages/posts`.
3. Add JavaScript or TypeScript code within the fences (known as the frontmatter script). For more on setting up TypeScript projects, see [[04-languages-and-frameworks/Typescript Simplified/Initialising a TS Project]] or [[04-languages-and-frameworks/Node Starter/Typescript Setup]].
```astro
---
const pageTitle = "pageTitle";
const happy = true;

const skillColor = "green";
const typeColor = "blue";
---

// use them like this in html code (or components?)
<h1>{pageTitle}</h1>
```
4. JavaScript or TypeScript can be used in HTML, but it must be surrounded with curly braces:
```astro
{happy && <p>I am happy to be learning Astro!</p>}
```
5. You can style Astro pages with a `style` tag within the `head` tag of the HTML. This style tag can access variables from the frontmatter script like this:
```astro
<style>
	<style define:vars={{ skillColor, typeColor }}>
            h1 {
                color: purple;
                font-size: 4rem;
            }

            .skill {
                color: var(--typeColor);
                font-weight: bold;
            }
        </style>
</style>
```
6. You may add a global css in file in `src/styles/global.css`. Import it in the frontmatter script: `import '../styles/global.css';`. Of course, local styles override global styles.
7. Create components in `src/components`. The files should be named starting with a capital letter. A component is just a blob of html. e.g.:
```html
// Navigation.astro in src/components/

<a href="/">Home</a>
<a href="/about/">About</a>
<a href="/blog/">Blog</a>
```
```jsx
---
import Navigation from "../components/Navigation.astro";
---
// index.astro in src/pages/
...
<body>
	<Navigation />
</body>
```
8. Note, you can remove the frontmatter script fences if there's nothing inside. Add them back if needed.
9. Components can receive props:
```astro
// Social.astro

---
const { platform, username } = Astro.props;
---

<a href={`https://www.${platform}.com/${username}`}>{platform}</a>
```
```
// Footer.astro
---
const github_username = "henrychris";
const x_username = "hiddenhenry";

import Social from "./Social.astro";
---

<footer>
    <Social platform="github" username={github_username} />
    <Social platform="X" username={x_username} />
</footer>
```
10. You can strongly type props by adding an interface:
```
// Social.astro
---
interface Props {
    platform: string;
    username: string;
}

const { platform, username } = Astro.props;
---
```
11. You can add scripts within a component or page. You don't have to write the code there either, you can import it from elsewhere:
```ts
<script>
	import "../scripts/menu.ts";
<script/>
```
- Note, all Javascript in component **frontmatter** is executed at **build-time** and used to build the static HTML sent to the browser. The frontmatter code is then thrown away.
  Code in a **script** tag is sent to the browser. So, use the script tag to add client-side interactivity.
12. Astro components can also be used to create layouts. Add them to `src/layouts`. The file should start with a capital letter, like BaseLayout.astro.
```astro
---
import Header from "../components/Header.astro";
import Footer from "../components/Footer.astro";
import "../styles/global.css";

interface Props {
    pageTitle: string;
}

const { pageTitle } = Astro.props;
---

<html lang="en">
    <head>
        <meta charset="utf-8" />
        <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
        <meta name="viewport" content="width=device-width" />
        <meta name="generator" content={Astro.generator} />
        <title>{pageTitle}</title>
    </head>
    <body>
        <Header />
        <h1>{pageTitle}</h1>
        <slot />
        <Footer />
        <script>
            import "../scripts/menu.js";
        </script>
    </body>
</html>
```

For this layout, the page title is passed in as a prop. The `slot` element is where the content from the component using this layout is injected. Usage:
```astro
---
import BaseLayout from "../layouts/BaseLayout.astro";

const pageTitle = "My Blog";
---

<BaseLayout pageTitle={pageTitle}>
    <p>This is where I will post about my journey learning Astro.</p>

    <ul>
        <li><a href="/posts/post-1/">Post 1</a></li>
        <li><a href="/posts/post-2/">Post 2</a></li>
        <li><a href="/posts/post-3/">Post 3</a></li>
    </ul>
</BaseLayout>
```
13. You can use a layout for markdown files. Specify the layout in the frontmatter:
```md
---
layout: ../../layouts/MarkdownPostLayout.astro
title: 'My First Blog Post'
---
```
The items in the frontmatter are passed to the layout as props. As such, we can create an interface to access the props:
```ts
interface Props {
    frontmatter: {
        title: string;
        pubDate: string;
        description: string;
        author: string;
        image: {
            url: string;
            alt: string;
        };
        tags: string[];
    };
}

const { frontmatter } = Astro.props;
```
14. And of course, we can combine layouts:
```astro
<BaseLayout pageTitle={frontmatter.title}>
    <p>Written by {frontmatter.author}</p>
    <p>{frontmatter.description}</p>
    <p>Published on: {frontmatter.pubDate}</p>
    <img src={frontmatter.image.url} width="300" alt={frontmatter.image.alt} />
    <slot />

    <p>Tags: {frontmatter.tags.join(", ")}</p>
</BaseLayout>
```
15. We can generate pages as well. Astro has a `getStaticPaths` method that expects this a params object returned. The variable returned must match the name of the param in the filename:
```astro
// [tag].astro
return [
	{ params: { tag } }
];
```

A page will be created for each params object in the array. If you wish to pass more data, you can also pass props within the object:
```astro
// [tag].astro
return [
	{ params: { tag }, props: { posts: filteredposts } }
];
```

Within the same file, you can access these values & they will be used to generate the HTML pages at build-time.
```astro
const { tag } = Astro.params as Params;
const { posts } = Astro.props;
```

However you populate `params` is up to you.
16. You can create an index page with the same route as its folder by naming it `index.astro`. That is, `index.astro` in `src/pages/shoes/`, will have this URL: `base_url/shoes`. 
    If you create `src/pages/shoes.astro`, it will have the same URL. However, the latter will override the former if both exist.


# What's Next
- Find design inspiration for my blog
- Find how to style codeblocks when they are rendered to HTML
- Play with view transitions
- Add a sitemap to blog when deploying. See [this](https://docs.astro.build/en/guides/integrations-guide/sitemap/).
- Checkout [Bun](https://docs.astro.build/en/recipes/bun/) with Astro.
- Add [Last Modified time](https://docs.astro.build/en/recipes/modified-time/).
- Add [Reading time](https://docs.astro.build/en/recipes/reading-time/).
- 