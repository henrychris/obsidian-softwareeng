# Centring Content
Setting the `width` of a block-level element keeps it from stretching to the edges of its container. Use `auto` left and right margins to centre it within the container.
To improve handling on small screens, use `max-width`.
# Shorthand for Margin and Padding
```css
margin/padding: 10px /* all sides are 10px */
margin/padding: 10px 20px /* top and bottom are 10px, left and right are 20px */
margin/padding: top, right, bottom, left
```
# Remove Space between Inline-Block Elements
Place the opening tag of a succeeding element immediately after the closing tag of a previous element.
```html
<section>
  ...
</section><section>
  ...
</section>
```

Or start a comment immediately after closing an element tag, and end it immediately before a new element tag:
```html
<section>
  ...
</section><!--
--><section>
  ...
</section>
```

# Aligning Lists With Text
```css
ul / ol {
	list-style-position: inside;
	padding-left: 0;
}
```
The first rule includes the bullets with the text. The second removes any padding around the list items.
Reference: [Aligning List With Your Text](https://since1979.dev/aligning-your-lists-with-your-text/)

There is another approach, where you keep the `list-style-position` as default (outside) and instead add padding to the `ul` or `ol`. This keeps text on subsequent lines aligned with the first line.

```css
ul,
ol {
    display: block;
    padding-inline-start: 1.5rem;
}
```

# Indent Text In Lists
Here, we want to move the text in the list **away** from the bullet. We create a class & apply it to text wrapped in a `span`.
```css
.list-text {
    position: relative;
    left: 1rem;
  }
```

```html
<ol class="normal-text">
      <li>
          <span class="list-text">
              In a bowl, beat the eggs with a pinch of
              salt and pepper until they are well mixed.
              You can add a tablespoon of water or milk
              for a fluffier texture.
          </span>
      </li>
  </ol>
```
# Manipulate List Bullet
```css
ul li::marker {
   font-size: 0.8rem;
   color: var(--rose-800);
}
```

# Remove Borders On Last Table Row
```css
table tr:last-child {
    border-bottom: none;
}
```