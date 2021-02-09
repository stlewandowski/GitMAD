#!/usr/bin/python3

import math
from collections import Counter
import re
import _entropy_whitelist as ew

class GetEntropy:
    """Class to calculate entropy from a given input."""
    def __init__(self, in_line, entropy_level):
        """Initialize class and set variables."""        
        self.ent_level = entropy_level
        self.line = in_line

    def find_entropy(self, s):
        """Find shannon entropy for a given string."""
        p,lns = Counter(s), float(len(s))
        return -sum( count/lns * math.log(count/lns, 2) for count in p.values())

    def enum_entropy(self):
        """Use find_entropy() function to calculate entropy.
        
        Input is the line of the file, broken up via different characters listed below.
        """
        ent_wordlist = []
        ent_line_list = re.split(r'\"|\\|-|_|,|;|\[|]|<|>|%20| |\t|\||{|}|=|\(\)|\'|\.|:|@|/|\(|\)', self.line)
        ent_wordlist.extend(ent_line_list)
        ent_wordlist = set(ent_wordlist)
        ent_wordlist = list(ent_wordlist)

        whitelist = []
        for item in ew.r_whitelist:
            whitelist.append(re.compile(item['regex']))

        for word in ent_wordlist:
            for item in whitelist:
                if item.search(word):
                    ent_wordlist.remove(word)


        ent_out_list = []
        for item in ent_wordlist:
            try:
                if self.find_entropy(item) >= self.ent_level:
                    ent_out_dict = {'Entropy Match': item, 'Entropy Value': self.find_entropy(item)}
                    ent_out_list.append(ent_out_dict)
            except Exception as e:
                print(e)
                pass
        return ent_out_list
