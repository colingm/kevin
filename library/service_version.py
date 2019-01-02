import requests
import StringIO
from lxml import etree
from time import sleep
import sqlite3
import re
import math

RUNDECK_URL = ''
J_USERNAME = ''
J_PASSWORD = ''
base_url = '{}/api/12'.format(RUNDECK_URL)
headers = {'content-type': 'application/json', "accept": "application/json"}
#args = 'ops.st2'
#job = 'OrgH'

def authenticate():
    """
        Authenticates using username / pass and returns the cookie for the session
        :return cookie dict object
    """
    url = '{}/j_security_check'.format(RUNDECK_URL)
    auth = {'j_username': J_USERNAME, 'j_password': J_PASSWORD}
    r = requests.post(url, allow_redirects=False, params=auth)
    assert r.status_code == 302, "FAILED TO GET AUTH COOKIE"
    cookies = {'JSESSIONID': r.cookies['JSESSIONID']}
    return cookies

def get_job_map(cookies, service):
    """
        Gets the list of jobs and maps them by name / id
        :param cookies: the cookie object to use in the request
        :param service: the name of the service, if service is roll the project is different
        :return mapping of jobs in the format of {"JobName": "IDGUID1234"}
    """
    if 'role' in service.lower():
        params = {"project": "RoleService"}
    else:
        params = {"project": "EmployeeInsights"}
    r = requests.get(base_url + "/jobs", cookies=cookies, headers=headers, params=params)
    assert r.status_code == 200, "FAILED {}:\t{}".format(r.status_code, r.text)
    tree = etree.parse(StringIO.StringIO(r.text))
    job_map = {}
    comp = re.compile("([\w\s]+) Version[s]*")

    for element in tree.xpath("//job[group[text()='Versions']]"):
        job_name = comp.findall(element.xpath("name")[0].text)[0]
        job_id = element.get("id")
        job_map[job_name] = job_id
    return job_map

def start_job(job_id, dc, cookies):
    """
    will execute a job, and wait for it to finish, returning the execution id
    :param job_id: the ID of the job (call get_jobs first)
    :param cookies: The auth cookies to use
    :return: the execution job id
    """
    r = requests.post(base_url + "/job/{}/executions".format(job_id), cookies=cookies, headers=headers, params={'argString': '-dc {}'.format(dc)})
    assert r.status_code == 200, "FAILED {}:\t{}".format(r.status_code, r.text)

    # GET EXECUTION ID
    tree = etree.parse(StringIO.StringIO(r.text))
    execution_id = tree.xpath("//execution")[0].get("id")

    r = requests.get(base_url + "/execution/{}".format(execution_id), cookies=cookies, headers=headers)

    # GET STATUS
    tree = etree.parse(StringIO.StringIO(r.text))
    status = tree.xpath("//execution")[0].get("status")

    while status == 'running':
        sleep(1)
        r = requests.get(base_url + "/execution/{}".format(execution_id), cookies=cookies, headers=headers)

        # GET STATUS
        tree = etree.parse(StringIO.StringIO(r.text))
        status = tree.xpath("//execution")[0].get("status")
    return execution_id


def parse_output(execution_id, cookies):
    """
    Gets the output and returns a handy string
    :param job_id: ID of the execution job to get
    :param cookies: the cookies to use for the authentication (from the authenticate function)
    :return: string format of the results
    """
    results = ''

    # GET OUTPUT
    r = requests.get(base_url + "/execution/{}/output".format(execution_id), cookies=cookies, headers=headers)
    assert r.status_code == 200, "FAILED {}:\t{}".format(r.status_code, r.text)

    result = r.json()

    # GET THE OUTPUT
    output_results = []
    out_results = {}
    bad_nodes = []
    bad_entry = ''
    for entry in result['entries']:
        node = entry['node']
        try:
            if node not in bad_nodes:
                service, version = entry['log'].split(',')
                output_results.append({'service': service, 'version': version, 'node': node})
                if version not in out_results:
                    out_results[version] = dict(nodes=[node], service=service)
                else:
                    out_results[version]['nodes'].append(node)
        except Exception as e:
            bad_nodes.append(node)
            bad_entry += "\n{}: {}".format(node, entry['log'])

    # SORT LIST
    sorted_output = sorted(output_results, key=lambda k: k['version'], reverse=True)
    if len(sorted_output) > 1:
        latest_version = sorted_output[0]['version']
        sorted_output = sorted(output_results, key=lambda k: k['node'])
        results = "{0} [{1}]:  {2:>8}".format(sorted_output[0]['service'], len(sorted_output), latest_version)
    else:
        latest_version = '0.00'

    for output in sorted_output:
        width = abs((len(sorted_output[0]['service']) - len(output['node'])) + len(str(len(sorted_output))) + 11)
        results += "\n{0}:  {1:>{width}}".format(output['node'], output['version'], width=width)
    if len(bad_entry) > 0:
        results += "\nErrors:\n" + bad_entry
    return results



def main(parms, j_id=None, *args, **kw):
    """
    To avoid all the shadow nonsense, making a main
    :param dc: dc to get the version from
    :param service: what to get the version of
    :return:
    """
    dc, service = parms.split(",")
    # AUTHENTICATE
    cookies = authenticate()
    # IF ROLE HAVE TO DO IT SOME OTHER WAY
    # MAKE JOB MAP
    jobs = get_job_map(cookies, service)
    # FIND THE RIGHT JOB
    job_id = None
    for key, value in jobs.items():
        if service in key.lower():
            job_id = value
            break
    # EXECUTE JOB
    if job_id is None:
        print jobs
    else:
        execution_id = start_job(job_id, dc, cookies)
        results = parse_output(execution_id, cookies)
        # GET RESULTS
        if j_id:
            conn = sqlite3.connect('kevin.db')
            with conn:
                conn.execute("INSERT INTO RESULTS (job_id, result) VALUES (?, ?) ", (j_id, results))
                conn.execute("UPDATE JOBS SET status=1 WHERE id = ?", (job_id, ))
                conn.commit()
        else:
            return results


if __name__ == "__main__":
    print main('st2,dashboard')
