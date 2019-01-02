import json
from library.checks import check_channel, check_text

outputs = []
token = ''

def process_message(data):
    """
    @keyword `.*tr-*8r.*`
    @summary who is the team traitor?
    @see _find the *tr8r*_
    """
    # IF ALL CHECKS PASS SEND JOB TO DB
    if 'text' in data:
        text = data['text']
    else:
        text = ''
    if check_channel(data['channel']) and check_text(".*tr-*8r.*", text):
        import requests
        url = "https://slack.com/api/chat.postMessage"
        payload = dict(token=token, channel=data['channel'], as_user=True,
                       attachments=json.dumps([{"color": "#36a64f", "title": "TR-8R",
                                                 "image_url": "http://media0.giphy.com/gifsu/3orifdw1bewQErOomI/giphy-caption.gif"}]))
        r = requests.post(url, data=payload)
        if r.status_code != 200:
            print r.status_code, r.text
