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

The time complexity is **O(n).** For more on time complexity, refer to [[05-data-structures-and-algorithms/Data Structures/Big O Notation]].