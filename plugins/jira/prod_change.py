import sqlite3
from library.checks import check_channel, check_text

outputs = []
token = ''


def process_message(data):
    """
    @keyword *prod change:* `^kevin.*prod change*(\\n|\|){2}`
    *kevin* _[]_ *prod change* _[]_ * _|[user]|[summary title]|[|more details]_
    @summary instead of switching context to jira just to make a silly change to ST2, have kevin make the prod change
    @see *prod change:* _*kevin* create *prod change* ticket *|steve|Rolling Latest PHP Core to ST2
    """
    # IF ALL CHECKS PASS SEND JOB TO DB
    if 'text' in data:
        text = data['text'].encode('ascii', 'ignore')
    else:
        text = ''
    if check_channel(data['channel']) and check_text("^kevin.*prod change.*", text):
        # EXTRACT TICKET DATA FROM STATEMENT
        print "Prod CHange"
        n_text = text.split("\n")
        p_text = text.split("|")
        if len(n_text) >= 3 or len(p_text) >= 3:
            # ASSIGN THE TEXT
            split_text = p_text if len(p_text) >= 3 else n_text
            # user_id = data['user']
            # user_name = get_culprit_name(user_id)
            user_name = split_text[1]
            summary = "{} - {}".format(user_name, split_text[2])
            # desc = "\n".join(split_text[3:])
            conn = sqlite3.connect('kevin.db')
            with conn:
                conn.execute("INSERT INTO JOBS (channel, name, parms, status) VALUES (?, 'prod_change', ?, 0)",
                             (data['channel'], '{}|{}'.format(user_name, summary)))
                conn.commit()
            outputs.append([data['channel'], 'Summary: {}'.format(summary)])
        else:
            print "NOT ENOUGH FIELDS: {}".format(text)
            outputs.append([data['channel'], "SQUAAAWWKK Not enough Fields for Prod change"])

def get_culprit_name(user_id):
    """
        Takes the user_id and finds the human readable slack name
    """
    import requests
    url = "https://slack.com/api/users.info"
    payload = dict(token=token, user=user_id)
    r = requests.post(url, data=payload)
    if r.status_code != 200:
        print r.status_code, r.text
    else:
        return r.json()['user']['name']
