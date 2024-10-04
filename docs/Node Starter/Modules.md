# CommonJS Modules
Each file in Node is treated as a separate module. 

```js 
// index.js
const square = require("./square.js");
```

```js
// square.js

// export one prop per time
export.area = function (width) {
  return width * width;
};

// export an entire class
module.exports = class Square {
  constructor(width) {
    this.width = width;
  }

  area() {
    return this.width ** 2;
  }
}; 
```