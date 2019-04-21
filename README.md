GitMAD (Git Monitor, Alert, Discover) is a full stack application that monitors Github for a given keyword(s) or domain. GitMAD searches code hosted on Github for a matching keyword. On finding a match, GitMAD will clone the repository and search through the files for a series of configurable regular expressions. GitMAD then takes those results and inserts them into a database for later viewing. These results can also be sent as email alerts. GitMAD runs continuously to discover new repositories matching the input keyword.


Input

GitMAD searches Github for a keyword or domain. The user can also configure the maximum amount of results per search, the amount of time between searches, and the maximum size of a repository to clone. There are two modes, Monitor and Discovery. Discovery mode pulls out and searches new results with each run. Monitor mode will download all matches of a given keyword / domain first, search them, and then continue to search for new results.


Processing

GitMAD takes the results from above and searches the Git history of the repository. The history is searched for a set of configurable regular expressions. GitMAD can also break up each line of a history file and search this for matches in Shannon entropy.


Output

GitMAD takes the results above and inserts them into a database which contains information on the file the match was found, as well as information about the repository. It also inserts the string that was matched and the line of the match. These results are available via an email alert, in the database, and via the web application.

==========================================================

==========================================================

Running GitMAD:

==========================================================

Install requirements:

pip install -r requirements.txt

==========================================================

Use the github_search_db.sql script to create the necessary tables in MySQL:

> mysql -u username -p github_search < github_search_db.sql

==========================================================

Run main file:

EX (search Github for 'keyword' query, send email alerts on new findings, and re-run the search every hour.

>python main.py -q keyword -e -rt 3600 

==========================================================

A first-run will populate two configuration files:

<conf.ini>

Database Username

Database Password

Database Host

Github Username

Github Password

Directory to store files

==========================================================

<email_conf.ini> to set up email alerts.

From Address

To Address

Sending Domain

Sending Port

Email Password


==========================================================



Full main.py options below:

usage: main.py [-h] [-rt [REFRESH]] [-m [{m,d}]] -q QUERY [-e] [-l]
               [-r [NUM_RESULTS]] [-mx [MAX_SIZE]] [-ent] [-es [ENT_SIZE]]

optional arguments:
  -h, --help            show this help message and exit
  
  -rt [REFRESH], --refresh-time [REFRESH]
                        Amount of seconds to wait until next Github search
                        (default is 14400 [4 hours]).
                        
  -m [{m,d}], --mode [{m,d}]
                        Run Mode: [m]onitor or [d]iscovery. Discovery is
                        default
                        
  -q QUERY, --query QUERY
                        String to search for in Github.
                        
  -e, --email           Flag to send email alerts.
  
  -l, --logs            Flag to enable logging of results
  
  -r [NUM_RESULTS], --results [NUM_RESULTS]
                        Number of results to search per run (default 30
                        results).
                        
  -mx [MAX_SIZE], --max-size [MAX_SIZE]
                        Maximum size of repo to be downloaded by megabyte
                        (default 5mb).
                        
  -ent, --entropy       Flag to search via entropy.
  
  -es [ENT_SIZE], --entropy-size [ENT_SIZE]
                        Flag to return entropy results above a certain value
                        (default size is 4).

==========================================================
                        
Run Web Application:

>python web_home.py


==========================================================

NOTE:
This is in active development and should be considered in an Alpha stage.

This was first built on Windows, but it will get ported to Linux.

