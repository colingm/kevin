import time
import sqlite3

from library.checks import check_channel, check_text

crontable = []
outputs = []

def process_message(data):
    """
    @keyword *aks kevin a question:* `^kevin.*\?`
    @summary Ask kevin anything you like, and she will try and find an answer for you, or a link for it
    @see *ask kevin a question:* _*kevin what is the average air speed velocity of an unladen swallow?*_
    """
    if 'subtype' in data and data['subtype'] == 'message_changed':
        text = data['message']['text']
    elif 'text' in data:
        text = data['text']
    else:
        text = ''

    reg_ex = "^kevin.*\?"
    bad_ex = ["^kevin.*version.*service", "^kevin.*service.*version", "^kevin.*result.*/[\w\d ]+/[\w\d /.]+/[\w\d/. ]+",
              "^kevin.*add.*channel", "^kevin.*witness me.*"]
    # CHECK ALL THE KNOWN REGEX, CANNOT MATCH ANY OF THESE SO WE DON'T WOLFRAMFOR NO REASON
    match = False
    for reg in bad_ex:
        if check_text(reg, text):
            match = True
            break

    if check_channel(data['channel']):
        if check_text(reg_ex, text) and not match:
            # SEND JOB TO DB
            conn = sqlite3.connect('kevin.db')
            with conn:
                conn.execute("INSERT INTO JOBS (channel, name, parms, status) VALUES (?, 'wolfram', ?, 0)",
                             (data['channel'], text))
                conn.commit()
            outputs.append([data['channel'], "SQUAAAAWWKKK?"])
        elif (text.startswith('kevin') or text.startswith('kevin')) and not match:
            time.sleep(0.5)
            outputs.append([data['channel'], "*SQUAAAAWWKKK!*"])
