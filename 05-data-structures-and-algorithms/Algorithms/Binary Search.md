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

The time complexity is **O(log n)**, because the search space reduces with each iteration. For more on time complexity, refer to [[05-data-structures-and-algorithms/Data Structures/Big O Notation]]. 