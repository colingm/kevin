#!/usr/bin/env python

import sys
sys.dont_write_bytecode = True
import glob
import yaml
import os
import sys
import time
import logging
from pymongo import MongoClient
from argparse import ArgumentParser

from slackclient import SlackClient


def dbg(debug_string):
    if debug:
        logging.info(debug_string)


class RtmBot(object):
    def __init__(self, token):
        self.last_ping = 0
        self.token = token
        self.bot_plugins = []
        self.slack_client = None

    def connect(self):
        """Convenience method that creates Server instance"""
        self.slack_client = SlackClient(self.token)
        self.slack_client.rtm_connect()

    def start(self):
        self.connect()
        self.load_plugins()
        while True:
            for reply in self.slack_client.rtm_read():
                self.input(reply)
            self.crons()
            self.output()
            self.autoping()
            time.sleep(.1)

    def autoping(self):
        # hardcode the interval to 3 seconds
        now = int(time.time())
        if now > self.last_ping + 3:
            self.slack_client.server.ping()
            self.last_ping = now

    def input(self, data):
        if "type" in data:
            function_name = "process_" + data["type"]
            dbg("got {}".format(function_name))
            for plugin in self.bot_plugins:
                plugin.register_jobs()
                plugin.do(function_name, data)

    def output(self):
        for plugin in self.bot_plugins:
            limiter = False
            for output in plugin.do_output():
                channel = self.slack_client.server.channels.find(output[0])
                if channel != None and output[1] != None:
                    if limiter == True:
                        time.sleep(.1)
                        limiter = False
                    message = output[1].encode('ascii', 'ignore')
                    channel.send_message("{}".format(message))
                    limiter = True

    def crons(self):
        for plugin in self.bot_plugins:
            plugin.do_jobs()

    def load_plugins(self):
        for plugin in glob.glob(directory + '/plugins/*'):
            sys.path.insert(0, plugin)
            sys.path.insert(0, directory + '/plugins/')
        for plugin in glob.glob(directory + '/plugins/*.py') + glob.glob(directory + '/plugins/*/*.py'):
            logging.info(plugin)
            name = plugin.split('/')[-1][:-3]
            #            try:
            self.bot_plugins.append(Plugin(name))


# except:
#                print "error loading plugin %s" % name

class Plugin(object):
    def __init__(self, name, plugin_config={}):
        self.name = name
        self.jobs = []
        self.module = __import__(name)
        self.register_jobs()
        self.outputs = []
        if name in config:
            logging.info("config found for: " + name)
            self.module.config = config[name]
        if 'setup' in dir(self.module):
            self.module.setup()

    def register_jobs(self):
        if 'crontable' in dir(self.module):
            for interval, function in self.module.crontable:
                self.jobs.append(Job(interval, eval("self.module." + function)))
            logging.info(self.module.crontable)
            self.module.crontable = []
        else:
            self.module.crontable = []

    def do(self, function_name, data):
        if function_name in dir(self.module):
            # this makes the plugin fail with stack trace in debug mode
            if not debug:
                try:
                    eval("self.module." + function_name)(data)
                except:
                    dbg("problem in module {} {}".format(function_name, data))
            else:
                eval("self.module." + function_name)(data)
        if "catch_all" in dir(self.module):
            try:
                self.module.catch_all(data)
            except:
                dbg("problem in catch all")

    def do_jobs(self):
        for job in self.jobs:
            job.check()

    def do_output(self):
        output = []
        while True:
            if 'outputs' in dir(self.module):
                if len(self.module.outputs) > 0:
                    logging.info("output from {}".format(self.module))
                    output.append(self.module.outputs.pop(0))
                else:
                    break
            else:
                self.module.outputs = []
        return output


class Job(object):
    def __init__(self, interval, function):
        self.function = function
        self.interval = interval
        self.lastrun = 0

    def __str__(self):
        return "{} {} {}".format(self.function, self.interval, self.lastrun)

    def __repr__(self):
        return self.__str__()

    def check(self):
        if self.lastrun + self.interval < time.time():
            if not debug:
                try:
                    self.function()
                except:
                    dbg("problem")
            else:
                self.function()
            self.lastrun = time.time()
            pass


class UnknownChannel(Exception):
    pass


def main_loop():
    if "LOGFILE" in config:
        logging.basicConfig(filename=config["LOGFILE"], level=logging.INFO, format='%(asctime)s %(message)s')
    logging.info(directory)
    try:
        bot.start()
    except KeyboardInterrupt:
        sys.exit(0)
    except:
        logging.exception('OOPS')


def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        '-c',
        '--config',
        help='Full path to config file.',
        metavar='path'
    )
    return parser.parse_args()


def init_mongo(db):
    logging.info("Re-Initilizing the DB")
    logging.info("Clearing Old Data")
    for collection in db.collection_names(include_system_collections=False):
        db[collection].drop()
    logging.info("init channels")
    channel = db.channel
    for channel_id in config['CHANNELS']:
        channel.insert({"_id": channel_id})

def init_db():
    import sqlite3

    conn = sqlite3.connect('kevin.db')
    conn.execute('DROP TABLE IF EXISTS JOBS')
    conn.commit()
    conn.execute('DROP TABLE IF EXISTS CHANNELS')
    conn.commit()
    conn.execute('DROP TABLE IF EXISTS RESULTS')
    conn.commit()
    conn.execute('DROP TABLE IF EXISTS SETTINGS')
    conn.commit()
    conn.execute('DROP TABLE IF EXISTS QUOTELIST')
    conn.commit()
    conn.execute('''CREATE TABLE JOBS
              (id INTEGER PRIMARY KEY, channel TEXT, name TEXT, parms TEXT, status INTEGER)''')
    conn.execute('''CREATE TABLE CHANNELS
              (channel TEXT)''')
    for channel in config['CHANNELS']:
        conn.execute("INSERT INTO Channels VALUES (?)", (channel,))
    conn.execute('''CREATE TABLE RESULTS
                (id INTEGER PRIMARY KEY, job_id INTEGER, result TEXT)''')
    conn.commit()
    conn.execute('DROP TABLE IF EXISTS BOMBS')
    conn.commit()
    conn.execute('''CREATE TABLE BOMBS
                  (id INTEGER PRIMARY KEY, bomb_id TEXT, disarm_id TEXT, status INTEGER)''')
    conn.commit()
    conn.execute('''CREATE TABLE SETTINGS
                    (id INTEGER PRIMARY KEY, setting_type TEXT, setting_value TEXT)''')
    conn.commit()
    conn.execute('''CREATE TABLE QUOTELIST
                    (id INTEGER PRIMARY KEY, quote TEXT)''')
    conn.close()


if __name__ == "__main__":
    args = parse_args()
    directory = os.path.dirname(sys.argv[0])
    if not directory.startswith('/'):
        directory = os.path.abspath("{}/{}".format(os.getcwd(), directory))

    config = yaml.load(file(args.config or 'rtmbot.yaml', 'r'))
    connection_string = "mongodb://localhost"
    client = MongoClient('mongo')
    import os
    print os.environ
    db = client.headroom
    debug = config["DEBUG"]
    bot = RtmBot(config["SLACK_TOKEN"])
    site_plugins = []
    files_currently_downloading = []
    job_hash = {}

    if "DAEMON" in config and config["DAEMON"]:
            import daemon

            with daemon.DaemonContext():
                main_loop()
    #init_db()
    init_mongo(db)
    main_loop()
