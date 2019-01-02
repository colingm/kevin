import sqlite3
import requests
import json
from multiprocessing import Process
requests.packages.urllib3.disable_warnings()

token = ''


crontable = []
outputs = []

crontable.append([1, "check_jobs"])

crontable.append([2, 'check_status'])

for_great_justice = False
bomb_id = []


def check_jobs():
    conn = sqlite3.connect('kevin.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM JOBS WHERE status = 0")
    row = cur.fetchone()
    if row is not None:
        print row
        job_id = row[0]
        channel = row[1]
        job_name = row[2]
        parms = row[3]
        status = row[4]
        conn.execute("UPDATE JOBS SET status=1 WHERE id = ?", (job_id, ))
        conn.commit()
        # RUN JOBS
        # FIND JOB IN LIBRARY
        try:
            module = __import__("library.{}".format(job_name), fromlist=["library"])
            func = getattr(module, "main")
            p = Process(target=func, args=(parms, job_id, channel))
            p.start()
        except ImportError as e:
            print "Failed to import {}\n{}".format(job_name, str(e))


def check_status():
    conn = sqlite3.connect('kevin.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM JOBS WHERE status = 1")
    row = cur.fetchone()
    if row is not None:
        # CHECK RESULTS TABLE FOR ID
        cur.execute("SELECT result from RESULTS where job_id = ?", (row[0], ))
        ret = cur.fetchone()
        if ret is not None:
            channel_id = row[1]
            url = "https://slack.com/api/chat.postMessage"
            payload = dict(token=token, channel=channel_id, text=ret[-1], as_user=True)
            requests.post(url, data=payload, verify=False)
            complete_job(row[0])


def complete_job(job_id):
    conn = sqlite3.connect('kevin.db')
    with conn:
        conn.execute("UPDATE JOBS SET status=2 WHERE id = ?", (job_id,))
        conn.commit()
