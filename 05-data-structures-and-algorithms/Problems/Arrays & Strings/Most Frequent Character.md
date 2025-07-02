> Write a function, _mostFrequentChar_, that takes in a string as an argument. The function should return the most frequent character of the string. If there are ties, return the character that appears earlier in the string.
> 
> You can assume that the input string is non-empty.

The approach I used is the same in both solutions. The time and space complexity are O(n) for both too. The only difference is how the count checking is performed.
I used a hash map to store each character & the number of times it appeared in the string.
# Solution #1
```ts
type CharCount = { [key: string]: number };

const mostFrequentChar = (s: string) => {
    let charCount: CharCount = {};

    for (let char of s) {
        if (!(char in charCount)) {
            charCount[char] = 0;
        }

        charCount[char]++;
    }

    let maxChar = "";
    let maxCount = -Infinity;
    for (const key in charCount) {
        if (charCount[key] > maxCount) {
            maxCount = charCount[key];
            maxChar = key;
        }
    }

    return maxChar;
};
```
Here, I used two variables - one to track the character that was currently the maximum & one to track the number of times it appeared. We only set a new maximum if the new count is greater than the previous. This way, `o` would be max in `potato`.
# Solution #2
```ts
type CharCount = { [key: string]: number };

const mostFrequentChar = (s: string) => {
    let charCount: CharCount = {};

    for (let char of s) {
        if (!(char in charCount)) {
            charCount[char] = 0;
        }

        charCount[char]++;
    }

    let best = null;
    for (const key in charCount)
    {
        if (best === null || charCount[key] > charCount[best])
        {
            best = key;
        }
    }

    return best;
};
```
Here, I do a lot differently.

I used `let...of` to iterate over each character in the string.
I used a single variable to store the current most frequent character. When comparing it to other keys, I used `charCount[best]` to directly access its value, rather than storing it in another variable.