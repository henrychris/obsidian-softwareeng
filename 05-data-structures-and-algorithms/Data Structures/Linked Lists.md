---
share: "true"
---
# Definition
A linked list is a linear data structure used for organizing and storing a collection of elements, known as **nodes**. Unlike arrays, which store elements in contiguous memory locations, linked lists store elements in a way that each element, called a node, contains both data and a reference (or link) to the next node in the sequence. 

A singly linked list stores data and link to the **next** node.
A doubly linked list stores data and links to both the **previous** and **next** node.
## Key Terms
1. **Nodes**: The fundamental building blocks of a linked list are nodes. Each node contains two main components:
    - **Data**: The data element or value that the node holds. This can be of any data type.
    - **Next (or Link)**: A reference or link to the next node in the sequence. This reference points to the memory location or address of the next node. In a singly linked list, each node has only a "next" reference, while in a doubly linked list, nodes may have both "next" and "previous" references.
2. **Head**: The first node of the linked list is called the head. It serves as the starting point for traversing the list. If the list is empty, the head may be null.
3. **Tail**: The last node of the linked list is called the tail. In singly linked lists, the tail node's "next" reference is usually null. In doubly linked lists, it has both "next" and "previous" references.

## Complexity
- **Get head/tail**: If there's a pointer to the head or tail, it is **O(1)**.
- **Delete head/tail**: If there's a pointer to the head or tail, it is **O(1)**.
- **Get Within The List**: varies with the traversal cost.
- **Delete Within The List**: varies with the traversal cost.
- **Insert Within The List**: varies with the traversal cost.
- **Append**: If there's a pointer to the head or tail, it is **O(1)**.
- **Prepend**: If there's a pointer to the head or tail, it is **O(1)**.

## Comparison with Arrays
In contrast to [[05-data-structures-and-algorithms/Data Structures/Arrays]], linked lists do not store elements in contiguous memory. This allows for efficient O(1) insertions and deletions at the beginning or end (if pointers are maintained), but random access and middle operations are O(n) due to the need for traversal.

