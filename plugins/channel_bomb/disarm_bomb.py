import sqlite3
from library.checks import check_channel, check_text

outputs = []

def process_message(data):
    """
    @keyword *disarm bomb:* `^kevin for great justice`
    @summary to disarm a channel bomb, you must do so for great justice.
    @see *disarm bomb:* _*kevin for great justice*_
    """
    # IF ALL CHECKS PASS SEND JOB TO DB
    if 'text' in data:
        text = data['text']
    else:
        text = ''
    print data
    if check_channel(data['channel']) and check_text("^kevin for great justice", text):
        print "DISARMING BOMB"
        conn = sqlite3.connect('kevin.db')
        with conn:
            conn.execute("INSERT INTO JOBS (channel, name, parms, status) VALUES (?, 'disarm_bomb', '', 0)",
                         (data['channel'], ))
            conn.commit()
