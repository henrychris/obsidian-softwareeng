```sql
CREATE VIEW name AS
QUERY

-- eg
CREATE VIEW IT_DEPARTMENT AS
SELECT * FROM employees
WHERE department = 'IT';

-- can use joins, groups, etc in views

-- query a view like a table
SELECT * FROM IT_DEPARTMENT

-- delete a view
DROP VIEW IT_DEPARTMENT
```