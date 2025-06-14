from typing import List

def compute_lps_array(pattern: str) -> List[int]:
    """
    Computes the Longest Proper Prefix which is also a Suffix (LPS) array.
    Args:
        pattern: The string pattern to be analyzed.

    Returns:
        A List of integers representing the LPS array for the pattern.
    """
    assert(pattern != None)
    m = len(pattern)
    lps = [0] * m  # Initialize LPS array with zeros

    length = 0
    i = 1  # Start from the second character

    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    return lps


def kmp_search(text: str, pattern: str) -> List[int]:
    """
    Finds all occurrences of a pattern in a text using the KMP algorithm.
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

    lps = compute_lps_array(pattern)

    i = 0  # index for text
    j = 0  # index for pattern
    
    found_indices: List[int] = []

    while i < n:
        if pattern[j] == text[i]:
            i += 1
            j += 1

        if j == m:
            found_indices.append(i - j)
            j = lps[j - 1]

        elif i < n and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
                
    return found_indices

# For logic testing
if __name__ == '__main__':
    text1 = "ABABDABACDABABCABAB"
    pattern1 = "ABABC"
    matches1 = kmp_search(text1, pattern1)
    print(f"Text: '{text1}'")
    print(f"Pattern: '{pattern1}'")
    print(f"LPS Array for '{pattern1}': {compute_lps_array(pattern1)}")
    print(f"Pattern found at indices: {matches1}") # Expected: [10]
    print("-" * 30)

    text2 = "WOKWOKWOK"
    pattern2 = "WOKWOK"
    matches2 = kmp_search(text2, pattern2)
    print(f"Text: '{text2}'")
    print(f"Pattern: '{pattern2}'")
    print(f"LPS Array for '{pattern2}': {compute_lps_array(pattern2)}")
    print(f"Pattern found at indices: {matches2}") # Expected: [0, 1]
    print("-" * 30)

    text3 = "THIS IS A TEST TEXT"
    pattern3 = "TESTING"
    matches3 = kmp_search(text3, pattern3)
    print(f"Text: '{text3}'")
    print(f"Pattern: '{pattern3}'")
    print(f"LPS Array for '{pattern3}': {compute_lps_array(pattern3)}")
    print(f"Pattern found at indices: {matches3}") # Expected: []
    print("-" * 30)
