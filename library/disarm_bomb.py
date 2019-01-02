import sqlite3

def main(parms, job_id, channel, *args, **kwargs):
    print "Disarming Bomb"
    # GET THE LATEST BOMB JOB AND UPDATE ITS STATUS
    conn = sqlite3.connect('kevin.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM BOMBS WHERE status = 0")
    row = cur.fetchone()
    print "diarm row: {}".format(row)
    # row[0] = id, row[1] = bomb_id, row[2] = status
    if row is not None:
        # UPDATE THE STATUS
        with conn:
            conn.execute("UPDATE BOMBS SET disarm_id = ?, status = 1 where bomb_id = ?", (job_id, row[1]))
            conn.commit()

