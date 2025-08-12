```sql
-- simple
CREATE INDEX index_name on table(column)

-- composite
CREATE INDEX index_name on table(column_1, column_2)

-- unique
CREATE UNIQUE INDEX index_name on table(column)

-- partial
CREATE INDEX index_name on table(column)
WHERE column = value
```
