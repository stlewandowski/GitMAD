#!/usr/bin/python3

import requests
import os
import json
import datetime
import math
import time
import conf


class GithubSearch:
    def __init__(self, query, username, password, directory, proxy):
        c = conf.Configure()
        self.user = username
        self.pw = password
        self.query = query
        self.dir = directory
        self.pxy = proxy

    def search_github(self, results_per_page, search_type='continuous'):
        rpp = results_per_page
        page_num = []
        if search_type == 'continuous':
            page_num.append(1)

        if len(page_num) == 0:
            url = 'https://api.github.com/search/code?q="' + self.query + '"+in:file&sort=indexed&order=desc'
            if self.pxy != 'n':
                pxy_dict = {'https': self.pxy}
                q = requests.get(url, auth=(self.user, self.pw), proxies=pxy_dict, verify=False)
            else:
                q = requests.get(url, auth=(self.user, self.pw))
            get_total = q.json()
            total_items = get_total['total_count'] / results_per_page
            total_items = math.ceil(total_items)
            total_items += 1
            page_num = list(range(0,total_items))
            page_num.pop(0)

        for item in range(0,len(page_num)):
            url = 'https://api.github.com/search/code?q="' + self.query + '"+in:file&sort=indexed&order=desc' + '&per_page=' + str(rpp) + '&page=' + str(page_num[item])
            if self.pxy != 'n':
                pxy_dict = {'https': self.pxy}
                s = requests.get(url, auth=(self.user, self.pw), proxies=pxy_dict, verify=False)
            else:
                s = requests.get(url, auth=(self.user, self.pw))
            print("Github API Request: " + str(s.status_code))
            os.chdir(self.dir)
            date_str = datetime.datetime.now().strftime('%m%d-%Y-%H-%M')
            query_str = self.query.replace('.', '')
            output = date_str + query_str + '.json'
            s_json = s.json()
            if page_num[item] == 1:
                m_json = s_json
            else:
                for item in range(0,len(s_json['items'])):
                    m_json['items'].append(s_json['items'][item])
            time.sleep(15)

        with open(output, 'w') as fout:
            json.dump(m_json, fout)
        fout.close()
        return m_json


if __name__ == "__main__":

    git_search = GithubSearch('corp.amazon.com')
    git_search.search_github(20)#, 'initial') #continuous (1 page) is default, any other string is First Run (all results)