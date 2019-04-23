#!/usr/bin/python3

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import base64
from prettytable import PrettyTable

class EmailAction:

    def __init__(self, e_from, e_to, e_domain, e_port, e_pw):
        self.e_from = e_from
        self.e_to = e_to
        self.e_domain = e_domain
        self.e_port = e_port
        self.e_pw = e_pw

    def send_alert(self, full_path, num_results, email_body):
        message = MIMEMultipart()
        e_from = self.e_from
        e_to = self.e_to
        self.e_pw = self.e_pw[2:-1]
        password = base64.b64decode(self.e_pw)
        password = str(password, 'utf-8')
        f_name = os.path.basename(full_path)
        f_query = f_name.split("--")[2].replace('-','.').replace(".zip","")
        f_time = f_name.split("--")[1].replace("-",":")
        message['From'] = e_from
        message['To'] = e_to
        message['Subject'] = "There are " + str(num_results) + " results for query " + f_query + " at " + f_time
        body = 'Results for query: ' + f_query + '\n\n'

        tbl = PrettyTable(header_style='upper', padding_width=10,
                          field_names=["Repo Author", "Repo Name", "Repo File", "Line - first 64 chars"])
        for item in email_body:
            file_match = os.path.basename(item["Path"])
            tbl.add_row([item["Repo Author"], item["Repo Name"], file_match, item["Line"].strip()[:68]])

        body += str(tbl)
        message.attach(MIMEText(body, 'plain'))

        attachment = open(full_path, "rb")
        payload = MIMEBase('application', 'octet-stream')
        payload.set_payload((attachment).read())
        encoders.encode_base64(payload)
        payload.add_header('Content-Disposition', "attachment; filename= %s" % f_name)
        message.attach(payload)
        send = smtplib.SMTP(self.e_domain, self.e_port)
        send.starttls()
        send.login(e_from, password)
        text = message.as_string()
        send.sendmail(e_from, e_to, text)
        send.quit()


if __name__ == "__main__":
    a = EmailAction()
    a.send_alert()
