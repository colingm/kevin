import sqlite3
import uuid
from random import randint
from time import sleep
from multiprocessing import Process
from library.checks import check_channel, check_text

outputs = []
token = ''

def process_message(data):
    """
    @keyword *channel bomb:* `^kevin.*channel bomb.*`
    @summary send a channel bomb to really get peoples attention.
    @see *channel bomb:* _*kevin* send a giant *channel bomb* right now_
    """
    # IF ALL CHECKS PASS SEND JOB TO DB
    if 'text' in data:
        text = data['text']
    else:
        text = ''
    if check_channel(data['channel']) and check_text("^kevin.*channel bomb.*", text):
        import requests
        url = "https://slack.com/api/reactions.add"
        payload = dict(token=token, name='bomb', channel=data['channel'],
                       timestamp=data['ts'])
        r = requests.post(url, data=payload)
        if r.status_code != 200:
            print r.status_code, r.text
        bomb_count = randint(2, 10)
        lie_count = randint(2, 100)
        outputs.append([data['channel'], "Armed {} bombs".format(lie_count)])
        guid = uuid.uuid4().hex[0:10]
        conn = sqlite3.connect('kevin.db')
        with conn:
            conn.execute("INSERT INTO JOBS (channel, name, parms, status) VALUES (?, 'channel_bomb', ?, 0)",
                         (data['channel'], "{},{}".format(guid, bomb_count)))
            conn.execute("INSERT INTO BOMBS (bomb_id, disarm_id, status) VALUES (?, 0, 0)", (guid, ))
            conn.commit()

def arm_the_bomb(channel, timer, count, total, guid):
    sleep(timer)
    conn = sqlite3.connect('kevin.db')
    with conn:
        conn.execute("INSERT INTO JOBS (channel, name, parms, status) VALUES (?, 'channel_bomb', ?, 0)",
                     (channel, "{},{}/{}".format(guid, count, total)))
        conn.commit()
