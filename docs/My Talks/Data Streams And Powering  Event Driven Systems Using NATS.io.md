[GPT](https://chatgpt.com/c/aac46fa3-197a-4e62-aed0-4fa86319d2ba)
[Claude](https://claude.ai/chat/429ece95-a4c6-407b-903d-cd81e22d81bd)

im thinking
- talk about event driven systems, what they are and what problem they solve
- talk about NATS, the broker, and its features
- interact with the NATS server using the CLI
- show setup using docker
	- `docker run --name nats -p 4222:4222 -p 8222:8222 -d nats -js`
- demonstrate the features in isolation
- demonstrate the features tied together in building an event driven application
# Event Driven Systems
An event driven system uses events as a way for components to communicate within a system. The event publisher doesn't know who consumes the events, and the consumer need not know the specifics of the publisher, only the message contract.
It avoids tight coupling between components.

An **event** is a record of something that happened (a change) within a system or the real world. Events don't dictate what should happen next; they simply notify other parts of the system about the change.

In an event-driven system, there are three primary actors:
- **Producer (Emitter)**: Creates and publishes events.
- **Consumer**: Listens for events and performs actions in response.
- **Router**: Distributes events to consumers that are subscribed to them. Note that this isn't a manual component, but is abstracted away by the message broker. Rest easy, JS folk.
## Concepts
- **Idempotency**: Consumers must be able to process the same event multiple times without unintended effects.
- **Decoupling**: Services should be fully independent, with no knowledge of each other beyond the message contract. See more [here](https://serverlessland.com/event-driven-architecture/tight-coupling-vs-loose-coupling).
- **Eventual Consistency**: Data may not be perfectly synchronized across the system but will ultimately become consistent.
## Components
- **Event bus**: This is the key component that enables communication between producers and consumers. It handles routing events to the appropriate consumers.
- **Event store (optional):** stores a history of all events ever published. NATS allows us store all messages using Jetstream, that will be discussed later.
- Events related to a piece of data should only be published by one service.
## Benefits
- **Auto-Recovery**: If a service crashes, when it recovers, it can resume processing events from where it left off.
- **Service Independence**: If one service goes down, others can continue operating, unaffected.
- **Data Independence**: services store the data they need instead of coupling & sending API requests to others. Talk about distributed monoliths here.
## Problems
- Complexity
- In-order processing
- exactly-once processing
- guaranteed delivery - what if your server blows up after saving data to db but before publishing the event. hm?
## Designing Events
See: 
- [designing events - serverlessland](https://serverlessland.com/event-driven-architecture/designing-events)
- [put your events on a diet](https://particular.net/blog/putting-your-events-on-a-diet)
## Documenting Event-Driven Systems
see: 
- [event catalog](https://www.eventcatalog.dev/)
- [document events - serverlessland](https://serverlessland.com/event-driven-architecture/documenting-events)

# NATS
## Concepts
### Core NATS
This is the barebones functionality of NATS. A publish-subscribe model for sending messages using topics to address said messages.
#### Publish-Subscribe
A producer sends messages to a subject, and one or more consumers subscribe to that subject to receive messages. There's no persistence in Core NATS; consumers must be connected at the time the message is published.
Can be used in systems where message loss is tolerable.
##### Subjects & Wildcards
A subject is a string that serves as the address or topic for messages. Publishers send messages to a specific subject, and subscribers listen to a subject to receive messages.
Periods, `.`, can be used to denote hierachy & group messages by subject.
```text
ng.patient.patientId
gb.patient.patientId
us.patient.patientId
```

**Wildcards**
- "\*" (single-level): Matches a single token => appsettings.\*.json = appsettings.Development.json
- ">" (multi-level): Matches one or more tokens at the end of a subject => ng.> = ng.patient, ng.player, ng.officer

**Demo**: Play around with demo #1.
#### Queue Groups
Multiple consumers can form a queue group under a single subject. When a message is published, it is delivered to **only one** consumer in the group - used for to .

**Demo:** Jump to demo #4

#### Delivery Semantics
NATS core provides an ***at-most-once*** delivery guarantee. It is fire & forget. Messages are sent without waiting for acknowledgments. If a subscriber is not available or misses the message due to a crash, the message is lost.

**Demo:** To be demonstrated with JetStream.

1. Core NATS (demo 1 & 4)
	1. Pub-Sub
	2. Subjects & Wildcards
	3. Queue Groups
	4. How does it provide at most once delivery?
2. Jetstream (demo 2 &3)
	1. How does persistence work?
	2. How does it provide at least once delivery?
	3. Streams, Limits & Retention Policies
	4. Consumers, Types & How they interact with Streams
3. Monitoring & Observability
### JetStream
This is the built-in persistence engine which enables messages to be stored and replayed at a later time.
Published messages are stored in ***streams***. These streams allow for messages to be replayed, redelivered, or consumed at a later time, ensuring that messages aren't lost if consumers go offline.

**Mechanism**
- Streams are defined by a subject and can store messages based on retention policies like time-based, size-based, or message count limits.
- JetStream uses storage backends (e.g., memory or file on disk) to keep the messages, depending on configuration.

**Demo:** Go to demo 2 - service outage.
#### Streams, Limits & Retention Policies
##### [Streams](https://docs.nats.io/nats-concepts/jetstream/streams)
Logical containers for messages, identified by one or more subjects. Messages sent to a subject that matches the stream are stored. Messages may be stored in memory or on disk.

**Limits**: You can define message storage limits, including the maximum number of messages, the total size, or time duration.
**Retention Policies** define how messages are retained in the stream
    - **Limits-based**: Retain messages based on the configured limits.
    - **Interest-based**: Retain messages only as long as there's an active consumer.
    - **Work Queue**: Messages are deleted once acknowledged by any consumer.

**Demo:** Use demo #2 to play around with options. Except work queue, which is covered in demo #4.
##### [Consumers](https://docs.nats.io/nats-concepts/jetstream/consumers)
These are subscribers to a stream that can be configured to receive messages in different ways. They represent a view into the stream and track their position in the stream.

**Types**
- *Durable:* Retain state even if disconnected; can resume message consumption from where they left off.
- *Ephemeral*: Exist only as long as they're connected; once they disconnect, their state is lost.

#### Delivery Semantics
By default, JetStream provides ***at-least-once*** delivery. This means messages *can* be sent twice. However, it supports ***exactly-once*** publishing and consumption by combining [message deduplication](https://docs.nats.io/using-nats/developer/develop_jetstream/model_deep_dive#message-deduplication) & double acknowledgements.
The publisher uses message deduplication to ensure a duplicate message is ignored &

# **Demo**
1. **Basic Service Demo**
    - Show a simple **publish-subscribe** flow to illustrate event-driven communication between a producer and a consumer.
    - **DONE**
    - todo: Check if we can see what messages are stored by a nats server
2. **Service Outage**
    - **Pub/Sub Demo**: Simulate a service failure to demonstrate **message loss** (where messages are missed if the consumer is down).
    - **JetStream Persistence**: Show how JetStream ensures **message persistence**, even if a consumer temporarily goes offline.
	    - see: https://www.youtube.com/watch?v=_CN1OO7yN0I
	    - https://www.youtube.com/watch?v=ChSVWDW-874
	- **DONE**
	- check if messages stored in memory are wiped when the nats server is restarted
3. **Idempotency Demo**
    - Explain the importance of idempotent consumers
    - show problems with non-idempotent consumers
    - NATS may send the same message more than once, so demonstrate how to make consumers **idempotent**.
    - Core NATS = at most once delivery
    - Jetstream = at least once
    - **DONE**
4. **Load Balancing with Queue Groups**
    - Show how **queue groups** enable **load balancing**, where messages are evenly distributed across multiple consumers. This allows easy horizontal scaling without losing your mind in k8s.
	    - look into `nats micro`
	    - show how messages are distributed
5. **Clustering Demo**
    - Simulate shutting down a NATS server in a cluster and demonstrate how the system automatically **reconnects** and **resumes** message processing. NATS handles this automatically (I may need to subscribe to an event as it does this, or use monitoring).
    - Discuss NATS' **message limits** and how it handles throughput under different loads.
6. **Inter-Language Operability**
    - Showcase **multi-language interoperability** using NATS clients in different languages like **JavaScript**, **Go**, and **C#**.
    - write a demo for two different languages and show inter opearability
7. **Other NATS Features**
    - Highlight additional NATS capabilities like its **key-value store**, which can serve as an alternative to Redis for certain use cases.
    - Don't go in-depth for this. It's not core to the talk.
8. **Simple event-based system** 
	- 

# Sources
- [goperCon 2021](https://www.youtube.com/watch?v=NvmGgaWxx_U)
- [Events, Event Sourcing, and the Path Forward](https://relistan.com/event-sourcing-and-event-bus?s=09)
- [event driven microservices - Synadia](https://www.slideshare.net/slideshow/eventdriven-microservices-with-nats-streaming-95207688/95207688#10)
- [serverless land](https://serverlessland.com/event-driven-architecture/intro)
- [We need to talk about NATS](https://www.youtube.com/watch?v=AiUazlrtgyU) - it is actually fucking powerful bro

# Repo Structure
Each heading under demo should be a folder. 