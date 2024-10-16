A typeface is what we see.
A font is a file containing a typeface.

To change text colour use the `color` property:
```css
p {
	color: blue
}
```

The `font-family` allows you to declare what fonts should be used on the site. The values are comma-separated, and the first font is the primary. Others to its left are backup fonts.
```css
p {
	font-family: Helvetica, "Helvetica Neue", Arial 
}
```

Use `font-size` to change the text size. Pixels, ems, percentages, points and other length values are accepted.
```css
p {
	font-size: 14px;
}
```

Use `font-style` to italicise or prevent text from being italicised.
```css
p {
	font-style: italic; /* or normal or oblique or inherit */
}
```

To use small caps, specify with `font-variant`:
```css
p {
	font-variant: small-caps /* or normal or inherit */
}
```

To bolden text or change its weight, adjust `font-weight`:
```css
p {
	font-weight: 100 /* or `normal`, `bold`, `bolder`, `lighter`, and `inherit`. */
}
```

It's best to use normal and bold. For specific weights, use the numeric value. If the font doesn't have a matching weight, the closest value will be used.

Line height, the distance between two lines of text, is set with `line-height`.
```css
p {
	line-height: 1.5
}
```

The best practice for legibility is to set the `line-height` to around 1.5 times the `font-size` value, that is 1.5 or 150% (*this is the default behaviour*). However, it also accepts length inputs for fine-grained control. 

Align text:
```css
p {
	text-align: center /* or left, right */
}
```

Decorate text:
```css
p {
	text-decoration: underline /* or  none, overline, line-through, and inherit.*/
}
```

Underline is the default for anchor elements. There are other options to change the line appearance, like dotted, wavy, line-through. Multiple decorations may be used, separated by a space.

Indent text:
```css
p {
	text-indent: 20px /* accepts length values */
}
```
Positive values indent forwards, negative values indent backwards.

Add shadows to **text**:
```css
p {
	text-shadow: 3px 6px 2px rgba(0, 0, 0, .3);
}
```

First value is the horizontal offset.
Second value is the vertical offset.
Third value is the blur radius.
Fourth value is the colour.

Negative vertical and horizontal offsets move shadows to the left and top.

Transform text:
```css
p {
  text-transform: uppercase; /* or `none`, `capitalize`, `lowercase`, and `inherit`.*/
}
```

Adjust space between letters:
```css
p {
  letter-spacing: -.5em;
}
```

Accepts length values. It is best to use relative values, like em, so the spacing is constant as font size is changed.
Negative values bring them closer, positive values push them apart.

Adjust the space between words:
```css
p {
  word-spacing: .25em;
}
```
Negative values bring them closer, positive values push them apart.

# Web Safe Fonts
These fonts are installed on every device:
- Arial
- Courier New, Courier
- Garamond
- Georgia
- Lucida Sans, Lucida Grande, Lucida
- Palatino Linotype
- Tahoma
- Times New Roman, Times
- Trebuchet
- Verdana

They should be your backup fonts.
# Embedding Fonts
We can use `@font-face` to use fonts that exist on our server. See: [font-face](https://web.dev/learn/css/typography?continue=https%3A%2F%2Fweb.dev%2Flearn%2Fcss%23article-https%3A%2F%2Fweb.dev%2Flearn%2Fcss%2Ftypography#font-face).
