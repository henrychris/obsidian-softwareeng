Refer to [[HTML - Semantics#Element Display]] for inline and block-level elements.

Using CSS and the `display` property of elements, you can change how an element is displayed.
- `block` - displays as a block-level element.
- `inline` - displays as an inline-level element.
- `inline-block` - displays inline but accepts box model properties. Note that there is a tiny space between successive inline-block properties.

In the **box model**, every element is a **box** and has width, padding, margin and borders.

The total width of an element:
```
margin-right + border-right + padding-right + width + padding-left + border-left + margin-left
```

The total height of an element:
```
margin-top + border-top + padding-top + height + padding-bottom + border-bottom + margin-bottom
```

## Box Model Properties
### Width
This only matters for non-inline elements. The width of inline elements expands or decreases as their content's width changes.
Block-level elements have a default width of 100%, taking up all horizontal space.
### Height
The default height of all elements is the height of their content.
### Margin
The space surrounding an element.
The `margin-top` and `margin-bottom` elements are not accepted by inline elements.
### Padding
The space within an element, between its content and border.
### Border
The outline of an element, accepting `width`, `style` and `colour`. It can be set with shorthand in this format: 
```css
border: width style colour
```

You may specify what side to border, `border-bottom`
or specify the radius to round the border, `border-radius`
or specify the radius of a specific corner, `border-to-right-radius`.
## Box Sizing
This lets you change exactly how the box model works and how an element’s size is calculated.
### Content-Box
The default setting. The box model is additive. The border, margin and padding lengths are added to the width/height calculations.
### Border-Box
The padding and border values are included within the width and height. As padding or border values are changed, the size of the content changes to maintain the specified width and height.
The **margin** values are added to width and height regardless.

e.g.
total width = 400 & total height = 100.
padding = 20

The content width and content height are auto-adjusted to 360 and 60, respectively.
Add padding on all sides and the total width adds up to 400 and 100 h.

Border box is recommended, as elements will always maintain the specified dimensions - which makes calculations simpler.