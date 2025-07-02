This is also rather simple. Bubble sort loops through the array, over each element. If an element is larger than the one next to it, their positions are swapped.

```
function bubble_sort(arr: number[]): void {  
    // Outer loop controls the number of passes through the array  
    for (let i = 0; i < arr.length; i++) {  
        // Inner loop iterates through the unsorted portion of the array  
        for (let j = 0; j < arr.length - 1 - i; j++) {  
            // Compare adjacent elements and swap if they are in the wrong order  
            const temp = arr[j];  
            if (arr[j] > arr[j + 1]) {  
                // Swap the elements if they are out of order  
                arr[j] = arr[j + 1];  
                arr[j + 1] = temp;  
            }  
        }  
    }  
}
```

The time complexity is **O(n ^ 2).** The input is iterated over twice. For more on time complexity, refer to [[05-data-structures-and-algorithms/Data Structures/Big O Notation]].
