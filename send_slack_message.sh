#!/bin/bash
json_text=`cat json_text.txt`
slack_hook_url=`cat slack_hook_url.txt`

curl -X POST --data-urlencode "payload=$json_text" $slack_hook_url

