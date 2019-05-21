#!/usr/bin/python3

from flask import Flask, render_template, url_for, request
import db_ops as db
import conf
import regex_matches

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


@app.route('/search')
def search():
    """Search page."""
    return render_template('search.html')

@app.route('/repo_info')
def repo_info():
    """Initial repo_info page, showing various metadata for each repository."""
    post_dict = {'num_res': 100, 'r_user': '', 'r_name': '',
                 'r_cloned': '', 'r_desc': '', 'r_checked': ''}
    x = db.DbOps(db_u, db_p, db_h, db_db)
    res = x.display_repos(post_dict)
    c_list = ['cloned', 'not_cloned']
    return render_template('repo_info.html', results=res, select_opt=c_list)

@app.route('/repo_info', methods=['POST'])
def repo_info_upd():
    """Updated repo_info page, to handle filtering."""
    num_res = request.form['num_results']
    r_user = request.form['repo_user']
    r_cloned = request.form['is_cloned']
    r_desc = request.form['repo_description']
    r_checked = request.form['repo_checked']
    post_dict = {'num_res': num_res, 'r_user': r_user, 'r_cloned': r_cloned,
                 'r_desc': r_desc, 'r_checked': r_checked}
    x = db.DbOps(db_u, db_p, db_h, db_db)
    c_list = ['cloned', 'not_cloned']
    res = x.display_repos(post_dict)
    return render_template('repo_info.html', results=res, select_opt=c_list, p_dict=post_dict)

@app.route('/monitor')
def mon():
    """Initial monitor page, showing GitMAD search results."""
    post_dict = {'num_res':100, 'r_user':'', 'r_name':'',
                 'm_string': '', 'm_line':'', 'm_location':'', 'm_type':''}
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
    num_res = request.form['num_results']
    r_user = request.form['repo_user']
    r_name = request.form['repo_name']
    m_string = request.form['match_string']
    m_line = request.form['match_line']
    m_location = request.form['location']
    m_type = request.form['match_type']
    post_dict = {'num_res':num_res, 'r_user':r_user, 'r_name':r_name,
                 'm_string': m_string, 'm_line':m_line, 'm_location':m_location, 'm_type':m_type}
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
