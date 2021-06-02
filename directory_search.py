#!/usr/bin/python3

import os
import re
import json
import sys
import hashlib
import db_ops as database
import find_entropy as fe
import zipfile
import datetime
import email_alert as ea
import conf
import regex_matches as rm


class DirectorySearch:
    """Class to search through either a directory of committed files or a single commit file."""
    def __init__(self, in_query, in_dir, in_folder, in_dictionary, usr, pw,
                 host, db, email, logs, do_ent='', e_lvl=3.5, g_type='git_history'):
        self.d_in = in_dir
        self.f_in = in_folder
        self.in_dict = in_dictionary
        self.ent = do_ent
        self.ent_level = e_lvl
        self.db_user = usr
        self.db_pw = pw
        self.db_host = host
        self.db_database = db
        self.search_type = g_type
        self.in_query = in_query
        self.do_email = email
        self.do_logs = logs

    def generate_file_list(self, f_in_item):
        """Generate a list of files to search through, if not searching the single git history file."""
        file_list = []
        if self.search_type != 'git_history':
            search_path = os.path.join(self.d_in, f_in_item)
            os.chdir(self.d_in)
            file_list_f = open(self.d_in + '_files.txt', 'w')
            for root, directories, filenames in os.walk(search_path):
                for filename in filenames:
                    file_list_f.write(os.path.join(root, filename) + '\n')
                    file_list.append(os.path.join(root, filename))
            file_list_f.close()
            h_log = os.path.join(self.d_in, f_in_item, f_in_item + "_history.log")
            try:
                file_list.remove(h_log)
            except:
                pass
            return file_list
        elif self.search_type == 'git_history':
            search_path = os.path.join(self.d_in, f_in_item, f_in_item + "_history.log")
            file_list.append(search_path)
            return file_list

    def search_file_list(self, r_dir, file_list, db_repo_id):
        """Search through files / git commit file to pull out interesting results."""
        item_info_list = []

        if self.search_type != 'git_history':
            num_files = 0
            for line in file_list:
                filename = line.strip()
                try:
                    in_file = open(filename, 'r', encoding='utf-8', errors='ignore')
                except Exception as e:
                    print(e)
                    pass
                for new_line in in_file:
                    self.search_item(item_info_list, new_line, filename, "+")
                print(str(num_files) + ') Finished searching ' + filename + '\n')
                num_files += 1
                in_file.close()
                print('Number of files searched:')
                print(num_files)
            return item_info_list

        elif self.search_type == 'git_history':
            get_diff = re.compile(r'^diff --git a/')
            get_commit = re.compile(r'^commit [a-z0-9]{40}')
            get_previous_file = re.compile(r'--- a/')
            get_current_file = re.compile(r'\+\+\+ b/')
            get_new_file = re.compile(r'new file mode ')
            get_addition = re.compile(r'\+')
            get_deletion = re.compile(r'-')
            file = file_list[0]
            f = open(file, 'r', encoding='utf-8', errors='ignore')
            com_dict = {}
            key = 'first'  # initializer
            db_key = db_repo_id  # most recent commit in DB
            line_list = ['first']
            broke = ''
            most_recent_f_hash = f.readline().strip().split(' ')[1]
            f.seek(0)
            for line in f:
                if get_commit.match(line):
                    a = {key: line_list}
                    # print(a)
                    key1 = line.split(' ')[1].strip()
                    if key1 == db_key:
                        print(key1 + ' already in DB, exiting')
                        broke = 'yes'
                        break
                    key = line.split(' ')[1].strip()
                    com_dict.update(a)
                    line_list = []
                else:
                    line_list.append(line.strip())
            a = {key: line_list}
            com_dict.update(a)
            com_dict.pop('first')

            for key in com_dict:
                authr = com_dict[key][0]
                c_time = com_dict[key][1]
                c_message = com_dict[key][3]
                for item in com_dict[key][5:]:
                    if get_diff.match(item):
                        curr_file = item.split(' ')[3][1:]
                    if get_new_file.match(item):
                        new_file = "Yes"
                    if get_addition.match(item):
                        if not get_current_file.match(item):
                            self.search_item(r_dir, item_info_list, item, curr_file, "-", key, authr, c_time, c_message)
                    if get_deletion.match(item):
                        if not get_previous_file.match(item):
                            self.search_item(r_dir, item_info_list, item, curr_file, "+", key, authr, c_time, c_message)
            f.close()
            return item_info_list, most_recent_f_hash

    def search_item(self, repo_dir, master_list, in_line, in_fname, u_type, c_hash="n/a",
                    author="n/a", time="n/a", msg="n/a"):
        """Individual function to search for regexes and entropy for a given line/item."""
        ent_result_list = []
        query_match = re.compile(self.in_query, re.IGNORECASE).search(in_line)
        match_types = [{'regex_match': query_match, 'match_type': 'Query Match'}]
        for item in rm.to_match:
            r_var = re.compile(item['match_regex'], re.IGNORECASE).search(in_line)
            r_string = item['match_type']
            r_dict = {'regex_match': r_var, 'match_type': r_string}
            match_types.append(r_dict)

        file_path = repo_dir + in_fname
        for item in range(0, len(match_types)):
            if match_types[item]['regex_match']:
                output_dict = {'Match Type': match_types[item]['match_type'],
                               'Match Path': file_path,
                               'Match Value': match_types[item]['regex_match'].group(0),
                               'Match Line': in_line,
                               'Match Entropy': None,
                               'Match Line Hash': hashlib.sha256(in_line.encode('utf-8')).hexdigest(),
                               'Match Add or Del': u_type,
                               'Match Commit Hash': c_hash,
                               'Match Commit Author': author,
                               'Match Commit Time': time,
                               'Match Commit Message': msg,
                               'Match Original Query': self.in_query}
                master_list.append(output_dict)

            elif self.ent == 'entropy':
                get_ent = fe.GetEntropy(in_line, self.ent_level)
                ent_result_list = get_ent.enum_entropy()

        if len(ent_result_list) != 0:
            for e_m in range(0, len(ent_result_list)):
                entropy_output = {'Match Type': 'Entropy Match',
                                  'Match Path': file_path,
                                  'Match Value': ent_result_list[e_m]['Entropy Match'],
                                  'Match Entropy': ent_result_list[e_m]['Entropy Value'],
                                  'Match Line': in_line,
                                  'Match Line Hash': hashlib.sha256(in_line.encode('utf-8')).hexdigest(),
                                  'Match Add or Del': u_type,
                                  'Match Commit Hash': c_hash,
                                  'Match Commit Author': author,
                                  'Match Commit Time': time,
                                  'Match Commit Message': msg,
                                  'Match Original Query': self.in_query}
                master_list.append(entropy_output)

    def write_files(self, iil):
        """Write search results to a csv and json file."""
        q_name = self.in_query.replace(".", "-")
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d--%H-%M--')
        csv_out_filename = timestamp + q_name + '.csv'
        csv_file = os.path.join(self.d_in, csv_out_filename)
        csv_out_file = open(csv_file, 'w', encoding='utf-8', errors='ignore')
        for x in range(0,len(iil)):
            c = ','
            line = iil[x]["Repo Name"] + c + iil[x]["Repo Author"] + c + iil[x]["Query"] + c + iil[x]["Type"] + c
            line2 = iil[x]["Path"] + c + iil[x]["Add or Del"] + c
            line3 = iil[x]["Commit Author"] + c + iil[x]["Line"]
            w_line = line + line2 + line3
            csv_out_file.write(w_line + "\n")
        csv_out_file.close()
        file_list = [csv_file]
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d--%H-%M--')
        zip_name = timestamp + q_name + ".zip"
        zip_path = os.path.join(self.d_in, zip_name)
        os.chdir(self.d_in)
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as out_zip:
            out_zip.write(csv_out_filename)
        return zip_path


    def iterate_thru_repos(self):
        """Driver for this class, to put other functions together, search, and generate results.

        In addition, this will email results (if enabled) as well as insert them into the database.
        """
        dbc = database.DbOps(self.db_user, self.db_pw, self.db_host, self.db_database)
        total_added = 0
        total_list = []
        for key in self.in_dict:
            if 'cloned' in self.in_dict[key]:
                repo_id = self.in_dict[key][7]
                db_repo_id = dbc.get_recent_hash(repo_id)
                repo = self.in_dict[key][0]
                gen_file_list = self.generate_file_list(repo)
                gen_item_info_list, f_recent_commit = self.search_file_list(repo, gen_file_list, db_repo_id)
                dbc.update_repo_info(self.in_dict[key], f_recent_commit)
                num_added, added_list = dbc.update_repo_search_results(self.in_dict[key], gen_item_info_list, self.search_type)
                total_added += num_added
                total_list.extend(added_list)
            elif 'not_cloned' in self.in_dict[key]:
                dbc.update_repo_info(self.in_dict[key], 'n/a')
        print("Length of added list - a list of dicts")
        print(len(total_list))
        if total_list != []:
            if self.do_email == 1:
                num_results = len(total_list)
                email_body = []
                for item in range(0,len(total_list)):
                    if total_list[item]["Type"] == "Query Match":
                        email_body.append(total_list[item])
                zip_path = self.write_files(total_list)
                c = conf.Configure()
                e_conf_file, e_file_check = c.check_for_file(c.e_filename)
                e_from, e_to, e_domain, e_port, e_pw = c.populate_email_credentials(e_conf_file, e_file_check)
                e_alert = ea.EmailAction(e_from, e_to, e_domain, e_port, e_pw)
                e_alert.send_alert(zip_path, num_results, email_body)
        print("Items added to repo_search_results:")
        print(total_added)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Error: Incorrect syntax')
        print('Ex: C:\> python directory_search.py <full path> <directory>')
        print(r'Ex: C:\> python directory_search.py C:\Users\<user>\Downloads DirToSearch')
        sys.exit()

    search_dir = sys.argv[1]
    search_folder = sys.argv[2]
    gen_file_list = generate_file_list(search_dir, search_folder)
    gen_item_info_list = search_file_list(search_folder)
    write_files(gen_item_info_list, search_folder)
