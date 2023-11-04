---
share: "true"
---

#rabbitMQ 
I could easily use a library like MassTransit to implement RabbitMQ, but to truly get a grasp of the technology, I will be implementing it using abstractions.

# Basics

## Producer
1. When using RabbitMQ, you first need to create a connection with the host.
```
var factory = new ConnectionFactory  
{  
    HostName = "localhost"  
};  
  
using var connection = factory.CreateConnection();  
using var channel = connection.CreateModel();
```

2. Next, you create your exchange and the queues that exist on it. Make sure to bind the queues to the exchange. Here I use a direct queue, find more info here: [[RabbitMQ Intro]] 
```
channel.ExchangeDeclare(exchangeName, ExchangeType.Direct);

// Queues are only created if they don't already exist.  
channel.QueueDeclare(queueName, false, false, false, null);

// Bind the queues to the exchange using routing keys.  
// This means that messages sent to the exchange with specific routing keys  
// will be routed to the corresponding queue.  
channel.QueueBind(queueName, exchangeName, routingKey);  
```

3. Then you can publish messages to the queue:
```
channel.BasicPublish(exchangeName, queueName, basicProperties: null, messageBody);
```

## Consumer
A consumer would follow the same procedure as the producer (except publishing). That is to connect to the host and setup the queue bindings (in case they don't already exist).

1. Set up the consumer
```
var channel = factory.CreateConnection();
// stuff
var consumer = new EventingBasicConsumer(channel);

consumer.Received += (_, args) =>  
{  
   
    // Extract the message body and convert it to a string.  
    var body = args.Body.ToArray();  
    var message = Encoding.UTF8.GetString(body);  
  
    // Display the received message and acknowledge it.  
    Console.WriteLine($" [x] Received {message}");  
    channel.BasicAck(args.DeliveryTag, false);  
	
	// you can choose not to acknowledge the message. it's fine, but note that it can lead to errors.
	// Only leave messages unacknowledged when errors occur.
};
```

2. Start consuming messages:
```
var consumerTag = channel.BasicConsume(appleQueue, false, consumer);
```

3. Clean up when done. We are cleaning up here, because we create a new instance of channel, instead of using a  `using` statement.
```
channel.BasicCancel(consumerTag);  
channel.Close();
```

That's the basic flow.

**NOTE:** RabbitMQ does not allow redefinition of existing queues with new parameters. You'd have to to create a new queue with the new settings. Or delete the existing queue.

**NOTE:** This line of code: `channel.BasicQos(0, 1, false);` Sets the prefetch size. In normal words, it tells RabbitMQ not to send new messages to a worker, until the previous **n** messages have been processed and acknowledged. 
If it is set to 10, and only1 out of 10 messages sent is acknowledged, then RabbitMQ will send 1 more message to make up for it. Each message can be handled in the `consumer.Received` event handler, but **only** send acknowledgments after successful processing.

**NOTE:** You can have the server generate queue names for you. This is recommended for fanout exchanges. Just declare a queue with this code: `var queueName = channel.QueueDeclare().QueueName;`
Then bind it to the exchange like so: 
```
channel.QueueBind(queue: queueName,  
    exchange: AppConstants.LogExchange,  
    routingKey: string.Empty);
```

# Intermediate Concepts
## Binding Queues to Exchanges
Normally, you would bind a queue to an exchange with one binding key. However, you can also assign multiple binding keys to a queue. To do that use this snippet:
```
string exchangeName = "myExchange";
string queueName = "myQueue";
string[] bindingKeys = new string[] { "key1", "key2", "key3" };

foreach (string bindingKey in bindingKeys)
{
    channel.QueueBind(queueName, exchangeName, bindingKey);
}
```

The binding keys are up to you of course. The main thing is to ensure the queues are bound with all possible routing keys, and messages are published with **correct** keys. Else, messages would get lost on the server.

## Topics
Topic exchanges (more here: [[RabbitMQ Intro]]), 
**todo**: give short definition of topic exchanges.

## Setting Up RabbitMQ in .NET
1. Install RabbitMQ with Docker: `docker run -d --hostname my-rabit --name rabbit-learn -p 15672:15672 -p 5672:5672 rabbitmq:3-management`


[Building a Message Bus with .NET Core and RabbitMQ | by Fatih Dumanlı | Medium](https://fatihdumanli.medium.com/build-a-message-bus-implementation-with-net-core-and-rabbitmq-9ba350b777f4)
[A Beginners Guideline to RabbitMq and MassTransit(Part 2): Implement RabbitMQ in Code with MassTransit | by tong eric | Bina Nusantara IT Division | Medium](https://medium.com/bina-nusantara-it-division/a-beginners-guideline-to-rabbitmq-and-masstransit-part-2-implement-rabbitmq-in-code-with-af0503db2613)
