Syntax
```css
@media <target> () {

}
```
`target` is one of the following:
- screen (phones, laptops)
- print (print media)
- speech (screen readers)
- all (default)

The `breakpoint` goes within the parentheses. This is when the media query applies to the page.
Example: `min-width` only applies when the viewport width is above a certain value. `max-width` only applies when the viewport width is below a certain value.

Mobile first designs use `min-width` queries to make them responsive on larger screens.