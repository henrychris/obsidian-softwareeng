---
tags:
  - dsa
share: "true"
---
# Definition
Arrays are a single contiguous block of memory. Contiguous means they share a border, or touch each other.

4    h  i
\--   -- --
x    name

Above, is a representation of an array in memory. `x` is a variable holding the number 4. `name` is a string, or array of characters, holding the text `hi`. 

# Array Operations
## Insertion
This sets a section of memory in the array to a value, overwriting what was previously there. The time complexity varies:
1. **Insertion at the end**: the operation is typically straightforward and has a time complexity of `O(1)`. You place the new element in the next available slot in memory, and it doesn't require shifting any existing elements.
2. **Insertion at the beginning or between other elements:** it's more complex. You need to shift all elements after the insertion point to make room for the new element. This operation has a time complexity of O(n), where 'n' is the number of elements in the array.

## Getting
You provide an *index* representing the value you want. Using the width of the array's datatype (arrays contain values of the same type) and the index, it calculates the memory location of the value.
Assuming you have this array and want to fetch index 2:
+---+---+---+--+
| 1 | 2 | 3 | 4 | 5 |
+-+-+--+--+---+
*0   4   8  12  16* -> memory locations

The `int` data type uses up four bytes of memory. To calculate the memory location, we use:
`array memory address + (index * size)`.

`value address = 0 + (2 * 4) = 8`. The value at address 8 is 3. 
The time complexity of this operation is `O(1)`.

**NOTE**: The first element in an array is at index 0.
## Deletion
This removes an element from an array, the time complexity also varies.
1. **At the End**: Deleting an element from the end of an array is also straightforward and has a time complexity of O(1). You mark the space as empty or decrease the array size, but you don't need to shift any other elements.
2. **At the Beginning or Middle**: Deleting an element from the beginning or the middle of an array requires shifting all elements after the deletion point to close the gap. This operation has a time complexity of O(n), where 'n' is the number of elements in the array.

# Summary
- Arrays are a fixed size, contiguous block of memory.
- They do not grow automatically.


# Algorithms
## Linear Search
The easiest there is. Simply iterate over an array in search of a value. If the value is found, return true, else, return false.
```
function linear_search(haystack: number[], needle: number): boolean {
    for (let index = 0; index < haystack.length; index++) {
        if (haystack[index] == needle) {
            return true;
        }
    }
    return false;
}
```

## Binary Search
An efficient search algorithm used to find a specific element in a **sorted** array or list. It follows a divide-and-conquer approach, repeatedly dividing the search space in half until the desired element is found or determined to be absent.

```
function bs_list(haystack: number[], needle: number): boolean {

    let lowIndex = 0;
    let highIndex = haystack.length;

    do {
        const midIndex = Math.floor((lowIndex + highIndex) / 2);
        if (haystack[midIndex] === needle) {
            return true;
        }

        if (haystack[midIndex] > needle) {
            highIndex = midIndex;
        }
        else {
            lowIndex = midIndex + 1;
        }
    } while (lowIndex < highIndex);

    return false;
}
```

1. Set two variables to point to the start of the array, and to the last element in the array: `low` and `high`. 
2. Find the mid point in the array.
3. Compare the value at that mid point to the value being searched for:
	1. If value = target, return the index.
	2. if value > target, cut out the right side of the array. Set `high` to the index of the midpoint.
	3. if value < target, cut out the left side of the array. Set `low` to the midpoint, plus one to exclude the value.
4. Repeat while `low` < `high`.

## Bubble Sort
