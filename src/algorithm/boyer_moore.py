from typing import List

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

    i = 0  # index for text
    
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
    text1 = "ABABDABACDABABCABABC"
    pattern1 = "ABABC"
    matches1 = bm_search(text1, pattern1)
    print(f"Text: '{text1}'")
    print(f"Pattern: '{pattern1}'")
    print(f"LPS Array for '{pattern1}': {compute_l_function(pattern1)}")
    print(f"Pattern found at indices: {matches1}") # Expected: [10]
    print("-" * 30)

    text2 = "WOKWOKWOK"
    pattern2 = "WOKWOK"
    matches2 = bm_search(text2, pattern2)
    print(f"Text: '{text2}'")
    print(f"Pattern: '{pattern2}'")
    print(f"LPS Array for '{pattern2}': {compute_l_function(pattern2)}")
    print(f"Pattern found at indices: {matches2}") # Expected: [0, 1]
    print("-" * 30)

    text3 = "THIS IS A TEST TEXT"
    pattern3 = "TESTING"
    matches3 = bm_search(text3, pattern3)
    print(f"Text: '{text3}'")
    print(f"Pattern: '{pattern3}'")
    print(f"LPS Array for '{pattern3}': {compute_l_function(pattern3)}")
    print(f"Pattern found at indices: {matches3}") # Expected: []
    print("-" * 30)
