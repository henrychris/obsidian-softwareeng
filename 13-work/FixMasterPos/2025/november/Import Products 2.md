We are redesigning the import feature to support products that have unit + weight. There are three types of products that can be updated:
- single
- variant
- serialized

The difference between `weight` and `unit+weight`
- Weight - a product whose `stockType` is: `weight`.
- Unit + Weight - a product whose `stockType` is unit+weight

A `weight` product requires:
- `UnitOfMeasurement`

A `unit+weight` product has:
- `UnitOfMeasurement`
- `TotalUnits`
- `WeightPerUnit`

I want to rebuild this feature in an extensible way that allows it to be fully typed all the way down. This will involve modelling the different files as classes, with methods to validate, processItem and save. Validate returns a result - success or errors for the user. ProcessItem returns a Product that is added to an array and created in bulk. The types inferred from each line in the csv, will be used to determine the type passed to process item, and the ProductDocument it returns. its parsing, in a way.

This can be wrapped in another IImport class (idk lol) that allows structuring import flows  - with the websocket notifications - using a structure.

## Discussion With Gemini
Need to think about layered validation, based on the structure of unit and weight product above.
There are three product types: **simple, variable and serialised**. Unit and Weight products can be simple or variable, they have a `stockType` that determines which is which.

After validating simple/variable type, we need to move to the next one.

Then, for the abstraction. Ask about how validation works, type and play around with the code. How are errors bubbled up to callers?

Validation -> Enqueue -> Process & Report