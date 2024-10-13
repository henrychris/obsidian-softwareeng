In HTML, semantics means: to give content meaning and structure by using the right element. Screen readers, crawlers and search engines use these elements when parsing content.
Some semantic elements are: `<section>`, `<nav>` and `<header>`.
## Element Display
A block-level element is displayed on a new line and takes up all horizontal space.
An inline-level element is displayed on the same line, taking up the same width as its content.

`<span>` is usually used for smaller content within a block-level element. e.g:
```html
<p>
	Hello, <span>Henry</span>.
<p>
```

`<strong>` = bold. `<em>` = italics.

`<header>` - top of a page or introductory content in a section.
`<nav>` - navigation links.
`<article>` - independent, self-contained content. The content here should make sense if placed on a different site with 0 context.
`<section>` - used to link thematically related content.
`<aside>` - tangentially related content, often beside the main content on the left or right side of the page.
`<footer>` - closing a section or at the end of a page
## When should one use article, section or div?
**Styling only** -> `<div>`
**Independent, self-contained Content** -> `<article>`
**A group of related content** -> `<section>`