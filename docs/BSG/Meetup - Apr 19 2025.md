# Sodiq Akinjobi
- Soft skills matter now more than ever.
- As a dev, the true test of knowledge is being able to explain a concept to your parents. Or a five year old. Or a business exec who has never touched a computer.
- **Adapatability:** Thriving among changing circumstances and personalities
- **Collaboration:** Working effectively across disciplines and personalities
- Skill isn't all that matters, relationships do too. Often more than skill.
- **Emotional Intelligence:** Reading the room and managing interactions
- How to move from being an *individual contributor* to *growing as a group*. Use community to power your growth.
## Classwork
1. When last did you receive feedback on your communication style? What surprised you? What do you think you need to improve?
	- My co-founder mentioned that I often switch between different contexts which often seems random. The context switch is often followed by a vague reference to something else that causes listeners to get confused.
	- I need to improve how I carry people along while communicating. I oculd explicitly say, "oh unrelated to that, this made me think of X".
2. What soft skill do you rely on most in day-to-day work? Which do you use least?
	- I write a lot. I have to write about what I am working on, what I am having problems with, and what I am trying to implement.
	- I am not sure what I use the least.
3. What would your coworkers say is your greatest interpersonal strength?
	- My dependability. If I say I do something, I will.
4. What's one soft skill gap that has directly impacted a technical outcome in your work?
	- Inability to man-manage. In my role at Lights on Heights, my inability to extend grace/patience to coworkers not as good as me caused resentment, causing speed of implementation to slow.
	- It's a lack of empathy and patience.
5. How do you currently track your growth in non-technical areas?
	- I don't.
## Other
1. how would my communication needs change as I move from individual contributor to technical lead?
	- need to know a guy that knows a guy, that knows a guy
2. the human ability to communicate, connect and collaborate is invaluable in the age of ai
# Deep Dive Into Monitoring - Mbaoma Mary
Alerts ensure timely resolution of system anomalies and minimise downtime. They can be:
- Threshold-based: when metrics exceed predefined thresholds
- Anomaly-based: when metrics exhibit unusual patterns or behaviour, e.g excessive memory use or incoming requests
- https://github.com/Emmanuerl/prom-demo.git
# Building a Conversational Chatbot - Ifihan
The paper, [Attention Is All You Need](https://proceedings.neurips.cc/paper_files/paper/2017/file/3f5ee243547dee91fbd053c1c4a845aa-Paper.pdf) introduced transformer architecture. The neural network design that changed the AI landscape. 

LLMs are giant transformer networks trained on massive datasets that predict the most likely next token in a sequence. 

Multimodal models can accept and output data in multiple forms

## Prompt Engineering
A good prompt requires: clarity, context, structure and examples. This is why AI agents like Cursor work best when you have an existing codebase filled with high-quality code. Remember, computers have one key principle: garbage in, garbage out.
### Techniques
- Zero-Shot Prompting
- Few-Shot Prompting
- Chain of Thought Prompting
- Meta Prompting
- Prompt Chaining
- Retrieval Augmented Generation
### Memory
Langchain allows you to implement memory for chatbots. However, you must remember that as the number of tokens in memory increases, the bot will start to lose context and forget. This is why you need to start a new chat after a certain amount of messages
# System Design
Generally, you want to lay out:
1. The functional requirements, what the system should do.
2. The non functional requirements, how the system should behave.
3. Your assumptions about the system, its traffic and load
4. The models in the system and what data you will store

You should start with solving the core of the problem. For example, if designing a social media app where users can view a feed of posts made by people they follow. The main thing is:
- Fetch people a user follows
- Fetch items in the feed
- Only include feed items that are in the list of people the user follows.
From that we can extrapolate the db models, the services needed, the type of database to use and so on. Start simple, then scale.
# Reverse Proxies
A reverse proxy is a server that sits in front of another server and forwards client requests to it. It hides the main app structure and can handle load balancing, caching and security.
Some popular ones are NGINX and Caddy.
## Sample Scenarios
1. building a chat app and needing to balance users across multiple servers
2. an app serves a lot of images and js files. i need to reduce load on the app servers
3. your frontend js loads slowly due to large bundle sizes
4. you wish to monitor and log all incoming http requests without modifiying backend services
5. you need to restrict admin access to specific IP addresses
## Functional Requirements
1. Configuration - read configuration from JSON.
	- Port - the port to listen on
	- StaticDir - the directory to server static files
	- Routes
		- Path - the endpoint route
		- Targets - the urls to forward the requests to.
	- Auth gateway - the URL to send requests to to authenticate users.
2. Serve static files
3. Has an auth gateway
4. Implements round-robin to share load
### Implementation
1. Check for a json config file in the current directory
2. Deserialise the data and validate that exact data is needed
3. Spin up a server at specified port
4. Serve static files if requested
	- Update setting validation to check that specified static file path exists
5. 