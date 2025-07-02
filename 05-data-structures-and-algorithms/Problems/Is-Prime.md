Write an algorithm to check if a number is prime or not. This problem demonstrates how algorithmic optimizations can significantly impact performance, a concept central to [[05-data-structures-and-algorithms/Data Structures/Big O Notation]].
# Solution #1
We can brute force a solution by dividing the number by every number before it, except itself & 1.
```ts
export function isPrime(num: number): boolean {
    if (num === 1) {
        // 1 is not a prime number
        return false;
    }

    for (let index = 2; index <= num; index++) {
        if (num % index === 0) {
            return false;
        }
    }

    return true;
}
```
# Solution #2
We can optimise the solution above by only dividing by numbers less than or equal to its square root.

If a number is not prime, it has factors. Take *n as 16*. It has the following pairs: (2, 8) & (4,4).

The root of 16 is 4. Above, a factor in each pair is less than or equal to 4. We can divide 16 by *2* and *4*. Assuming we couldn't, then we won't be able to find any number to divide into it past 4.

No matter what, one factor in a pair that multiply to get `n` will always be less than the root of `n`.

```ts
function isPrime(num: number): boolean {
    if (num === 1) {
        // 1 is not a prime number
        return false;
    }

    for (let index = 2; index <= Math.sqrt(num); index++) {
        if (num % index === 0) {
            return false;
        }
    }

    return true;
}
```