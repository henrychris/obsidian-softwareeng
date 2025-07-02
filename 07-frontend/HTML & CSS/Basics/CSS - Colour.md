There are three ways to use colour in CSS:

## RGB
```css
color: rgb(0, 0, 255)

/* OR */

color: rgba(0, 0, 0, 0.5)
```

For `rgb` and `rgba`, the first three inputs are integers from 0 - 255. For `rgba`, the last input is a decimal value from 0 - 1. It represents the opacity of the colour.

## HSL
This stands for Hue, Saturation and Lighting.
```css
color: hsl(0, 0%, 0%)

/* OR */

color: hsla(0, 0%, 0%, 0.4);
```
For `hsl` and `hsla`, the first input is an integer from 0 - 360. The second and third inputs are percentages between 0 - 100. For `hsla`, the last input is a decimal value from 0 - 1. It represents the opacity of the colour.

# Hex
I believe you know this already. For the six characters hex, each set of two characters represents an RGB value when converted to base 10.

e.g. `#FFFFFF`.
FF = 255.
Therefore, `#FFFFFF` = `rgb(255, 255, 255)`.
