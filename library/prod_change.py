import requests
import json
import sqlite3
requests.packages.urllib3.disable_warnings()

JIRA_URL = ''
JIRA_AUTH = ('', '')

def main(parms, job_id, channel, *args, **kwargs):
    """
        Creates Prod Change Ticket and returns the ticket ID to the channel
    """
    owner, summary = parms.split('|')
    url = "{}/rest/api/2/issue".format(JIRA_URL)
    payload = {'fields': {'summary': summary,
                          'project': {'id': '13001'},
                          'issuetype': {'name': 'Software Release'}}}
    headers = {'Content-Type': 'application/json'}
    r = requests.post(url, data=json.dumps(payload), auth=JIRA_AUTH, headers=headers)
    if r.status_code != 201:
        print "FAILED TO CREATE PC TICKET" + r.text
        return
    issue_id = r.json()['key']
    payload = {"name": owner}
    r = requests.put(url + "/{}/assignee".format(issue_id), auth=JIRA_AUTH, headers=headers, data=json.dumps(payload))
    if r.status_code != 204:
        print "FAILED TO ASSIGN OWNER" + r.text
    out_url = "<{0}/browse/{1}|{1}>".format(JIRA_URL, issue_id)
    conn = sqlite3.connect('kevin.db')
    with conn:
            conn.execute("INSERT INTO RESULTS (job_id, result) VALUES (?, ?) ", (job_id, "Ticket: {}".format(out_url)))
            conn.execute("UPDATE JOBS SET status=1 WHERE id = ?", (job_id, ))
            conn.commit()
