Bitcoin facilitates P2P transfer of value without a central authority, while preventing double spending. The whole point is to agree on a chronological order of transactions in order to prevent double spending.
# 1. Introduction
This critiques the **trust-based** model we currently use in online commerce and proposes a move to a **cryptographic, trustless** model

- **Weakness of trust-based systems**: Current online commerce relies on financial institutions as trusted third parties to mediate and process transactions. This increases costs, limits small transactions, and introduces the possibility of transaction reversals, which leads to inefficiencies and fraud concerns.
- **Need for a trustless system**: The section calls for an electronic payment system that relies on **cryptographic proof** rather than trust, allowing parties to transact directly without intermediaries. This would reduce transaction costs and prevent fraud by making transactions irreversible through computational proof.

The solution? **Blockchain**. 
The proposed system addresses the double-spending problem using a **peer-to-peer distributed & decentralised timestamp server**, which ensures the chronological order of transactions through computational proof (such as Proof of Work). The system's security depends on honest nodes controlling the majority of computing power.

# 2. Transactions
An **electronic coin** is a chain of digital signatures. Ownership of the coin is transferred by each owner signing a hash of the previous transaction and the public key of the next owner. This forms a chain of signatures that can be verified by the payee to ensure the coin's history and ownership.
- **Double-spending problem**: The risk with this system is that the payee cannot verify if one of the previous owners has double-spent the coin (i.e., used the same coin in multiple transactions). Traditionally, a central authority (mint) would solve this by verifying each transaction and reissuing coins to prevent double-spending.
- **Decentralised solution**: The section proposes eliminating the mint and introducing a decentralised way to ensure the payee knows the transaction is valid and hasn't been double-spent. This requires all transactions to be **publicly announced**, and a system for participants to agree on the order of transactions, ensuring the first transaction is the valid one.
- **Consensus**: The payee needs proof that the majority of nodes in the network agree that the transaction they received was the first occurrence of the coin being spent, ensuring no double-spending occurred. This forms the foundation of how a decentralised consensus (such as Proof of Work) operates.

# 3. Timestamp Server
!!![[../../../../../assets/bitcoin-whitepaper-1.png]]
The proposed solution begins with a **timestamp server**, which creates a verifiable record of when data existed. The timestamp server works by taking a hash of a block of items that need to be timestamped and widely publishing the hash (e.g., in a newspaper or Usenet post). The purpose of the timestamp is to prove that the data must have existed at a specific point in time, since it was included in the hash.

Each **timestamp** includes the hash of the previous timestamp, forming a continuous chain. This creates a sequence where each new timestamp reinforces the previous ones, providing a secure and immutable record of the order in which events occurred.

Of course, changing any data in the chain will affect the subsequent items in the chain.
# 4. Proof Of Work
!!![[../../../../../assets/bitcoin-whitepaper-2.png]]
The network has a difficulty target set. This defines how many zero bits should be padded to the start of the hash when it is generated.
The hash is generated using the data in the block & the nonce. The nonce is any number that when used in the hash function, generates a hash that satisfies the difficulty target. How is the nonce computed?

Starting from 0, the number is incremented and used to hash the block. If the generated hash doesn't satisfy the difficulty target, the process is repeated until it does. This is computationally expensive.

If any data in the block is changed, the hash changes & the PoW must be recomputed. The PoW must also be recomputed for subsequent blocks.

Consensus is reached across the network using the **Longest Chain Rule.** See: [[../1.2 Blockchain Structure#Longest Chain Rule]]
# 5. Network
1. New transactions are broadcast to all nodes
	- A node sends to nodes it is connected with, and those nodes send to those they are connected with, and so on.
	- They are sent to the entire network really.
2. Each node collects transaction in a block
3. Each node computes the PoW for the bloch
4. When PoW is computed, it is broadcast to all nodes
5. Nodes only accepts a block after validating the block, all its transactions, and ensuring the coins haven't already been spent
6. Nodes accept a block by using its hash as the previous hash when creating the next block in the chain
## How are blocks validated?
First, the node checks that the block's hash, when combined with the provided nonce, meets the required difficulty level (e.g., starts with a certain number of leading zeros). The node also verifies that the block references the correct previous block and that all transactions in the block are valid.
### But how are transactions validated?
Each transaction is validated by:
1. Verifying the signature using the sender's public key. This ensures the transaction was signed with the correct private key, proving its authenticity.
2. Checking whether the sender has enough unspent outputs (in UTXO models) or sufficient account balance (in account models) to cover the transaction.

Transactions are efficiently verified using **Merkle trees**, which allow nodes to confirm that a specific transaction belongs to a block. Once a transaction is confirmed, it is marked as **spent** (for UTXO) or the account balance is updated (for account-based models).

If all transactions are valid and the block hash meets the required difficulty, the block is considered **valid** and added to the chain.
# 6. Incentive
- The first transaction in a block creates a new coin, issued to the miner. Miners receive new coins as a reward for expending computing power and electricity. 
- Miners can also receive **transaction fees** as an additional reward. If a transaction's **input value** (the total amount of coins spent) exceeds its **output value** (the total amount being sent), the difference is considered a transaction fee, which is added to the block reward.
- Bitcoin has a cap of 21 million coins in circulation, once that number is reached, miners will no longer receive new coins for the first transaction in a block. 
- Instead, miners will receive rewards through transaction fees, ensuring the network stays inflation free.

The economic incentives of mining encourage nodes to behave honestly. Even if a miner amasses enough computational power to attack the network (e.g., a 51% attack), it is more profitable to mine new coins legitimately rather than undermining the system.
By following the rules, the miner would continue to accumulate wealth through mining, which would be more lucrative than attempting to defraud the system and risk devaluing the currency they hold.
# 7. 
# Notes
Bitcoin uses the Unspent Transaction Output Model (UTXO). See: [[UTXO]].
