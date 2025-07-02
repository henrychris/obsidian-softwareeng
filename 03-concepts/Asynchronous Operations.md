---
share: "true"
---
In general, you should use asynchronous methods when you expect ***I/O-bound*** or ***CPU-bound*** work that may **block** the thread. It's a good practice to use asynchronous methods when dealing with I/O-bound operations to improve the responsiveness of your application, but not every method needs to be asynchronous if it doesn't involve such operations. Message brokers, for example, are a common way to achieve asynchronous communication between different parts of a system. See: [[06-backend/Message Brokers]]