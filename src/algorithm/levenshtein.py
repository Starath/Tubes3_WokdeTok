from typing import List

def levenshtein_distance(substring: str, pattern: str) -> int:
    substringLen, patternLen = len(substring), len(pattern)
    
    dp = [[0] * (patternLen + 1) for _ in range(substringLen + 1)]
    
    for i in range(substringLen + 1):
        dp[i][0] = i
    for j in range(patternLen + 1):
        dp[0][j] = j

    for i in range(1, substringLen + 1):
        for j in range(1, patternLen + 1):
            cost = 0 if substring[i - 1] == pattern[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,
                dp[i][j - 1] + 1, 
                dp[i - 1][j - 1] + cost 
            )
    
    return dp[substringLen][patternLen]

def levenshtein_search(text: str, pattern: str, threshold: int) -> List[int]:
    textLen = len(text)
    patternLen = len(pattern)
    
    found_indices: List[int] = []

    for i in range(textLen - patternLen + 1):
        substring = text[i:i + patternLen]
        if levenshtein_distance(substring, pattern) <= threshold:
            found_indices.append(i)
    
    return found_indices