---
share: "true"
---
#software-architecture
# Intro
**Message brokers** are a piece of software that act as an intermediary between software systems. One system is a *producer* that creates messages, and the other is a *consumer* that subscribe to channels and receive messages. A *message* is simply a binary blob of data. 
They help decouple systems, as producers and consumers need not directly interact or *know* about one another. The means of *passing* the messages can change, but the applications need not know that.
## Why are they useful?
1. **Fault Tolerance**: In case a consumer fails or becomes unavailable, the message broker can store messages until the consumer is ready to process them. This enhances system fault tolerance.
2. **Message Persistence**: Some message brokers offer message persistence, ensuring that messages are not lost even in the case of system failures.
3. **Asynchronous Communication**: Message brokers enable asynchronous communication between components. Producers can continue their tasks without waiting for consumers to process messages immediately.
4. **Load Balancing**: Message brokers can distribute messages to multiple consumers, balancing the workload. This is particularly useful for ensuring fair processing when dealing with a large number of messages.
5. **Scalability**: Message brokers can be distributed and scaled to handle increased message loads and provide high availability. They are a key component in building scalable and resilient systems.

Related: [What is RabbitMQ?](https://www.youtube.com/watch?v=7rkeORD4jSw), [[RabbitMQ Intro]]