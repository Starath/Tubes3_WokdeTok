# File: src/algorithm/aho_corasick.py

from collections import deque
from typing import List, Dict, Optional, Deque

class TrieNode:
    """
    Represents a node in the Trie.

    Attributes:
        children (Dict[str, TrieNode]): A dictionary of child nodes.
        failure (Optional['TrieNode']): The failure link for the Aho-Corasick algorithm.
        output (List[str]): A list of keywords ending at this node.
    """
    def __init__(self):
        self.children: Dict[str, TrieNode] = {}
        self.failure: Optional['TrieNode'] = None
        self.output: List[str] = []

class AhoCorasick:
    """
    Implements the Aho-Corasick algorithm.
    """
    def __init__(self, keywords: List[str]):
        """
        Initializes the Aho-Corasick automaton.

        Args:
            keywords: A list of keyword strings to search for.
        """
        self.root = TrieNode()
        self._build_trie(keywords)
        self._build_failure_links()

    def _build_trie(self, keywords: List[str]):
        """
        Builds the Trie data structure from a list of keywords.

        Args:
            keywords: The list of keywords to be added to the Trie.
        """
        for keyword in keywords:
            processed_keyword = keyword.lower()
            node = self.root
            for char in processed_keyword:
                node = node.children.setdefault(char, TrieNode())
            node.output.append(processed_keyword)

    def _build_failure_links(self):
        """
        Constructs the failure links for each node in the Trie using a breadth-first search.
        """
        queue: Deque[TrieNode] = deque()
        
        for char, node in self.root.children.items():
            node.failure = self.root
            queue.append(node)

        while queue:
            current_node = queue.popleft()

            for char, child_node in current_node.children.items():
                failure_node = current_node.failure
                
                while failure_node and char not in failure_node.children:
                    failure_node = failure_node.failure

                if failure_node:
                    child_node.failure = failure_node.children[char]
                else:
                    child_node.failure = self.root

                child_node.output.extend(child_node.failure.output)
                
                queue.append(child_node)

    def search(self, text: str) -> Dict[str, List[int]]:
        """
        Finds all occurrences of the keywords in a given text.

        Args:
            text: The main string to search within.

        Returns:
            A dictionary mapping each found keyword to a list of its starting indices
            in the text.
        """
        processed_text = text.lower()
        results: Dict[str, List[int]] = {}
        current_node = self.root

        for i, char in enumerate(processed_text):
            while current_node and char not in current_node.children:
                current_node = current_node.failure

            if not current_node:
                current_node = self.root
                continue

            current_node = current_node.children[char]

            if current_node.output:
                for keyword in current_node.output:
                    if keyword not in results:
                        results[keyword] = []
                    results[keyword].append(i - (len(keyword) - 1))
        
        return results

# For testing
if __name__ == '__main__':
    print("Menjalankan pengujian untuk algoritma Aho-Corasick...")

    keywords1 = ["he", "she", "his", "hers"]
    text1 = "ushers"
    ac1 = AhoCorasick(keywords1)
    result1 = ac1.search(text1)
    print(f"\nText: '{text1}', Keywords: {keywords1}")
    print(f"Result: {result1}")

    keywords2 = ["aba", "bab", "ababa"]
    text2 = "abababa"
    ac2 = AhoCorasick(keywords2)
    result2 = ac2.search(text2)
    print(f"\nText: '{text2}', Keywords: {keywords2}")
    print(f"Result: {result2}")

    keywords3 = ["a", "ab", "abc"]
    text3 = "abce"
    ac3 = AhoCorasick(keywords3)
    result3 = ac3.search(text3)
    print(f"\nText: '{text3}', Keywords: {keywords3}")
    print(f"Result: {result3}")

    keywords4 = ["Python", "SQL"]
    text4 = "I love python, and also PYTHON and sql."
    ac4 = AhoCorasick(keywords4)
    result4 = ac4.search(text4)
    print(f"\nText: '{text4}', Keywords: {keywords4}")
    print(f"Result: {result4}")

    keywords5 = ["java", "c++"]
    text5 = "This is a test in python."
    ac5 = AhoCorasick(keywords5)
    result5 = ac5.search(text5)
    print(f"\nText: '{text5}', Keywords: {keywords5}")
    print(f"Result: {result5}")
    
    print("\nPengujian selesai.")