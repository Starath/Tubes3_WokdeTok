from typing import List
from pdf_extractor import extract_text_pypdf2
import time

def compute_l_function(pattern: str) -> dict[str, int]:
    """
    Computes the last instance of a char in the pattern.
    Args:
        pattern: The string pattern to be analyzed.

    Returns:
        A List of integers representing the LPS array for the pattern.
    """
    assert(pattern != None)
    l_func : dict[str, int]= {}
    for i, char in enumerate(pattern):
        l_func[char] = i
    return l_func


def bm_search(text: str, pattern: str) -> List[int]:
    """
    Finds all occurrences of a pattern in a text using the Boyer-Moore algorithm.
    Args:
        text: The main string to search within.
        pattern: The pattern string to search for.

    Returns:
        A List of integers, where each integer is the starting index of
        a match. Returns an empty List if no matches are found.
    """
    if not pattern or not text:
        return []

    n = len(text)
    m = len(pattern)
    if m>n:
        return []
    l_function = compute_l_function(pattern)

    i = 0  #index for text
    
    matches: List[int] = []

    while i <= n-m:
        j = m - 1  #index for pattern
        #Find rightmost mismatch
        while j >= 0 and pattern[j] == text[i + j]:
            j-=1

        if j < 0:  #found a match
            matches.append(i)
            i += m
        else:
            mismatch = text[i + j]
            if mismatch in l_function:
                shift = max(1, j - l_function[mismatch])
            else:
                shift = j + 1
            i += shift
    return matches

# For logic testing
if __name__ == '__main__':
    '''
    text1 = extract_text_pypdf2("test/DIGITAL-MEDIA/10005171.pdf").lower()
    patterns = ["bronze", "silver", "gold", "master", "supervise"]
    matches = []
    x = time.time()
    for i in patterns:
        matches.append(kmp_search(text1, i))
    y = time.time()
    z = y - x
    print(f"Time taken: {z:.6f} seconds")
    for i, pattern1 in enumerate(patterns):
        print(f"Pattern: '{pattern1}'")
        print(f"L Function Array for '{pattern1}': {compute_lps_array(pattern1)}")
        print(f"Pattern found at indices: {matches[i]}")
        print("-" * 30)
    '''
    keywords1 = ["bronze", "silver", "gold", "master", "supervise"]
    text1 = extract_text_pypdf2("test/DIGITAL-MEDIA/10005171.pdf").lower()
    ac1 = AhoCorasick(keywords1)
    x = time.time()
    result1 = ac1.search(text1)
    y = time.time()
    print(f"\nText: {len(text1)}, Keywords: {keywords1}")
    print(f"time : {y-x:.6f} seconds")
    print(f"Result: {result1}")
    '''
    print(f"Time taken: {z:.6f} seconds")
    print(f"Text: {len(text1)} Char long")
    print(f"Pattern: '{pattern1}'")
    print(f"L Function Array for '{pattern1}': {compute_l_function(pattern1)}")
    print(f"Pattern found at indices: {matches1}")
    print("-" * 30)'''
