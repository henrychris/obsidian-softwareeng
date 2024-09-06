[Mongoose Primer](https://developer.mozilla.org/en-US/docs/Learn/Server-side/Express_Nodejs/mongoose#mongoose_primer)
[MasteringMongoose](https://masteringjs.io/mongoose)
# Setup With Docker
1. Pull the image and run the container
```bash
docker run --name mongodb -p 27017:27017 -d mongodb/mongodb-community-server:latest

docker run --name mongodb -p 27017:27017 -d mongodb/mongodb-community-server:latest
```
2. Exec into the container and create the database
```bash
docker container exec -it mongodb bash

#container-root: use mydbone 
```
Now the database is running and can be reached on localhost at port 27017.
# Connecting To Mongo
We only need to connect to mongoose from the entry point file. The connection is stored internally, and our models will reuse the same connection by default.
```js
const mongoose = require("mongoose");
mongoose.set("strictQuery", false);
const mongoDB = "mongodb://127.0.0.1/mydbone";

main().catch((err) => console.log(err));
async function main() {
    await mongoose.connect(mongoDB);
    console.log("Connected to MongoDB");
}
```
Use `mongoose.connection` to get this default connection when needed.
# Schemas, Models & Collections
## TLDR
1. **Collections** store documents in MongoDB.
2. **Schemas** define the structure of documents within a collection when using Mongoose.
3. **Models** provide an interface to work with documents in a collection, using the structure defined by a schema.

In practice:
- **Schema** defines the shape of the documents.
- **Model** connects the schema to a **collection**.
- **Collection** is where the documents are physically stored.
## Collection
A collection is like a table in a relational DB. It stores documents, which can be likened to rows. Each document is a JSON-like object.
## Schema
A schema is a blueprint that defines the structure of documents in a collection. It defines properties, validation rules & the type of data they store.
We can specify [virtual](https://mongoosejs.com/docs/guide.html#virtuals) properties which aren't saved in the database, but can be used to get values in a specific format (e.g. first name + last name = full name).
We can add other stuff like instance methods (with access to values of the current object), static methods or query helpers (think extension methods).
## Model
A model is an interface for interacting with a collection. We can use it to CRUD documents in a collection.
##
This sample creates a schema with a single string property & a `virtual` URL. It exports the model, which is used by the rest of the application to interact with the `Genres` collection.
```js
const mongoose = require("mongoose");
const Schema = mongoose.Schema;

const GenreSchema = new Schema({
    name: { type: String, required: true, min: 3, max: 100 },
});

// Virtual for genre URL
GenreSchema.virtual("url").get(function () {
    // We don't use an arrow function as we'll need the this object
    return `/catalog/genres/${this._id}`;
});

// Export model
module.exports = mongoose.model("Genre", GenreSchema);
```

# Working With Related Documents
To work with related documents, we need to add a field referencing the `_id` property of the document. This field has a `mongoose.Schema.Types.ObjectId` type and specifies the name of the model being referenced.
```js
const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const AuthorSchema = new Schema({
  name: { type: String, required: true },
  age: Number,
  books: [{type: Schema.Types.ObjectId, ref: 'Book'}]
});

module.exports = mongoose.model('Author', AuthorSchema);

// book.js
const BookSchema = new Schema({
  title: { type: String, required: true },
  author: { type: Schema.Types.ObjectId, ref: 'Author', required: true },
});

module.exports = mongoose.model('Book', BookSchema);
```

```js
const Author = require('./models/author');
const Book = require('./models/book');

// Create an author
const author = new Author({ name: 'J.K. Rowling', age: 55 });
await author.save();

// Create a book and link it to the author
const book = new Book({ title: 'Harry Potter', author: author._id });
await book.save();
```

Note that while Author references an Array of books, we should only add a reference in one place. It is either we add the new book to the Author array, or we set the author \_id in the Book model.

```js
const book = await Book.findOne({ title: 'Harry Potter' }).populate('author');
console.log(book);
// Output will include the full Author document under `author` field
```

Of course, `populate` can be chained or even nested.
```js
// chaining to populate multiple fields
Book.find()
  .populate('author')
  .populate('publisher')  // Assuming `publisher` is another reference
  .exec((err, books) => {
    // books now contain fully populated `author` and `publisher` fields
  });
```

```js
// nesting to populate a field inside a field
Book.findOne({ title: 'Harry Potter' })
  .populate({
    path: 'author',
    populate: { path: 'publisher' }  // Assuming Author references Publisher
  });
```

```js
// populate specific fields
Book.findOne({ title: 'Harry Potter' })
  .populate('author', 'name age')  // Only populate the `name` and `age` fields
  .exec((err, book) => {
    console.log(book.author.name); // Only `name` and `age` fields are populated
  });
```

Read more on [Queries](https://mongoosejs.com/docs/queries.html), [Validation](https://mongoosejs.com/docs/validation.html) and [Schema Types](https://mongoosejs.com/docs/schematypes.html).