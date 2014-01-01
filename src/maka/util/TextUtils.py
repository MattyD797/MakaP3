'''Utility functions pertaining to text.'''


def splitCamelCaseString(s):
    
    parts = []
    
    n = len(s)
    i = 0
    j = 1
    
    while i != n:
        
        if j == n or s[j].isupper():
            parts.append(s[i:j])
            i = j
            
        j += 1
            
    return parts
        