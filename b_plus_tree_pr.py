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

from __future__ import annotations

from typing import Optional

from BPlusTreeDrawer import BPlusTreeDrawer


class Node:
    def __init__(self, is_leaf: bool = False):
        self.is_leaf: bool = is_leaf
        self.keys: list[int] = []
        self.child_pointers: list[Node] = []
        self.record_values: list[str] = []
        self.next_leaf: Optional[Node] = None


class BPlusTree:
    root: Node
    order: int

    def __init__(self, order: int = 4):
        if order < 3:
            raise ValueError("order must be at least 3")

        self.order = order
        self.root = Node(is_leaf=True)

    def search(self, key: int) -> Optional[str]:
        leaf_node: Node = self.__find_leaf(key)

        for index, current_key in enumerate(leaf_node.keys):
            if current_key == key:
                return leaf_node.record_values[index]

        return None

    def insert(self, key: int, value: str) -> None:
        root_node: Node = self.root

        if len(root_node.keys) == self.order:
            new_root: Node = Node(is_leaf=False)
            new_root.child_pointers.append(root_node)
            self.__split_child(new_root, 0)
            self.root = new_root

        self.__insert_non_full(self.root, key, value)

    def delete(self, key: int) -> bool:
        leaf_node: Node = self.__find_leaf(key)

        for index, current_key in enumerate(leaf_node.keys):
            if current_key == key:
                leaf_node.keys.pop(index)
                leaf_node.record_values.pop(index)
                return True

        return False

    def range_search(self, start_key: int, end_key: int) -> list[tuple[int, str]]:
        if start_key > end_key:
            start_key, end_key = end_key, start_key

        matching_records: list[tuple[int, str]] = []
        leaf_node: Optional[Node] = self.__find_leaf(start_key)

        while leaf_node is not None:
            for index, current_key in enumerate(leaf_node.keys):
                if start_key <= current_key <= end_key:
                    matching_records.append(
                        (current_key, leaf_node.record_values[index])
                    )
                elif current_key > end_key:
                    return matching_records

            leaf_node = leaf_node.next_leaf

        return matching_records

    def print_leaves(self) -> None:
        current_node: Optional[Node] = self.root

        while not current_node.is_leaf:
            current_node = current_node.child_pointers[0]

        while current_node is not None:
            print(current_node.keys, end=" -> ")
            current_node = current_node.next_leaf

        print("None")

    def print_tree(self) -> None:
        current_level: list[Node] = [self.root]

        while current_level:
            next_level: list[Node] = []
            level_parts: list[str] = []

            for current_node in current_level:
                level_parts.append(str(current_node.keys))
                if not current_node.is_leaf:
                    next_level.extend(current_node.child_pointers)

            print(" | ".join(level_parts))
            current_level = next_level

    def print_ascii_tree(self, drawer: Optional[BPlusTreeDrawer] = None) -> None:
        if drawer is None:
            self.print_tree()
            return

        drawer.draw(self.root, self.order)

    def __find_leaf(self, key: int) -> Node:
        current_node: Node = self.root

        while not current_node.is_leaf:
            child_index: int = 0
            while (
                child_index < len(current_node.keys)
                and key >= current_node.keys[child_index]
            ):
                child_index += 1
            current_node = current_node.child_pointers[child_index]

        return current_node

    def __insert_non_full(self, node: Node, key: int, value: str) -> None:
        if node.is_leaf:
            insert_index: int = 0
            while insert_index < len(node.keys) and node.keys[insert_index] < key:
                insert_index += 1

            if insert_index < len(node.keys) and node.keys[insert_index] == key:
                node.record_values[insert_index] = value
                return

            node.keys.insert(insert_index, key)
            node.record_values.insert(insert_index, value)
            return

        child_index: int = 0
        while child_index < len(node.keys) and key >= node.keys[child_index]:
            child_index += 1

        child_node: Node = node.child_pointers[child_index]

        if len(child_node.keys) == self.order:
            self.__split_child(node, child_index)

            if key >= node.keys[child_index]:
                child_index += 1

        self.__insert_non_full(node.child_pointers[child_index], key, value)

    def __split_child(self, parent: Node, child_index: int) -> None:
        child_node: Node = parent.child_pointers[child_index]
        right_node: Node = Node(is_leaf=child_node.is_leaf)
        middle_index: int = len(child_node.keys) // 2

        if child_node.is_leaf:
            right_node.keys = child_node.keys[middle_index:]
            right_node.record_values = child_node.record_values[middle_index:]

            child_node.keys = child_node.keys[:middle_index]
            child_node.record_values = child_node.record_values[:middle_index]

            right_node.next_leaf = child_node.next_leaf
            child_node.next_leaf = right_node

            parent.keys.insert(child_index, right_node.keys[0])
            parent.child_pointers.insert(child_index + 1, right_node)
            return

        promoted_key: int = child_node.keys[middle_index]

        right_node.keys = child_node.keys[middle_index + 1 :]
        right_node.child_pointers = child_node.child_pointers[middle_index + 1 :]

        child_node.keys = child_node.keys[:middle_index]
        child_node.child_pointers = child_node.child_pointers[: middle_index + 1]

        parent.keys.insert(child_index, promoted_key)
        parent.child_pointers.insert(child_index + 1, right_node)


if __name__ == "__main__":
    tree: BPlusTree = BPlusTree(order=3)
    drawer: BPlusTreeDrawer = BPlusTreeDrawer()

    numbers: list[int] = [25, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95]
    # numbers: list[int] = [25, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 20, 30, 45, 52, 58, 62, 68, 72, 78, 82, 88]

    for number in numbers:
        tree.insert(number, f"V({number})")

    tree.insert(70, "U(70)")

    print("Tree level by level:")
    tree.print_tree()

    print("\nLeaf nodes:")
    tree.print_leaves()

    # print("\nSearch 70:", tree.search(70))
    # print("Search 45:", tree.search(45))

    # print("\nRange search 60 to 85:")
    # print(tree.range_search(60, 85))

    # print("\nDelete 90:", tree.delete(90))
    # tree.print_leaves()

    print("\nDrawn tree view: ")
    tree.print_ascii_tree(drawer)

    print("\nSearch 70:", tree.search(70))
