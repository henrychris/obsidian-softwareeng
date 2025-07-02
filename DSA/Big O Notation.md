Big O is notation used to approximately describe the performance of algorithms, usually with an emphasis on how performance *scales* with *input size*.
# Simplification Rules
1. Drop any constant factors
$$\begin{align}
O(5n) \implies O(n) \\ \\

O(\frac{n}{2}) \implies O(\frac{1}{2} * n) => O(n) \\ \\
\end{align}
$$
2. In a sum, drop smaller items
$$\begin{align}
O(n^{2} + n) \implies O(n^{2}) \\ \\

O(n + n + n^{4}) \implies O(n^{4}) \\ \\

O(n^{4} - n^{3}) \implies O(n^{4})
\end{align}
$$
*Do not subtract. This is not algebra!*

Algorithms are measured on a scale & used to measure time and space complexity.
- **Space Complexity:** How much memory an algorithm uses
- **Time Complexity:** How much time an algorithm takes to run, based on the size of the input. It is not the running time, but instead the number of operations needed to run.
# Scale
![[complexity.png]]

- $O(n!)$ - factorial
- $O(c^n)$ - exponential
- $O(n^c)$ - polynomial
- $O(n \space log \space n)$
- $O(n)$ - linear
- $O(log(n))$ - logarithmic
- $O(1)$ - constant. Performance does not scale with input, it uses the same space or no. of operations regardless of input size.

Regarding simplification, the chart above is important. A big O measurement is a large term than the one below it in the chart. As input size increases, the value of the higher terms increase dramatically compared to those below it.

An example:
$$
O(2^{n} + n^{10})
$$
$2^{n}$ = exponential
$n^{10}$ = polynomial

Assume n = 100
$$\begin{align}
2^{10} = 1.26 \times 10^{30} \\ \\

10^{10} = 1 \times 10^{20}
\end{align}
$$

Therefore, just like in the chart, exponential > polynomial.

# Measuring Complexity
- When measuring space complexity
	- no variables created = $O(1)$.
	- if adding variables to an array, it might be $O(n)$ if it depends on the input size, $n$.

- When measuring time complexity
	- When an operation occurs within another (like within a loop), multiply their complexities together
	- A loop within a loop is $O(n^{2})$.
	- When operations occur in sequential order (not within one another), add their complexities together
## Examples 
1. Sum of array elements
```js
function sumArray(arr) {
    let sum = 0;
    for (let i = 0; i < arr.length; i++) {
        sum += arr[i];
    }
    return sum;
}
```

Time complexity = $O(n)$ because the loop iterates over each item in the array.
Space complexity = $O(1)$ because only one variable is created.

2. Factorial Calculation
```js
function factorial(n) {
    if (n === 0) {
        return 1;
    }
    return n * factorial(n - 1);
}
```

The time complexity is $O(n)$. The function will be called $n$ times until a result is returned.
The space complexity is O(n) as well. Each time the function is called, a new layer is place on the stack. 