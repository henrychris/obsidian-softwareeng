## Key takeaways — TL;DR
- Small, focused teams can build mission-critical infrastructure quickly. Eight engineers built a production-grade core banking system in ~6 months.
- Invest in the invisible work first. Two months of foundation work (contracts, schemas, infra, observability) unlocked rapid delivery afterwards.
- Design for 10x. Building for future scale (not just present traffic) prevents expensive rewrites as you grow.
- Keep the money path synchronous. Real-time transaction processing must be atomic — use queues only for side effects.
- Be pragmatic with technology: prefer tools the team knows, but add thin abstractions (e.g., Dapr) to avoid long-term lock-in.    
- Control matters: custom micro-ORMs or lightweight libraries can give performance and DX that full ORMs don’t.    
- Concurrency ≠ magic: use optimistic row-versioning + retries to make money operations safe under contention.    
- Make observability and failure-handling first-class: multi-AZ, automatic failover, distributed tracing, and regular snapshots reduce blast radius.    
- Building often beats buying when you need speed, flexibility, and data ownership — but only if you have the right people, leadership trust, and discipline.    
- Operational outcome metrics to watch: end-to-end latency, peak RPS (design vs actual), outage frequency, and cost vs vendor baseline.

If you plan to attempt this:
- Ensure senior engineers and a technical leader who can provide air cover. 
- Budget an upfront “no visible progress” foundation sprint.    
- Set measurable staging targets (mirror production) and load benchmarks before cutover.
- Trade documentation for concrete tests and runbooks that make failover routine.

In 2020, during a global pandemic that sent most companies scrambling to maintain the status quo, a small team at [Kuda](https://kuda.com/joinKuda/?gad_campaignid=23268674391&gbraid=0AAAAA9ZcCQkbvAslYWKkYi_0Ltc5Gbxcc) did something audacious: they decided to rebuild the beating heart of their bank from scratch.

This wasn't a hackathon project or a technical vanity exercise. This was existential. Every weekend, customers complained. Every Monday morning, the system went down. The third-party [core banking](https://en.wikipedia.org/wiki/Core_banking) solution that powered Kuda's operations was buckling under growth, and the clock was ticking. With barely 100,000 customers—and ambitions to reach millions—the team faced a choice: watch their dreams collapse under technical debt, or take control of their destiny.

They chose the latter. Six months later, Nerve was born.
## When Downtime Was Normal
"Before 2019 or 2020, the statement we normally make that it's not normal for a bank app to be down was not really correct," [Damilola Olowoporoku](https://www.linkedin.com/in/damilola-olowoporoku-01aa60125/), one of the backend engineers on the Nerve team(now Development Manager at Kuda) reflects, his voice carrying the weight of lived experience. "Before then, bank apps were actually normally down."

For the Nerve team, this wasn't merely a fact—it was unacceptable.

Kuda launched in 2019 with a bold promise: banking without physical brick-and-mortal branches, powered entirely by mobile technology. But promises mean nothing when your infrastructure can't deliver. Customers sent money that didn't reflect. Transfers failed silently. Login attempts hung in digital purgatory. The operational bottleneck wasn't just frustrating—it was existential.

"The moment that we thought, you know what, we can't continue this anymore, was when the third party application we were using was really giving us a terrible experience," [Abdulazeez Murainah](https://www.linkedin.com/in/abdulazeez-imran-b81419111/?originalSubdomain=ng), known as **Zee**, one of the backend engineers who would help architect Nerve(now leading engineering at Kuda) explains. "Every now and then you get customers just complaining about failed transfers, not being able to log into the app. They send money to Kuda, the money did not reflect."

The team was barely six months into operations, still finding their footing, when reality hit: the system supporting them couldn't scale to their ambitions. Traditional core banking solutions from major vendors cost tens of millions of dollars—resources Kuda simply didn't have. Local alternatives existed, but came with the same fundamental problem: someone else held the keys to their future.

"We looked at several alternatives, both locally and internationally," Zee continues. "But we thought that if we really want to be responsible for our own destiny, have our destiny in our own hands, the best option would be to think of building our own core banking."

At the time, they didn't fully grasp the magnitude of what they were proposing. Building a core banking system isn't like building an app or even a complex web service. It's building the invisible infrastructure that must never fail—the system that manages every Naira, tracks every transaction, ensures every balance is accurate to the Kobo. When it breaks, the bank breaks.

And yet, they began.
## What Makes a Core Banking System the "Nerve Center"
To understand why this decision was both necessary and terrifying, you need to understand what a core banking system actually does.

"The core banking application is like the control center," [Kayode Ilesanmi](https://www.linkedin.com/in/kaynuel/), who led the Nerve engineering team(now Head of Engineering at Kuda) explains with the precision of someone who's architected such systems. "It's not the system that customers get to see, but it's the system that when things are not going well, customers will get to point out."

Think of it as the backend of the bank—but that description barely captures its criticality. Every balance customers see on their mobile app is pulled from the core banking system. Every transfer, every deposit, every withdrawal flows through it. When you walk into a commercial bank and they tell you "our network is down," what they really mean is: the core banking system is down.

"For withdrawal, they need to actually see your balance so that they are sure they are taking out what you have and immediately they can update the balance," Kayode notes. "So when they say the network is down, we are sorry, you can't withdraw your money—it's the core banking that's actually down."

The system touches every part of the operation. Finance teams use it for reporting. Customer experience teams need it to support users. Compliance and fraud teams rely on it for oversight. Regulators examine it during audits. It's the single point of truth for an entire financial institution.

And for most banks in Nigeria—indeed, in Africa—this critical system is owned by someone else.
## The Legacy Problem
The banking technology landscape is dominated by vendors who built their systems decades ago, long before mobile transfers became ubiquitous, before real-time expectations became the norm, before cloud infrastructure existed.

"When the core banking system was designed, it predates the current landscape of technology," Dami points out. "Mobile transfers became a thing in the last 10 years. The systems were built over many years before the mobile technology that we have today."

These legacy systems struggle with modern demands. They're built on outdated networking architectures. They can't easily integrate with contemporary APIs. They lack the responsiveness that today's customers expect. As Kayode puts it: "Some of these solutions are built decades ago. They do not fit into the responsive and real-time applications that customers and users expect today."

Even banks that want to upgrade face years-long migration projects. Major banks migrating between core banking platforms often take years to complete the transition—a testament to how complex and risky these migrations are.

Years. Not months—years. That's how complex and risky these migrations are.

But Kuda didn't have years to wait, and off-the-shelf solutions weren't delivering the reliability Nigerian customers needed. What they had was more valuable: experienced engineers, a culture of daring innovation, and a CTO who was himself a hands-on engineer.

"Our CTO is a hands-on engineer originally," Dami notes. "That's also what drove our confidence."

Still, confidence and capability are different things. What they were proposing had never been done in Nigeria. No bank had built its own core banking system. The expertise was scarce. The risks were massive. And they had customers—real people with real money—depending on them.
## The Pitch That Changed Everything
In most organizations, proposing to rebuild critical infrastructure from scratch would trigger months of stakeholder meetings, risk assessments, and executive hand-wringing. Kuda had none of that luxury—and, paradoxically, that became their advantage.

"The good thing was that at the time, we were a very small team," Zee recalls. "We were very nimble and we were a team that could make decisions on the fly and actually run with it without having to do stakeholder meetings, engagement and whatnot. We were kind of like in the same room—the CEO, CTO, and everybody."

The conversation stemmed from shared frustration. Everyone felt the pain of the failing system. Everyone understood the risk of doing nothing. And critically, building the seemingly impossible was already in Kuda's DNA.

"Kuda by design is kind of like a crazy adventure," Dami reflects. "Imagine some set of guys thinking they can take on the banking industry and compete with the big boys within two or three years. It's kind of like a crazy adventure, right? A lot of people said that to us in the early days—that we don't know what we're talking about."

The decision matrix was stark: on one side, the status quo—a system that was already failing at 100,000 customers with plans to reach millions. On the other, an unprecedented engineering challenge with no guarantee of success.

"It was between the devil and the deep blue sea," Dami says. "We don't do this, we are in a position that's threading the other side, which is a business pole. So it was sort of easier to make a case for it."

But there was another factor, one that would prove crucial in the months ahead: the problem solver sat at the table. The CTO wasn't just approving the project—he understood it viscerally, could evaluate technical trade-offs, could support the team when challenges emerged.

The decision was made. **January 2020**: Project Nerve would begin.
## Building for 10X: The Architecture of Ambition
Most teams, facing a crisis, would build something to solve the immediate problem. Kuda's engineers took a different approach: they built for the future they wanted, not the present they had.

"We weren't building what fixes our problem at the moment. We were building actually for the future," Kayode emphasizes. "In our guiding principles, we are not building for the 150,000 customers—we're building for 10X now. Whatever it is we are doing, when we get to 1 million, what will happen? When we get to 5 million, 10 million, 50 million, what will happen?"

This wasn't just optimistic thinking—it was architectural philosophy. The testament to their foresight: the same system built in 2020 serves 10 million customers today without reaching its designed limits.

The technical decisions flowed from this principle.
## Microservices Over Monolith
"It was an adventure that made us dare the [microservice](https://en.wikipedia.org/wiki/Microservices) architecture pattern," Dami recalls. "It was not a popular pattern when we were doing it."

They grouped related services into standalone modules, each with its own database, each communicating through REST APIs or event-driven architecture using [Kafka](https://kafka.apache.org/). This wasn't the path of least resistance—microservices introduce complexity in coordination, deployment, and monitoring—but it provided exactly what they needed: flexibility, scalability, and the ability to evolve parts of the system independently.

"Nerve, in a nutshell, is a testament of the importance of modularization in real life," Dami explains. "Because it's extremely modular, that's why we have different parts joining, connecting. We can remove/hide and join to it because it's not one giant system."
### Caching as a First-Class Citizen
With millions of potential transactions, every database query matters. The team implemented aggressive caching using Redis to minimize expensive database operations.

"We have a lot of customers. A customer can do 10 transactions a day," Kayode notes. "We don't want to be going to the database every time for name inquiry or some information that doesn't change often. Databases are expensive. Connecting to the database is one of the most expensive operations in an application."
### Technology Choices Rooted in Pragmatism
The application runs on [.NET](https://dotnet.microsoft.com/en-us/download/dotnet) Core—not because it was fashionable, but because the team knew it intimately. They used [Microsoft SQL Server](https://en.wikipedia.org/wiki/Microsoft_SQL_Server) for the database, Elasticsearch for audit trails and fast queries, [Docker](https://www.docker.com/) for containerization, and [Kubernetes](https://kubernetes.io/) for orchestration across Azure and AWS.

"The application is built with .NET Core and we chose it because it's what the team at that time were very comfortable with," Kayode explains simply. "It's the tool that everyone was comfortable with."

This pragmatism extended to infrastructure decisions. They ran on Kubernetes rather than cloud-specific container services to avoid vendor lock-in. They used [Dapr](https://docs.dapr.io/) (Distributed Application Runtime) to abstract communication layers, making it possible to swap out Kafka for Redis Streams or other message brokers without rewriting code.

"We use this distributed application runtime to abstract the pub-sub communications that happen," Zee explains. "So you really don't have a tightly coupled connection to Kafka. You could decide to use Kafka today, tomorrow you change it to [Redis Streams](https://redis.io/docs/latest/develop/data-types/streams/) or EventBus or any other."
### The ORM They Didn't Have
One of the most interesting technical decisions came from a constraint. Entity Framework Core—the standard .NET ORM—was immature in 2020. The team needed performance and control that full ORMs couldn't provide, but they didn't want to write raw SQL queries for every operation.

Their solution: build their own micro-ORM wrapper around [Dapper](https://github.com/DapperLib/Dapper).

"There's a big gap between what we have today and what we had five years ago," Dami explains. "We realised we don't want that level of abstraction because we want flexibility to manage things, manage the way we query, and manage our resources."

They created a library that dynamically generates SQL queries, handles column mapping automatically, manages scope identity, and provides the developer experience of Entity Framework without the overhead. Every engineer joining Kuda today uses this library without thinking about SQL—yet the system maintains low-level control over database operations.

"Any engineer that is joining Kuda today does not need to worry about ORM," Zee notes. "They will use that library as though they will use Entity Framework Core. They don't think about writing SQL queries because that library handles it—and since we still manage it in a very low-level manner, we have the control we need."
## The Invisible Enemy: Concurrency and Consistency
Building a system that handles money introduces challenges that most software engineers never face. Every transaction must be atomic. Every balance must be accurate. Every race condition must be eliminated.

"When it comes to money, customers don't joke with their money," Kayode says with the gravity of someone who's handled crisis tickets at 2 AM. "The smallest of things, the customer is going to say, 'I can't find my money.'"

The core challenge: concurrency. Customers access their money through multiple channels simultaneously—mobile app, card transactions, gateway integrations, partner APIs. Multiple requests can hit the system for the same account at the exact same moment.

"There are times when requests can hit a customer at the same time. And then the core banking application will need to figure out what to do," Kayode explains.

Their solution: database row versioning. Every time a record updates, its version changes. When a transaction reads a customer's balance and later attempts to update it, the system checks if the version has changed.

> **info**
> 
> Database row versioning is a mechanism used to manage concurrency and track changes to data within a database. It is a form of optimistic concurrency control where each row in a table is associated with a version identifier, which is typically a unique binary number or a timestamp.

"If by the time the application has read the customer's balance and there is a change when it's ready to actually update it, the system can automatically tell that this version has changed," Kayode details. "Which means the version I read is now stale. I cannot continue with this. I have to start again."

Client systems understand the response codes and automatically retry. It's elegant, standard practice—but **the engineering is in the application**, in ensuring every service respects this contract, in building retry mechanisms that work under load, in testing scenarios that expose race conditions.
### Synchronous at the Core, Asynchronous at the Edges
One of the most critical architectural decisions was choosing when to use synchronous versus asynchronous processing. For transaction processing—the actual movement of money—the team chose synchronous, atomic operations.

Every transfer must be immediate and complete: the customer is debited and the recipient credited in one transaction, or neither happens at all. This eliminates a class of race conditions and ensures customers always see accurate balances.

"For transaction processing, we use synchronous operations to maintain consistency," Kayode explains. "The customer must see accurate balances immediately. You can't show them money in their account that's already been transferred, or they might attempt to use the same balance multiple times."

This design choice shaped the entire architecture: synchronous transaction processing at the core ensures data consistency and accuracy, while event-driven architecture handles peripheral operations like notifications, analytics, and non-critical updates. The best of both worlds—strong consistency where it matters, scalability and resilience where it doesn't.
## The Foundation Phase: Two Months of Nothing
January turned to February, February to March. The team worked intensely—daily stand-ups, architecture reviews, code reviews, infrastructure setup. But there was a problem: they had nothing to show.

No endpoints. No APIs. No visible progress.

"The first two to three months, we had nothing to show," Zee recalls. "[Musty](https://www.linkedin.com/in/mustaphamo/?originalSubdomain=uk) asked, 'Are you guys doing anything?' We're like, 'Yeah, we are building the foundation. This foundation is what we'll be able to build every other thing on top of.' And he was like, 'Can I see any endpoints? Can I see any API? Can I see anything?' We were like, 'No, you can't see anything yet.'"

For a startup burning cash with a broken system in production, those months must have felt eternal. But the team held firm.

"We just told him that after this phase it will just be boom boom boom afterwards," Zee continues. "We'll be able to sprint things out and move very quickly. That phase, I would say, was challenging because we had to do a lot of convincing to let the CTO know that, although he trusts us, what we are doing right now—you may not see any results yet—but this is the foundation to what will make Nerve a very stable and solid system."

They were building abstractions, defining contracts between services, creating the database schema that would handle billions of transactions, implementing the ORM wrapper, setting up the observability stack, configuring Kubernetes clusters, establishing deployment pipelines.

Foundation work is invisible by nature. But skip it, and the building collapses.

"If you ask him today, he will say, even if it was going to take us six months to build that foundation, he would definitely support it," Zee reflects.

The patience paid off. After the foundation phase, development accelerated exactly as promised. Services came online rapidly. APIs proliferated. The system took shape.
## Testing the Untestable
By July, six months after starting, the team had a system. But having code and having confidence are different things. They needed to test Nerve under production-like load before putting real customer money at risk.

They set up a staging environment that mirrored their planned production setup and began aggressive testing. API testing. Load testing. Performance testing. Functional testing. The QA lead built automated test scripts. Engineers tested locally using Docker Compose to spin up dependent services.

"Since we were using Docker and Kubernetes, it was easier for us to test on the development environment," Zee explains. "It wasn't a case of 'it works on my machine.' If there was a service that I need to consume on my side, all I need to do is pull that Docker Compose and just run it."

Their benchmark: 1,000 concurrent transactions per second. If a thousand users opened the Kuda app simultaneously and tried to transfer money, could the system handle it?

Initial results: disastrous.

"When we started, the results were so bad," Kayode recalls. "They were failing. We were having connection issues, timeouts, HTTP issues. We were seeing a lot of reds."

**The culprit:** Redis connection management. Under load, the system was opening new connections for every request rather than reusing a connection pool. Redis couldn't handle a thousand simultaneous connections—not because of Redis limitations, but because of how they were using it.

"We realized that we're not reusing the Redis connection we opened. We're firing a thousand connections to Redis," Kayode explains. "The solution is not to increase Redis capacity. The solution is to optimize our service to manage the connection."

They fixed the connection pooling. The QA lead ran the test again.

"That was like that moment of yes, we're ready," Kayode remembers. "We told everybody: we are ready to go live."
## The Night Before Launch: When Everything Broke
The date was set. August 2020. After six months of development, weeks of testing, and careful preparation, Kuda would migrate to Nerve. The staging environment had been rock solid for weeks. The team was confident.

Then, the night before launch, they spun up the production environment—an exact copy of staging with higher specs.

It refused to work.

"For some reason, this environment refused to work," Zee says, still baffled years later. "We don't know why. It just refused to work. And we didn't have the time to actually figure out why it didn't work."

In many organizations, this would trigger an emergency postponement. Committees would form. Root cause analysis would be demanded. Launch dates would slip.

Kuda's team made a different call.

"We just eventually turned the staging environment where we've been doing all our load tests to the production environment," Zee explains. "And that is the Eureka moment."

The staging environment became production. The broken production environment was abandoned for forensics later. They had customers waiting, a failing system to replace, and a tested platform ready to go.

They launched 🚀.
## Launch Day: Customers Reactions
In the backend world, there's a joke: if you're doing your job right, nobody notices. Frontend developers can point to beautiful interfaces, but backend engineers deal in the invisible—milliseconds of latency, database query optimization, connection pooling.

Nerve broke that pattern.

"From the moment we launched, customers were tweeting that they can notice the improvement," Dami recalls with barely concealed pride. "That alone was self-fulfilling. The response time, the transaction processing time—all of those were checked. But the end user was able to even validate our expectation."

The operational transformation was immediate. The customer experience team, who had spent months apologising for failed transactions and mysterious errors, suddenly had a system they could depend on.

"The CX(Customer Experience) team, the experience changed immediately," Dami notes. "We didn't need to wait for 10 days to know that what we have done is actually solid."

Zee initiated a challenge: 100 days without critical incidents. It wasn't just a goal—it was a statement. The old system couldn't go a week without issues. Nerve would go months.

They hit the target.
## The Architecture of Resilience
Uptime isn't luck—it's architecture, monitoring, and relentless attention to failure modes.

Nerve runs across multiple availability zones with automatic failover. [Azure Front Door](https://azure.microsoft.com/en-us/products/frontdoor) manages traffic, continuously pinging services and redirecting requests if an environment goes down. Customers rarely notice when failovers occur.

"For critical services, if a particular network is down, it will automatically just start to push requests to the other setup," Kayode explains. "Most customers will not even notice when that happens."

The database strategy is similarly redundant: primary database, secondary replica, and transactional data streaming to BigQuery for analytics and additional backup. Daily snapshots provide point-in-time recovery.

"We have primary database, then we have the secondary database. The primary replicates into the secondary and also pushes data to [BigQuery](https://cloud.google.com/bigquery?&gad_campaignid=21054825557)," Kayode details. "That way we have a replica of all transactions at near real time."

But resilience isn't just about infrastructure—it's about visibility. The team deployed an extensive observability stack: Datadog for tracing, logging, and metrics; OpenTelemetry for distributed tracing; Grafana and [Loki](https://grafana.com/oss/loki/) for open-source monitoring; custom dashboards for specific scenarios.

"The fact that there's proper separation of concern makes layering easy," Dami notes. "That's why we can switch from one tool to another, whatever we need to do."

A dedicated incident management team monitors these systems continuously, watching for anomalies, filtering out noise, and escalating issues before they become outages.

"They look out for anomalies and things that the system may not catch," Zee explains. "When we see things are going wrong—maybe a CPU spike, a database query timing out—we get the responsible individual and they resolve it as soon as possible."

> **info**
> 
> At peak periods, Nerve handles approximately 300 requests per second. The system was designed to handle far more.
## The Human Architecture: How Eight Engineers Stayed Sane
Technical architecture is one thing. Human architecture—how a team works together under pressure—is another.

The Nerve team numbered eight engineers: four backend engineers handling APIs, databases, and optimization; two full-stack engineers building the internal UI and consuming the APIs; one DevOps engineer managing infrastructure; one QA lead testing everything.

Supporting them: a project manager, a designer, two product managers, a database administrator, and the CTO—Musty—who provided technical guidance and organisational air cover.

"We're just eight engineers in total," Dami reflects. "Because it's the backend of a bank, four of us out of the was focused writing the APIs and all the optimisation, networking, database. Two were frontend-backend, consuming the APIs and handling the UI. Then one QA and one DevOps."

They worked intensely—late nights, weekend debugging sessions, constant communication. But what kept them going wasn't fear of failure or management pressure. It was something more fundamental: they believed they could do it.

"The spirit was ultra-high," Kayode remembers. "Even if you had doubts, once you see the other guys and start discussing the things we want to do, you start to get excited. You start to see the possibilities."

At points, the team lived together, ate together, shipped code together. Like a football team preparing for a championship match, they built camaraderie through shared purpose.

"We had to all stay together at some point. We were living together, just staying together, going out together," Kayode says. "Just one common goal: to solve the core banking application."

And they did it during COVID-19, when the world was learning to work remotely, when Teams and Zoom calls replaced in-person collaboration, when uncertainty was the only constant.

"We built this during COVID," Kayode notes. "It was also a challenge, but we were able to just navigate around it."
## Speed Without Sacrifice
In startups, there's always tension between speed and quality. Move fast and break things—unless you're building a bank, in which case breaking things means breaking trust, losing money, and possibly violating regulations.

Kuda's team rejected the trade-off.

"There's no trade-off like you have to go for speed and you can't go for quality," Kayode states flatly. "You just have to be balanced."

They achieved balance through several mechanisms. First, everyone owned quality—it wasn't just the QA engineer's job.

"We all saw it as everyone's responsibility to drive quality," Kayode explains. "We told ourselves that we don't build applications that we have to rework every time. That is what has made Nerve a very reliable application."

Second, they argued—constantly, passionately, constructively.

"There are lots of disagreements. Maybe the story is looking like Romeo and Juliet, but it wasn't... there were tough moments," Dami admits. "We used to argue."

But they had a crucial rule: once a decision was made, it belonged to everyone. No finger-pointing. No "I told you so."

"When we pick a solution, it no longer becomes someone's idea. It now becomes everyone's own," Kayode explains. "The success, the failure—we share it. If it fails, it's not 'I told you.' It's 'What do we do now? What are the learnings and how do we move forward?'"

Third, they were ruthlessly pragmatic. They knew engineering principles, but they weren't slaves to them. They identified limitations—like account number generation algorithms that would run out at 50 million customers—and documented them for future resolution rather than letting them block progress.

"We were able to identify things that are limitations and say, okay, this is a problem for the next 10 years, next 20 years. Things will advance," Kayode notes. "We didn't allow those things to slow us down. We wrote it down and moved on."

Finally, speed was inherent in the situation. They didn't have the luxury of leisurely development.

"Speed was inherent. We needed to be fast, and safety is required. Safety first," Dami says. "We didn't have an engineering limitation per se. The team had a very strong engineering background. But we were extremely pragmatic. We knew what we needed to do and what we didn't need to be theoretical about."
## Iterating Towards Excellence
Nerve didn't stop evolving after launch. The system that went live in August 2020 was complete enough to replace the failing third-party solution, but it was just the beginning.

Over the years, the team added features that didn't exist at launch: overdraft facilities, loans, a second-generation "smart overdraft" that works like revolving credit in developed markets. They integrated fraud detection and transaction monitoring. They built systems for tax reporting to FIRS. They created internal tools for finance, compliance, and fraud teams.

They also kept the platform current. Nerve launched on .NET Core 3.1. When .NET 8 became the stable version, they upgraded to maintain security, get vulnerability fixes, and leverage performance improvements.

"We are on .NET 8 right now, which means we are keeping abreast with all the security fixes, vulnerability fixes, ensuring we're not using packages with known vulnerabilities," Kayode explains.

Perhaps most significantly, Nerve enabled geographic expansion. The same system that handles 10 million customers in Nigeria can be deployed in other countries as Kuda grows.

"International expansion—the system can be taken to other countries," Kayode confirms.

The modularity that took months to build in the foundation phase paid dividends. New services integrate cleanly. Features can be developed independently. The system scales horizontally as load increases.

"Nerve is a testament of the importance of modularization in real life," Dami emphasizes. "Because it's extremely modular, we can remove, hide and join parts to it. It's not one giant system."
## The Cost Calculation: Building vs. Buying
Banking technology is expensive. Enterprise core banking solutions from vendors like Temenos or Finacle cost tens of millions of dollars upfront, plus annual licensing fees, support contracts, and customization costs.

When asked about Nerve's operational costs compared to buying, Dami doesn't hesitate: "We are running at a situation where it's probably 90 percent cheaper than buying."

Ninety percent. Not just cheaper—an order of magnitude cheaper.

The cost advantage comes from multiple factors: no licensing fees, no vendor support contracts, no customization charges, no being held hostage during negotiations. Cloud infrastructure costs are predictable and scale linearly. Engineering salaries are an investment in capability, not a recurring vendor tax.

But the real value isn't just monetary. It's control—the ability to fix bugs immediately rather than waiting for vendor patch cycles. The ability to add features based on business needs rather than vendor roadmaps. The ability to optimize performance without depending on external consultants.

"Flexibility and control—it has allowed us to add more features, more services, build more products," Kayode reflects. "When we started, there was no Kuda for Business. Now we have Kuda for Business. Owning the core banking has made it very easy for us to integrate that."

And perhaps most valuable: data ownership and access. The core banking system generates enormous amounts of transactional data. Owning the system means owning that data, enabling robust data platforms for machine learning, decision science, and risk assessment.

"We also have control over our data, which has allowed us to build a very robust data platform for machine learning, decision science," Kayode notes. "We have overdrafts today that we can offer to customers based on that data."
## Lessons from the Trenches
When asked about the top three lessons from building Nerve, the team's answers reveal what they value most.
### Lesson 1: Trust Foundation Engineering Concepts
"Trust foundation engineering concepts. It really goes a long way," Dami emphasizes. "We have to trust things we've tried out before. The basics are always true—they're like laws. We don't need to theorize them, we need to practicalize them."

Microservices architecture, event-driven systems, caching strategies, database optimization—these aren't buzzwords. They're proven patterns that work when applied thoughtfully.
### Lesson 2: Flexibility and Control Matter More Than You Think
Owning your infrastructure isn't just about cost savings. It's about being able to respond to opportunities and challenges without waiting for third-party approval.

"It has allowed us to be able to add more features, build more products," Kayode says. "Flexibility—we don't have to wait for vendor approval, vendor timelines, vendor priorities."
### Lesson 3: Build for Tomorrow's Scale, Not Today's Needs
The discipline of designing for 10X growth—even when you're not sure you'll get there—creates systems that last.

"We weren't building what fixes our problem at the moment. We were building for the future," Kayode reiterates. "The testament is that the same application since 2020 is still serving the bank, from 110,000 customers to 10 million customers now."
## Advice for the Builders
For other African fintech companies considering whether to build or buy core infrastructure, the Nerve team offers nuanced guidance.

"It depends," Kayode says, then elaborates. "There are factors. You need the people—the quality people. It depends on your roadmap. Where are you going? What flexibility are you yearning for? Do you want control?"

The problem with buying is vendor dependence. You request features and hear "three months" or "six months" or "we'll add it to the roadmap." Your growth is constrained by someone else's priorities.

But building requires resources—not just money, but time and talent. It requires leadership that understands technology enough to evaluate trade-offs and provide air cover during the foundation phase when there's nothing to show.

"At the time, our CTO is a hands-on engineer originally," Dami notes. "That's what drove our confidence."

The team doesn't regret using a third-party solution initially. It let them launch quickly and prove the business model before committing to infrastructure build-out.

"I don't think we should sit and regret the decision of using a third-party core banking app initially," Kayode reflects. "It actually served the purpose, which was to get us ready to launch. If we wanted to build everything internally before launching, we would have launched very late."

The key is knowing when to transition—recognizing the inflection point where vendor limitations constrain your future more than build costs.

"When we saw that we are ready to take the next step, marketing was coming towards us. We already sponsored Big Brother. We saw those numbers and were able to prepare for it," Kayode explains.
## What This Means for African Engineering
Nerve represents more than one bank's infrastructure. It's proof of concept for African technical capability operating at global standards.

"In terms of talent, we have it. That's why we can see the migration to developed countries—the demand is high for African engineers," Kayode observes. "This is a testament that we have the right people and the confidence."

But talent alone isn't enough. The system worked because of confidence—from investors, from the board, from management—that local engineers could solve hard problems.

"It's time we started believing in talents here and then trusting them," Kayode urges. "Without trust, we can't continue to build more and more of this."

The challenge works both ways. Engineers must believe in their own capacity. "It's a case of believing in your capacity," Dami says. "That's on engineers in Africa."

And stakeholders must be willing to trust and fund that capacity. "The other side is for stakeholders to make the testament to be able to trust our own engineers," Dami continues. "It's a mix of both worlds."

Years ago, Nigerian companies seeking sophisticated software would contract firms from India or the US. The assumption was that local engineers couldn't handle enterprise-scale systems. Nerve disproves that assumption definitively.

"Today you walk into a commercial bank and you're talking about a core banking application, I'm not sure they will easily want to trust that," Kayode admits. "But this is something any other person can point to and say, Africans did this."

The implications extend beyond banking. Aviation systems. Government platforms. Healthcare infrastructure. Logistics networks. All of these depend on software that African engineers are fully capable of building—if given the trust, resources, and opportunity.
## The Nerve to Build
Building Nerve wasn't just an engineering project. It was an act of defiance against low expectations, against the assumption that critical infrastructure must come from elsewhere, against the idea that African engineers can't compete at the highest levels.

Eight engineers, six months, one pandemic, countless late nights, and the audacity to believe they could rebuild the foundation of a bank without causing it to collapse.

They succeeded not because they had all the answers at the start, but because they had the courage to begin. They succeeded because they balanced pragmatism with principle, speed with quality, confidence with humility. They succeeded because when the staging environment became production and nothing made sense, they adapted and shipped anyway.

Most of all, they succeeded because they owned their destiny. They put their bank's future in their own hands, wrote the code themselves, fixed the bugs themselves, optimized the queries themselves, handled the incidents themselves.

And in doing so, they proved what's possible.

"Kuda is the first bank in Nigeria to build its own core banking," Zee states with quiet pride.

The first—but not the last.

Somewhere in Lagos, Nairobi, Accra, or Cairo, another team of engineers is reading this story and thinking: if they could do it, why can't we?

That's exactly the point.

> **note**
> 
> Today, Nerve processes transactions for 10 million customers, handles approximately 300 requests per second at peak, and has fundamentally transformed how Kuda operates. The system runs across multi-availability zones with automatic failover, streams transactional data to BigQuery for analytics, and continues to evolve with new features like smart overdraft and integrated fraud detection.

The team that built it:
-   Musty Mustapha - Co-founder and former CTO, he is now the Managing Director of Kuda MFB.
-   Emmanuel Opara
-   Damilola Olowoporoku
-   Kayode Ilesanmi
-   Abdulazeez Murainah (Zee)
-   Dayo Ojo (DOJ)
-   Olugbenga Oje
-   Shola Odeniya
-   Adebayo Adeyemi-Suenu
-   Tunde Mason
-   Ore Fakorede
-   Ayoola Samagbeyi
-   Okezie Okpara
-   Omotolani Zubair 

They had the nerve to build. And that made all the difference and showed that with the right combination of talent, trust, and audacity, African engineers can build world-class infrastructure.

**Technical Appendix: The Stack**
-   **Language**: .NET Core (currently on .NET 8)
-   **Database**: Microsoft SQL Server with row versioning for concurrency control
-   **Caching**: Redis
-   **Message Queue**: Kafka for event-driven architecture
-   **Containerization**: Docker
-   **Orchestration**: Kubernetes (Azure Kubernetes Service and Elastic Kubernetes Service)
-   **API Communication**: REST and Dapr for distributed communication abstraction
-   **Monitoring**: Datadog, OpenTelemetry, Grafana, Loki
-   **Infrastructure**: Multi-availability zone deployment with Azure Front Door for failover
-   **ORM**: Custom micro-ORM wrapper around Dapper for performance and flexibility
-   **Architecture Pattern**: Microservices with event-driven peripheral operations and synchronous transaction processing
### **Key Engineering Principles**
1.  Build for 10X scale, not just current needs
2.  Trust foundation engineering concepts
3.  Optimize database connections and queries aggressively
4.  Use caching to minimize expensive operations
5.  Implement connection pooling for all external resources (databases, Redis, etc.)
6.  Abstract vendor-specific implementations to maintain flexibility
7.  Implement comprehensive observability from day one
8.  Design for failure with automatic failover and redundancy
9.  Prioritize data ownership and control
10.  Balance pragmatism with principle—document limitations, ship functionality
11.  Make quality everyone's responsibility, not just QA's
### **Performance Metrics**
-   ~300 requests per second at peak
-   Designed for 1,000+ concurrent transactions per second
-   Multi-AZ deployment with automatic failover
-   Near real-time data replication to BigQuery
-   Daily database snapshots with point-in-time recovery
-   10 million customers on same architecture built for 100,000+