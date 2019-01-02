import random
import re
from library.checks import check_channel, check_text

outputs = []
token = ''

gif_list = ['http://heavyeditorial.files.wordpress.com/2012/11/tumblr_me30zwmcd11rozti5o1_500.gif?w=780',
            'http://heavyeditorial.files.wordpress.com/2012/11/tumblr_m413hm0lyl1r4etbjo1_500.gif?w=780',
            'http://heavyeditorial.files.wordpress.com/2012/11/cage-gifs-monster.gif?w=780',
            'http://heavyeditorial.files.wordpress.com/2012/11/tumblr_m4hr2wmzhu1qhp5p0.gif?w=780',
            'http://heavyeditorial.files.wordpress.com/2012/11/tumblr_m3tvb9q9jn1r4etbjo1_500.gif?w=780',
            'http://heavyeditorial.files.wordpress.com/2012/11/tumblr_lykv5dq2of1qid3c0.gif?w=780',
            'http://heavyeditorial.files.wordpress.com/2012/11/tumblr_lybpc3w1mr1r4etbjo1_r1_500.gif?w=780',
            'http://heavyeditorial.files.wordpress.com/2012/11/tumblr_lxx2p0ktpb1r4etbjo1_500.gif?w=780',
            'http://heavyeditorial.files.wordpress.com/2012/11/rip.gif?w=780',
            'http://heavyeditorial.files.wordpress.com/2012/11/not-the-bees.gif?w=780',
            'http://heavyeditorial.files.wordpress.com/2012/12/niccagerainbow.gif?w=780',
            'http://heavyeditorial.files.wordpress.com/2012/11/kiss.gif?w=780',
            'http://heavyeditorial.files.wordpress.com/2012/11/cagellujah.gif?w=780',
            'http://heavyeditorial.files.wordpress.com/2012/11/cage-gifs-skyline.gif?w=780',
            'http://heavyeditorial.files.wordpress.com/2012/11/cage-gifs-getburned.gif?w=780',
            'http://heavyeditorial.files.wordpress.com/2012/11/cage-gifs-dealwithit.gif?w=780',
            'http://heavyeditorial.files.wordpress.com/2012/11/cage-gifs-bear.gif?w=780',
            'http://heavyeditorial.files.wordpress.com/2012/12/crycage.gif?w=780',
            'http://heavyeditorial.files.wordpress.com/2012/12/conair.gif?w=780',
            'http://heavyeditorial.files.wordpress.com/2012/12/exercise.gif?w=780',
            'http://esq.h-cdn.co/assets/cm/15/06/54d3d4cc8f586_-_tumblr_lo22s0nghu1qzxr43.gif',
            'http://esq.h-cdn.co/assets/cm/15/06/54d3d4d1be431_-_6tgk45w.gif',
            'http://www.eonline.com/eol_images/Entire_Site/201506/rs_500x244-150106140226-tumblr_lxerqsvUIA1r4etbjo1_500.gif',
            'http://www.eonline.com/eol_images/Entire_Site/201506/rs_500x283-150106140253-258ee4e087a9069f8b887715e1180f0a.gif',
            'http://www.eonline.com/eol_images/Entire_Site/201506/rs_500x206-150106140308-tumblr_mf058tW94Q1r4etbjo1_500.gif',
            'http://www.eonline.com/eol_images/Entire_Site/201506/rs_500x273-150106140227-tumblr_lxt6e1mHAi1r4etbjo1_r1_500.gif',
            'http://www.eonline.com/eol_images/Entire_Site/201506/rs_500x206-150106140303-tumblr_m0umm5OUJh1r4etbjo1_500.gif',
            'http://cdn0.dailydot.com/uploaded/images/original/2013/1/7/cage8.gif',
            'http://cdn0.dailydot.com/uploaded/images/original/2013/1/7/cage36.gif',
            'http://cdn0.dailydot.com/uploaded/images/original/2013/1/7/cage37.gif',
            'http://cdn0.dailydot.com/uploaded/images/original/2013/1/7/cage42.gif',
            ]

def process_message(data):
    """
    @keyword *cage bomb:* `^(?i)kevin .*teach ([a-zA-Z]+) .*cage.*`
    @summary ever want to make sure your buddy knows more about Nicolas Cage? Kevin can teach them!
    @see *cage bomb:* _*kevin* please *teach* *colinm* about the great Nicolas *Cage*_
    """
    # IF ALL CHECKS PASS SEND JOB TO DB
    if 'text' in data:
        text = data['text']
    else:
        text = ''
    if check_channel(data['channel']) and check_text("^(?i)kevin .*teach ([a-zA-Z]+) .*cage.*", text):
        import requests
        culprit_id = data['user']
        culprit = get_culprit_name(culprit_id)
        url = "https://slack.com/api/users.list"
        payload = dict(token=token)
        r = requests.post(url, data=payload, verify=False)
        if r.status_code != 200:
            print r.status_code, r.text
        members = r.json()['members']

        user_name = re.findall("^(?i)kevin.*teach ([a-zA-Z]+) .*cage.*", text)[0]

        user_id = None

        for member in members:
            if member['name'] == user_name:
                user_id = member['id']

        if user_id is None:
            print 'User not found'
        else:
            open_message(user_id, culprit)


def get_culprit_name(user_id):
    import requests
    url = "https://slack.com/api/users.info"
    payload = dict(token=token, user=user_id)
    r = requests.post(url, data=payload, verify=False)
    if r.status_code != 200:
        print r.status_code, r.text
    else:
        return r.json()['user']['name']


def open_message(user_id, culprit):
    import requests
    url = "https://slack.com/api/im.open"
    payload = dict(token=token, user=user_id)
    r = requests.post(url, data=payload, verify=False)
    if r.status_code != 200:
        print r.status_code, r.text
    else:
        channel_id = r.json()['channel']['id']
        message_person(channel_id, "{} would like to teach you about Cage".format(culprit))
        message_person(channel_id, gif_list[random.randint(0, len(gif_list)-1)])


def message_person(channel, message):
    import requests
    url = "https://slack.com/api/chat.postMessage"
    payload = dict(token=token, channel=channel, text=message, as_user=True)
    requests.post(url, data=payload, verify=False)
