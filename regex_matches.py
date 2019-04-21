# match file
# add / remove items to search within the content of a repo
# Dict Content:
# match_regex = Regular expression to be used to search
# match_type = Descriptive string of match_regex, to be added to the database

to_match = [
    {'match_regex': r'password', 'match_type': 'Password Match'},
    {'match_regex': r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', 'match_type': 'IP Match'},
    {'match_regex': r'username', 'match_type': 'Username Match'},
    {'match_regex': r'\b[\w.]*@[\w]*\.[\w.]*\b', 'match_type': 'Email Match'}
    ]
