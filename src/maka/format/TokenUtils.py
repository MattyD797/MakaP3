import re


NONE_TOKEN = '""'

_SPACE = r'\s*'

# A quoted token comprises zero or more characters enclosed in double quotes.
# Within the token, double quotes and backslashes must be escaped with
# backslashes.
_QUOTED = r'"(?:[^"\\]*\\\\|[^"\\]*\\")*[^"\\]*"'
_QUOTED_RE = re.compile(r'({:s}){:s}'.format(_QUOTED, _SPACE))

# An unterminated quoted token is just like a quoted token except that it
# extends to the end of the string being tokenized and has no closing quote.
_UNTERMINATED_QUOTED_RE = re.compile(_QUOTED[:-1] + '$')

# An unquoted token comprises a non-whitespace, non-quote character followed
# by zero or more non-whitespace characters.
_UNQUOTED = r'[^"\s]\S*'
_UNQUOTED_RE = re.compile(r'({:s}){:s}'.format(_UNQUOTED, _SPACE))


# TODO: Document how labor of observation and command parsing is divided between
# tokenizer, field formats, and observation formats. In particular, note that the
# tokenizer only partitions the input into tokens: it does not, for example,
# unescape strings or parse numbers, leaving those sorts of operations to the
# field formats. This makes the `parse` and `format` operations of the field
# formats inverses, a desirable property.


def tokenizeString(s):
    
    inputLength = len(s)
    
    # Ignore leading space.
    s = s.lstrip()
    
    tokens = []
    
    while len(s) != 0:
        
        if s[0] == '"':
            # next token starts with a quote
            
            regExp = _QUOTED_RE
            quoted = True
            
        else:
            # next token does not start with a quote
            
            regExp = _UNQUOTED_RE
            quoted = False
            
        m = regExp.match(s)
            
        if m is not None:
            # match succeeded
            
            matchedText = m.group(0)
            token = m.group(1)
            
            n = len(matchedText)
            
            if n != len(s) and n == len(token):
                # not all remaining text was matched but no trailing whitespace was matched
                
                prefix = 'Quoted token' if quoted else 'Token'
                startIndex = inputLength - len(s) + 1
                endIndex = startIndex + len(token) - 1
                
                raise ValueError(
                    '{:s} from characters {:d} through {:d} is not followed by space.'.format(
                        prefix, startIndex, endIndex))

            tokens.append(token)
            s = s[len(matchedText):]
            
        else:
            # match failed
            
            if quoted and _UNTERMINATED_QUOTED_RE.match(s):
                prefix = 'Unterminated quoted'
                
            else:
                prefix = 'Could not parse' + (' quoted' if quoted else '')
                
            startIndex = inputLength - len(s) + 1
            
            raise ValueError('{:s} token starting at character {:d}.'.format(prefix, startIndex))
            
    return tokens
