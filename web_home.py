#!/usr/bin/python3

from flask import Flask, render_template, url_for, request
import db_ops as db
import conf
import regex_matches

c = conf.Configure()
conf_file, file_check = c.check_for_file(c.c_filename)
db_u, db_p, db_h, db_db, g_u, g_p, d = c.populate_credentials(conf_file, file_check)
db_user = db_u
db_pw = db_p
db_host = db_h
db_db = db_db


app = Flask(__name__)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/search')
def search():
    return render_template('search.html')


@app.route('/monitor')
def mon():
    post_dict = {'num_res':100, 'r_user':'', 'r_name':'',
                 'm_string': '', 'm_line':'', 'm_location':''}
    x = db.DbOps(db_u, db_p, db_h, db_db)
    res, num, stmt = x.display_match_results(post_dict['num_res'], post_dict)
    s_val = regex_matches.to_match
    s_list = []
    for item in s_val:
        s_list.append(item['match_type'])
    return render_template('monitor.html', results=res, num_results=100,
                           select_opt=s_list, query=stmt)

@app.route('/monitor', methods=['POST'])
def mon_upd():
    num_res = request.form['num_results']
    r_user = request.form['repo_user']
    r_name = request.form['repo_name']
    m_string = request.form['match_string']
    m_line = request.form['match_line']
    m_location = request.form['location']
    post_dict = {'num_res':num_res, 'r_user':r_user, 'r_name':r_name,
                 'm_string': m_string, 'm_line':m_line, 'm_location':m_location}
    x = db.DbOps(db_u, db_p, db_h, db_db)
    s_val = regex_matches.to_match
    s_list = []
    for item in s_val:
        s_list.append(item['match_type'])
    res, num, stmt = x.display_match_results(post_dict['num_res'], post_dict)
    return render_template('monitor.html', results=res, num_results=num,
                           select_opt=s_list, query=stmt)


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404



if __name__ == "__main__":
    app.run(debug=True)
