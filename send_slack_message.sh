#!/bin/bash
slack_hook_url=`cat slack_hook_url.txt`
python QueryAndParseEmail.py

if [ ls text*.json 1> /dev/null 2>&1 ]; then
	echo "Could not find json files, perhaps there are no unread emails in the inbox?"
	exit
fi

for filename in text*.json
do
	curl -X POST --data @./$filename $slack_hook_url
done
rm text*.json
