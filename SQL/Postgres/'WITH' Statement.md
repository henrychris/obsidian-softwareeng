This is used to simplify complex queries. In cases where you make multiple sub-queries in one 'transaction' or 'block' to accomplish something, you can assign the results of a sub-query to a temporary table. See: [WITH - Postgres](https://www.postgresql.org/docs/current/queries-with.html#QUERIES-WITH-MODIFYING)
```sql
-- table structure
CREATE TABLE nodes (
  node_id INT PRIMARY KEY,
  parent_id INT
);

-- delete node & assign children to its parent
with grand_parent_node as (select "parent_id" from "nodes" where "node_id" = 5)

update "nodes"
set "parent_id" = (SELECT parent_id FROM grand_parent_node)
where "parent_id" = 5;
```

