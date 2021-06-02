import re

# Whitelist for entropy matches.
# Add regexes to
# camel_case = re.compile(r'\b[A-Za-z][a-z]*([A-Z][a-z]*)*\b')

r_whitelist = [{'regex': r'\b[A-Za-z][a-z]+([A-Z][a-z]*)+\b'}]  # Camel Case
