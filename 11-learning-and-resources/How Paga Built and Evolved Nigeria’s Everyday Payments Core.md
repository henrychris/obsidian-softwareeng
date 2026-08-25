# The Relentless Engine: 

From feature phones and voice-PIN transfers to cloud-native rails and agent-first flows: the 15-year journey of building, evolving, and scaling Paga’s payments core under relentless regulatory, infrastructure, and market constraints, proving that owning the technology, designing for reliability, and evolving without rewrites can turn a constraint-heavy Nigerian fintech into a resilient platform serving millions.

This deep dive issue of The African Engineer traces the 15-year engineering journey behind [Paga’s](https://www.mypaga.com/?gad_campaignid=23055214312&gbraid=0AAAAACU7Mpd6k5iEWr1wP90qBFDASzxlK) payments platform and explains how a series of deliberate technical and organisational choices turned a small Lagos fintech into resilient, change-friendly infrastructure for everyday payments in Nigeria and beyond.

From the outset, Paga rejected off-the-shelf core banking solutions after discovering they could not keep pace with Nigeria’s regulatory volatility, connectivity challenges, and fast-changing product ideas. Instead, CTO Eric Chijioke and his team built and owned their core, accepting the complexity in exchange for the ability to ship changes daily in a heavily regulated environment.

The story shows how constraints in Nigeria, such as low smartphone penetration, lack of USSD in the early days, strict KYC rules, and unreliable third party rails, forced an agent-first model and even voice PIN authentication.

Architecturally, Paga evolved a single Java and Spring core running in on-premise data centers into a containerized, Kubernetes based platform on Azure without a full rewrite.

Scale came not from flashy microservice overhauls but from careful database strategy: read replicas, aggressive caching, and queuing to protect the write path under load. Over time, Paga reduced its dependence on intermediaries by building direct connections to banks and telcos and, when necessary, its own rails, improving both reliability and unit economics.

The issue also frames talent and security as first class infrastructure concerns. Paga’s leadership assumes two to three year engineer tenures, invests heavily in training, and assigns dedicated senior architects to each product line to maintain speed and resilience.

On security, the company combines PCI discipline, cloud security scoring, and multi region redundancy to sustain a 15 year record with no known intrusions. Across technology, organization, and security, the core principle is consistent: **evolve the system in place, add new services only when they clearly improve reliability or speed, and never let third parties or “perfect” architectures dictate the pace or direction of the business.**

## Key takeaways — TL;DR;
-   **Build what you control:** Off-the-shelf platforms couldn’t keep up with Nigeria’s fast-changing market and heavy regulations. Paga’s custom core enabled daily shipping and rapid adaptation.
-   **Constraints shape the product:** Feature phones, missing USSD, strict KYC limits, and unreliable rails forced an agent-first model and innovative solutions like voice-PIN authentication.
-   **Architecture evolves, doesn’t need restart:** A single Java/Spring core with channel-specific front ends grew into a Kubernetes cloud-native system without ever being rewritten.
-   **Scaling starts at the database:** Read replicas, aggressive caching, and “Q-axis” queuing protected writes; heroic app rewrites weren’t needed.
-   **Ownership beats dependency:** Direct bank and telco integrations and in-house rails minimized failures, reduced cost, and improved reliability compared to third-party hops.
-   **Talent is infrastructure:** Dedicated architects per product line, planned two-to-three-year tours, and systematic upskilling keep velocity and resilience high.
-   **Security comes from paranoia, not certificates:** PCI discipline, cloud security scoring, multi-AZ deployments, and a 15-year zero-intrusion track record demonstrate discipline and foresight.
-   **Evolve, don’t reboot:** Decompose or add new services only when reliability or speed is gained; “perfect patterns” never justify churn.

## The architect who wouldn’t outsource destiny
[Eric Chijioke](https://www.linkedin.com/in/eric-chijioke-4099b72/) built enterprise systems for banks and the World Bank long before digital cash was common in Africa. At Apposit, the software company he co-founded in Addis Ababa, Ethiopia, he and his team specialised in complex financial software while the world around them rushed toward mobile apps and fintech dreams.

A chance connection brought Chijioke into Paga early on. The founder, [Tayo Oviosu](https://x.com/oviosu), had studied with his brother, and in the early days of the startup, Apposit dedicated an engineering team to build Paga’s technology. Over a decade this relationship became foundational, with Chijioke eventually becoming Paga’s Chief Technology Officer while Apposit continued to operate independently.

Paga launched in Nigeria to tackle the problem of cash usage in a market where most people had no bank account and needed a safe and simple way to send and receive money. Over time it became a payments leader, processing billions in transactions, serving millions of users, and building an infrastructure that now powers wallets, merchant payments, the most recent collaboration with PayPal to bring the payment juggernaut to Africans, and enterprise services across channels and devices.

In 2020 Paga completed the natural next step by [acquiring Apposit LLC](https://mypaga.medium.com/paga-has-acquired-us-software-company-apposit-llc-9d5bfb90ab77), bringing the company and its 62 engineers fully into the Paga organization. This acquisition gave Paga an immediate presence in Ethiopia under Apposit co-founder [Adam Abate](https://x.com/adamabate), who became CEO of Paga Ethiopia, and added Apposit’s in-house products such as Terra, a data platform for agricultural value chains, and Tangio, a sales automation platform, to Paga’s portfolio.

The acquisition reflects the ethos that has propelled Paga from a small Lagos fintech to a global emerging markets payments engine. The company now operates teams in Nigeria, Ethiopia, Germany, India, Mexico City, and Vietnam while continuing its mission to make financial access simple for one billion people.

In this exclusive with The African Engineer, Eric Chijioke spoke about what this milestone means not just for Paga’s technology but for the future of payments across emerging markets.

## **How One India Trip Made Paga Bet on Its Own Platform**
The first serious attempt to buy rather than build was earnest. Early in Paga’s journey, the leadership team, including Tayo Oviosu and Eric Chijioke, travelled to India to license a ready made payments platform. The thesis was straightforward: **if they could stand on someone else’s technology, they could get to market faster and reassure investors that the technology risk had been neutralised.**

For three long days they sat in requirements reviews, walking the vendor through everything Paga needed to do in Nigeria, from registration flows and agent operations to how transactions should behave when networks or counterparties misbehaved.

By the end of that visit, the conclusion was clear and uncomfortable. To match Paga’s vision, the Indian platform would effectively have to be rebuilt in place. Every deviation from the vendor’s standard way of doing things would be treated as a paid change order.

Paga would fund a slow motion rewrite of someone else’s codebase, rent access to it, and still be constrained by its original assumptions. As Eric dug under the hood, his confidence in the technical foundations and team on the other side dropped each day. It became hard to justify betting Paga’s destiny on a codebase whose internals they could neither shape nor fully trust.

Several hard realities made buying untenable. Nigeria’s payments environment moves quickly but in uneven ways. Regulations from the Central Bank or new directives from banks and telcos can land with little warning, and compliance is not something that can wait for a vendor’s roadmap. Paga’s own model was also non standard.

The company was leaning into an agents-do-the-transaction-for-you flow, using human agents as the primary interface in communities where smartphones were rare, data was expensive, and trust was built face to face.

That flow did not exist in any off the shelf product they saw. Retrofitting it would have meant fighting the platform at every turn and trying to force a retail, app first system to behave like an agent first, multi channel, multi party switch.

On top of this, every extra hop to an external platform would have multiplied points of failure in a country where connectivity is patchy and core rails are not always reliable. In a payments business, reliability is the product.

If a customer is standing at an agent stall with cash in hand and the transaction fails, they do not blame a partner in another country, they blame Paga. Renting uptime from a third party would have meant absorbing that party’s outages, latency spikes, and deployment constraints as Paga’s own. For a company that needed to ship fixes quickly, control its incident response, and protect wafer thin unit economics, that trade was simply too expensive.

Coming back from India, the choice crystallised into a bigger question: would Paga adapt its business to fit a vendor’s software, or would it build software to fit its business and market. The team chose the latter.

Working with Apposit, the engineering firm Eric co-founded in Addis Ababa, they agreed to build Paga’s core platform from the ground up. Apposit dedicated a full time team led by Eric, with clear terms: Paga would own the intellectual property, Apposit would not work with competitors, and both sides would be aligned in the long term upside.

Investors were understandably nervous about building their own core, and Paga eventually had independent reviews done by external engineering teams, including at VMware in Germany, to validate the architecture’s scalability and extensibility. Those reviews came back positive and reinforced that the bet on building had been the right one.

That decision set the tone for everything that followed. Instead of a black box backend, Paga invested early in a detailed architecture: a multi currency, multi channel system that could speak SMS, USSD, web, apps, and voice, a core designed to handle growth in transactions, new markets, and new rails, and an internal training pipeline that turned bright African engineers into specialists on the Paga codebase.

Over the next decade this core would move from on premise data centers in Lagos to Kubernetes on Azure without a rewrite, scale through disciplined database strategy rather than dramatic re platforming, and gradually replace third party hops with direct connections to banks and telcos.

The India trip did not just change a vendor decision, it became the moment Paga decided to own its technical destiny, even though that meant more work upfront, because in markets such as Nigeria and Ethiopia the ability to adapt quickly, control reliability end to end, and evolve architecture in place is not a luxury.

It is the difference between a nice product idea and a resilient payments rail that can survive fifteen years of turbulence.

## **Why Constraints Forced Paga To Double Down On Agents**
Paga did not become an agent first company because agents sounded interesting. The original vision looked closer to PayPal: sign up on your phone, move money in a few taps, let software do the rest. In Nigeria, the first version of that vision ran into three hard constraints.
-   The first was KYC. Without BVN or NIN, a new customer sat behind a tiny transaction ceiling. Lifting that ceiling meant emailing documents, waiting for back office review, and hoping every system in the chain stayed online. For a mass market product, that process was not just annoying, it made the wallet barely useful for the people who needed it most.
-   The second was devices and networks. Most people carried feature phones, not smartphones, and Paga did not yet have USSD access from the telcos. Interactions had to ride on clumsy SMS and voice PIN flows, all on shaky connectivity. A single dropped message could turn a first time user into someone who never tried again.
-   The third was how people actually handled money. ATMs were sparse, cards were rare, and communities were deeply cash driven. People trusted the shopkeeper who had served them for years more than a short code they had never seen, and certainly more than an app on a phone they might not own.

Agents were the structural way through these constraints. Regulators were willing to grant higher limits when the primary account holder was a fully KYC’d agent that Paga had vetted deeply. Those agents already sat at the center of local trust networks.

They could explain new flows in person, handle the phones, and absorb the interface complexity. Instead of forcing each end user through heavy KYC and new patterns, Paga concentrated the hardest work into the agent relationship and let everyday customers transact through someone they already knew.

Seen in this light, the agent network was not a distribution trick added on top of a consumer app. It was the core design response to Nigerian reality. It turned a hostile KYC regime into a workable compliance model, turned a scattered set of shops into a national branch network, and wrapped a multi channel, multi currency platform in the most intuitive interface available in a cash heavy economy: another human being on the other side of the counter.

## Inside Paga's Service Oriented Monolith
Paga’s first architecture was a single, well factored, service oriented core designed to survive Nigeria’s early payments landscape and grow with it.

The core stack sat firmly in the enterprise Java world of the late 2000s. Business logic ran in Java on the Spring framework, deployed to clusters of the [Apache Tomcat](https://tomcat.apache.org/) application server. For the web layer, the team used the [Apache Struts MVC framework](https://struts.apache.org/), then a standard way to structure Java web applications.

Data lived primarily in Microsoft SQL Server, with heavy use of [stored procedures](https://en.wikipedia.org/wiki/Stored_procedure) to keep critical logic close to the database engine and to squeeze as much reliability and performance as possible out of the hardware they had. For search and audit trails they adopted ElasticSearch, which gave them fast querying over large volumes of operational and compliance data.

Logically, this was a single core service rather than a swarm of microservices. Inside that core, the system was segmented by domain, with clear boundaries between payments, on ramps that moved money into the system, and off ramps that moved money back out.

Around that core, Paga built separately deployable channels: a web interface for early users, SMS based flows, voice driven interactions, a dedicated agent application, and later a USSD channel for feature phones. This let them reuse one well understood transaction engine while presenting appropriate front ends for a wide range of devices and contexts.

The infrastructure story was shaped by Lagos, not Silicon Valley. Paga ran on two on premise data centers in the city, with manual failover procedures that depended on people as much as on software. The team had to manage their own hardware procurement cycles, fight heat and power problems, and occasionally keep servers alive in less than ideal conditions, including flooded rooms. Those constraints pushed them toward a design that favoured a single, resilient core they could understand completely over a fragile constellation of heavily networked services.

Security was treated as a first class concern from the beginning. The platform was built with a payment card industry mindset, even before formal certifications were in place. Voice PIN flows reduced the risk of secrets leaking over SMS. Physical access to the data centers was tightly controlled. Over time, that posture grew into the broader security story that supports Paga’s long running clean record.

This architecture was never meant to be disposable. It was designed to be evolved in place. As traffic grew and Paga expanded, they containerized the same core, lifted it into Azure, and wrapped it with new services where it made sense, rather than tearing it out and starting over. No full rewrites followed, only careful evolution.

The same core, with much of its early code still intact, continues to run Paga’s Nigerian operations today. Underneath the Kubernetes clusters and modern tooling is the same monolith that was built to survive Lagos data centers, unreliable power, and a harsh regulatory environment, and that long lived stability is part of what makes the platform so valuable.

## 2020: Liftoff to The Cloud
By 2020, staying on premise had turned from a badge of seriousness into an operational tax. Hardware was failing, power was unreliable, replacement parts had to be imported on slow timelines, and every spike in traffic meant another round of hardware sizing, procurement, and physical installation in Lagos. Platform engineering was spending too much time babysitting servers, managing heat and power, and arguing with data center staff, and not enough time scaling Paga’s core.

That pressure finally converged into a single decision. A four person platform team, led by long time architect and infrastructure specialist Simon Solomon, planned and executed a full lift of Paga’s live platform into Microsoft Azure. The system was already a large, mature payments core by then, processing significant volumes in Nigeria. Moving all of that to the cloud with roughly ten hours of planned downtime was not just a maintenance window, it was a high wire act.

They blew past the original six hour target, but landed safely in about ten. For a fintech of Paga’s size, moving an entire production stack into the cloud in a single overnight cutover is about as close as you get to a controlled miracle.

The move did more than change the data center address. The platform was fully containerized on Kubernetes, so the old Tomcat clusters became pods, and horizontal scale became a configuration setting instead of a purchase order. Ingress and traffic management were consolidated behind Nginx, simplifying how traffic flowed into the core and setting up cleaner patterns for future services.

Reliability took a step up as automatic scaling, managed disks, and multi availability zone deployments replaced the days of manual failover and sweating over overheating racks. Cost visibility improved too. Pay as you go cloud pricing, combined with much cheaper memory and easier use of read replicas and caches, beat the capital expense of hardware, diesel, and emergency equipment runs in Lagos.

Crucially, this was a lift and evolve, not a rewrite. The same Java and Spring based core, with much of its early code still intact, kept running. The team changed the environment around it, wrapped it in containers and better tooling, and used the new platform to keep decomposing and scaling where it mattered. The cloud move is a good example of Paga’s broader pattern. When the rails underneath them were not good enough, they built or adopted better ones, but they did it in a way that kept the core alive, instead of throwing it away every few years.

## **Paga’s X Y Z Q Scaling Playbook**
At Paga, scalability is not a single pattern, it is a mental model. When Eric Chijioke talks about scale he describes a cube with four axes and treats every performance problem as a question of which axis to lean on. The goal is simple. Keep the money path fast and safe, keep the database from melting, and let everything else bend around that.

**The first axis is X**, which is about replicating the same thing. On the application side this is the most straightforward form of scale. Java and Spring services run in containers on Kubernetes, and Paga can add more pods for a service when CPU or latency crosses a threshold. Horizontal scale becomes a tuning problem rather than a procurement exercise. If a core payments service needs to handle a spike, you add replicas until the graph looks healthy again.

**The second axis is Y**, which is about splitting unlike things. New products and platform services do not go into the original Nigeria database by default. They are built as separate services with their own data stores, so they can evolve and scale independently. Even inside the legacy core, when a domain grows important or heavy enough, Paga will invest the effort to peel its data and logic out into its own service and database. The costly part is always the data, with years of records and many join relationships. They only do that surgery when the long term reliability and performance payoff is clear.

**The third axis is Z**, which is about splitting like things. At the highest level this shows up as regional separation. Nigeria runs on its own instances and data, and new markets such as the United States or Ethiopia run on theirs. Within a region they use techniques such as partitioning in the database to keep hot tables manageable, but they have not yet had to do full sharding inside a single market. When and if they do, the Z axis gives them a vocabulary for deciding how to slice.

**The fourth axis is Q**, which is about queues and protection. Once a relational database becomes CPU bound or connection bound, failure tends to snowball. Requests slow down, users retry, upstreams hammer the same endpoints again, and every click makes the problem worse. To avoid that spiral, Paga puts queues in front of constrained resources and is willing to answer some requests with a pending status when the system is under stress. If a write cannot be processed quickly enough, the user sees a clear “we are processing this” response and later a confirmation, instead of staring at a frozen spinner or an error page. The database stays within safe limits, and the rest of the platform keeps breathing.

Around this cube are a set of practical levers. Heavy reads are pushed to read replicas so that the primary write database can focus on transactional work. Aggressive caching, implemented with [Infinispan](https://infinispan.org/) in memory, keeps hot lookups entirely off the database.

The move to Azure made memory cheap enough that caching can be generous instead of miserly. Connection discipline is enforced at every layer. Database and cache access go through well tuned connection pools, which prevents the thousand new sockets on every spike pattern that has brought down other systems.

On the integration side, Paga keeps the edges asynchronous wherever possible and the money path strictly synchronous. The actual movement of value runs as an atomic transaction. Anything around it, such as notifications, analytics, and streaming to data platforms, runs as events over RabbitMQ or Kafka. If an event consumer slows down, it does not hold money hostage.

Taken together, the X Y Z Q model and these supporting tools give Paga a way to scale a long lived core without constantly rebuilding it. When volumes grow, they can replicate, split, partition, or queue, and they know which trade they are making each time.

## **Product Velocity Without Rewrites**
Paga’s engineering culture is built on a simple rule: **only decompose when it clearly buys reliability or speed**. The team has never paused the business for a heroic full rewrite. Instead, they keep the original core alive, and change its shape only when reality forces their hand.

New capabilities, such as platform as a service rails for partners or support for entirely new markets, are introduced as standalone services with their own databases. Those services integrate with the existing core, but they are free to use newer patterns, their own stacks, and independent deployment pipelines. This lets Paga move quickly in new directions without dragging the entire legacy system along with every experiment.

Inside the original Nigerian core, stability is a feature. Legacy code that works and is well understood is allowed to stay where it is. The team does not touch it just to align with the latest architecture fashion.

Perfect pattern compliance is never a sufficient reason to churn a working system that moves real money. The test for decomposition is practical:

> will this change reduce incidents, cut latency, or make future changes meaningfully easier? If the answer is no, the code stays.

When they do decide to pull something apart, they treat data as the last and hardest step. Years of records and dense referential links are what makes a domain expensive to move, not the Java classes or Spring controllers on top.

Paga approaches these migrations surgically. They introduce new services and schemas in parallel, add the integration glue, and only then start moving data in controlled ways while the old paths continue to run. Done well, the customer never sees a cutover at all. They just see a system that keeps gaining features and capacity without ever being switched off and rebuilt from scratch.

## **When Rails Do Not Exist, Build Them**
In Paga’s early years, the “rails” underneath the product were as much of a constraint as devices or regulation. To move money to other banks, they had to go either directly to each bank or through a small set of third party processors.

Those processors sat between Paga and the financial system, took a cut on every transaction, and were themselves at the mercy of fragile bank systems and networks. On the telco side it was similar. Connectivity to SMS centers, USSD, and other channels was tightly controlled, and access often came with high fees and patchy reliability.

Each extra hop in that chain made things worse in two ways. Technically, every intermediary was another point of failure in an environment where data centers, networks, and bespoke integration layers were already fragile.

Commercially, every intermediary took a slice of revenue in a market where transaction margins are thin to begin with. If a customer experienced a failed transfer at an agent stall, they held Paga responsible, not the unnamed processor in the middle. Yet if the transaction did succeed, Paga still had to share the fee.

The long term answer was to own more of the path from Paga’s systems to the counterparties that mattered. Where possible, Paga built direct connections to banks and telcos and invested in making those connections reliable.

That meant fewer moving parts for each transaction, fewer vendors in every incident, and fewer invoices to pay on each Naira of volume. In places where no acceptable rails existed at all, they built their own. That could mean standing up systems to connect into core banking environments, wiring directly into telco infrastructure once regulators forced doors open, or creating their own switching logic where no shared scheme was available.

The principle was consistent. If a link was central to customer experience and unit economics, it belonged on Paga’s side of the line, not rented from someone else.

As Nigeria’s infrastructure matured, this constraint eased but did not disappear. The creation and growth of NIBSS and the NIP transfer scheme dramatically improved bank to bank connectivity. More third party providers entered the market, competition pushed prices down, and uptime improved. It became quite reasonable for a new fintech to assemble a product by stitching together other people’s APIs. Yet Paga’s bias did not flip.

The team still treats core rails as something to own or at least anchor directly, not something to outsource wholesale, because the lesson from the early years has not changed. In a low margin market, where trust is fragile and outages are remembered, the links that define customer experience and unit economics are too important to leave entirely in someone else’s hands.

## **Talent As A System Requirement**
From Paga’s earliest days, the hardest scaling problem was not Kubernetes or SQL Server. It was people. In African engineering reality, brain drain is not an edge case, it is the baseline. Great developers leave for NGOs, offshore contracts, or foreign companies that can pay three or four times as much. Eric Chijioke’s response was not to pretend otherwise, but to design around it.

One of the quiet decisions Paga made was to treat two to three years as a normal tour of duty for many engineers. If someone stays longer, that is a win. If they leave after that window, the goal is for both sides to feel that the time was well spent.

As Eric put it, part of the legacy is “upskilling hundreds of engineers to the point where they can triple or quadruple their take home,” and considering that a positive outcome rather than a failure. That mindset turns departures into a predictable part of the system instead of a series of personal betrayals.

On the flip side, Paga is ruthless about the number of truly senior architects it needs and what they focus on.

**You can only run as many serious products at scale as you have deeply experienced technical leads who are one hundred percent dedicated to them**. Splitting an architect across two or three large systems is treated as a recipe for drift and hidden complexity. That constraint shows up in decisions about how many big bets to run at once. If there is no dedicated senior owner, the product does not graduate into the “serious” lane.

To make this sustainable, Paga runs deliberate recruit train promote loops. New engineers are hired not just on raw ability, but on the assumption that the company will invest heavily in them for two or three years. They go through a customised onboarding program that covers both general engineering skills and the specifics of Paga’s architecture and domain.

Many start in support or maintenance, where they learn how the platform behaves under real load and how incidents are handled. From there, the strongest are promoted into core product teams and, over time, into the next generation of technical leads.

Over the long run, this approach has produced more than just internal capacity. It has built a diaspora. Alumni who now work at global companies or high paying remote gigs still carry Paga in their story. That network becomes a recruiting channel, a source of informal advice, and a pool of people who are willing to stretch for Paga when a particularly critical hire needs to be made.

In a market where [talent will always move to the highest bidder,](https://africanindiehackers.org/blog/more-talents-not-needed/) Paga’s answer is not to fight gravity. It is to accept churn, design for it, and treat talent development as core infrastructure rather than a side project of HR.

## 15 years of Security **Vigilance**, 0 intrusions
If there is one place where Paga is deliberately conservative, it is security. Eric describes waking up thinking about security and going to bed thinking about security, and the architecture reflects that. Compliance is treated as a floor, not a ceiling.

The company maintains [PCI compliance](https://stripe.com/guides/pci-compliance) and ISO style controls, and it tracks [Azure Secure Score](https://learn.microsoft.com/en-us/azure/defender-for-cloud/secure-score-security-controls?pivots=defender-portal) as an executive level KPI, not just a checkbox for auditors. The goal is to have external tools constantly scanning the platform for weak spots and to keep that score in a narrow, high band over time.

Wherever possible, Paga avoids holding sensitive data at all. For card payments, that means designing flows so that primary account numbers never live long term inside Paga’s systems. The fewer places secrets exist, the smaller the blast radius if something goes wrong. Where data must be stored, it is wrapped in layers of access control, encryption, and monitoring that are part of the platform’s basic fabric rather than an afterthought.

On the infrastructure side, redundancy is treated as a non negotiable baseline. Services run across multiple Azure availability zones, with health checks and automatic failover managed through Azure Front Door and related tooling. The database layer combines a primary write instance with read replicas, plus streaming into BigQuery and other analytics stores. Daily snapshots and replication strategies are chosen so that point in time recovery is always possible if a failure or corruption ever gets past the first lines of defence.

Paga also brings in external eyes regularly. Independent pen testing firms are contracted to attack the system from the outside, and any vulnerabilities they find are subject to strict internal service level agreements for closure. Those tests complement internal static analysis and code review, catching issues that slip past the normal development process or emerge from configuration drift over time.

The result, so far, is a rare track record. In fifteen years of operation, Paga has had no known intrusions into its core systems. Distributed denial of service attacks still happen, as they do to everyone, but the combination of capacity, filtering, and failover makes Paga a relatively unattractive target. In a business where trust can disappear overnight, that quiet, relentless paranoia is as much a part of the platform as any line of Java or SQL.

## **AI: Useful, But On A Short Leash**
Inside Paga, AI is already part of the engineering toolkit, but it is not yet part of the production stack. Eric is clear about that boundary. Individual engineers use large language models for research, for drafting code snippets, and for quickly scaffolding internal tools or admin dashboards.

In his words, Eric has already used agents to “build it mostly just using prompts” for an internal tech‑team management app, a simple CRUD system with a React front end and Spring Boot back end that they then hardened and deployed on Paga’s own infrastructure. For the right kind of low‑risk internal software, AI is treated as an accelerator.

That freedom stops at the edge of core systems and data. “For example, we do not have AI agents running on our infrastructure,” Eric explains. The reasons are twofold. First is security and confidentiality. Production code, secrets, and customer data cannot be pushed through external models without very tight controls, and those controls are still being defined. Second is process parity.

However good AI‑assisted code becomes, it does not remove the need for the review and testing discipline Paga relies on: static analysis, senior code review, and risk‑based release checks remain the standard for anything that touches the money path.

The current work, as Eric frames it, is on policy rather than technology. “One of the things I am working through right now actually is that policy,” he says, meaning a clear set of rules for how Paga will allow AI into its development and operations without loosening its grip on security, privacy, and reliability.

That includes deciding where AI can review or generate code, how to prevent leakage of sensitive information, and when AI outputs must be treated as untrusted suggestions rather than authoritative changes.

So for now, AI sits in two places. Individually, engineers treat it as an advanced search and scaffolding engine that can speed up everyday work, especially on isolated tools. Organisationally, it is a potential force multiplier that will only move closer to production when Paga is satisfied that its use will not weaken the very controls that have kept the platform safe for fifteen years. In a company that already thinks in terms of “security first, speed second,” even AI is required to respect the ordering.

## What It All Adds Up To
Taken together, Paga’s story is not about a clever microservices migration or a flashy rewrite. It is about a team that refused to let infrastructure, regulation, or fashion dictate its pace. They walked away from an off the shelf platform in India when it became clear they would spend years paying for change orders on someone else’s code.

They shifted from a consumer first dream to an agent first reality when KYC rules, feature phones, and cash culture made it the only viable way to reach real Nigerians. They kept a single well factored Java core alive for more than a decade, evolving it in place through Lagos data centers, floods and power cuts, and eventually into Azure and Kubernetes.

The principles are simple and hard to copy. Own the rails that define reliability and margin. Front load invisible work in architecture, observability, and contracts so you can change quickly when the environment moves. Decompose only when it buys reliability or speed, and treat data migrations as surgery rather than refactors.

Treat senior technical leadership and talent pipelines as hard constraints, not nice to haves. Be paranoid about security in practice, not only on paper. And never confuse a new pattern with a reason to throw away a working system that moves money for real people.

In a landscape where many startups have already rebuilt their core two or three times, Paga is an existence proof for a different approach. You can build one core, treat it as a living thing, and evolve it for fifteen years through regulation, new markets, and technology shifts. You just have to be willing to do the unglamorous work, over and over, in service of a simple promise: the system stays up, the money moves, and the rails belong to you.

## Technical Appendix
This appendix collects the concrete technologies and patterns behind Paga’s architecture, for readers who want to map the story to specific tools.
-   **Languages and frameworks:** Core services are written in Java, with the [Spring Framework](https://spring.io/) as the primary application framework. Early web interfaces used the Struts MVC framework. Data access started with a custom DAO layer and heavy use of stored procedures. Newer services use [jOOQ](https://www.jooq.org/) as a type safe SQL builder on top of SQL Server and Postgres.
-   **Data:** The main transactional stores are Microsoft SQL Server and PostgreSQL. The system leans on stored procedures for hot paths, read replicas to offload heavy reads, and partitioning where tables grow large. Operational and analytical streams are pushed into systems such as BigQuery to keep long running analytics off the primary OLTP databases.
-   **Caching:** Paga uses [Infinispan](https://infinispan.org/) as its primary in memory cache, largely because the team has deep operational experience with it. Caches are used to keep hot reads off the database, with careful attention to synchronization so that the money path remains correct even when other readers see slightly stale values.
-   **Queues and events:** For work queues and job style workloads, Paga uses [RabbitMQ](https://www.rabbitmq.com/) . For event streams and broader pub or sub cases, it uses [Apache Kafka](https://kafka.apache.org/).
-   **Infrastructure:** The platform runs on Azure Kubernetes Service, with all major services containerized since the 2020 cloud migration. Ingress and traffic management are handled through Nginx based controllers today, with further upgrades planned. Deployments are spread across multiple Azure availability zones, with Azure Front Door and related services used for health checks and failover.
-   **Security:** Security posture combines a PCI style control mindset with cloud native tooling. Azure Secure Score is tracked at the executive level and kept within a tight band, which forces continuous remediation of configuration drift and vulnerabilities. Card PANs and other high risk secrets are deliberately kept out of Paga’s own stores wherever possible, reducing the surface area that must be protected.
-   **Observability:** Metrics, traces, and logs are collected using Prometheus, OpenTelemetry based instrumentation, and Grafana and Loki for dashboards and log exploration. The company maintains custom dashboards for critical flows and a dedicated incident team that watches them, reflecting the belief that you cannot run a long lived payments core without first class observability.
-   **Concurrency and safety:** The money path remains synchronous and transactional. Database level row version checks and careful use of locking prevent double spends and dirty reads, while retries are used where appropriate to handle transient failures. Side effects, such as notifications and analytics updates, run asynchronously via queues and event streams, so they cannot block or corrupt core transactions.
-   **Throughput:** Across regions, the platform now handles on the order of tens of functional requests per second in steady state, with design headroom for several multiples of that. The combination of horizontal scaling at the application layer, read replicas and partitioning at the data layer, and queue based protection for the write path allows the system to absorb spikes without collapsing the core databases.