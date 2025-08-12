```sql
BEGIN;

INSERT INTO customers (name, email) VALUES ('John Doe', 'john@email.com'); INSERT INTO orders (customer_id, total) VALUES (LAST_INSERT_ID(), 100.00);

COMMIT;

-- rollback if sth goes wrong
-- With error handling
BEGIN;
    UPDATE accounts SET balance = balance - 100 WHERE id = 1;
    UPDATE accounts SET balance = balance + 100 WHERE id = 2;
    
    -- Check if balances are valid
    IF (SELECT balance FROM accounts WHERE id = 1) < 0 THEN
        ROLLBACK;
    ELSE
        COMMIT;
    END IF;

-- set isolation levels
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
```
# Isolation Levels
1. READ UNCOMMITTED
	- Allows:
		- Can read uncommitted changes from other transactions.
		- Fast but least safe
	- Problems:
		- Dirty reads
		- Non repeatable reads
		- Phantom reads
2. READ COMMITTED (usually default)
	- Prevents:
		- No dirty reads
	- Problems:
		- Non repeatable reads
		- Phantom reads
	- Scenarios:
		- Most web applications
3. REPEATABLE READ
	- Prevents:
		- No dirty reads
		- Non non repeatable reads
	- Problems:
		- Phantom reads
	- Scenarios:
		- Financial calculations, audit trails
4. SERIALIZABLE (highest isolation)
	- Prevents:
		- No dirty reads
		- No non repeatable reads
		- No phantom reads
	- Problems:
		- Slow because it locks the table
	- Scenarios:
		- Critical financial transactions, inventory management