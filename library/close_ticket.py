import requests
import json
import sqlite3
requests.packages.urllib3.disable_warnings()

JIRA_URL = ''

def main(issue_id, job_id, channel, *args, **kwargs):
    url = "{0}/rest/api/2/issue/{1}/transitions?expand=transitions.fields".format(JIRA_URL, issue_id)
    auth = ('', '')
    payload = {"transition": {"id": 41}}
    headers = {'Content-Type': 'application/json'}
    r = requests.post(url, data=json.dumps(payload), auth=auth, headers=headers)
    if r.status_code != 204:
        print "FAILED" + r.text
    else:
        result = "<{0}/browse/{1}|{1}>".format(JIRA_URL, issue_id)
        conn = sqlite3.connect('kevin.db')
        with conn:
            conn.execute("INSERT INTO RESULTS (job_id, result) VALUES (?, ?) ", (job_id, result))
            conn.execute("UPDATE JOBS SET status=1 WHERE id = ?", (job_id, ))
            conn.commit()
