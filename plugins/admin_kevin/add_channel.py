import yaml
import sqlite3
from library.checks import check_text

outputs = []

def process_message(data):
    """
    @keyword *add channel:* `^kevin.*add.*channel`
    @summary this will add the channel to kevin's listed channels she's allowed to post in. Command only works from an admin
    @see *add channel:* _*kevin* I want you to *add* this *channel*_
    """
    if 'subtype' in data and data['subtype'] == 'message_changed':
        text = data['message']['text']
        if 'user' in data['message']:
            user = data['message']['user']
    elif 'text' in data:
        text = data['text']
        if 'user' in data:
            user = data['user']
    else:
        text = ''
        user = ''
    reg_ex = "^kevin.*add.*channel"

    if check_text(reg_ex, text) and user == 'U03ADBTJ9':
        # LOAD YAML CONFIG AND ADD CHANNEL
        config = yaml.load(file('rtmbot.conf', 'r'))
        config['CHANNELS'].add(data['channel'].encode('ascii'))
        yaml.dump(config, file('rtmbot.conf', 'w'))
        # DUMP IT IN THE DB AS WELL SO CHANGES TAKE IMMEDIATE EFFECT
        conn = sqlite3.connect('kevin.db')
        with conn:
            conn.execute("INSERT INTO CHANNELS (channel) VALUES (?) ", (data['channel'].encode('ascii'), ))
            conn.commit()
        # PRINT TO THE CHANNEL SO THAT ONE KNOWS THE JOB WORKED
        outputs.append([data['channel'], "SQUAAAAWWKKK!\n{}".format(config['CHANNELS'])])

