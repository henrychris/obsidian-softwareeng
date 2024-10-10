Bitcoin nodes verify transactions by following a set of predefined rules to ensure that the transactions are valid and consistent with the blockchain’s protocol. First see: [[UTXO]].
# Transaction Structure
Each transaction must have:
- **Inputs**: The source of the funds, referencing previous outputs (UTXOs). This contains:
	- A transaction id, referencing the transaction containing the UTXO being spent
	- An index, referencing which UTXO from the transaction is spent
	- A **scriptSig** which satisfies the conditions placed on the UTXO, unlocking it for spending
- **Outputs**: The destination where the funds are going. This contains:
	- An amount of bitcoin, denominated in _satoshis_, the smallest bitcoin unit
	- A cryptographic puzzle that determines the conditions required to spend the output - a **scriptPubKey**
Nodes first check the structure of the transaction to make sure it is properly formatted.
The **scriptSig** and **scriptPubKey** are discussed below.
# Input Validation (UTXO Verification)
Bitcoin operates using **UTXOs** (Unspent Transaction Outputs), which represent the unspent funds from previous transactions. To verify a transaction, nodes check:
- **Existence of UTXOs**: The inputs of the transaction reference prior outputs (UTXOs). The node verifies that these referenced UTXOs actually exist on the blockchain and haven’t been spent yet.
- **Ownership of UTXOs**: Each input must include a digital signature proving that the sender owns the private key associated with the public key that controls the UTXO. Nodes verify the digital signature to ensure that the sender has the authority to spend those funds.
# Double-Spending Check
Nodes ensure that the UTXOs being spent haven’t already been used in another transaction. This prevents **double-spending**, where someone tries to spend the same funds twice. If a UTXO has already been spent, the transaction is considered invalid.
# Input and Output Amount Matching
- Nodes check that the sum of inputs **equals** or **exceeds** the sum of outputs. If the outputs exceed the inputs, the transaction is invalid.
- **Transaction fees** are calculated as the difference between inputs and outputs. A small discrepancy between input and output is allowed, representing the miner’s fee.
# Script Validation (Unlocking UTXOs)
Bitcoin uses a scripting language to lock and unlock UTXOs. Each UTXO is locked by a script (usually a **Pay-to-PubKey-Hash** script, where the recipient’s public key hash is stored). To unlock and spend the UTXO, the transaction must include a valid signature that satisfies this script.
- Nodes run the **scriptPubKey** (locking script) and the **scriptSig** (unlocking script) to check if the transaction properly satisfies the script and can spend the UTXO.
# Signature Validation
- Each input includes a **cryptographic signature**, proving that the owner of the referenced UTXO has signed the transaction. The node checks that this signature matches the public key of the UTXO and that the signature is valid.
- The signature also ensures the transaction hasn't been altered since it was signed.
# Transaction Size and Limits
Nodes ensure that the transaction adheres to network rules regarding:
- **Transaction size**: Must not exceed the block size limit.
- **Dust transactions**: If an output is too small (below a dust threshold), it might be considered spam and invalid.
# Mempool Check
Before a transaction is confirmed in a block, it is placed in the **mempool** (memory pool) where it waits to be included by miners. Transactions with higher fees are preferred by miners. Nodes verify:
- The transaction hasn’t already been included in a block.
- The transaction is not conflicting with any other transaction in the mempool.
- The transaction is not a coinbase transaction - the first transaction in a block, that creates new currency.
# Block Inclusion and Consensus
Once a miner includes the transaction in a block, it verifies:
- **Proof of Work (PoW)**: The block containing the transaction must have a valid PoW, ensuring the miner expended computational effort.
- **Block structure**: The block must conform to network rules (correct format, valid timestamp, proper nonce, etc.).
- **Chain validity**: The block must extend the longest valid blockchain. Miners reject forks that aren’t consistent with the current valid chain.
# Broadcasting
If a block passes all checks, it’s added to the blockchain, and the transaction is removed from the mempool. The miner then broadcasts the block to the rest of the network.
# Summary
Bitcoin nodes verify transactions by:
1. Checking the existence and validity of UTXOs.
2. Ensuring proper ownership and signatures.
3. Preventing double-spending.
4. Verifying that inputs and outputs match.
5. Running and validating Bitcoin scripts.
6. Ensuring the transaction complies with size and policy limits.
7. Finally, verifying that the block containing the transaction adheres to the consensus rules.

See: [Saylor Academy - Transactions](https://learn.saylor.org/mod/book/view.php?id=36340&chapterid=18908), [Study Guide - Transactions](https://learn.saylor.org/mod/book/view.php?id=54971&chapterid=40652), [Study Guide - Consensus](https://learn.saylor.org/mod/book/view.php?id=54971&chapterid=40651).

