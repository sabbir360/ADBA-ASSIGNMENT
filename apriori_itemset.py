from itertools import combinations
from typing import List, Set, FrozenSet, Dict, Tuple


class Apriori:
    def __init__(
        self,
        transactions: List[List[str]],
        min_support_count: int,
        min_confidence: float,
    ):
        self.transactions: List[Set[str]] = [set(t) for t in transactions]
        self.min_support_count = min_support_count
        self.min_confidence = min_confidence

        self.frequent_itemsets: Dict[FrozenSet[str], int] = {}

    def fit(self) -> Dict[FrozenSet[str], int]:
        """Run the Apriori algorithm to find frequent itemsets."""   

        current_frequent_itemsets = self._find_frequent_1_itemsets()
        k = 2

        while current_frequent_itemsets:
            candidates = self._apriori_gen(current_frequent_itemsets, k)
            candidate_counts = self._count_candidates(candidates)

            current_frequent_itemsets = {
                itemset: count
                for itemset, count in candidate_counts.items()
                if count >= self.min_support_count
            }

            self.frequent_itemsets.update(current_frequent_itemsets)
            k += 1

        return self.frequent_itemsets

    def _find_frequent_1_itemsets(self) -> Dict[FrozenSet[str], int]:
        item_counts: Dict[FrozenSet[str], int] = {}

        for transaction in self.transactions:
            for item in transaction:
                itemset = frozenset([item])
                item_counts[itemset] = item_counts.get(itemset, 0) + 1

        frequent_1_itemsets = {
            itemset: count
            for itemset, count in item_counts.items()
            if count >= self.min_support_count
        }

        self.frequent_itemsets.update(frequent_1_itemsets)
        return frequent_1_itemsets

    def _apriori_gen(
        self, previous_frequent_itemsets: Dict[FrozenSet[str], int], k: int
    ) -> Set[FrozenSet[str]]:
        previous_itemsets = list(previous_frequent_itemsets.keys())
        previous_itemsets_set = set(previous_itemsets)

        candidates: Set[FrozenSet[str]] = set()

        for i in range(len(previous_itemsets)):
            for j in range(i + 1, len(previous_itemsets)):
                first = sorted(previous_itemsets[i])
                second = sorted(previous_itemsets[j])

                # Join step:
                # Join only if first k-2 items are same.
                if first[: k - 2] == second[: k - 2]:
                    candidate = frozenset(previous_itemsets[i] | previous_itemsets[j])

                    if len(candidate) == k and not self._has_infrequent_subset(
                        candidate, previous_itemsets_set, k
                    ):
                        candidates.add(candidate)

        return candidates

    def _has_infrequent_subset(
        self,
        candidate: FrozenSet[str],
        previous_itemsets_set: Set[FrozenSet[str]],
        k: int,
    ) -> bool:
        # Prune step:
        # Every (k-1)-subset must be frequent.
        for subset in combinations(candidate, k - 1):
            if frozenset(subset) not in previous_itemsets_set:
                return True
        return False

    def _count_candidates(
        self, candidates: Set[FrozenSet[str]]
    ) -> Dict[FrozenSet[str], int]:
        counts = {candidate: 0 for candidate in candidates}

        for transaction in self.transactions:
            for candidate in candidates:
                if candidate.issubset(transaction):
                    counts[candidate] += 1

        return counts

    # def generate_rules(self) -> List[Tuple[Set[str], Set[str], int, float]]:
    #     """Generate association rules from the frequent itemsets."""
    #     rules = []

    #     for itemset, support_count in self.frequent_itemsets.items():
    #         if len(itemset) < 2:
    #             continue

    #         for size in range(1, len(itemset)):
    #             for left in combinations(itemset, size):
    #                 left = frozenset(left)
    #                 right = itemset - left

    #                 confidence = support_count / self.frequent_itemsets[left]

    #                 if confidence >= self.min_confidence:
    #                     rules.append((set(left), set(right), support_count, confidence))

    #     return rules


if __name__ == "__main__":
    transactions = [
        ["I1", "I2", "I5"],
        ["I2", "I4"],
        ["I2", "I3"],
        ["I1", "I2", "I4"],
        ["I1", "I3"],
        ["I2", "I3"],
        ["I1", "I3"],
        ["I1", "I2", "I3", "I5"],
        ["I1", "I2", "I3"],
    ]

    apriori = Apriori(
        transactions=transactions, min_support_count=2, min_confidence=0.70
    )

    frequent_itemsets = apriori.fit()
    #rules = apriori.generate_rules()

    print("Frequent Itemsets:")
    for itemset, count in sorted(
        frequent_itemsets.items(), key=lambda x: (len(x[0]), sorted(x[0]))
    ):
        print(set(itemset), "=>", count)

    # print("\nAssociation Rules:")
    # for left, right, support, confidence in rules:
    #     print(f"{left} => {right}, support={support}, confidence={confidence:.2f}")
