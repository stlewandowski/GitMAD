#!/usr/bin/python3

from flask import Flask, render_template, url_for, request, Response
import db_ops as db
import conf
import regex_matches
import json
import datetime

c = conf.Configure()
conf_file, file_check = c.check_for_file(c.c_filename)
pxy, db_u, db_p, db_h, db_db, g_u, g_p, d = c.populate_credentials(conf_file, file_check)
db_user = db_u
db_pw = db_p
db_host = db_h
db_db = db_db

app = Flask(__name__)


@app.route('/')
@app.route('/index')
def index():
    """Index page."""
    return render_template('index.html')


def process_repos(db_res, num_res, page):
    results = {}
    r_list = []
    for r in db_res:
        local_list = []
        r_dict = {}
        for item in r:
            local_list.append(item)
        r_dict["Repo ID"] = local_list[0]
        r_dict["Repo Owner ID"] = local_list[1]
        r_dict["Repo User"] = local_list[2]
        r_dict["Repo Name"] = local_list[3]
        r_dict["Repo Full Name"] = local_list[4]
        if isinstance(local_list[5], datetime.datetime):
            r_dict["Repo Updated Timestamp"] = local_list[5].strftime("%Y-%m-%d %H:%M:%S")
        else:
            local_list[5] = None
        r_dict["Repo Size"] = local_list[6]
        r_dict["Repo Cloned"] = local_list[7]
        r_dict["Repo Description"] = local_list[8]
        r_dict["Repo Last Checked Timestamp"] = local_list[9].strftime("%Y-%m-%d %H:%M:%S")
        r_dict["Repo Last Commit Hash"] = local_list[10]

        r_list.append(r_dict)
    matches = {"total_count": num_res, "page": page, "matches": r_list}
    results.update(matches)
    results = json.dumps(results)
    return results


@app.route('/api/repos')
def api_repo():
    """Get most recent 100 results of Repos"""
    x = db.DbOps(db_u, db_p, db_h, db_db)
    res, num, pg = x.display_repos_api()
    results = process_repos(res, num, pg)
    resp = Response(results, status=200, mimetype='application/json')
    return resp


@app.route('/api/repos', methods=['POST'])
def api_repo_filter():
    """Accepts filters to return more specific results."""
    post_dict = request.get_json()
    # {"num_res": 100, "page": 1, "repo_user": "ddd", "repo_name": "ccc", "repo_cloned": "yes", "repo_desc": "config"}
    # Sanitizing the post_dict to only accept specific keys for filtering.
    if ("num_res" in post_dict) or \
            ("page" in post_dict) or \
            ("repo_user" in post_dict) or \
            ("repo_name" in post_dict) or \
            ("repo_cloned" in post_dict) or \
            ("repo_desc" in post_dict):
        pd = {}
        if ("num_res" in post_dict) and (isinstance(post_dict["num_res"], int) is True):
            upd = {"num_res": post_dict["num_res"]}
            pd.update(upd)
        else:
            upd = {"num_res": 100}
            pd.update(upd)
        if ("page" in post_dict) and (isinstance(post_dict["page"], int) is True):
            upd = {"page": post_dict["page"]}
            pd.update(upd)
        else:
            upd = {"page": 1}
            pd.update(upd)
        if ("repo_user" in post_dict) and (isinstance(post_dict["repo_user"], str) is True):
            upd = {"repo_user": post_dict["repo_user"]}
            pd.update(upd)
        else:
            upd = {"repo_user": "%"}
            pd.update(upd)
        if ("repo_name" in post_dict) and (isinstance(post_dict["repo_name"], str) is True):
            upd = {"repo_name": post_dict["repo_name"]}
            pd.update(upd)
        else:
            upd = {"repo_name": "%"}
            pd.update(upd)
        if ("repo_cloned" in post_dict) \
                and (isinstance(post_dict["repo_cloned"], str) is True) \
                and ((post_dict["repo_cloned"] == "cloned") or (post_dict["repo_cloned"] == "not_cloned")):
            upd = {"repo_cloned": post_dict["repo_cloned"]}
            pd.update(upd)
        else:
            upd = {"repo_cloned": "%"}
            pd.update(upd)
        if ("repo_desc" in post_dict) and (isinstance(post_dict["repo_desc"], str) is True):
            upd = {"repo_desc": post_dict["repo_desc"]}
            pd.update(upd)
        else:
            upd = {"repo_desc": "%"}
            pd.update(upd)

        x = db.DbOps(db_u, db_p, db_h, db_db)
        res, num, pg = x.display_repos_api(pd)
        results = process_repos(res, num, pg)
        resp = Response(results, status=200, mimetype='application/json')
        return resp
    else:
        invalid_post = {
            "error": "Invalid POST parameters passed in request.",
            "helpString": '''Send a JSON object (Content-Type: application/json) with at least one of the following keys:
1) page - Results are given in pages of 100.  {"page": 2} equals 101-200, {"page": 3} equals 201-300 and so on.
2) repo_user - Username of the individual posting the repository.
3) repo_name - Name of the repository.
4) repo_cloned - Whether the repo(s) being searched for were cloned locally or not due to size {"repo_cloned": "not_cloned"}
5) repo_desc - Keywords to search for in the repository description {"repo_desc": "config"}
                        
POST data example (at least one of these keys must be used):
 {
 "page": 1, 
 "repo_user": "<Username of the repository>", 
 "repo_name": "<Name of the repository>", 
 "repo_cloned": "<cloned|not_cloned>", 
 "repo_desc": "<text string to search for in the repository description>"
 }'''
        }
        resp = Response(json.dumps(invalid_post), status=400, mimetype='application/json')
        return resp


@app.route('/api/results')
def api_results():
    """Get most recent 100 results of Search Results"""
    return render_template('/api/results.html', title="Search Results API")


@app.route('/api/results', methods=['POST'])
def api_results_filter():
    """Accepts filters to return more specific results."""
    return render_template('/api/results.html', title="Search Results API")


@app.route('/search')
def search():
    """Search page."""
    return render_template('search.html')


@app.route('/repo_info')
def repo_info():
    """Initial repo_info page, showing various metadata for each repository."""
    post_dict = {'num_res': 100, 'r_user': '', 'r_name': '',
                 'r_cloned': 'Any', 'r_desc': '', 'r_checked': ''}
    x = db.DbOps(db_u, db_p, db_h, db_db)
    res, num = x.display_repos(post_dict)
    c_list = ['cloned', 'not_cloned']
    return render_template('repo_info.html', results=res, num_results=num, select_opt=c_list, p_dict=post_dict)


@app.route('/repo_info', methods=['POST'])
def repo_info_upd():
    """Updated repo_info page, to handle filtering."""
    if request.form['btn'] == "Submit":
        num_res = request.form['num_results']
        r_user = request.form['repo_user']
        r_name = request.form['repo_name']
        r_cloned = request.form['is_cloned']
        r_desc = request.form['repo_description']
        # r_checked = request.form['repo_checked']
        r_checked = ''
        post_dict = {'num_res': num_res, 'r_user': r_user, 'r_name': r_name, 'r_cloned': r_cloned,
                     'r_desc': r_desc, 'r_checked': r_checked}
    if request.form['btn'] == "Clear Filter":
        post_dict = {'num_res': 100, 'r_user': '', 'r_name': '',
                     'r_cloned': 'Any', 'r_desc': '', 'r_checked': ''}
    x = db.DbOps(db_u, db_p, db_h, db_db)
    c_list = ['cloned', 'not_cloned']
    res, num = x.display_repos(post_dict)
    return render_template('repo_info.html', results=res, num_results=num, select_opt=c_list, p_dict=post_dict)


@app.route('/monitor')
def mon():
    """Initial monitor page, showing GitMAD search results."""
    post_dict = {'num_res': 100, 'r_user': '', 'r_name': '',
                 'm_string': '', 'm_line': '', 'm_location': '', 'm_type': ''}
    x = db.DbOps(db_u, db_p, db_h, db_db)
    res, num, stmt = x.display_match_results(post_dict['num_res'], post_dict)
    s_val = regex_matches.to_match
    s_list = []
    for item in s_val:
        s_list.append(item['match_type'])
    return render_template('monitor.html', results=res, num_results=100,
                           select_opt=s_list, query=stmt, p_dict=post_dict)


@app.route('/monitor', methods=['POST'])
def mon_upd():
    """Updated monitor page, to handle filtering."""
    if request.form['btn'] == "Submit":
        num_res = request.form['num_results']
        r_user = request.form['repo_user']
        r_name = request.form['repo_name']
        m_string = request.form['match_string']
        m_line = request.form['match_line']
        m_location = request.form['location']
        m_type = request.form['match_type']
        post_dict = {'num_res': num_res, 'r_user': r_user, 'r_name': r_name,
                     'm_string': m_string, 'm_line': m_line, 'm_location': m_location, 'm_type': m_type}
    if request.form['btn'] == "Clear Filter":
        post_dict = {'num_res': 100, 'r_user': '', 'r_name': '',
                     'm_string': '', 'm_line': '', 'm_location': '', 'm_type': ''}
    x = db.DbOps(db_u, db_p, db_h, db_db)
    s_val = regex_matches.to_match
    s_list = []
    for item in s_val:
        s_list.append(item['match_type'])
    res, num, stmt = x.display_match_results(post_dict['num_res'], post_dict)
    return render_template('monitor.html', results=res, num_results=num,
                           select_opt=s_list, query=stmt, p_dict=post_dict)


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(debug=True)
