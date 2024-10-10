The **UTXO** (Unspent Transaction Output) model is a key concept in blockchain systems, particularly in Bitcoin. It represents a way of keeping track of who owns what amount of cryptocurrency. Instead of maintaining account balances like a traditional bank, Bitcoin and similar blockchains use UTXOs to represent spendable "chunks" of cryptocurrency.

A UTXO contains:
- transaction id of the transaction that created this UTXO
- index of this UTXO in the transactions output list
- the value of the UTXO
- optionally, it specifies the conditions where the UTXO can be spent.
	- I believe this is done using [Script](https://en.bitcoin.it/wiki/Script).

A transaction contains:
- reference number
- references to one or more input UTXOs
- reference to one or more created output UTXOs
- total input and output amounts
### How UTXO Works:
1. **Transaction Outputs**: 
   - In Bitcoin, every transaction creates outputs. Each output is a specified amount of Bitcoin that can be spent by the recipient. These outputs are assigned to specific addresses, controlled by the recipient’s private key.   
2. **Unspent Transaction Outputs**: 
   - When someone receives Bitcoin, that value is recorded as an **unspent transaction output** (UTXO). The key point is that this UTXO is **unspent** and can be used in a future transaction.
   - UTXOs are essentially "coins" or "tokens" that haven't been spent yet.
3. **Spending UTXOs**:
   - When you make a transaction, you reference one or more UTXOs you control as **inputs** for the transaction. These inputs are "spent" and become invalid for future use.
   - After spending, the transaction usually creates new UTXOs for the recipient(s) and, potentially, a "change" UTXO sent back to the sender (if the input amount exceeds the transaction amount).
4. **Blockchain Verification**: 
   - Nodes in the blockchain track all UTXOs. When a new transaction is created, the network checks if the referenced UTXOs are valid (i.e., unspent). If valid, the transaction is confirmed, and the UTXOs are updated (the old ones are marked as spent, and new UTXOs are created).
### Example:
- Alice receives 2 BTC from Bob in a transaction. This 2 BTC becomes an unspent output (UTXO) associated with Alice’s address.
- Alice later wants to send 1.5 BTC to Charlie. To do this, she creates a transaction that uses her 2 BTC UTXO as an input. The transaction sends 1.5 BTC to Charlie (creating a new UTXO for him) and 0.5 BTC back to herself as "change" (another new UTXO).
### Key Characteristics of UTXO:
- **No Balances**: There are no direct balances like in a traditional account-based system. Instead, you hold UTXOs of various sizes, which together make up your spendable amount.
- **Immutability**: Once a UTXO is spent, it’s recorded on the blockchain and can never be used again. The blockchain ensures that no one can double-spend or use the same UTXO more than once.
- **Efficiency**: UTXOs allow transactions to be easily verifiable. Each node only needs to check that the UTXOs referenced in a transaction are unspent.
### Comparison to Account Model:
- In an **account-based model** (like Ethereum), balances are updated directly in an account ledger after each transaction.
- In the **UTXO model**, transactions reference specific outputs from previous transactions, and no running account balance is maintained directly.
### Summary:
UTXOs represent unspent outputs from previous transactions and are the foundation of how value is tracked and transferred in Bitcoin. When you spend Bitcoin, you're using UTXOs as inputs to create new UTXOs, and the process repeats itself with each new transaction.

In a blockchain like Bitcoin, **UTXOs (Unspent Transaction Outputs)** are stored in a special data structure called the **UTXO set**, which is maintained by full nodes on the network. This set allows nodes to quickly check whether a transaction is valid by ensuring that the inputs being spent haven't already been used in another transaction.
## UTXO Storage
1. **UTXO Set**:
   - The **UTXO set** is a collection of all the unspent outputs that exist on the blockchain. These outputs represent the spendable funds available in the network.
   - Each node maintains a copy of this UTXO set locally. The UTXO set is constantly updated as new transactions are validated and confirmed into blocks.
2. **Data Structure**:
   - The UTXO set is typically stored in memory or on disk using efficient data structures such as **hash maps** or **database systems** like LevelDB (in Bitcoin’s case).
   - Each UTXO entry contains:
     - **Transaction ID (TxID)**: The unique ID of the transaction that created the UTXO.
     - **Output index**: The position of the output within the transaction.
     - **Value**: The amount of cryptocurrency held by this UTXO.
     - **ScriptPubKey**: A script that defines the conditions under which the UTXO can be spent (usually involving a public key).
3. **When a New Block is Processed**:
   - When a block is mined and added to the blockchain, nodes perform two operations:
     1. **Remove spent UTXOs**: The inputs of transactions in the block reference UTXOs. These UTXOs are considered "spent" and are removed from the UTXO set.
     2. **Add new UTXOs**: The outputs of new transactions in the block are added to the UTXO set as new unspent outputs.   
4. **Efficient Lookup**:
   - Because UTXOs are stored in a **hash map** or **database**, lookups are fast. When validating a transaction, a node can quickly check whether the inputs of the transaction are still in the UTXO set (i.e., they are unspent) and whether the transaction is valid.
5. **Persistence and Storage**:
   - Nodes persist the UTXO set on disk to ensure it is not lost between restarts.
   - In Bitcoin, the full UTXO set can take several gigabytes of storage, and it grows over time as new blocks are added. However, it is still far smaller than the entire blockchain, as it only contains the unspent outputs rather than the complete history of all transactions.
### Key Points on UTXO Storage:
- **UTXO Set**: A set of all current unspent transaction outputs stored by full nodes.
- **Efficiency**: The UTXO set allows nodes to verify transactions without scanning the entire blockchain.
- **Data Structure**: Typically stored in a hash map or database system for fast access and lookup.
- **Updates**: The set is updated with each new block, removing spent UTXOs and adding new ones.
- **Size**: The UTXO set grows over time as the blockchain grows, but it only contains the current spendable outputs, not the entire history of all transactions.

This model ensures that blockchain nodes can efficiently validate transactions and maintain consensus without having to scan the entire blockchain every time.