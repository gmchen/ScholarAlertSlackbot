#!/usr/bin/env python
########################################################################################################
#
# QueryAndParseEmail.py
# Author: Gregory M Chen
# 
# Description: Log into an IMAP4 email server, fetch unread email, identify Google Scholar Alerts
# and generate text message for Slack.
#
#
########################################################################################################

import imaplib
import email
import re
import datetime
import sys
from BeautifulSoup import BeautifulSoup

## A text file with two lines: username and password
f = open('creds.txt')
lines = f.readlines()
f.close()

username = lines[0].rstrip()
password = lines[1].rstrip()

print "Connecting to Gmail server..."
mail = imaplib.IMAP4_SSL('imap.gmail.com')
print "Connected. Logging in..."
mail.login(username, password)
print "Logged in. Fetching unread emails..."
mail.select('inbox')
result, data = mail.uid('search', None, 'UnSeen')
ids = data[0].split()

email_texts = [];
email_senders = []

for i in ids:
	result, data = mail.uid('fetch', i, '(RFC822)')
	raw_email = data[0][1]
	email_message = email.message_from_string(raw_email)
	if email_message['subject'] != 'Scholar Alert - New citations to my articles':
		continue
	
    # The following snippet was originally derived from http://stackoverflow.com/a/1463144
    count = 0
    # Grab the first html part
    charset = part.get_content_charset()
    html_text = ""
	for part in email_message.walk():
		if part.get_content_type() == 'text/html':
			html_text = unicode(part.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace')
			break

	if(html_text == ""):
		print("Error: could not find html text in email")
		sys.exit()
	
	soup = BeautifulSoup(html_text)

	paper_titles = []
	paper_urls = []
	author_lists = []

	for header_tag in soup.findAll('h3'):
	if len(header_sections) != len(body_sections):
		paper_urls.append(header_tag.a['href'])
		paper_titles.append(header_tag.a.font.contents[0])

	for header_section in header_sections:
		author_lists