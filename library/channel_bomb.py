import sqlite3
from random import randint
from time import sleep

def main(parms, job_id, channel):
    guid, count = parms.split(',')
    count = int(count)
    print "bomb count: {}".format(count)
    timer = randint(1, 4)
    if count < 1:
        # COMPLETE THE BOMB STATUS IN THE BOMB TABLE
        result = "*bomb!*"
        conn = sqlite3.connect("kevin.db")
        with conn:
            conn.execute("UPDATE BOMBS SET status = 1 where bomb_id = ?", (guid, ))
            conn.execute("INSERT INTO RESULTS (job_id, result) VALUES (?, ?) ", (job_id, result))
            conn.execute("UPDATE JOBS SET status=1 WHERE id = ?", (job_id, ))
            conn.commit()
    else:
        arm_the_bomb(channel, timer, count, guid, job_id)


def arm_the_bomb(channel, timer, count, guid, job_id):
    # SLEEP FOR TIMER
    sleep(timer)
    # CHECK IF BOMB DISABLED
    conn = sqlite3.connect('kevin.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM BOMBS WHERE bomb_id = ? AND status = 1", (guid,))
    # row[0] = id, row[1] = bomb_id row[2] = disarm_id, row[3] = status. 0 = armed, 1 = disarmed
    row = cur.fetchone()
    print "arm the bomb row: {}".format(row)
    # IF DISABLED SEND TO RESULTS SO BOMBS STOP GOING OFF
    if row is not None:
        result = 'Take off every "zig"!! You know what you doing. Move "zig"'
        print result
        with conn:
            conn.execute("INSERT INTO RESULTS (job_id, result) VALUES (?, ?) ", (row[2], result))
            conn.execute("UPDATE JOBS SET status=1 WHERE id = ?", (row[2], ))
            conn.execute("INSERT INTO RESULTS (job_id, result) VALUES (?, ?) ", (job_id, ''))
            conn.execute("UPDATE JOBS SET status=1 WHERE id = ?", (job_id, ))
            conn.commit()
        return
    # SEND RESULT JOB
    result = "<!channel> :bomb:"
    conn = sqlite3.connect('kevin.db')
    with conn:
        print "result: {}".format(result)
        conn.execute("INSERT INTO RESULTS (job_id, result) VALUES (?, ?) ", (job_id, result))
        conn.execute("UPDATE JOBS SET status=1 WHERE id = ?", (job_id, ))
        conn.commit()
    # ARM THE NEXT BOMB
    with conn:
        conn.execute("INSERT INTO JOBS (channel, name, parms, status) VALUES (?, 'channel_bomb', ?, 0)",
                     (channel, "{},{}".format(guid, count - 1)))
        conn.commit()
