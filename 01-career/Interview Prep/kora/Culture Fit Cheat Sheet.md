# About Kora
Founded in 2017.
## Vision
An Africa free of financial barriers. 
## Mission
To connect an interconnected Africa to the world.
## The Future
A business in Nigeria can collect payments from the US or Europe and settle instantly in Naira or Kenyan Shillings.
## The Gist
Show that you take your work **seriously**, **care** about what you build, and give a damn about the **people** you work with.
## People
- **Head of People and Culture** - Adeteju Adeleye
	- She was the first HR hire at Kora!
- **Lead Backend Engineer** - Chigozie Madubuko
- **Chief Operating Officer** - Dr Stephen Oluwatobi
	- Got his Bachelors & Masters in Economics at CU from 2003 - 2007
	- Got a PhD in Innovation Economics at CU between 2012-2016
	- Founded Hebron Startup Lab
- CTO- Oluwasegun Adeleye
- Favour Olawale - 
## Values
### Customers — Work to provide the best services for them
- At ErrandPay, customers reported webhooks dropping — I diagnosed and fixed it with the Outbox pattern
### Integrity — Act in ways consistent with your beliefs
- I believe engineers should care about the effects of their work — not just "does it run" but "is it correct, is it safe, will the next person understand it
- In practice: I leave documentation, write tests, make code easy to read and change
### Growth — Build an environment that encourages constant growth and self-improvement
- I always look to improve. I review my work, learn from mistakes, read and write about what I build, share articles I read with my teammates.
- I hated not being able to build FE applications. So I learned Svelte and now I can build whatever I want, 0 to 1.
### Tenacity — Work together to overcome the challenge, no matter the size
- Limestone API gateway went down mid-migration — built Docker Compose replicating the full topology so no other team lost a day
- Kora assessment: late instructions, 3-day window, full-time job running in parallel — delivered anyway
- Ilupeju incident: hosting a QBall game day, area boys wouldn't leave the pitch during the time we had paid for, a crowd of ~30 surrounded me, someone poked me in the eye — I negotiated, held my ground without escalating, got them off by 5:30, session ran.
### People -  All for one, and one for all.
- At Limestone: onboarded teammates onto the NATS library, wrote docs, reviewed 20 PRs in a day, rewrote Chima's broken PR chain rather than just rejecting it (because he was unavailable)
## Core Principles
### Leadership at every seat
At Kora, leadership means to fulfill the purpose of your role with excellence. The effort of every employee at Kora adds up when chasing their grand vision.
- I find it hard not to take responsibility. If something is broken, I fix it. I try to leave things better than I found them.
- Docker Compose at Limestone: not my problem, solved it anyway
- Cross-region latency at LunixPos: nobody asked me to look at infra, I noticed it, moved the DB, measured the results
### Relentless execution with world class standards
### Trust As The Foundation
- I say what I think, document what I don't know, don't oversell
	- Hell, my problem is I tend to undersell what I do or have done.
- I trust teammates to do their best work and don't micromanage
### Go and light up Africa.
- I play football in Lagos. I build tools for football in Lagos.
- I went to Morocco for AFCON, played there using their systems — I know what functional infrastructure feels like and how hard it is to build functional infrastructure.
- I tried to convert Naira to Dirhams in Morocco, dollar card didn't work, my friends' card hit its limit, PayPal blocked my account — we ended up finding a Nigerian at one of our football games to exchange cash with. In 2026. If Kora makes that disappear, sign me up.
# About Me
## Tell Us About Yourself
- Product engineer, not just backend — 0 to 1 by myself
- Wanted consulting → landed fintech (ErrandPay) → never left
- Limestone → LunixPos → Football tech & side projects (Qball, Listenfy)
- I have played nearly every sport I have had the chance to. But now, I play football 3x a week to stay sane.
- Other than that, I write, read, play video games or head to the cinema.
- Or if I really need a break, I go to Ibadan and spend a week or two.
## Where do you see yourself in 3-5 years?
- I want to be extremely competent — working here will help me get there
- Constantly in a room with engineers who are better than me, learning from them and the problems we solve
- In 3 years, I want to be someone others can learn from
- Preference: stay IC, not management. I want to keep shipping.
## What does good engineering culture look like to you?
- Psychological safety. It shouldn't feel like asking a question on Stack Overflow.
- High standards without pointing fingers
- Honest feedback, given kindly
- People who care about the craft, without ego-tripping.
## How do you balance your full-time job and QBall?
- Nights and weekends. 9-5 for my main role. Evenings and weekends for my side projects.
- I don't have much down time, but I'm young, this is the best time to grind. And I do enjoy it, so it doesn't feel like a grind.
- At Kora this role is my primary focus during working hours. No conflict.
## How do you handle conflict or disagreement?
- Make it concrete: discuss tradeoffs openly, not personalities
- Advocate for what I believe is right, but if someone has a better argument, I change my mind
- Once we decide, we go all-in as a team
## What's a weakness you're actively working on?
- Operating at scale is the honest gap — that's why I'm here
- Tendency to want to understand systems deeply before moving, which can slow initial delivery.
	- I'm learning to timebox the exploration, ship an MVP then refine it.
## Tell us about a time you failed or made a mistake
- NATS distributed monlith. 
- Used request-reply for inter-service comms — realised it created tight coupling through the broker, defeating the point of microservices
- Caught it before serious damage, refactored to event-driven with eventual consistency
- Lesson: difference between using a tool and understanding what it's actually for
# Questions!
## COO
- I read the CEO letter, and he mentioned 2026 as the year of going beyond Africa. What does success look like for Kora at the end of this year from your seat?
## Head Of People & Culture
- What does career progression actually look like for an engineer at Kora? Is management the inevitable path, or can I stay IC and keep shipping?
	- There are grid levels and competencies where you see where you are at, and what you need to do to get to the next level. it is collaborative and the manager doesn't make the decisions for you. They will also discuss it with you.
	- You can remain an individual contributors without remaining stagnant.
- You're remote, operating across multiple African countries. How do you keep the culture consistent? Or is it intentionally different in each place? And how have you managed to do that, going from 20 to 200
	- They are conscious about scaling and always ensure to communicate the culture. There are some things that are non negotiables. They try to be inclusive.
	- e.g. if using slang, explain what it means and keep it inclusive
- I saw you started a monthly newsletter (which I assume is internal), but this was an article from May 2025. If it still runs, do you accept submissions from within? I like to write, and would love to contribute.
	- It is employee led and they accept submissions!
## Engineering Lead
- What's the thing that surprised you most about working at Kora vs your expectations when you joined?
	- He had been there since the start with just 5 engineers. How could anything shock him when he started the journey? But what shocked him was the need to always evolve. And he realised at some point he had to stop writing code and switch from IC to manager. Now, he is completely hands off.
	- Management was challenging at the start. But he saw his shortcomings as things to improve on, not blockers from being a good manager.
- I did think of a solution to one of the questions I couldn't answer during the technical interview, but I guess we can talk about that some other time.
	- Regarding moving the network call out of a DB transaction.
		- generate reference -> calculate fee -> lock wallets -> validate balance -> debit wallets atomically -> release lock -> queue job to complete transaction initiation that runs immediately.
		- the queued job calls Kora and creates the transaction entries. if the provider call fails, we reverse the debit.

Favour Olawale.
Olusasegun Adeleye - he's been there since zero transactions. 