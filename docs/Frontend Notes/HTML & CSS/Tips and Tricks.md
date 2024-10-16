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
