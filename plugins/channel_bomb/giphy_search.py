import json
from library.checks import check_channel, check_text

outputs = []
token = ''

def process_message(data):
    """
    @keyword *giphy post:* `^kevin.*post.*[picture|gif|image] of (.*)`
    @summary ever want kevin to post a funny gif, now you can tell him to.
    @see_*kevin* could you *post* a *picture* *of* *Nicholas Cage*_
    """
    # IF ALL CHECKS PASS SEND JOB TO DB
    if 'text' in data:
        text = data['text']
    else:
        text = ''
    if check_channel(data['channel']) and check_text("^kevin.*post.*[picture|gif|image] of .*", text):
        pos = text.find("of") + 2
        image_name = text[pos:].strip()
        image_tag = image_name.replace(" ", "+")
        import requests

        giphy_url = "http://api.giphy.com/v1/gifs/random?api_key=dc6zaTOxFJmzC&rating=pg&tag={}".format(image_tag)
        r = requests.get(giphy_url)
        if r.status_code == 200:
            image_data = r.json()['data']
            if not image_data:
                outputs.append([data['channel'], "*SQUAAAAWWKKK! NOT FOUND!*"])
            else:
                image_url = image_data['image_url']
                url = "https://slack.com/api/chat.postMessage"
                payload = dict(token=token, channel=data['channel'], as_user=True,
                               attachments=json.dumps([{"color": "#36a64f", "title": image_name,
                                                         "image_url": image_url}]))
                r = requests.post(url, data=payload)
                if r.status_code != 200:
                    print r.status_code, r.text
