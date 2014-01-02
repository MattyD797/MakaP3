'''Utility functions pertaining to text.'''


import re


_SPACE = r'\s*'

# A string token comprises zero or more characters enclosed in double quotes.
# Within the string, double quotes and backslashes must be escaped with
# backslashes.
_STRING = r'"(?:[^"\\]*\\\\|[^"\\]*\\")*[^"\\]*"'
_STRING_RE = re.compile(r'({:s}){:s}'.format(_STRING, _SPACE))

# An unterminated string token is just like a string token except that it
# extends to the end of the string being tokenized and has no closing quote.
_UNTERMINATED_STRING_RE = re.compile(_STRING[:-1] + '$')

# A nonstring token comprises a non-whitespace, non-quote character
# followed by zero or more non-whitespace characters.
_NONSTRING = r'[^"\s]\S*'
_NONSTRING_RE = re.compile(r'({:s}){:s}'.format(_NONSTRING, _SPACE))


def tokenizeString(s):
    
    inputLength = len(s)
    
    s = s.lstrip()
    
    tokens = []
    
    while len(s) != 0:
        
        if s[0] == '"':
            # string token
            
            regExp = _STRING_RE
            tokenType = 'string'
            
        else:
            # nonstring token
            
            regExp = _NONSTRING_RE
            tokenType = 'non-string'
            
        m = regExp.match(s)
            
        if m is not None:
            # match succeeded
            
            tokens.append(m.group(1))
            s = s[len(m.group(0)):]
            
        else:
            # match failed
            
            charNum = inputLength - len(s)
            
            if tokenType == 'string' and _UNTERMINATED_STRING_RE.match(s):
                prefix = 'Unterminated'
                
            else:
                prefix = 'Bad'
                
            raise ValueError(
                '{:s} {:s} token starting at character {:d}.'.format(
                    prefix, tokenType, charNum + 1))
            
    return tokens


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
        