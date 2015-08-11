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
import sys
import BeautifulSoup
import json

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
	if not "google" in email_message['From']:
		continue
	if not ("Scholar Alert" in email_message['subject']):
		continue
	
	subject_text = re.sub(r'^Re: ', '', email_message['subject'])
	
	# The following snippet was originally derived from http://stackoverflow.com/a/1463144
	count = 0
	# Grab the first html part
	html_text = ""
	for part in email_message.walk():
		charset = part.get_content_charset()
		if part.get_content_type() == 'text/html':
			html_text = unicode(part.get_payload(decode=True),
								charset,
								"replace")
			break

	if(html_text == ""):
		print("Error: could not find html text, skipping this email.")
		continue
	
	soup = BeautifulSoup.BeautifulSoup(html_text,convertEntities="html")

	paper_titles = []
	paper_urls = []
	author_lists = []
	
	for header_tag in soup.findAll('h3'):
		paper_urls.append(header_tag.a['href'])
		paper_title = header_tag.a.font.contents[0]
		if paper_title == paper_title.upper():
			def replacement(match):
				return match.group(1).lower()
			paper_title = re.sub("(?<=[A-Z])([^ ]+)", replacement, paper_title)
			
		paper_titles.append(paper_title)

	for green_font_tag in soup.findAll("font", attrs={"color":"#006621"}):
		author_lists.append(green_font_tag.contents[0])
	
	if len(paper_titles) != len(paper_urls) or len(paper_urls) != len(author_lists):
		print("Error: mismatch in the size of paper_titles, paper_urls, and author_lists. Skipping this email.")
		continue

	for ind in range(len(paper_titles)):
		paper_titles[ind] = paper_titles[ind].replace("\r\n", "")
		paper_urls[ind] = paper_urls[ind].replace("\r\n", "")
		author_lists[ind] = author_lists[ind].replace("\r\n", "")
	
	text_to_write = "*" + subject_text + "*\n"
	for i in range(len(paper_titles)):
		text_to_write = text_to_write + "<" + paper_urls[i] + "|" + paper_titles[i] + ">\n" + author_lists[i] + "\n\n"

	data = {}
	data['text'] = text_to_write
	data['channel'] = "#publications"
	data['username'] = "scholar-bot"
	data['icon_emoji'] = ":fish:"

	outfile = open("text" + str(i) + ".json", "w")
	outfile.write(json.dumps(data))
	outfile.close()
