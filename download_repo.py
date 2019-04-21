#!/usr/bin/python3
import os
import requests
from collections import OrderedDict
import datetime
import time # for testing of the repo dict (can remove)
import conf

class DownloadRepo:

    def __init__(self, results, max_repo_size, username, password):

        self.results_dict = results
        self.max_size = max_repo_size
        self.user = username
        self.pw = password

    def check_repo_size(self):
        full_name_set = set()
        repo_size_dict = {}

        size_url = 'https://api.github.com/repos/'
        for item in self.results_dict['items']:
            full_name_set.add(item['repository']['full_name'])
        full_name_list = list(full_name_set)

        for item in full_name_list:
            full_url = size_url + item
            r = requests.get(full_url, auth=(self.user, self.pw))
            ri_list = []
            if r.status_code == 200:
                get_json = r.json()
                repo_size = get_json['size']
                repo_updated = get_json['updated_at']
                repo_full_name = get_json['full_name']
                repo_description = get_json['description']
                repo_user = get_json['owner']['login']
                repo_name = get_json['name']
                repo_id = get_json['id']
                repo_owner_id = get_json['owner']['id']
                repo_updated_ts = datetime.datetime.strptime(repo_updated, "%Y-%m-%dT%H:%M:%SZ").timestamp()
                repo_updated_ts_db = repo_updated.replace('T',' ').replace('Z','') #to add to DB timestamp
                ri_list.append(repo_size)
                ri_list.append(repo_updated_ts)
                ri_list.append(repo_full_name)
                ri_list.append(repo_description)
                ri_list.append(repo_user)
                ri_list.append(repo_name)
                ri_list.append(repo_id)
                ri_list.append(repo_owner_id)
                ri_list.append(repo_updated_ts_db)
                add_to_dict = {item: ri_list}
                repo_size_dict.update(add_to_dict)
            else:
                print(r.status_code)
        ordered_repo_size_dict = sorted(repo_size_dict.items(), key=lambda x: x[1][1], reverse=True)

        ordered_repo_size_dict = dict(ordered_repo_size_dict)
        return ordered_repo_size_dict
        # NOTE the size is returned in KBs.  5657210 from api == 5.65 gb when cloned.

    def download_repo(self, input_dict, directory):
        os.chdir(directory)
        maximum = self.max_size * 100
        cloned_list = []
        too_large_dict = {}
        for key in input_dict:
            repo_name = str(key).split('/')[1]
            folder_name = str(key).replace('/', '-')

            if input_dict[key][0] <= maximum:
                html_url = "https://github.com/" + key
                git_url = html_url + ".git"
                clone = "git clone " + git_url + " " + folder_name
                folder_path = os.path.join(directory, folder_name)
                history_filename = folder_name + "_history.log"
                git_ignore_filename = os.path.join(directory, folder_name, ".gitignore")
                if os.path.exists(folder_path):
                    if directory[0:1] != '/':
                        drive_letter = directory[0:2]
                    else:
                        drive_letter = 'true'
                    enter_dir_cmd = "cd " + folder_path
                    git_pull_cmd = "git pull"
                    git_history_cmd = "git --no-pager log -p > " + history_filename
                    check_pull_command = drive_letter + " & " + enter_dir_cmd + " & " + git_pull_cmd
                    check_pull_result = os.popen(check_pull_command).read()
                    if check_pull_result != "Already up to date.\n":
                        full_command = drive_letter + " & " + enter_dir_cmd + " & " + git_pull_cmd + " & " + git_history_cmd
                        os.system(full_command)
                if not os.path.exists(folder_path):
                    os.system(clone)
                    if directory[0:1] != '/':
                        drive_letter = directory[0:2]
                    else:
                        drive_letter = "true"
                    enter_dir_cmd = "cd " + folder_path
                    git_history_cmd = "git --no-pager log -p > " + history_filename
                    full_command = drive_letter + " & " + enter_dir_cmd + " & " + git_history_cmd
                    os.system(full_command)
                if not os.path.isfile(git_ignore_filename):
                    git_file = open(git_ignore_filename, 'w')
                    git_file.write(history_filename)
                    git_file.close()
                else:
                    git_file = open(git_ignore_filename, 'r')
                    ignore_text = git_file.read()
                    git_file.close()
                    ignore_list = ignore_text.split('\n')
                    if history_filename not in ignore_list:
                        git_file = open(git_ignore_filename, 'a')
                        git_file.write("\n" + history_filename)
                    git_file.close()
                cloned_list.append(folder_name)
                input_dict[key].append('cloned')
                input_dict[key].insert(0, folder_name)
            else:
                input_dict[key].append('not_cloned')
                input_dict[key].insert(0, folder_name)
        return input_dict, cloned_list
