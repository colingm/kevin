import sqlite3
import requests
from random import randint
from time import sleep
import uuid
from multiprocessing import Process
from library.checks import check_channel, check_text
requests.packages.urllib3.disable_warnings()

outputs = []
token = 'xoxb-6815030849-SBpOQUZ9QfBbVectkXNDb9ve'

def process_message(data):
    """
    @keyword *send the bombs:* `^kevin.*squawk @ \a*`
    @summary send a channel bomb directly at someone, in case the group channel bombs where not enough
    @see *send the bombs:* _*kevin* I need you to *squawk @ matts* to find out if he's at lagoon with colinm_
    """
    # IF ALL CHECKS PASS SEND JOB TO DB
    if 'text' in data:
        text = data['text']
    else:
        text = ''
    if check_channel(data['channel']) and check_text("^kevin.*squawk @ \a*", text):
        culprit_id = data['user']
        culprit = get_culprit_name(culprit_id)
        url = "https://slack.com/api/users.list"
        payload = dict(token=token)
        r = requests.post(url, data=payload)
        if r.status_code != 200:
            print r.status_code, r.text
        members = r.json()['members']

        pos = text.find("@") + 1
        user_name = text[pos:].strip()

        user_id = None

        for member in members:
            if member['name'] == user_name:
                user_id = member['id']

        if user_id is None:
            print 'User not found'
        else:
            open_message(user_id, culprit)

def alert_user(channel, culprit):
    import requests
    message = "{} set up us the bomb.!!!".format(culprit)
    url = "https://slack.com/api/chat.postMessage"
    payload = dict(token=token, channel=channel, text=message, as_user=True)
    r = requests.post(url, data=payload)
    print r.status_code


def get_culprit_name(user_id):
    url = "https://slack.com/api/users.info"
    payload = dict(token=token, user=user_id)
    r = requests.post(url, data=payload)
    if r.status_code != 200:
        print r.status_code, r.text
    else:
        return r.json()['user']['name']


def open_message(user_id, culprit):
    url = "https://slack.com/api/im.open"
    payload = dict(token=token, user=user_id)
    r = requests.post(url, data=payload)
    if r.status_code != 200:
        print r.status_code, r.text
    else:
        channel_id = r.json()['channel']['id']
        alert_user(channel_id, culprit)
        bomb_count = randint(2, 10)
        lie_count = randint(2, 100)
        outputs.append([channel_id, "Armed {} bombs".format(lie_count)])
        guid = uuid.uuid4().hex[0:10]
        conn = sqlite3.connect('kevin.db')
        with conn:
            conn.execute("INSERT INTO JOBS (channel, name, parms, status) VALUES (?, 'channel_bomb', ?, 0)",
                         (channel_id, "{},{}".format(guid, bomb_count)))
            conn.execute("INSERT INTO BOMBS (bomb_id, disarm_id, status) VALUES (?, 0, 0)", (guid, ))
            conn.commit()
        # for x in range(0, bomb_count):
        #     timer += randint(5, 10)
        #     print timer
        #     p = Process(target=arm_the_bomb, args=(channel_id, timer, x, bomb_count, guid))
        #     p.start()


#
# def arm_the_bomb(channel, timer, count, total, guid):
#     sleep(timer)
#     conn = sqlite3.connect('kevin.db')
#     with conn:
#         conn.execute("INSERT INTO JOBS (channel, name, parms, status) VALUES (?, 'channel_bomb', ?, 0)",
#                      (channel, "{},{}/{}".format(guid, count, total)))
#         conn.commit()
