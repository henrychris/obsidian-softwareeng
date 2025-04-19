Data required
```text
- timestamp
- strike price
- volume
- last trade date?
- ticker / option name
```

# Implementation
Leaning towards using .NET Dataflow for the pipelines. [Pipelines with Dataflow](https://michaelscodingspot.com/pipeline-pattern-tpl-dataflow/) seems like a good reference. 
- The main concern are the *first* step in the pipeline. I guess it would have a *void* input, and output the raw API data for transformation. 
- Another concern is how to setup retries. If transformation fails for whatever reason, how do we handle it?
- We can make use of parallelism for the first two steps. Fetch the data in parallel, then transform the data in parallel before merging into a final output, which is passed to the next step. The last(or third) step, saving data to db has to be in a single transaction (I think), plus no parallelism allowed for dbcontexts. Sha, is 6000 records a lot to insert at once?
- I think we can have *four* steps: Fetching -> Transforming -> Saving to Db -> Saving to CSV.
- Also, for the fetching part, if a request fails, it needs to be retried reliably. We don't want duplicate data. 
- Client say 6000 clients, but since he also said he wants *all* options, he probably means more than 6000.

# Plan
- Build pipeline pattern with Dataflow
- Implement retry functionality
- Get dummy data for a variety of options. 20 should suffice.
- Test running the pipeline every minute.
# References
- https://jack-vanlightly.com/blog/2018/4/17/processing-pipelines-series-introduction
	- https://jack-vanlightly.com/blog/2018/4/18/processing-pipelines-series-tpl-dataflow
- https://michaelscodingspot.com/pipeline-pattern-tpl-dataflow/
	- https://michaelscodingspot.com/pipeline-implementations-csharp-3/
- https://learn.microsoft.com/en-us/dotnet/standard/parallel-programming/walkthrough-creating-a-dataflow-pipeline
- https://medium.com/@bonnotguillaume/software-architecture-the-pipeline-design-pattern-from-zero-to-hero-b5c43d8a4e60

# API
- https://eodhd.com/lp/us-stock-options-api
	- https://eodhd.com/marketplace/unicornbay/options
- https://eodhd.com/marketplace/unicornbay/options/docs