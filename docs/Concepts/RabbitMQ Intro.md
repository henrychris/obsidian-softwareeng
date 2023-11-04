#rabbitMQ 
It is a message broker that implements the AMQP message model (v0.91). Instead of producing messages directly to a **queue**, messages go to an **exchange**. Exchanges receive all messages and distribute them as they are addressed.
An exchange can connect to many queues, and the queues are connected to the consuming services (many services can connect to one queue). The exchanges use connections called **bindings**, which can be referenced using a **binding key**.
RabbitMQ is cloud-friendly, language independent, highly secure, utilizes acknowledgments, has a rich plugin ecosystem and comes with management UI and CLI tools.

More on [[Message Brokers]]. 
### Types of Exchanges
1. **Fanout** - As messages are produced, they are duplicated and sent to every connected queue. Binding keys are ignored so just use an empty string.
2. **Direct** - As messages are produced, they receive a **routing key** (at the producer). The key is compared to the binding key of the queue, and if they match, it moves on to that queue (and the services).
	In code, the binding key is set when binding the queue to exchange: 
	`channel.QueueBind(queueName, exchangeName, bindingKey);`
3. **Topic** - As messages are produced, they receive both a **routing key** AND a **topic**. Topics consist of words separated by periods. First, it checks that the routing key matches a binding. If not, the message is not delivered. Next, it uses the topic to further filter which queues receive the message.
		Consider: 
		- Queue A is bound with a pattern like "stock.\**.nyse."
		- Queue B is bound with a pattern like "stock.apple.\*"
		- Queue C is bound with a pattern like "weather.usa.california."
		If a message with the routing key "stock.apple.nyse" is published:
		- Queue A will receive the message as it matches the topic pattern.
		- Queue B will receive the message as well.
		- Queue C won't receive as it doesn't match the pattern.
4. **Header**- As messages are produced, the routing key is ignored completely and the message header is used to filter.
5. **Default/Nameless**- Unique to RabbitMQ, the routing key is tied to the queue name. Messages are sent to a queue that has the same name as its routing key.

### Keywords
1. **Exchange**: An exchange is a routing mechanism that receives messages from producers and routes them to one or more queues based on certain criteria.
2. **Topic**: A topic is a pattern or string used to filter messages. Topics consist of words or phrases separated by periods (e.g., "stock.usd.nyse" or "weather.usa.california"). Each word in a topic can be seen as a routing key, and wildcards can be used to match multiple words or phrases.
3. **Routing Key**: A routing key is a single word or phrase that a producer specifies when publishing a message. It is used to match against topics.
4. **Binding**: A binding is a relationship between an exchange and a queue, where the exchange is configured to route messages to the queue based on specific routing keys and topics.
5. **Wildcard Characters**: In topic exchanges, two wildcard characters are commonly used:
    - `*` (asterisk): Matches a single word or phrase in a topic.
    - `#` (hash): Matches one or more words or phrases in a topic.
6. **Queue:** a buffer that stores messages.
7. **Consumer:** a user application that receives messages.
8. **Producer:** a user application that sends messages.