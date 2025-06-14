from typing import List

def levenshtein_distance(s1: str, s2: str) -> int:
    m, n = len(s1), len(s2)
    
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,
                dp[i][j - 1] + 1, 
                dp[i - 1][j - 1] + cost 
            )
    
    return dp[m][n]

def levenshtein_search(text: str, pattern: str, threshold: int) -> List[int]:
    n = len(text)
    m = len(pattern)
    
    found_indices: List[int] = []

    for i in range(n - m + 1):
        substring = text[i:i + m]
        if levenshtein_distance(substring, pattern) <= threshold:
            found_indices.append(i)
    
    return found_indices