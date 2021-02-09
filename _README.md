# GitMAD (Git Monitor, Alert, Discover)

GitMAD is a full stack application that monitors Github for a given keyword(s) or domain. GitMAD searches code hosted on Github for a matching keyword. On finding a match, GitMAD will clone the repository and search through the files for a series of configurable regular expressions. GitMAD then takes those results and inserts them into a database for later viewing. These results can also be sent as email alerts. GitMAD runs continuously to discover new repositories matching the input keyword.


## Input

GitMAD searches Github for a keyword or domain. The user can also configure the maximum amount of results per search, the amount of time between searches, and the maximum size of a repository to clone. There are two modes, Monitor and Discovery. Discovery mode pulls out and searches new results with each run. Monitor mode will download all matches of a given keyword / domain first, search them, and then continue to search for new results.


## Processing

GitMAD takes the results from above and searches the Git history of the repository. The history is searched for a set of configurable regular expressions. GitMAD can also break up each line of a history file and search this for matches in Shannon entropy.

### There are two configurable files:

#### regex_matches.py
This is the location to put keywords and regular expressions to search within the content of a repository, just add a dictionary to the list below:

```python
to_match = [
    {'match_regex': r'password', 'match_type': 'Password Match'},
    {'match_regex': r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', 'match_type': 'IP Match'},
    {'match_regex': r'username', 'match_type': 'Username Match'},
    {'match_regex': r'\b[\w.]*@[\w]*\.[\w.]*\b', 'match_type': 'Email Match'}
    ]
```

#### entropy_whitelist.py
This is the location to remove items the Entropy feature is matching that you do not want.  Just add a dictionary to the list below:

```python
r_whitelist = [{'regex':r'\b[A-Za-z][a-z]+([A-Z][a-z]*)+\b'}] # Camel Case
```

## Output

GitMAD takes the results above and inserts them into a database which contains information on the file the match was found, as well as information about the repository. It also inserts the string that was matched and the line of the match. These results are available via an email alert, in the database, and via the web application.

### Web Application
Running web_home.py will open a web application on port 5000.  There is a 'Monitor' section which allows a user to view and filter on individual matches within a repository.  The 'Repo Info' section allows a user to view and filter on the repository matches themselves.

### API
#### /api/repos
Allows a user to view either the first 100 most recent repositories, or to use various filters to search for a given repo or set of repos.

A GET request with no parameters to /api/repos will return the 100 most recent results.
```python
GET http://localhost:5000/api/repos
Content-Type: application/json
```

A POST request allows a user to filter for a specific repo or repos.

Send a JSON object (Content-Type: application/json) with at least one of the following keys:
1) page - Results are given in pages of 100.  {"page": 2} equals 101-200, {"page": 3} equals 201-300 and so on.
2) repo_user - Username of the individual posting the repository.
3) repo_name - Name of the repository.
4) repo_cloned - Whether the repo(s) being searched for were cloned locally or not due to size {"repo_cloned": "not_cloned"}
5) repo_desc - Keywords to search for in the repository description {"repo_desc": "config"}
                        
POST data example (at least one of these keys must be used):
```python
POST http://localhost:5000/api/repos
Content-Type: application/json
 
 {
 "page": 1, 
 "repo_user": "<Username of the repository>", 
 "repo_name": "<Name of the repository>", 
 "repo_cloned": "<cloned|not_cloned>", 
 "repo_desc": "<text string to search for in the repository description>"
 }
```

#### /api/results
Allows a user to view either the first 100 most recent results, or to use various filters to search for a given match or set of matches.


A GET request with no parameters to /api/repos will return the 100 most recent results.
```python
GET http://localhost:5000/api/results
Content-Type: application/json
```

A POST request allows a user to filter for a specific match or type of match.

Send a JSON object (Content-Type: application/json) with at least one of the following keys:
1) page - Results are given in pages of 100.  {"page": 2} equals 101-200, {"page": 3} equals 201-300 and so on.
2) match_type - String for type of match {"match_type": ["password", "username"]}
3) match_string - A string to match the matched item {"match_string": "password"}
4) match_location - A string to match the file path {"match_location": "conf"}
5) match_line - A string that will match on the line the item was found {"match_line": "jdbc:mysql://"}
6) match_update_type - '+' for items added to the repo, '-' for items deleted. {"match_update_type": "-"}
7) match_author - String for the author of the commit {"match_author": "johndoe"}
8) match_message - String to match the commit message {"match_message": "credentials"}
                        
POST data example (at least one of these keys must be used):
```python
POST http://localhost:5000/api/repos
Content-Type: application/json
 
{
"page": 2,
"match_type": "<type of match>", 
"match_string": "<item that was matched>",
"match_location": "<file location where item was matched>", 
"match_line": "<match something on the line of the initial match>", 
"match_update_type": "<['+','-'] addition or deletion to/from repo>",
"match_author": "<commit author>", 
"match_message": "<commit message>"
 }
```

## Current Status
*This project is in active development*

# Install

GitMAD was originally written in Python3.6 on Windows.  It has also been tested on Ubuntu 18.04.

## Software Requirements
Python 3.6+ (f-strings are used in this project, which requires Python 3.6)

Pip for Python3

Git

MySQL 8.0

For MySQL 8.0 on Windows, you should be able to download from the Oracle Website.
For Ubuntu 18.04, the default version is still 5.7, so you will have to change the version:
```
wget -c https://dev.mysql.com/get/mysql-apt-config_0.8.12-1_all.deb 
sudo dpkg -i mysql-apt-config_0.8.12-1_all.deb
#select version 8.0
sudo apt update 
sudo apt install mysql-server
sudo mysql_secure_installation
```

## Step By Step (commands performed on Ubuntu 18.04)

### 1) Clone the repository and enter directory:
```
git clone https://github.com/deepdivesec/GitMAD.git
cd GitMAD
```

### 2) Install dependencies:
```
pip3 install -r requirements.txt
```

### 3) Add script to MySQL:
```
$sudo mysql -u username -p
mysql> source /<path-to-gitmad>/GitMAD/_github_search_db.sql
```

### 4) Run main.py and on first run enter configuration information:
```
python3 /<path-to-gitmad>/GitMAD/main.py -q <keyword-to-search> [see other options below]
```
![GitMAD Help](https://github.com/deepdivesec/GitMAD/blob/master/GitMAD-install/gitmad-help.PNG)

### 5) Run web application:
```
python3 /<path-to-gitmad>/GitMAD/web_home.py
```

### 6) (Optional) Download and install MySQL Workbench to directly interact with results:
https://dev.mysql.com/downloads/workbench/


## Additional Ubuntu install gifs available here:
https://github.com/deepdivesec/GitMAD/tree/master/GitMAD-install

## Known Issues
* Sometimes the Github API will return 0 for the size of a repository, regardless of its size.  Due to the fact that a lot of the time these are significantly larger than the maximum size flag, a repository with size of 0 will not be downloaded.


