There are three selectors:
1. **ID:** 1-0-0
2. **Class:** 0-1-0
3. **Type:** 0-0-1

ID > Class > Type

```css
p {
	/* type selector */
}

#id{
	/* id selector */
}

.class{
	/* class selector */
}
```

Remember that styles cascade in CSS. BUT, specificity can override the cascades!

Assuming A  & B are styles and A appears before B in the CSS file. If A has a higher specificity, it will be applied, regardless of the cascade.
## Combining Selectors
```css
.hotdog p.mustard
{
 /* .hotdog is a prequalifer */
 /* p.mustard is the key selector */
}
```

The key selector specifies exactly what property receives a style. Generally, don't prefix a class selector with a type selector like we did above (p.mustard).
# Layering
Use classes to reuse styles, similar to inheritance in OOP. Assume we have a lot of buttons. All buttons have the same font, but may have different colours. Create two classes:
```css
.btn {
	font-size: 16;
}

.btn-red {
	background: red;
}
```

Then use it like so:
```html
<button class="btn btn-red"></button>
```