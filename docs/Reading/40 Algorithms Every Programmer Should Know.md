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
It's important to specify the logic and architecture of the algorithm before implementing. The easiest way is to use [[Pseudocode]]. But before this, you need to completely understand the problem and write the steps in plain English, **then**, you convert it to pseudocode. 

However, in some cases, you can represent the logic in a programming language - if it is that simple.

# Algorithm Design Techniques
When designing an algorithm, keep the following concerns in mind as you iterate:
- **Concern 1**: Is this algorithm producing the result we expected?
- **Concern 2**: Is this the most optimal way to get these results?
- **Concern 3**: How is the algorithm going to perform on larger datasets?

When designing a solution, you would find it beneficial to understand the complexity of the problem (and maybe even **categorise** it).

## Algorithm Categories
- **Data-intensive algorithms**: Data-intensive algorithms are designed to deal with a large amount of data. 
- **Compute-intensive algorithms**: Compute-intensive algorithms have considerable processing requirements but do not involve large amounts of data.
- **Both data and compute-intensive algorithms**: There are certain algorithms that deal with a large amount of data and also have considerable computing requirements.