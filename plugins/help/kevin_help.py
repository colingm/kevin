import sqlite3
import os
import sys
import glob

from library.checks import check_channel, check_text

outputs = []

def process_message(data):
    # IF ALL CHECKS PASS SEND JOB TO DB
    if 'text' in data:
        text = data['text']
    else:
        text = ''
    if check_channel(data['channel']) and check_text("^kevin help", text):
        commands = ''
        examples = ''
        count = 0
        results = ''
        help_commands = "{}) *kevin help*\n\n" \
                   "{}) *kevin help examples*\n\n" \
                   "{}) *kevin help verbose*\n\n".format(count+1, count+2, count+3)
        count += 3
        directory = os.getcwd()
        for plugin in glob.glob(directory + '/plugins/*'):
            sys.path.insert(0, plugin)
            sys.path.insert(0, directory + "/plugins/")
        for plugin in glob.glob(directory + '/plugins/*.py') + glob.glob(directory + "/plugins/*/*.py"):
            name = plugin.split('/')[-1][:-3]
            module = __import__(name)
            # print module.__name__
            if hasattr(module, 'process_message'):
                # print module.process_message.__doc__
                doc_string = module.process_message.__doc__
                doc_dict = help_builder(doc_string)
                if len(doc_dict) > 0:
                    count += 1
                    results += "{count}) {keyword}\n{summary}\n{see}\n\n".format(count=count, **doc_dict)
                    commands += "{count}) {keyword}\n\n".format(count=count, keyword=doc_dict['keyword'])
                    examples += "{count} {see}\n\n".format(count=count, see=doc_dict['see'])
        if 'example' in text:
            outputs.append([data['channel'], help_commands + examples])
        elif 'verbose' in text:
            outputs.append([data['channel'], help_commands + results])
        else:
            outputs.append([data['channel'], help_commands + commands])

def help_builder(doc_string):
    """
    takes the doc string and turns it into a dict of the doc
    """
    doc_dict = {}
    # SANATIZE DOC LIST
    try:
        doc_list = doc_string.split('\n')
        doc_list = map(lambda x: x.strip().replace('\t', ''), doc_list)
        doc_list = filter(lambda x: len(x) > 0, doc_list)
        for val in doc_list:
            if '@summary' in val:
                doc_dict['summary'] = val[len('@summary'):].strip()
            elif '@keyword' in val:
                doc_dict['keyword'] = val[len('@keyword'):].strip()
            elif '@see' in val:
                doc_dict['see'] = val[len('@see'):].strip()
    except Exception:
        print "Empty Doc String"
    return doc_dict
