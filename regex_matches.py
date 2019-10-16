# match file
# add / remove items to search within the content of a repo
# Dict Content:
# match_regex = Regular expression to be used to search
# match_type = Descriptive string of match_regex, to be added to the database

to_match = [
    {'match_regex': r'password', 'match_type': 'Password Match'},
    {'match_regex': r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', 'match_type': 'IP Match'},
    {'match_regex': r'username', 'match_type': 'Username Match'},
    {'match_regex': r'\b[\w.]*@[\w]*\.[\w.]*\b', 'match_type': 'Email Match'},
    # begin, from source: https://github.com/cyberark/summon/blob/master/.gitleaks.toml
    # had to adjust some of the regexes from this source as they were written in Go and not Python compatible.
    {'match_regex': r'''\b(A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}\b''', 'match_type': "AWS Client ID"},
    {'match_regex': r'''\b(?i)aws(.{0,20})?['\"][0-9a-zA-Z\/+]{40}['\"]\b''', 'match_type': "AWS Secret Key"},
    {'match_regex': r'''\bamzn\.mws\.[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b''', 'match_type': "AWS MWS key"},
    {'match_regex': r'''-----BEGIN PRIVATE KEY-----''', 'match_type': "PKCS8"},
    {'match_regex': r'''-----BEGIN RSA PRIVATE KEY-----''', 'match_type': "RSA"},
    {'match_regex': r'''-----BEGIN OPENSSH PRIVATE KEY-----''', 'match_type': "SSH"},
    {'match_regex': r'''-----BEGIN PGP PRIVATE KEY BLOCK-----''', 'match_type': "PGP"},
    {'match_regex': r'''\b(?i)(facebook|fb)(.{0,20})?['\"][0-9a-f]{32}['\"]\b''', 'match_type': "Facebook Secret Key"},
    {'match_regex': r'''\b(?i)(facebook|fb)(.{0,20})?['\"][0-9]{13,17}['\"]\b''', 'match_type': "Facebook Client ID"},
    {'match_regex': r'''\bEAACEdEose0cBA[0-9A-Za-z]+\b''', 'match_type': "Facebook access token"},
    {'match_regex': r'''\b(?i)twitter(.{0,20})?['\"][0-9a-z]{35,44}['\"]\b''', 'match_type': "Twitter Secret Key"},
    {'match_regex': r'''\b(?i)twitter(.{0,20})?['\"][0-9a-z]{18,25}['\"]\b''', 'match_type': "Twitter Client ID"},
    {'match_regex': r'''\b(?i)github(.{0,20})?['\"][0-9a-zA-Z]{35,40}['\"]\b''', 'match_type': "Github"},
    {'match_regex': r'''\b(?i)linkedin(.{0,20})?['\"][0-9a-z]{12}['\"]\b''', 'match_type': "LinkedIn Client ID"},
    {'match_regex': r'''\b(?i)linkedin(.{0,20})?['\"][0-9a-z]{16}['\"]\b''', 'match_type': "LinkedIn Secret Key"},
    {'match_regex': r'''\bxox[baprs]-([0-9a-zA-Z]{10,48})?\b''', 'match_type': "Slack"},
    {'match_regex': r'''-----BEGIN EC PRIVATE KEY-----''', 'match_type': "EC"},
    {'match_regex': r'''\b(?i)api_key(.{0,20})?['|"][0-9a-zA-Z]{32,45}['|"]\b''', 'match_type': "Generic API key"},
    {'match_regex': r'''\b(?i)secret(.{0,20})?['|"][0-9a-zA-Z]{32,45}['|"]\b''', 'match_type': "Generic Secret"},
    {'match_regex': r'''\bAIza[0-9A-Za-z\\-_]{35}\b''', 'match_type': "Google API key"},
    {'match_regex': r'''\b(?i)(google|gcp|youtube|drive|yt)(.{0,20})?['\"][AIza[0-9a-z\\-_]{35}]['\"]\b''', 'match_type': "Google Cloud Platform API key"},
    {'match_regex': r'''(?i)(google|gcp|auth)(.{0,20})?['"][0-9]+-[0-9a-z_]{32}\.apps\.googleusercontent\.com['"]''', 'match_type': "Google OAuth"},
    {'match_regex': r'''\bya29\.[0-9A-Za-z\-_]+\b''', 'match_type': "Google OAuth access token"},
    {'match_regex': r'''\b(?i)heroku(.{0,20})?['"][0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}['"]\b''', 'match_type': "Heroku API key"},
    {'match_regex': r'''\b(?i)(mailchimp|mc)(.{0,20})?['"][0-9a-f]{32}-us[0-9]{1,2}['"]\b''', 'match_type': "MailChimp API key"},
    {'match_regex': r'''\b(?i)(mailgun|mg)(.{0,20})?['"][0-9a-z]{32}['"]\b''', 'match_type': "Mailgun API key"},
    {'match_regex': r'''\b[a-zA-Z]{3,10}:\/\/[^\/\s:@]{3,20}:[^\/\s:@]{3,20}@.{1,100}\/?.?\b''', 'match_type': "Password in URL"},
    {'match_regex': r'''access_token\$production\$[0-9a-z]{16}\$[0-9a-f]{32}''', 'match_type': "PayPal Braintree access token"},
    {'match_regex': r'''sk_live_[0-9a-z]{32}''', 'match_type': "Picatic API key"},
    {'match_regex': r'''https://hooks.slack.com/services/T[a-zA-Z0-9_]{8}/B[a-zA-Z0-9_]{8}/[a-zA-Z0-9_]{24}''', 'match_type': "Slack Webhook"},
    {'match_regex': r'''(?i)stripe(.{0,20})?['\"][sk|rk]_live_[0-9a-zA-Z]{24}''', 'match_type': "Stripe API key"},
    {'match_regex': r'''sq0atp-[0-9A-Za-z\-_]{22}''', 'match_type': "Square access token"},
    {'match_regex': r'''sq0csp-[0-9A-Za-z\\-_]{43}''', 'match_type': "Square OAuth secret"},
    {'match_regex': r'''(?i)twilio(.{0,20})?['\"][0-9a-f]{32}['\"]''', 'match_type': "Twilio API key"}
    # end, from source: https://github.com/cyberark/summon/blob/master/.gitleaks.toml
    ]
