> Write a function, _anagrams_, that takes in two strings as arguments. The function should return a boolean indicating whether or not the strings are anagrams. Anagrams are strings that contain the same characters, but in any order.
> 
> Assume two inputs $S1, \space S2$. Both are strings.
# Solution #1
Anagrams contain the same characters but in any order. As such we can do the following:
- Check that both strings are of the same length, if not, return *false*.
- Sort $S1$ & $S2$ in alphabetical order.
- Iterate over each character in $S1$ checking that the corresponding character in $S2$ is the same.
	- If any character differs, return *false*.
- Else, return *true*.

```ts
function anagrams(s1: string, s2: string) {
    if (s1.length !== s2.length) {
        return false;
    }

    s1 = s1.split("").sort().join("");
    s2 = s2.split("").sort().join("");

    return s1 === s2;
}
```

This is $O(n \space log \space n)$ time complexity. `split` and `join` are $O(N)$ as well as the string comparison `s1 === s2`.
`sort` is $O(n \space log \space n)$. Since these operations occur after another, we have:
$$\begin{align}
O(n + n + n + (n \log n)) \implies O(n \log n)
\end{align}
$$
Space complexity is $O(n)$. We create 2 new arrays and assign to `s1` & `s2`. This is originally $O(n + n)$ which is then simplified.
# Solution #2
Here we use hash maps to optimise the solution. We store each character as a key in the map. Each time the character is found in `s1` we add or find a key and increment its value by 1. Each time we find the character in `s2`, we add or find the key and decrement its value by 1.
If the same characters occur in both strings, with the same frequency, the final value for all keys should be 0. If any key has a positive or negative value, the strings are not anagrams.
```ts
type CharCount = { [key: string]: number };

function anagrams(s1: string, s2: string) {
    if (s1.length !== s2.length) {
        return false;
    }

    const charCount: CharCount = {};

    for (let i = 0; i < s1.length; i++) {
        if (!(s1[i] in charCount)) {
	        // if key not in hashMap, set and initialise the key's value
            charCount[s1[i]] = 0;
        }
        if (!(s2[i] in charCount)) {
            charCount[s2[i]] = 0;
        }

        charCount[s1[i]]++;
        charCount[s2[i]]--;
    }

    for (const key in charCount) {
        if (charCount[key] !== 0) {
            return false;
        }
    }

    return true;
}
```

// add space and time complexity

