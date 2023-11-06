# Definition
Big O is a mathematical notation used to the define the time and memory requirements of an algorithm. It helps software engineers make decisions on which data structures or algorithms to use when solving a problem. 

	As input grows, how fast does the time taken or memory used grow?

Note that the growth is always with respect to input.

# What To Note When Calculating Big O
1. Checks for loops in the algorithm and how many times elements are iterated over.
2. Remove constants.
	In an expression like `3n + 2`, we'd simplify it to `O(n)` by removing the constants. Constants can vary based on external factors, so for simplicity sake, they are removed.
3. Consider the **worst case.** 
	Developers use Big O to consider how an algorithm scales. The worst case scenario answers this question: `With a large amount of input, how fast does this algorithm perform?`

# Common Big O notations
1. **O(1)** (Constant Time):
    - This represents an algorithm that executes in constant time regardless of the input size. It's the most efficient time complexity.
2. **O(log n)** (Logarithmic Time):
    - An algorithm with logarithmic time complexity reduces the problem size by a constant fraction with each step. Common in binary search.
3. **O(n)** (Linear Time):  
    - The running time of the algorithm is directly proportional to the size of the input. Linear algorithms perform one operation for each element in the input.
4. **O(n log n)** (Linearithmic Time): 
    - Algorithms with linearithmic time complexity often occur in efficient sorting algorithms like Merge Sort and Quick Sort.
5. **O(n^2)** (Quadratic Time): 
    - The running time grows with the square of the input size. This is common in nested loops and inefficient sorting algorithms like Bubble Sort.
6. **O(n^k)** (Polynomial Time):
    - Represents algorithms whose time complexity is a polynomial function of the input size. Higher values of k indicate more significant growth in running time.
7. **O(2^n)** (Exponential Time):
    - Algorithms with exponential time complexity grow rapidly as the input size increases. These are often considered highly inefficient.
8. **O(n!)** (Factorial Time):
    - Represents the worst-case scenario where the running time increases factorially with the input size. This is extremely inefficient.