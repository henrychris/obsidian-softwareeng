This, `...` is the spread or rest operator. The name changes depending on the context it is used.
## Spread
It is used to spread the contents of an array or object into an array.
```ts
const arr1 = [1, 2, 3]; 
const arr2 = [...arr1, 4, 5]; // [1, 2, 3, 4, 5] 

const obj1 = { a: 1, b: 2 };
const obj2 = { ...obj1, c: 3 }; // { a: 1, b: 2, c: 3 }
```
## Rest
It is used to pack the remaining items in an array, or properties in an object into a single variable.
```ts
const [a, ...b] = [1, 2, 4, 5]; // a = 1, b = [2, 4, 5];
// note use square brackets when packing arrays
```