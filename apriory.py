"""
Data Mining book 5.2 Apriori Algorithm
"""

from __future__ import annotations

from itertools import combinations
from typing import List


class AprioriAnalyzer:
    def __init__(self, transactions: List[List[str]], min_support_count: int, min_confidence: int) -> None:
        self.transactions = transactions
        self.min_support_count = min_support_count
        self.min_confidence = min_confidence / 100

    def find_frequent_itemsets(self) -> List[List[str]]:
        """ 
        Finds and returns all frequent itemsets that meet the minimum support count. 
        """
        all_items = sorted(set(item for transaction in self.transactions for item in transaction))
        candidate_itemsets = [[item] for item in all_items]
        frequent_itemsets: List[List[str]] = []

        while candidate_itemsets:
            current_frequent_itemsets = []

            for itemset in candidate_itemsets:
                if self.count_support(itemset) >= self.min_support_count:
                    current_frequent_itemsets.append(itemset)
                    frequent_itemsets.append(itemset)

            candidate_itemsets = []

            for first_itemset in current_frequent_itemsets:
                for second_itemset in current_frequent_itemsets:
                    merged_itemset = sorted(set(first_itemset + second_itemset))

                    if len(merged_itemset) == len(first_itemset) + 1:
                        if merged_itemset not in candidate_itemsets:
                            candidate_itemsets.append(merged_itemset)

        return frequent_itemsets

    def generate_rules(self, frequent_itemsets: List[List[str]]) -> None:
        """
         Generates and prints association rules from the frequent itemsets.
        """
        label = "Association Rules"
        print(f"\n{label}")
        print("-" * len(label))

        for itemset in frequent_itemsets:
            if len(itemset) < 2:
                continue

            for size in range(1, len(itemset)):
                for left_tuple in combinations(itemset, size):
                    left_side = list(left_tuple)
                    right_side = [item for item in itemset if item not in left_side]

                    itemset_support = self.count_support(itemset)
                    left_side_support = self.count_support(left_side)
                    confidence = itemset_support / left_side_support

                    if confidence >= self.min_confidence:
                        print(
                            f"{left_side} -> {right_side} "
                            f"confidence={confidence:.2f}, support_count={itemset_support}"
                        )

    def count_support(self, itemset: List[str]) -> int:
        """
        Counts how many transactions contain the given itemset.
        """
        count = 0

        for transaction in self.transactions:
            if all(item in transaction for item in itemset):
                count += 1

        return count

    def print_frequent_itemsets(self, frequent_itemsets: List[List[str]]) -> None:
        label = "Frequent Itemsets"

        print(f"\n{label}")
        print("-" * len(label))

        for itemset in frequent_itemsets:
            support_count = self.count_support(itemset)
            print(f"{itemset} support_count={support_count}")


def main() -> None:
    transactions = [
        ["milk", "bread", "butter"],
        ["milk", "bread"],
        ["milk", "butter"],
        ["bread", "butter"],
        ["milk", "bread", "butter"],
        
        # ["Diet Coke", "Burger", "Hot Dog"],
        # ["milk", "Burger"],          
        # ["bread", "Burger"],    
        # ["Burger", "Hot Dog"],     
    ]

    analyzer = AprioriAnalyzer(
        transactions=transactions,
        min_support_count=3,
        min_confidence=60,
    )

    frequent_itemsets = analyzer.find_frequent_itemsets()
    analyzer.print_frequent_itemsets(frequent_itemsets)
    analyzer.generate_rules(frequent_itemsets)


if __name__ == "__main__":
    main()
