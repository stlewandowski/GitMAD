#!/usr/bin/python3

import github_search as gs
import download_repo as dr
import directory_search as ds
import time
import datetime
import conf
import base64
import os
import configparser
import sys
import argparse
import web_home as wh


class RunProgram:

    def __init__(self, query, email, logging, res_per_pull, max_repo_size, ent, entropy_amt=4):
        c = conf.Configure()
        conf_file, file_check = c.check_for_file(c.c_filename)
        db_u, db_p, db_h, db_db, g_u, g_p, d = c.populate_credentials(conf_file, file_check)
        if email == 1:
            e_conf_file, e_file_check = c.check_for_file(c.e_filename)
            e_from, e_to, e_domain, e_port, e_pw = c.populate_email_credentials(e_conf_file, e_file_check)

        if logging == 1:
            # configure logging
            print("placeholder")
        self.directory = d
        self.user = g_u
        self.pw = g_p
        self.db_user = db_u
        self.db_pw = db_p
        self.db_host = db_h
        self.db_db = db_db
        self.query = query
        self.do_email = email
        self.do_logs = logging
        self.rpp = res_per_pull
        self.max_size = int(max_repo_size)
        self.ent_size = int(entropy_amt)
        if int(ent) == 1:
            self.do_ent = 'entropy'
        else:
            self.do_ent = 'no entropy'

    def main_first(self):
        git_search = gs.GithubSearch(self.query, self.user, self.pw, self.directory)
        search_results = git_search.search_github(100, 'initial')
        repo_check = dr.DownloadRepo(search_results, self.max_size, self.user, self.pw)
        get_repo_info = repo_check.check_repo_size()
        all_repo_dict, dl_repo_list = repo_check.download_repo(get_repo_info, self.directory)
        search_repos = ds.DirectorySearch(self.query, self.directory, dl_repo_list, all_repo_dict, self.db_user,
                                          self.db_pw, self.db_host, self.db_db, self.do_email, self.do_logs,
                                          self.do_ent, self.ent_size)  # , "no_git")
        search_repos.iterate_thru_repos()

    def main_continuous(self):
        git_search = gs.GithubSearch(self.query, self.user, self.pw, self.directory)
        search_results = git_search.search_github(self.rpp)
        repo_check = dr.DownloadRepo(search_results, self.max_size, self.user, self.pw)
        get_repo_info = repo_check.check_repo_size()
        all_repo_dict, dl_repo_list = repo_check.download_repo(get_repo_info, self.directory)
        search_repos = ds.DirectorySearch(self.query, self.directory, dl_repo_list, all_repo_dict, self.db_user,
                                          self.db_pw, self.db_host, self.db_db, self.do_email, self.do_logs,
                                          self.do_ent, self.ent_size)  # , "no_git")
        search_repos.iterate_thru_repos()
        # TODO Chaining of filters together in WebApp
        # TODO Enhance entropy whitelist
        # TODO Make this proxy aware...
        # TODO Add log output from results (in addition to email)
        # TODO Add logging.
        # TODO Add error handling.
        # TODO API
        # TODO AdHoc download of a repo


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-rt', '--refresh-time', action='store', dest='refresh',
                        help='Amount of seconds to wait until next Github search (default is 14400 [4 hours]).',
                        nargs='?', default=14400, const=14400, type=int)
    parser.add_argument('-m', '--mode', action='store', choices=('m', 'd'), dest='mode',
                        help='Run Mode: [m]onitor or [d]iscovery.  Discovery is default', nargs='?',
                        default='d', const='d')
    parser.add_argument('-q', '--query', action='store', dest='query', help='String to search for in Github.',
                        required=True, type=str)
    parser.add_argument('-e', '--email', action='store_true', dest='email', help='Flag to send email alerts.')
    parser.add_argument('-l', '--logs', action='store_true', dest='logging', help='Flag to enable logging of results')
    parser.add_argument('-r', '--results', action='store', dest='num_results',
                        help='Number of results to search per run (default 30 results).', nargs='?',
                        default=30, const=30, type=int)
    parser.add_argument('-mx', '--max-size', action='store', dest='max_size',
                        help='Maximum size of repo to be downloaded by megabyte (default 5mb).', nargs='?',
                        default=5, const=5, type=int)
    parser.add_argument('-ent', '--entropy', action='store_true', dest='entropy', help='Flag to search via entropy.')
    parser.add_argument('-es', '--entropy-size', action='store', dest='ent_size',
                        help='Flag to return entropy results above a certain value (default size is 4).', nargs='?',
                        default=4, const=4, type=int)

    args = parser.parse_args()
    rfrsh_flag = args.refresh
    e_flag = args.email
    l_flag = args.logging
    r_flag = args.num_results
    m_flag = args.max_size
    ent_flag = args.entropy
    ent_sz_flag = args.ent_size
    q_flag = args.query
    mode_flag = args.mode
    qry = q_flag
    e_alert = 0
    logs = 0
    entropy = 0

    if e_flag:
        e_alert = 1

    if l_flag:
        logs = 1

    if ent_flag:
        entropy = 1

    results = r_flag
    mx_size = m_flag
    ent_size = ent_sz_flag

    # Monitor mode.  Search all results first, then search updated repos.
    if mode_flag == 'm':
        run_first = RunProgram(qry, e_alert, logs, results, mx_size, entropy, ent_size)
        run_first.main_first()
        print("First Run complete.")
        a = datetime.datetime.now()
        b = a.strftime('%c')
        print("First run:")
        print(b)
        print("Sleeping for 10 minutes and running in continuous mode.")
        time.sleep(600)
        while True:
            run_first.main_continuous()
            a = datetime.datetime.now()
            b = a.strftime('%c')
            print("Last run:")
            print(b)
            print("Sleeping for " + str(rfrsh_flag) + " seconds and running again.")
            time.sleep(rfrsh_flag)

    # Discovery mode.  Search updated repos.
    if mode_flag == 'd':
        while True:
            run_continuous = RunProgram(qry, e_alert, logs, results, mx_size, entropy, ent_size)
            run_continuous.main_continuous()
            a = datetime.datetime.now()
            b = a.strftime('%c')
            print("Last run:")
            print(b)
            print("Sleeping for " + str(rfrsh_flag) + " seconds and running again.")
            time.sleep(rfrsh_flag)
