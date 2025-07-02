---
share: "true"
tags:
  - dsa
---
# Algorithms 101
An algorithm is a set of instructions to be followed to achieve a certain goal. *Algorithm design* aims to create an **efficient** set of instructions, that can be **effectively** used to solve a real-world problem.

## Phases of an algorithm

```
Problem Statement -> Algorithm -> Computing Device

Input -> Computing Device -> Output
```
There are two phases:
1. **Design:** An iterative phase where the architecture and logic of the algorithm are considered. In this stage, different possible solutions are conceptualised and compared against one another. The final algorithm should be an efficient solution that provides both satisfactory performance and reasonable accuracy at the same time.
2. **Coding:** The designed algorithm is converted into a computer program.

Both phases are iterative. The aim is an algorithm that meets both functional and non-functional requirements.
- **Functional:** requirements that dictate what the right output for a piece of data should be. **Algorithm validation** checks that an algorithm meets its functional requirements.
- **Non-functional:** For algorithms, these usually measure it's performance given a set of data. **Performance analysis** of an algorithm is about verifying that it meets its main non-functional requirement: performance.

Next is deployment. The production environment must suit the algorithm being run. For instance, parallelizable algorithms may require a cluster with an appropriate number of nodes for efficient execution.

## Specifying the Logic 
It's important to specify the logic and architecture of the algorithm before implementing. The easiest way is to use [[../../03-concepts/Pseudocode]]. But before this, you need to completely understand the problem and write the steps in plain English, **then**, you convert it to pseudocode. 

However, in some cases, you can represent the logic in a programming language - if it is that simple.

# Algorithm Design Techniques
When designing an algorithm, keep the following concerns in mind as you iterate:
- **Concern 1**: Is this algorithm producing the result we expected?
- **Concern 2**: Is this the most optimal way to get these results?
- **Concern 3**: How is the algorithm going to perform on larger datasets?

When designing a solution, you would find it beneficial to understand the complexity of the problem (and maybe even **categorise** it).

## Algorithm Categories
- **Data-intensive algorithms**: they are characterized by their heavy reliance on data processing and manipulation. These algorithms typically involve large datasets that need to be analysed, transformed, or queried. **Example:** Algorithms for data analytics, database queries, and data mining.
- **Compute-intensive algorithms**: - they are those that demand significant computational power or processing capabilities. These algorithms involve complex mathematical calculations, simulations, or other operations that require substantial CPU resources. **Example:** Scientific simulations, weather modelling, and certain types of encryption algorithms can be compute-intensive.
- **Both data and compute-intensive algorithms**: Algorithms that are both data and compute-intensive require substantial processing power for both data manipulation and complex computations. These algorithms often involve a combination of large-scale data processing and intensive mathematical or computational operations. **Example:** Machine learning algorithms, such as deep learning neural networks, often fall into this category. Training a neural network involves processing large datasets (data-intensive) and performing numerous mathematical computations during the training process (compute-intensive).