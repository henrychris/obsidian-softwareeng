# Inner Join
```sql
SELECT column, another_table_column, …
FROM mytable
INNER JOIN another_table 
    ON mytable.id = another_table.id
WHERE condition(s)
ORDER BY column, … ASC/DESC
LIMIT num_limit OFFSET num_offset;
```
An inner join is the default, as such you can simply use `JOIN`. It selects records that have matching values in two tables.
# Outer Joins
```sql
SELECT column, another_column, …
FROM mytable
LEFT/RIGHT/FULL JOIN another_table 
    ON mytable.id = another_table.matching_id
WHERE condition(s)
ORDER BY column, … ASC/DESC
LIMIT num_limit OFFSET num_offset;
```
Assume there are two tables, A & B.
## Left Join
Includes all rows from A, whether or not there are matching values in B.
## Right Join
Keeps rows from B, whether or not there are matching values in A.
## Full Join
Rows from both tables are kept, whether they have matching values or not.
# Continued
	It is up to the developer to decide how to handle NULL.