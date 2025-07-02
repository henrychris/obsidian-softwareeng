> Write a function, _pairSum_, that takes in an array and a target sum as arguments. The function should return an array containing a pair of indices whose elements sum to the given target. The indices returned must be unique.
> 
> Be sure to return the indices, not the elements themselves. There is guaranteed to be one such pair that sums to the target.

# Solution #1
First, we brute force a solution using nested for loops. The time complexity is $O(n^2)$ and the space complexity is $O(1)$.
```ts
const pairSum = (numbers: number[], targetSum: number) => {
    for (let index = 0; index < numbers.length; index++) {
        for (let innerIndex = 1; innerIndex < numbers.length; innerIndex++) {
            const prevNumber = numbers[index];
            const nextNumber = numbers[innerIndex];

            if (nextNumber + prevNumber === targetSum) {
                return [index, innerIndex];
            }
        }
    }
};
```
# Solution #2
We have a target sum as an argument. As we iterate through the [[05-data-structures-and-algorithms/Data Structures/Arrays]], we calculate the `complement` by subtracting the value at the current index from our target. Then, we check if a key with this complement value exists in our hash map. 
Our hashmap stores values & their indexes: `{ 3:0, 2:1, 5:2 }`. If the complement does not exist, then we add the current value to the hash map. 
This solution is $O(n)$ for both time and space complexity. For more on complexity analysis, refer to [[05-data-structures-and-algorithms/Data Structures/Big O Notation]]. 
```ts
type NumStuff = { [key: number]: number };
const pairSum = (numbers: number[], targetSum: number) => {
    const numStuff: NumStuff = {};

    for (let index = 0; index < numbers.length; index++) {
        const complement = targetSum - numbers[index];

        if (complement in numStuff) {
            return [numStuff[complement], index];
        }

        numStuff[numbers[index]] = index;
    }
};
```
