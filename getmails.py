# Python 2.7
"""
This is a basic email extract module for gmail accounts.
When the module is run it requests an email address and a password.
The subject header text is optional and can be used to filter emails.
Multipart emails are not supported.
The module was build using some of the code and instructions from:
http://www.voidynullness.net/blog/2013/07/25/gmail-email-with-python-via-imap/
A simple HTMLStrip was build on examples from
https://gist.github.com/erogol/7296578
"""
import imaplib
import getpass
import email
import re
from HTMLParser import HTMLParser
import os

html_entity_table = {}
html_entity_table['lg'] = '<'
html_entity_table['rg'] = '>'

class HTMLStrip(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)
    def handle_entityref(self, name):
        if name in html_entity_table.keys():
            self.fed.append(html_entity_table[name])
        else:
            self.fed.append("&"+name+";")
    def handle_charref(self, name):
        self.fed.append("&#"+name+";")
            
def strip_tags(html):
    """
    creates a HTMLStrip object to strip HTML markup from a string
    """
    s = HTMLStrip()
    s.feed(html)
    return s.get_data()

def process_mailbox(M, subj_cond):
    """
    processes a mailbox object M and finds emails fitting the
    subject header condition subj_cond
    a list of tuples is returned (email_address, email_text)
    """
    email_lst = []
    rv, data = M.search(None, "ALL")
    if rv != 'OK':
        print "No messages found!"
        return
    for num in data[0].split():
        rv, data = M.fetch(num, '(RFC822)')
        if rv != 'OK':
            print "ERROR getting messages", num
            return
        msg = email.message_from_string(data[0][1])
         
        if (re.findall(subj_cond, msg['Subject'])):
            try:
                txt = strip_tags(msg.get_payload().decode("UTF-8"))
                m = re.findall(r"\w+\.?\w+@\w+\.\w+", txt);

                for item in m:
                    email_lst.append((item, txt))
            except AttributeError:
                print "Multipart email could not be processed."
    return email_lst
    
def write_to_file(email_lst):
    """
    function takes a list of tuples as parameter (email_address, email_text)
    the email addresses are printed to a file
    """
    with open(FILE_PATH, 'w') as f:
        print "File {0} created".format(FILE_PATH)
        f.write(', '.join([addr[0] for addr in email_lst]))

if __name__ == "__main__":
    #set mailserver
    M = imaplib.IMAP4_SSL('imap.gmail.com')

    #get email account info
    CWD = os.getcwd()
    FILE_NAME = "emailaddr.txt"
    FILE_PATH = CWD + os.sep + FILE_NAME
    email_addr = raw_input("Enter your email address: ")
    pw = getpass.getpass()
    folder_name = raw_input("Enter a folder name within your account (default is INBOX): ")
    #enter a word or phrase from the subject header, emails will be filtered based on this
    subj_cond = raw_input("Enter a word or phrase that should be in the subject header: ")

    if folder_name == '':
        folder_name = 'INBOX'
    
    if subj_cond == '':
        subj_cond = "\w*"

    try:
        M.login(email_addr, pw)
        rv, data = M.select(folder_name)
        if rv == 'OK':
            print "Processing mailbox...\n"
            email_lst = process_mailbox(M, subj_cond)
            write_to_file(email_lst)
            print "Emails processed"
        else:
            print "Account Error. Check that folder name is correct!!! "
            M.close()
        M.logout()
    except imaplib.IMAP4.error:
        print "LOGIN FAILED!!! "





    

