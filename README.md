# GitMAD (Git Monitor, Alert, Discover)

GitMAD is a full stack application that monitors Github for a given keyword(s) or domain. GitMAD searches code hosted on Github for a matching keyword. On finding a match, GitMAD will clone the repository and search through the files for a series of configurable regular expressions. GitMAD then takes those results and inserts them into a database for later viewing. These results can also be sent as email alerts. GitMAD runs continuously to discover new repositories matching the input keyword.


## Input

GitMAD searches Github for a keyword or domain. The user can also configure the maximum amount of results per search, the amount of time between searches, and the maximum size of a repository to clone. There are two modes, Monitor and Discovery. Discovery mode pulls out and searches new results with each run. Monitor mode will download all matches of a given keyword / domain first, search them, and then continue to search for new results.


## Processing

GitMAD takes the results from above and searches the Git history of the repository. The history is searched for a set of configurable regular expressions. GitMAD can also break up each line of a history file and search this for matches in Shannon entropy.


## Output

GitMAD takes the results above and inserts them into a database which contains information on the file the match was found, as well as information about the repository. It also inserts the string that was matched and the line of the match. These results are available via an email alert, in the database, and via the web application.

# Install

GitMAD was originally written in Python3.6 on Windows.  It has also been tested on Ubuntu 18.04.

## Software Requirements
Python3
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
mysql> source /<path-to-gitmad>/GitMAD/github_search_db.sql
```

### 4) Run main.py and on first run enter configuration information:
```
python3 /<path-to-gitmad>/GitMAD/main.py
```

### 5) Run web application:
```
python3 /<path-to-gitmad>/GitMAD/web_home.py
```

### 6) (Optional) Download and install MySQL Workbench to directly interact with results:
https://dev.mysql.com/downloads/workbench/

# GitMAD options are found in the main.py file:
