First off, you need to understand *normal flow.* This is the natural rendering of elements before styling like `float` or `position` is applied. It's how browsers render block and inline-level elements.

Block-level elements take the full width and stack **vertically** on top of one another.
Inline-level elements flow horizontally, next to other inline elements till the line runs out of space.
Inline-block elements render inline but respect box model properties.
# Float
This positions an element to the left or right of its parent, outside of normal flow. The element floats to the edge of its closest parent, or to the edge of the page. Since it's outside normal flow, other elements act like it doesn't exist - and this may cause overlaps.
Float changes an elements display value to block.
Floated elements align next to one another while their is space on the line, else they wrap to the next line.

This is usually used when you wish to wrap elements around another, like text around an image. Can also be used to create column structures (although not recommended).

To reset the rest of the document to recognise the floated element as part of normal flow (without changing how it displays), you will need to `clear` the floats.

```css
div {
  clear: left;
}

div {
  clear: right;
}

div {
  clear: both; /* both sides */
}

```

You can also contain the float using `clearfix`. Google it if you ever need it. 
# Inline Block
This is primarily used to layout pages or place elements next to one another on a line. To use this, set `display` to `inline-block`. This displays elements in a line, while allowing them to receive box model properties.
# Positioning With `Position`
By default, the `position` property is set to `static`. Elements stack on top of one another as expected.
## Relative Positioning
This moves the element in relation to its position in the normal flow. The original space is reserved and other elements shall behave like the element is in its original location.
```css
div {
	position: relative;
}
```
## Absolute Positioning
The element is removed from normal flow - other elements shall behave like it does not exist. The original space is not reserved. 
The element is positioned in relation to the closest parent element or the `body` element if no parent exists.

Assume you have this:
```html
<section class="offset">
</section>

<section>
</section>
```

```css
.offset{
	position: absolute;
	left: 20px;
}
```

The section below (without a class), will be displayed in the space 'reserved' for the section above. The section with class 'offset', will be placed 20 pixels to the right - overlapped by the other element.