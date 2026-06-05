# MIT_DBA

Small Python scripts for two database/data-structure exercises:

- `b_plus_tree_pr.py` implements a B+ tree with insert, search, delete, range search, and tree-print helpers.
- `BPlusTreeDrawer.py` renders the tree as ASCII art.
- `apriory.py` runs an Apriori frequent-itemset and association-rule demo.

## Requirements

- Python 3.12 or newer is recommended.
- No third-party dependencies are required.

## Running the scripts

### B+ tree demo

```bash
python3 b_plus_tree.py
```

### Apriori demo

```bash
python3 apriori_itemset.py
```

## Algo 
### B+ Tree
```python
"""
# B+ Tree Algorithms

## Insert
1. If root is full, split the root.
2. Traverse from root to the target leaf.
3. Before descending, split any full child.
4. Insert the key in sorted order into the leaf.
5. If key exists, update its value.

## Leaf Split
1. Create a new leaf node.
2. Split keys/values at the middle.
3. Move the second half to the new leaf.
4. Update leaf links (`next_leaf`).
5. Copy the first key of the new leaf to the parent.

## Internal Node Split
1. Create a new internal node.
2. Find the middle key.
3. Promote the middle key to the parent.
4. Move keys and child pointers after the middle to the new node.

## Search
1. Start at the root.
2. Follow child pointers using separator keys.
3. Reach the target leaf.
4. Search for the key in the leaf.

## Range Search
1. Find the leaf containing the start key.
2. Scan keys in the leaf.
3. Follow `next_leaf` pointers.
4. Stop when keys exceed the end key.

## Delete 
1. Find the target leaf.
2. Remove the key and value if found.
3. Return success or failure.

"""
```
### Apriori
```python
"""
Apriori Algorithm

Purpose:
    Find item combinations that frequently occur together
    in a transaction database.

Input:
    - Transactions
    - Minimum Support Count

Output:
    - All Frequent Itemsets

Key Idea:
    If an itemset is frequent, then all of its subsets
    must also be frequent.

Algorithm:

1. Find Frequent 1-Itemsets (L1)

    - Scan all transactions.
    - Count how many times each item appears.
    - Remove items whose support count is less than
      the minimum support.
    - Store remaining items as L1.

2. Generate Candidate Itemsets (Ck)

    - Join frequent itemsets from the previous level.
    - Create larger itemsets of size k.

    Example:

        L2:
            {Milk, Bread}
            {Milk, Butter}

        Candidate:
            {Milk, Bread, Butter}

3. Prune Candidates

    - For each candidate itemset, generate all
      (k - 1)-sized subsets.
    - If any subset is not frequent, remove
      the candidate immediately.

    Example:

        Candidate:
            {Milk, Bread, Butter}

        Subsets:
            {Milk, Bread}
            {Milk, Butter}
            {Bread, Butter}

        If any subset is missing from L2,
        remove the candidate.

4. Count Support

    - Scan every transaction.
    - Check whether each candidate itemset
      exists in the transaction.
    - Increase its support count if found.

5. Generate Frequent Itemsets

    - Keep only candidates whose support count
      is greater than or equal to the minimum support.
    - Store them as Lk.

6. Repeat

    Generate Candidates
        ->
    Prune Candidates
        ->
    Count Support
        ->
    Generate Frequent Itemsets

    Continue until no new frequent itemsets
    can be generated.

7. Return Result

    - Combine all frequent itemsets from
      every level.
    - Return the complete set of frequent itemsets.

Example:

    Transactions:

        T1 = {Milk, Bread}
        T2 = {Milk, Bread, Butter}
        T3 = {Milk, Butter}
        T4 = {Bread, Butter}
        T5 = {Milk, Bread}

    Minimum Support = 2

    L1:

        Milk   = 4
        Bread  = 4
        Butter = 3

    L2:

        {Milk, Bread}   = 3
        {Milk, Butter}  = 2
        {Bread, Butter} = 2

    L3:

        {Milk, Bread, Butter} = 1

    Since support is less than 2,
    remove the itemset.

    Final Frequent Itemsets:

        {Milk}
        {Bread}
        {Butter}
        {Milk, Bread}
        {Milk, Butter}
        {Bread, Butter}
"""
```

## Project Notes

- The repository is intentionally lightweight and script-based.
- A `.gitignore` is included for Python caches, virtual environments, editor files, and common build artifacts.

## License

This project is licensed under a custom GPL-3.0-based license with an additional restriction: commercial use is not permitted without prior written permission from the copyright holder.

See [`LICENSE`](./LICENSE) for the full text.

