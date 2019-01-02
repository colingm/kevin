import sqlite3
import re
from library.checks import check_channel, check_text

outputs = []

def process_message(data):
    """
    @keyword *close ticket:* `^kevin.*close.*ticket.*PC-\d+`
    @summary tired of those pesky prod change tickets just sitting in pending, in progress or open? Then ask kevin to close them
    @see *close ticket:* _*kevin* can you please just *close* the silly *ticket* *PC-1234*_
    """
    # IF ALL CHECKS PASS SEND JOB TO DB
    if 'text' in data:
        text = data['text']
    else:
        text = ''
    if check_channel(data['channel']) and check_text("^kevin.*close.*ticket.*PC-\d+", text):
        # EXTRACT TICKET FROM STATMENT
        comp = re.compile("(PC-\d+)")
        result = comp.findall(text)
        if len(result) != 1:
            print "DIDNT FIND MATCH"
            outputs.append([data['channel'], "DIDNT FIND MATNC"])
        else:
            conn = sqlite3.connect('kevin.db')
            with conn:
                conn.execute("INSERT INTO JOBS (channel, name, parms, status) VALUES (?, 'close_ticket', ?, 0)",
                             (data['channel'], '{}'.format(result[0])))
                conn.commit()
            outputs.append([data['channel'], "SQUAAAAWWKKK {}".format(result[0])])