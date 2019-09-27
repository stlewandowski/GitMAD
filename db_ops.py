#!/usr/bin/python3

from sqlalchemy import create_engine
from sqlalchemy import MetaData #to get table data
from sqlalchemy import Table
from sqlalchemy.sql import select #to select data
from sqlalchemy.sql import text #for text query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import join
from sqlalchemy import desc
from sqlalchemy.sql import and_, or_, not_
import conf
import datetime
import configparser
import json
import os

class DbOps:
    """Class that contains database queries and inserts for the program."""
    def __init__(self, username, password, host, database):
        self.user = username
        self.pw = password
        self.host = host
        self.db = database

    def create_conn(self):
        """Connect to database."""
        usr = self.user
        pw = self.pw
        host = self.host
        database = self.db
        db_connect_string = 'mysql+pymysql://' + usr + ':' + pw + '@' + host + '/' + database
        engine = create_engine(db_connect_string)
        conn = engine.connect()
        return conn, engine

    def get_table(self, table_name, engine):
        """Get table metadata."""
        meta = MetaData(engine)
        meta.reflect()
        table = Table(table_name, meta, autoload=True)
        return table

    def test_str_length(self):
        print("testing")

    def get_recent_hash(self, r_id):
        """Get the hash of the most recent commit."""
        cnxn, enxn = self.create_conn()
        result = ''
        tbl = self.get_table('repo_info', enxn)
        stmt = select([tbl.c.repo_latest_commit]).where(tbl.c.repo_id == r_id)
        try:
            res = cnxn.execute(stmt)
        except:
            res = 'no commit in db'
        for row in res:
            result = row[0]
        res.close()
        return result


    def update_repo_info(self, in_list, commit_hash):
        """Update repo_info table with repository metadata."""
        cnxn, enxn = self.create_conn()
        ins = self.get_table('repo_info', enxn).insert()
        upd_table = self.get_table('repo_info', enxn)
        try:
            ins.execute(repo_id=in_list[7],
                        repo_owner_id=in_list[8],
                        repo_user=in_list[5],
                        repo_name=in_list[6],
                        repo_full_name=in_list[3],
                        repo_updated__ts=in_list[9],
                        repo_size=in_list[1],
                        repo_cloned=in_list[10],
                        repo_description=self.truncate(in_list[4], 4096),
                        repo_latest_commit=commit_hash)

        except IntegrityError as e:
            # print(e)
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            upd_table.update().values(repo_last_checked=timestamp,
                                      repo_latest_comit=commit_hash,
                                      repo_cloned=in_list[10]).where(upd_table.c.repo_id==in_list[7])

    def update_repo_search_results(self, in_list_repo, in_list_matches, search_type):
        """Update repo_search_results table with keyword/regex matches."""
        cnxn, enxn = self.create_conn()
        ins = self.get_table('repo_search_results', enxn).insert()
        upd = self.get_table('repo_search_results', enxn).update()
        added = 0
        added_list = []
        for item in in_list_matches:
            if search_type == 'git_history':
                matching_line = item['Match Line'][1:]
            else:
                matching_line = item['Match Line']
            try:
                ins.execute(match_repo_id=in_list_repo[7],
                        match_type=self.truncate(item['Match Type'], 256),
                        match_string=self.truncate(item['Match Value'], 256),
                        match_location=self.truncate(item['Match Path'], 2048),
                        match_line=self.truncate(matching_line, 8192),
                        match_item_entropy=item['Match Entropy'],
                        match_line_hash=item['Match Line Hash'],
                        match_update_type=item['Match Add or Del'],
                        match_commit_hash=item['Match Commit Hash'],
                        match_commit_author=item['Match Commit Author'],
                        match_commit_time=item['Match Commit Time'],
                        match_commit_message=self.truncate(item['Match Commit Message'], 1024),
                        match_original_query=item['Match Original Query'])
                added += 1
                added_dict = {"Repo Name": in_list_repo[6], "Repo Author": in_list_repo[5],
                              "Query": item['Match Original Query'], "Type": self.truncate(item['Match Type'], 32),
                              "Path": self.r_truncate(item['Match Path'], 128), "Line": self.truncate(matching_line, 256),
                              "Item Entropy": item['Match Entropy'], "Add or Del": item['Match Add or Del'],
                              "Commit Author": item['Match Commit Author'], "Commit Time": item['Match Commit Time']}
                added_list.append(added_dict)
            except Exception as e: #IntegrityError:
                pass

        return added, added_list

    def search_for_repo(self):
        # search for a repo (repo_info)
        print("testing")

    def search_for_repo_match(self):
        # search for a repo match
        print("testing")

    def display_repos(self, post_dict):
        """Query and display repo info based on filtering items in web app."""
        # display list of repos, based on some constraint (time)
        cnxn, enxn = self.create_conn()
        r_info = self.get_table('repo_info', enxn)

        if post_dict['r_user'] != '':
            stmt = select([r_info.c.repo_id, r_info.c.repo_owner_id, r_info.c.repo_user,
             r_info.c.repo_name, r_info.c.repo_size, r_info.c.repo_cloned,
             r_info.c.repo_description, r_info.c.repo_last_checked,
             r_info.c.repo_latest_commit]).where(r_info.c.repo_user == post_dict['r_user']).order_by(desc(r_info.c.repo_last_checked)).limit(post_dict['num_res'])

        elif post_dict['r_cloned'] != '' and post_dict['r_cloned'] != 'Any':
            stmt = select([r_info.c.repo_id, r_info.c.repo_owner_id, r_info.c.repo_user,
             r_info.c.repo_name, r_info.c.repo_size, r_info.c.repo_cloned,
             r_info.c.repo_description, r_info.c.repo_last_checked,
             r_info.c.repo_latest_commit]).where(r_info.c.repo_cloned == post_dict['r_cloned']).order_by(desc(r_info.c.repo_last_checked)).limit(post_dict['num_res'])

        elif post_dict['r_desc'] != '':
            r_d = post_dict['r_desc']
            stmt = select([r_info.c.repo_id, r_info.c.repo_owner_id, r_info.c.repo_user,
             r_info.c.repo_name, r_info.c.repo_size, r_info.c.repo_cloned,
             r_info.c.repo_description, r_info.c.repo_last_checked,
             r_info.c.repo_latest_commit]).where(r_info.c.repo_description.like(f'%{r_d}%')).order_by(desc(r_info.c.repo_last_checked)).limit(post_dict['num_res'])

        else:
            stmt = select(
                [r_info.c.repo_id, r_info.c.repo_owner_id, r_info.c.repo_user,
                 r_info.c.repo_name, r_info.c.repo_size, r_info.c.repo_cloned,
                 r_info.c.repo_description, r_info.c.repo_last_checked,
                 r_info.c.repo_latest_commit]).order_by(desc(r_info.c.repo_last_checked)).limit(
                post_dict['num_res'])

        res = cnxn.execute(stmt)

        return res

    def display_match_results(self, num_results, post_dict = {}):
        """Query and display repo search results based on filtering items in web app."""
        cnxn, enxn = self.create_conn()
        #r_s_r = self.get_table('repo_search_results', enxn)
        #select_st = select([r_s_r]).order_by(desc(r_s_r.c.match_inserted)).limit(500)
        #res = cnxn.execute(select_st)
        r_info = self.get_table('repo_info', enxn)
        r_res = self.get_table('repo_search_results', enxn)

        join_obj = r_res.join(r_info, r_info.c.repo_id == r_res.c.match_repo_id)

        if post_dict:
            if post_dict['r_user'] == '':
                post_dict['r_user'] = '%'
            if post_dict['r_name'] == '':
                post_dict['r_name'] = '%'
            if post_dict['m_string'] == '':
                post_dict['m_string'] = '%'
            if post_dict['m_line'] == '':
                post_dict['m_line'] = '%'
            if post_dict['m_location'] == '':
                post_dict['m_location'] = '%'
            if post_dict['m_type'] == 'Any':
                post_dict['m_type'] = '%'
            if post_dict['m_type'] == '':
                post_dict['m_type'] = '%'

            m_s = post_dict['m_string']
            m_ln = post_dict['m_line']
            m_l = post_dict['m_location']
            m_n = post_dict['r_name']
            m_u = post_dict['r_user']
            m_t = post_dict['m_type']


            stmt = select(
                [r_info.c.repo_user, r_info.c.repo_name, r_res.c.match_inserted, r_res.c.match_type,
                 r_res.c.match_string, r_res.c.match_line, r_res.c.match_location, r_res.c.match_update_type,
                 r_res.c.match_commit_message,
                 r_info.c.repo_description]).select_from(join_obj).where(
                and_(
                r_info.c.repo_user.like(f'%{m_u}'),
                r_info.c.repo_name.like(f'%{m_n}%'),
                r_res.c.match_type.like(f'%{m_t}%'),
                r_res.c.match_string.like(f'%{m_s}%'),
                r_res.c.match_line.like(f'%{m_ln}%'),
                r_res.c.match_location.like(f'%{m_l}%')
                )
            ).order_by(desc(r_res.c.match_inserted)).limit(
                post_dict['num_res'])


        if not post_dict:
            def_results = {'num_res':100}
            post_dict.update(def_results)
            stmt = select(
                [r_info.c.repo_user, r_info.c.repo_name, r_res.c.match_inserted, r_res.c.match_type,
                 r_res.c.match_string, r_res.c.match_line, r_res.c.match_location, r_res.c.match_update_type,
                 r_res.c.match_commit_message,
                 r_info.c.repo_description]).select_from(join_obj).order_by(desc(r_res.c.match_inserted)).limit(post_dict['num_res'])

        res = cnxn.execute(stmt)
        nr = res.rowcount

        return res, nr, stmt

    def truncate(self, in_line, max_len):
        """Truncate line."""
        if in_line is not None:
            if len(in_line) > max_len:
                return in_line[:max_len-1]
            else:
                return in_line

    def r_truncate(self, in_line, max_len):
        """Truncate line - from the left side."""
        if in_line is not None:
            if len(in_line) > max_len:
                return in_line[max_len-1:]
            else:
                return in_line



if __name__ == "__main__":
    x = DbOps()
    x.display_match_results()



