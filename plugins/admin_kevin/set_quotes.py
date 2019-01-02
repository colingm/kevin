import yaml
import sqlite3
import re
from library.checks import check_text

outputs = []


def process_message(data):
    """
     *kevin* _[]_ *quotes* _[]_ *star_wars:{x}* _[]_
     This will set the quote type and quote rate in the config, accepts (star_wars, mad_max)
     _*kevin* I want you to set the *quotes* to *star_wars:2*
    """
    if 'subtype' in data and data['subtype'] == 'message_changed':
        text = data['message']['text']
        if 'user' in data['message']['user']:
            user = data['message']['user']
    elif 'text' in data:
        text = data['text']
        if 'user' in data:
            user = data['user']
    else:
        text = ''
        user = ''
    reg_ex = "^kevin.*quotes.*(star_wars|mad_max):\d"

    if check_text(reg_ex, text):
        # LOAD YAML CONFIG
        config = yaml.load(file('rtmbot.conf', 'r'))
        # GET QUOTE TYPE AND LEVEL
        ret = re.findall("^kevin.*quotes.*(star_wars|mad_max):(\d)", text, re.IGNORECASE)
        if len(ret) > 0:
            quote_type = ret[0][0]
            quote_rate = ret[0][1]
        config['QUOTES'] = quote_type
        config['QUOTE_RATE'] = quote_rate
        yaml.dump(config, file('rtmbot.conf', 'w'))
        # DUMP IT IN THE DB AS WELL SO CHANGES TAKE IMMEDIATE EFFECT
        conn = sqlite3.connect('kevin.db')
        with conn:
            conn.execute("INSERT INTO CHANNELS (channel) VALUES (?) ", (data['channel'].encode('ascii'), ))
            conn.commit()
        # PRINT TO THE CHANNEL SO THAT ONE KNOWS THE JOB WORKED
        outputs.append([data['channel'], "SQUAAAAWWKKK!\n{}".format(config['CHANNELS'])])