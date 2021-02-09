#!/usr/bin/python3
import configparser
import os
import base64
import getpass


class Configure:
    """Class to set up configuration files, both for the main program as well as for email alerts."""
    def __init__(self):
        abs_path = os.path.abspath(__file__)
        path_dir, fname = os.path.split(abs_path)
        self.path = path_dir
        self.c_filename = 'conf.ini'
        self.e_filename = 'email_conf.ini'
        file = os.path.join(self.path, self.c_filename)
        config = configparser.ConfigParser()
        config.read(file)

    def check_for_file(self, fname):
        """Determine whether a configuration file exists, if not create it."""
        file = os.path.join(self.path, fname)
        if not os.path.isfile(file):
            open(file, 'w').close()
            present = 'absent'
        else:
            print('Config file already present.')
            present = 'present'
        return file, present

    def populate_email_credentials(self, file_path, is_present):
        """Check to see whether email configuration is present.  If not populate it."""
        config = configparser.ConfigParser()
        config.read(file_path)
        try:
            conf_list = [{'Value': config['Email']['From'], 'Section': 'Database', 'Section_Value': 'From'},
                         {'Value': config['Email']['To'], 'Section': 'Database', 'Section_Value': 'To'},
                         {'Value': config['Email']['Domain'], 'Section': 'Database', 'Section_Value': 'Domain'},
                         {'Value': config['Email']['Port'], 'Section': 'Database', 'Section_Value': 'Port'},
                         {'Value': config['Email']['Password'], 'Section': 'Github', 'Section_Value': 'Password'},
                         ]

            for item in conf_list:
                if item['Value'] == '':
                    value_var = input('Enter ' + item['Section'] + ' ' + item['Section_Value'] + ': ')
                    section = item['Section']
                    value = item['Section_Value']
                    config[section][value] = value_var
                    with open(file_path, 'w') as configfile:
                        config.write(configfile)
            e_from = config['Email']['From']
            e_to = config['Email']['To']
            e_domain = config['Email']['Domain']
            e_port = config['Email']['Port']
            e_pw = config['Email']['Password']
        #else:
        except Exception as e:
            print(e)
            e_from = input('Enter email address to send from:')
            e_to = input('Enter email address to send to:')
            e_domain = input('Enter domain name of SMTP server:')
            e_port = input('Enter port to connect to SMTP server on:')
            e_pw = getpass.getpass('Enter email password:')#input('Enter email password:')
            e_pw = base64.b64encode(e_pw.encode("utf-8")) # encoding to accept all characters in PWs
            config['Email'] = {'From': e_from,
                               'To': e_to,
                               'Domain': e_domain,
                               'Port': e_port,
                               'Password': e_pw}

            with open(file_path, 'w') as configfile:
                config.write(configfile)
            configfile.close()
        return e_from, e_to, e_domain, e_port, e_pw

    def populate_credentials(self, file_path, is_present):
        """Check to see whether main configuration is present.  If not populate it."""
        config = configparser.ConfigParser()
        config.read(file_path)
        try:
            conf_list = [{'Value': config['Database']['User'], 'Section': 'Database', 'Section_Value': 'User'},
                         {'Value': config['Database']['Password'], 'Section': 'Database', 'Section_Value': 'Password'},
                         {'Value': config['Database']['Host'], 'Section': 'Database', 'Section_Value': 'Host'},
                         {'Value': config['Database']['Database'], 'Section': 'Database', 'Section_Value': 'Database'},
                         {'Value': config['Github']['G_user'], 'Section': 'Github', 'Section_Value': 'G_user'},
                         {'Value': config['Github']['G_password'], 'Section': 'Github', 'Section_Value': 'G_password'},
                         {'Value': config['Directory']['Path'], 'Section': 'Directory', 'Section_Value': 'Path'},
                         {'Value': config['Proxy']['Host-Port'], 'Section': 'Directory', 'Section_Value': 'Host-Port'}]

            for item in conf_list:
                if item['Value'] == '':
                    value_var = input('Enter ' + item['Section'] + ' ' + item['Section_Value'] + ': ')
                    section = item['Section']
                    value = item['Section_Value']
                    config[section][value] = value_var
                    with open(file_path, 'w') as configfile:
                        config.write(configfile)
            db_user = config['Database']['User']
            db_password = config['Database']['Password']
            db_host = config['Database']['Host']
            db_database = config['Database']['Database']
            git_user = config['Github']['G_user']
            git_pw = config['Github']['G_password']
            directory = config['Directory']['Path']
            proxy = config['Proxy']['Host-Port']
        except Exception as e:
            print(e)
            db_user = input('Enter database user:')
            db_password = getpass.getpass('Enter database password:')  # input('Enter database password:')
            db_host = input('Enter hostname or IP of database connection:')
            db_database = input('Enter name of database:')
            git_user = input('Enter Github username:')
            git_pw = getpass.getpass('Enter Github password:')  # input('Enter Github password:')
            directory = input('Enter working [data] directory:')
            proxy = input('Enter proxy host:port (127.0.0.1:3128).  Enter \'n\' for no proxy.')
            config['Database'] = {'User': db_user,
                                  'Password': db_password,
                                  'Host': db_host,
                                  'Database': db_database}
            config['Github'] = {'G_user': git_user,
                                'G_password': git_pw}
            config['Directory'] = {'Path': directory}
            config['Proxy'] = {'Host-Port': proxy}

            with open(file_path, 'w') as configfile:
                config.write(configfile)
            configfile.close()
        return proxy, db_user, db_password, db_host, db_database, git_user, git_pw, directory


if __name__ == "__main__":
    c = Configure()
    conf_file, file_check = c.check_for_file()
    c.populate_credentials(conf_file, file_check)
