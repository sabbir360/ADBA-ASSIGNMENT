from __future__ import annotations

import json
import os
import urllib.request
from typing import Optional

DICTIONARY_URL = (
    "https://raw.githubusercontent.com/matthewreagan/"
    "WebstersEnglishDictionary/master/dictionary_compact.json"
)
DATA_CACHE_FILE = "dictionary_data.json"

WORD_LIMIT: Optional[int] = None


class WordNode:
    def __init__(self, is_leaf: bool = False):
        self.is_leaf: bool = is_leaf
        self.keys: list[str] = []
        self.child_pointers: list[WordNode] = []
        self.meanings: list[str] = []
        self.next_leaf: Optional[WordNode] = None


class WordDictionaryBPlusTree:
    root: WordNode
    order: int

    def __init__(self, order: int = 644):
        if order < 3:
            raise ValueError("order must be at least 3")

        self.order = order
        self.root = WordNode(is_leaf=True)

    def search(self, word: str) -> Optional[str]:
        key: str = word.lower()
        leaf_node: WordNode = self.__find_leaf(key)

        for index, current_key in enumerate(leaf_node.keys):
            if current_key == key:
                return leaf_node.meanings[index]

        return None

    def insert(self, word: str, meaning: str) -> None:
        key: str = word.lower()
        root_node: WordNode = self.root

        if len(root_node.keys) == self.order:
            new_root: WordNode = WordNode(is_leaf=False)
            new_root.child_pointers.append(root_node)
            self.__split_child(new_root, 0)
            self.root = new_root

        self.__insert_non_full(self.root, key, meaning)

    def delete(self, word: str) -> bool:
        key: str = word.lower()
        leaf_node: WordNode = self.__find_leaf(key)

        for index, current_key in enumerate(leaf_node.keys):
            if current_key == key:
                leaf_node.keys.pop(index)
                leaf_node.meanings.pop(index)
                return True

        return False

    def prefix_search(self, prefix: str, limit: int = 10) -> list[tuple[str, str]]:
        normalized_prefix: str = prefix.lower()
        matching_words: list[tuple[str, str]] = []
        leaf_node: Optional[WordNode] = self.__find_leaf(normalized_prefix)

        while leaf_node is not None:
            for index, current_key in enumerate(leaf_node.keys):
                if current_key < normalized_prefix:
                    continue
                if current_key.startswith(normalized_prefix):
                    matching_words.append((current_key, leaf_node.meanings[index]))
                    if len(matching_words) >= limit:
                        return matching_words
                elif current_key > normalized_prefix:
                    return matching_words

            leaf_node = leaf_node.next_leaf

        return matching_words

    def range_search(self, start_word: str, end_word: str) -> list[tuple[str, str]]:
        start_key: str = start_word.lower()
        end_key: str = end_word.lower()

        if start_key > end_key:
            start_key, end_key = end_key, start_key

        matching_records: list[tuple[str, str]] = []
        leaf_node: Optional[WordNode] = self.__find_leaf(start_key)

        while leaf_node is not None:
            for index, current_key in enumerate(leaf_node.keys):
                if start_key <= current_key <= end_key:
                    matching_records.append((current_key, leaf_node.meanings[index]))
                elif current_key > end_key:
                    return matching_records

            leaf_node = leaf_node.next_leaf

        return matching_records

    def word_count(self) -> int:
        total: int = 0
        current_node: Optional[WordNode] = self.root

        while not current_node.is_leaf:
            current_node = current_node.child_pointers[0]

        while current_node is not None:
            total += len(current_node.keys)
            current_node = current_node.next_leaf

        return total

    def height(self) -> int:
        levels: int = 1
        current_node: WordNode = self.root

        while not current_node.is_leaf:
            current_node = current_node.child_pointers[0]
            levels += 1

        return levels

    def __find_leaf(self, key: str) -> WordNode:
        current_node: WordNode = self.root

        while not current_node.is_leaf:
            child_index: int = 0
            while (
                child_index < len(current_node.keys)
                and key >= current_node.keys[child_index]
            ):
                child_index += 1
            current_node = current_node.child_pointers[child_index]

        return current_node

    def __insert_non_full(self, node: WordNode, key: str, meaning: str) -> None:
        if node.is_leaf:
            insert_index: int = 0
            while insert_index < len(node.keys) and node.keys[insert_index] < key:
                insert_index += 1

            if insert_index < len(node.keys) and node.keys[insert_index] == key:
                node.meanings[insert_index] = meaning
                return

            node.keys.insert(insert_index, key)
            node.meanings.insert(insert_index, meaning)
            return

        child_index: int = 0
        while child_index < len(node.keys) and key >= node.keys[child_index]:
            child_index += 1

        child_node: WordNode = node.child_pointers[child_index]

        if len(child_node.keys) == self.order:
            self.__split_child(node, child_index)

            if key >= node.keys[child_index]:
                child_index += 1

        self.__insert_non_full(node.child_pointers[child_index], key, meaning)

    def __split_child(self, parent: WordNode, child_index: int) -> None:
        child_node: WordNode = parent.child_pointers[child_index]
        right_node: WordNode = WordNode(is_leaf=child_node.is_leaf)
        middle_index: int = len(child_node.keys) // 2

        if child_node.is_leaf:
            right_node.keys = child_node.keys[middle_index:]
            right_node.meanings = child_node.meanings[middle_index:]

            child_node.keys = child_node.keys[:middle_index]
            child_node.meanings = child_node.meanings[:middle_index]

            right_node.next_leaf = child_node.next_leaf
            child_node.next_leaf = right_node

            parent.keys.insert(child_index, right_node.keys[0])
            parent.child_pointers.insert(child_index + 1, right_node)
            return

        promoted_key: str = child_node.keys[middle_index]

        right_node.keys = child_node.keys[middle_index + 1 :]
        right_node.child_pointers = child_node.child_pointers[middle_index + 1 :]

        child_node.keys = child_node.keys[:middle_index]
        child_node.child_pointers = child_node.child_pointers[: middle_index + 1]

        parent.keys.insert(child_index, promoted_key)
        parent.child_pointers.insert(child_index + 1, right_node)


def load_dictionary(
    limit: Optional[int] = WORD_LIMIT, cache_file: str = DATA_CACHE_FILE
) -> list[tuple[str, str]]:
    if not os.path.exists(cache_file):
        print(f"Downloading dictionary dataset to {cache_file} ...")
        urllib.request.urlretrieve(DICTIONARY_URL, cache_file)

    with open(cache_file, encoding="utf-8") as data_file:
        raw_entries: dict[str, str] = json.load(data_file)

    cleaned_entries: dict[str, str] = {}
    for word, meaning in raw_entries.items():
        key: str = word.strip().lower()
        if not key.isalpha():
            continue
        if not meaning or not meaning.strip():
            continue
        cleaned_entries.setdefault(key, meaning.strip())

    sorted_entries: list[tuple[str, str]] = sorted(cleaned_entries.items())
    if limit is None or len(sorted_entries) <= limit:
        return sorted_entries

    stride: float = len(sorted_entries) / limit
    return [sorted_entries[int(index * stride)] for index in range(limit)]


def shorten(text: str, width: int = 200) -> str:
    collapsed: str = " ".join(text.split())
    if len(collapsed) <= width:
        return collapsed

    return collapsed[: width - 3] + "..."


if __name__ == "__main__":
    word_entries: list[tuple[str, str]] = load_dictionary()
    import time 
    start_time: float = time.time()
    dictionary_tree: WordDictionaryBPlusTree = WordDictionaryBPlusTree(order=64)
    for entry_word, entry_meaning in word_entries:
        dictionary_tree.insert(entry_word, entry_meaning)

    print("B+ tree word dictionary built.")
    print(f"  Words indexed : {dictionary_tree.word_count()}")
    print(f"  Tree order    : {dictionary_tree.order}")
    print(f"  Tree height   : {dictionary_tree.height()}")

    print("\nType a word to look up its meaning.")
    print("Type 'quit' or 'exit' (or press Ctrl+C) to stop.")
    end_time: float = time.time()

    print(f"\nInitialization completed in {end_time - start_time:.2f} seconds")
    
  
    dictionary_tree.search("example")
    exit(0)
    while True:
        try:
            query: str = input("\nWord> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not query:
            continue

        if query.lower() in {"quit", "exit"}:
            print("Goodbye.")
            break

        meaning: Optional[str] = dictionary_tree.search(query)
        if meaning is None:
            print(f"  {query!r}: not found")

            suggestions: list[tuple[str, str]] = dictionary_tree.prefix_search(
                query, limit=5
            )
            if suggestions:
                print("  Did you mean:")
                for found_word, _ in suggestions:
                    print(f"    - {found_word}")
        else:
            print(f"  {query}: {shorten(meaning)}")
